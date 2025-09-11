import os

from langchain.llms.base import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableSerializable

from src.config import env
from src.config.env.llm import PARALLEL_GENERATION
from src.evaluate_tools.model import ToolConfig
from src.evaluate_tools.model.tool_config import (
    ToolConfigWithResponse,
    ToolConfigWithWhatsAppResponse,
)
from src.llm.service import load_model


class EvaluateTools:
    model: BaseLLM | BaseChatModel
    prompt: str
    chain: RunnableSerializable
    whatsapp_chain: RunnableSerializable
    output_class = ToolConfig

    def __init__(self):
        if PARALLEL_GENERATION:
            self.output_class = ToolConfigWithResponse

        self.model = load_model(
            env.TOOL_EVALUATOR_LLM_PROVIDER,
            env.TOOL_EVALUATOR_LLM_MODEL_NAME,
            env.TOOL_EVALUATOR_LLM_API_KEY,
            model_stop=env.TOOL_EVALUATOR_LLM_STOP,
            model_temperature=env.TOOL_EVALUATOR_LLM_TEMPERATURE,
            **env.TOOL_EVALUATOR_LLM_KWARGS,
        )
        self.prompt = self._load_prompt()
        self.chain = self._load_chain()

        if PARALLEL_GENERATION:
            self.whatsapp_chain = self._load_whatsapp_chain()

    def decide_next_step(
        self,
        config: RunnableConfig | None = None,
        query: list | None = None,
    ) -> ToolConfig | ToolConfigWithResponse:
        response = self.chain.invoke(
            {
                "query": query,
            },
            config=config,
        )

        return self.output_class.model_validate(response)

    def decide_whatsapp_next_step(
        self,
        config: RunnableConfig | None = None,
        query: list | None = None,
    ) -> ToolConfigWithWhatsAppResponse:
        response = self.chain.invoke(
            {
                "query": query,
            },
            config=config,
        )

        return ToolConfigWithWhatsAppResponse.model_validate(response)

    def _load_prompt(self) -> str:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        prompt_dir = os.path.join(root_dir, "prompts")
        primary_path = os.path.join(prompt_dir, "evaluate_tools.md")
        fallback_file = "evaluate_tools.example.md"
        if PARALLEL_GENERATION:
            fallback_file = "evaluate_tools_parallel.example.md"
        fallback_path = os.path.join(prompt_dir, fallback_file)

        if os.path.isfile(primary_path):
            with open(primary_path, encoding="utf-8") as f:
                return f.read()
        elif os.path.isfile(fallback_path):
            with open(fallback_path, encoding="utf-8") as f:
                return f.read()
        else:
            raise FileNotFoundError(
                f"Neither prompts/evaluate_tools.md nor prompts/${fallback_file} found."
            )

    def _load_chain(self):
        parser = JsonOutputParser(pydantic_object=self.output_class)
        prompt = PromptTemplate(
            template=f"{self.prompt}",
            input_variables=[
                "query",
            ],
            output_parser=parser,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        return chain

    def _load_whatsapp_chain(self):
        parser = JsonOutputParser(pydantic_object=ToolConfigWithWhatsAppResponse)
        prompt = PromptTemplate(
            template=f"{self.prompt}",
            input_variables=[
                "query",
            ],
            output_parser=parser,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        return chain
