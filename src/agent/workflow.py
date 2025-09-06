import logging
from collections import Counter
from datetime import datetime
from typing import cast

from fastapi import HTTPException
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row

from src.agent.model.chat_interface import ChatInterface
from src.agent.model.graph_state import GraphState
from src.agent.model.steps import Steps
from src.agent.model.tool_data import ToolData
from src.calendar_manager.main import CalendarManager
from src.calendar_manager.model.retrieve_events import RetrieveEvents
from src.config import env
from src.error_handler import ErrorHandler
from src.evaluate_tools.main import EvaluateTools
from src.generate_response import ResponseGenerator
from src.generate_response.model.response import BaseLLMResponse
from src.summarize.main import Summarizer
from src.system_prompt.main import SystemPromptBuilder
from src.vector_manager.main import VectorManager

# from psycopg import Connection  # ⇐ open sync conn
# from psycopg.rows import dict_row  # ⇐ row factory

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class Workflow(SystemPromptBuilder):
    tool_evaluator: EvaluateTools
    response_generator: ResponseGenerator
    calendar_manager: CalendarManager
    graph: StateGraph
    compiled_graph: CompiledStateGraph | None
    memory: BaseCheckpointSaver | None
    vector_manager: VectorManager
    summarizer: Summarizer

    def __init__(self) -> None:
        super().__init__()
        self.tool_evaluator = EvaluateTools()
        self.response_generator = ResponseGenerator()
        self.calendar_manager = CalendarManager()
        self.vector_manager = VectorManager()
        self.error_handler = ErrorHandler()

        self.graph = self._load_graph()
        self.memory = None
        self.compiled_graph = None
        self._db_conn: AsyncConnection[DictRow] | None = (
            None  # keep to close later if you want
        )

    async def ensure_ready(self) -> None:
        """Idempotent: prepares memory + compiles graph once."""
        if self.compiled_graph is not None:
            return
        self.memory = await self._load_memory()
        self.compiled_graph = self.graph.compile(checkpointer=self.memory)

    def context_incrementer(self, state: GraphState) -> GraphState:
        state.step_history.append(Steps.context_incrementer)
        state.messages = state.input

        if state.function == "context_incrementer":
            state.next_step = Steps.end
            return state

        state.next_step = Steps.context_builder
        return state

    # Build the context for the AI.
    def context_builder(self, state: GraphState) -> GraphState:
        state.step_history.append(Steps.context_builder)

        # Check if the universal context have been passed
        if len(state.messages) > 2:
            return state

        agent_context = SystemMessage(content=self.prompt)
        state.messages = [agent_context]

        return state

    # Build the context for the AI.
    def get_current_date(self, state: GraphState) -> GraphState:
        state.step_history.append(Steps.get_current_date)

        date_context = SystemMessage(content=f"Current date is: {str(datetime.now())}")

        state.messages = [date_context]

        return state

    def generate_response(
        self,
        state: GraphState,
        config: RunnableConfig | None = None,
    ) -> GraphState:
        state.step_history.append(Steps.generate_response)
        try:
            match state.chat_interface:
                case ChatInterface.api:
                    response = self.response_generator.generate_response(
                        config,
                        state.messages,
                    )
                case ChatInterface.whatsapp:
                    response = self.response_generator.generate_whatsapp_response(
                        config,
                        state.messages,
                    )

            state.next_step = Steps(response.next_step)

            ai_message = AIMessage(content=[response.model_dump()])
            state.response = ai_message
            state.messages = [ai_message]
        except Exception as e:
            state.error = str(e)
            state.next_step = Steps.error_handler

        return state

    def decide_next_step(
        self,
        state: GraphState,
        config: RunnableConfig | None = None,
    ) -> GraphState:
        state.step_history.append(Steps.evaluate_tools)
        try:
            # Preventing double injection of context and loops
            if self._is_looping(
                state.step_history,
                state.loop_threshold,
            ):
                raise ValueError(
                    f"Loop detected in step history: {state.step_history}. "
                    f"The loop threshold ({state.loop_threshold}) was exceeded due to repeated steps."
                )
            # if state.previous_step == Steps(response.tool):
            #     state.previous_step = Steps.evaluate_tools
            #     raise ValueError("Loop detected: Tool already used.")

            response = self.tool_evaluator.decide_next_step(
                config,
                state.messages,  # Verify need
            )

            ai_message = SystemMessage(content=[response.model_dump()])
            state.messages = [ai_message]

            state.next_step = Steps(response.tool)
            calendar_manager_payload = response.search_calendars
            if calendar_manager_payload is not None:
                retrieve_events_obj = RetrieveEvents.model_validate(
                    calendar_manager_payload
                )
                state.tool_payloads.search_calendars = retrieve_events_obj
            rag_query = response.rag_query
            if rag_query is not None:
                state.tool_payloads.rag_query = rag_query

        except Exception as e:
            state.error = str(e)
            state.next_step = Steps.error_handler

        return state

    def search_calendars(self, state: GraphState) -> GraphState:
        state.step_history.append(Steps.search_calendars)
        try:
            payload = state.tool_payloads.search_calendars
            if not payload:
                raise ValueError("No payload provided for calendar manager.")

            events = self.calendar_manager.retrieve_events(payload)

            ai_response = SystemMessage(
                content=[
                    # This are the different ways I tested to attach the calendar data. Most of them give serialization errors.
                    # "Data retrieved from the calendar", events,
                    # {"data": events, "label": "Data retrieved from the calendar"},
                    # f"Data retrieved from the calendar: {events}", # This one works
                    str(
                        ToolData(
                            data=events,
                            label=f"All events scheduled between {payload.start_time} and {payload.end_time} retrieved at {Steps.search_calendars}",
                        )
                    ),
                ]
            )
            state.messages = [ai_response]

            state.next_step = Steps.evaluate_tools
        except Exception as e:
            state.error = str(e)
            state.next_step = Steps.error_handler

        return state

    def modify_calendar(self, state: GraphState) -> GraphState:
        state.step_history.append(Steps.modify_calendar)
        try:
            state.next_step = Steps.end

            message = state.messages[-1]
            logger.info(f"Modifying calendar with message: {message}")
            content = message.content[0]

            # Parse the last message as LLMResponse
            llm_response = BaseLLMResponse.model_validate(content)

            payloads = llm_response.action_payloads
            if payloads is None:
                return state

            modification_logs: list[BaseMessage] = []
            # confirmations = llm_response.action_confirmations

            # Execute create
            if payloads.create_events:  # and confirmations.create_events:
                created = self.calendar_manager.create_events(payloads.create_events)
                system_message = SystemMessage(content=f"Created events: {created}")
                modification_logs.append(system_message)
                logger.info(f"Created events: {[e['id'] for e in created]}")

            # Execute update
            if payloads.update_events:  # and confirmations.update_events:
                updated = self.calendar_manager.update_events(payloads.update_events)
                system_message = SystemMessage(content=f"Updated events: {updated}")
                modification_logs.append(system_message)
                logger.info(f"Updated events: {[e['id'] for e in updated]}")

            # Execute delete
            if payloads.delete_events:  # and confirmations.delete_events:
                self.calendar_manager.delete_events(payloads.delete_events)
                system_message = SystemMessage(
                    content=f"Deleted events: {payloads.delete_events}"
                )
                modification_logs.append(system_message)
                logger.info("Deleted events.")

            if len(modification_logs) > 0:
                state.messages = modification_logs
        except Exception as e:
            state.error = str(e)
            state.next_step = Steps.error_handler

        return state

    def rag(self, state: GraphState) -> GraphState:
        state.step_history.append(Steps.rag)
        try:
            query = state.tool_payloads.rag_query
            if not isinstance(query, str):
                raise ValueError("Expected the query to be a string.")

            logger.info(f"Running RAG retrieval for query: {query}")

            # Retrieve relevant documents from the vectorstore
            retrieved_docs = self.vector_manager.retrieve(
                query=query, top_k=state.top_k
            )

            logger.info(f"Retrieved {len(retrieved_docs)} documents.")

            # Create a new SystemMessage with the retrieved documents
            documents_message = SystemMessage(
                content=[
                    str(
                        ToolData(
                            data=retrieved_docs,
                            label=f"Knowledge base documents retrieved for: '{query}'",
                        )
                    )
                ]
            )

            # Update the messages in state
            state.messages = [documents_message]
            state.next_step = Steps.evaluate_tools

        except Exception as e:
            logger.error(f"Error during RAG retrieval: {str(e)}", exc_info=True)
            state.error = str(e)
            state.next_step = Steps.error_handler

        return state

    def handle_error(self, state: GraphState) -> GraphState:
        state.step_history.append(Steps.error_handler)
        if state.error is None:
            raise ValueError("No error to handle.")

        if state.current_retries >= state.max_retries:
            raise HTTPException(status_code=500, detail=state.error)

        state.current_retries += 1

        handling_context = self.error_handler.handle(state.error)

        state.messages = [handling_context]

        state.next_step = Steps.evaluate_tools

        return state

    def _is_looping(self, step_history: list[Steps], threshold: int) -> bool:
        counts = Counter(step_history)
        most_common_step, count = counts.most_common(1)[0]
        return count > threshold

    # ---------- internal helpers ---------- #
    def _load_graph(self) -> StateGraph:
        graph = StateGraph(GraphState)

        # Setup nodes
        graph.add_node(str(Steps.context_incrementer), self.context_incrementer)
        graph.add_node(str(Steps.context_builder), self.context_builder)
        graph.add_node(str(Steps.evaluate_tools), self.decide_next_step)
        graph.add_node(str(Steps.generate_response), self.generate_response)
        graph.add_node(str(Steps.search_calendars), self.search_calendars)
        graph.add_node(str(Steps.get_current_date), self.get_current_date)
        graph.add_node(str(Steps.modify_calendar), self.modify_calendar)
        graph.add_node(str(Steps.rag), self.rag)
        graph.add_node(str(Steps.error_handler), self.handle_error)

        # Setup edges
        graph.set_entry_point(str(Steps.context_incrementer))
        graph.add_conditional_edges(
            str(Steps.context_incrementer),
            lambda x: x.next_step,
            {
                Steps.context_builder: str(Steps.context_builder),
                Steps.end: END,
            },
        )
        graph.add_edge(str(Steps.context_builder), str(Steps.evaluate_tools))
        graph.add_conditional_edges(
            str(Steps.evaluate_tools),
            lambda x: x.next_step,
            {
                Steps.search_calendars: str(Steps.search_calendars),
                Steps.get_current_date: str(Steps.get_current_date),
                Steps.rag: str(Steps.rag),
                Steps.generate_response: str(Steps.generate_response),
                Steps.error_handler: str(Steps.error_handler),
            },
        )
        graph.add_edge(str(Steps.get_current_date), str(Steps.evaluate_tools))
        graph.add_conditional_edges(
            str(Steps.search_calendars),
            lambda x: x.next_step,
            {
                Steps.evaluate_tools: str(Steps.evaluate_tools),
                Steps.error_handler: str(Steps.error_handler),
            },
        )
        graph.add_conditional_edges(
            str(Steps.rag),
            lambda x: x.next_step,
            {
                Steps.evaluate_tools: str(Steps.evaluate_tools),
                Steps.error_handler: str(Steps.error_handler),
            },
        )
        graph.add_conditional_edges(
            str(Steps.generate_response),
            lambda x: x.next_step,
            {
                Steps.modify_calendar: str(Steps.modify_calendar),
                Steps.end: END,
                Steps.error_handler: str(Steps.error_handler),
            },
        )
        graph.add_conditional_edges(
            str(Steps.modify_calendar),
            lambda x: x.next_step,
            {
                Steps.end: END,
                Steps.error_handler: str(Steps.error_handler),
            },
        )

        graph.add_conditional_edges(
            str(Steps.error_handler),
            lambda x: x.next_step,
            {
                Steps.evaluate_tools: str(Steps.evaluate_tools),
                Steps.end: END,
            },
        )

        return graph

    async def _load_memory(self) -> BaseCheckpointSaver:
        uri = env.POSTGRES_URI
        if uri:
            conn = await AsyncConnection.connect(
                uri,
                autocommit=True,
                prepare_threshold=0,
            )
            conn.row_factory = dict_row  # type: ignore[assignment]
            self._db_conn = cast(AsyncConnection[DictRow], conn)

            saver = AsyncPostgresSaver(self._db_conn)
            await saver.setup()  # one-time DDL
            return saver

        # fallback when no PG URI
        return MemorySaver()
