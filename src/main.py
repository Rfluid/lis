import logging
from textwrap import dedent

from fastapi import APIRouter, FastAPI

from src.config.env import main
from src.rest.graph import router as graph_router
from src.rest.messages import router as messages_router
from src.rest.threads import router as threads_router
from src.rest.vectorstore import router as vectorstore_router

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.info(f"Initializing {__name__} for environment {main.ENV}...")

# --- Metadata taken from README ------------------------------------------------
app = FastAPI(
    title="Lis Secretary Agent",
    version="0.1.1",  # bump automatically from pyproject/version if you wish
    summary="Lean Interactive Secretary – a lightweight assistant that manages your calendar.",
    description=dedent(
        """
        **Lis** (*Lean Interactive Secretary*) is a personal assistant agent that can
        manage your calendar and schedule meetings for you.

        ### Why “Lis”?
        - **Lightweight Intelligent Support**
        - **Life Information Specialist**
        - **Language-Integrated Secretary**
        - **Lifestyle Integration Scheduler**

        ---

        Full installation and contribution guide in the [README](https://github.com/Rfluid/lis).
        """
    ),
    contact={
        "name": "Ruy Vieira",
        "email": "ruy.vieiraneto@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Tag metadata (shows up as sections in the docs) ---------------------------
tags_metadata = [
    {
        "name": "Messages",
        "description": "Send inputs to the agent.",
    },
    {
        "name": "Threads",
        "description": "Handle thread data.",
    },
    {
        "name": "Graph",
        "description": "Inspect graph details.",
    },
    {
        "name": "Vectorstore",
        "description": "Handle vectorstore data.",
    },
]
app.openapi_tags = tags_metadata

# --- Routes --------------------------------------------------------------------
#
# Agent
agent_router = APIRouter(prefix="/agent")

agent_router.include_router(messages_router, prefix="/messages", tags=["Messages"])
agent_router.include_router(threads_router, prefix="/threads", tags=["Threads"])
agent_router.include_router(graph_router, prefix="/graph", tags=["Graph"])

app.include_router(agent_router)

# Other routes
app.include_router(vectorstore_router, prefix="/vectorstore", tags=["Vectorstore"])
