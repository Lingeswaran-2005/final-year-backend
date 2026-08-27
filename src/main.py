from fastapi import FastAPI
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import os

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver

from src.utils.helper_functions import extract_text
from src.graph import graph
from src.dto import ChatResponse , ChatRequest

graph_app = None

@asynccontextmanager
async def lifespan(api :FastAPI) :
    load_dotenv()
    
    global graph_app
    
    AGENT_DB_URI = os.getenv('AGENT_DB_URI')
    
    with PostgresSaver.from_conn_string(AGENT_DB_URI) as checkpointer:
        checkpointer.setup()
    
        graph_app = graph.compile(checkpointer= checkpointer)
    
        yield

api = FastAPI(lifespan= lifespan)
    

@api.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    config = {
        "configurable":{
            "thread_id":"user_1"
        }
    }
    result = graph_app.invoke({
        "messages": [
            HumanMessage(content=request.message)
        ]
    },
        config=config
    )

    response = result["messages"][-1]
    content = extract_text(response.content)

    return ChatResponse(
        response=content
    )
    