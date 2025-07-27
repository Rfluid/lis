import logging

from langchain.llms.base import BaseLLM
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableSerializable

from src.config import env
from src.generate_response.model.response import (
    LLMAPIResponse,
    LLMWhatsAppResponse,
)
from src.llm.service import load_model

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class ResponseGenerator:
    model: BaseLLM | BaseChatModel
    chain: RunnableSerializable
    whatsapp_chain: RunnableSerializable

    def __init__(self):
        self.model = load_model(
            env.LLM_PROVIDER,
            env.LLM_MODEL_NAME,
            env.LLM_API_KEY,
            model_stop=env.LLM_STOP,
            model_temperature=env.LLM_TEMPERATURE,
        )
        self.chain = self._load_chain()
        self.whatsapp_chain = self._load_whatsapp_chain()

    def generate_response(
        self,
        # data: Any,
        config: RunnableConfig | None = None,
        query: list | None = None,
    ) -> LLMAPIResponse:
        response = self.chain.invoke(
            {
                "query": query,
            },
            config=config,
        )
        logger.info(f"Response: {response}")
        return LLMAPIResponse.model_validate(response)

    def generate_whatsapp_response(
        self,
        # data: Any,
        config: RunnableConfig | None = None,
        query: list | None = None,
    ) -> LLMWhatsAppResponse:
        response = self.whatsapp_chain.invoke(
            {
                "query": query,
            },
            config=config,
        )
        logger.info(f"Response: {response}")
        return LLMWhatsAppResponse.model_validate(response)

    def _load_chain(self):
        parser = JsonOutputParser(pydantic_object=LLMAPIResponse)
        prompt = PromptTemplate(
            template="""Based on the chat history
{query}
generate a response to the user considering the data retrieved from the tools.

You should also consider to make modify calendar if necessary and respond with the data to do so.

{format_instructions}""",
            input_variables=[
                "query",
                # "data",
            ],
            output_parser=parser,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        return chain

    def _load_whatsapp_chain(self):
        parser = JsonOutputParser(pydantic_object=LLMWhatsAppResponse)
        prompt = PromptTemplate(
            template="""Based on the chat history
{query}
generate a response to the user considering the data retrieved from the tools.

You should also consider to make modify calendar if necessary and respond with the data to do so.

When generating the response in WhatsApp format, you should consider the following:
1. Make heavy use of interactive messages, using buttons and links to make the conversation more engaging.
2. Send media messages only if you have the appropriate data to do so.
3. You will probably not need to send order and some types of messages, so you can ignore them.

{format_instructions}""",
            input_variables=[
                "query",
                # "data",
            ],
            output_parser=parser,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        return chain
