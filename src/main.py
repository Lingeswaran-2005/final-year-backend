from fastapi import FastAPI
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import os
import logging


from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.core.exception_handlers import register_exception_handlers


from src.agent.graph import graph
from src.router.chat_router import router as chat_router
from src.router.cred_router import router as cred_router
from src.db.database import init_db , engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    
    await init_db()

    db_uri = os.getenv("AGENT_DB_URI")

    if db_uri:
        logger.info("Initializing graph with Postgres checkpointer")

        async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
            await checkpointer.setup()
            app.state.graph = graph.compile(
                checkpointer=checkpointer
            )

            yield

    else:
        logger.warning(
            "AGENT_DB_URI not found. "
            "Initializing graph without checkpointer."
        )

        app.state.graph = graph.compile()

        yield
    
    await engine.dispose()

api = FastAPI(lifespan=lifespan)
    
api.include_router(chat_router)
api.include_router(cred_router)

register_exception_handlers(app=api)