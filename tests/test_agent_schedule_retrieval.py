import logging
import uuid

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.agent import start

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def test_agent_schedule_retrieval():
    """Test if the agent can retrieve schedule information for next week."""
    logger.info("🧪 Starting schedule retrieval test")

    # Basic agent configuration
    thread_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    logger.debug(f"⚙️ Configuration: {config}")

    # Ask about schedule for next week
    schedule_query = HumanMessage(
        content="What is scheduled in my calendar for next week?"
    )
    logger.debug(f"📝 Input query: {schedule_query.content}")

    try:
        response = start(input=[schedule_query], config=config)
        logger.info("✅ Schedule retrieval test completed")
        logger.debug(f"📦 Response: {response['messages'][-1]}")
    except Exception as e:
        logger.error("❌ Error during schedule retrieval", exc_info=True)
        raise AssertionError(f"Schedule retrieval failed: {e}") from e

    # Basic validation - just check we got a response
    assert response["messages"][-1] is not None, (
        "Expected a non-null response for schedule query"
    )

    logger.info(
        f"🎉 Schedule retrieval test passed. Response received: {response['messages'][-1]}"
    )
