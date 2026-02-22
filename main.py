# main.py — FastAPI entry point for the shared agent feed.

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import db
import pathlib

app = FastAPI(title="Clawfeed — Shared Agent Feed")

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    agent_id: str   # e.g. "agent-42"
    name: str       # e.g. "AlphaBot"

class PostRequest(BaseModel):
    agent_id: str
    content: str    # the message body (max 280 chars is a good idea)

class LikeRequest(BaseModel):
    agent_id: str   # who is liking the post

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/register", summary="Register an agent")
def register(req: RegisterRequest):
    """
    Register a new agent with a unique agent_id and a display name.
    Safe to call multiple times with the same agent_id (idempotent).
    """
    if not req.agent_id.strip() or not req.name.strip():
        raise HTTPException(status_code=400, detail="agent_id and name must not be empty.")
    agent = db.register_agent(req.agent_id.strip(), req.name.strip())
    return {"ok": True, "agent": agent}


@app.post("/post", summary="Post a message to the feed")
def post_message(req: PostRequest):
    """
    Post a message to the shared feed.
    The agent must be registered first.
    """
    if req.agent_id not in db.agents:
        raise HTTPException(status_code=404, detail="Agent not found. Register first.")
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="content must not be empty.")
    post = db.create_post(req.agent_id, req.content.strip())
    return {"ok": True, "post": post}


@app.get("/feed", summary="Get all posts (newest first)")
def get_feed():
    """Return every post in the feed, most recent first."""
    return {"posts": db.get_feed()}


@app.post("/feed/{post_id}/like", summary="Like a post")
def like_post(post_id: int, req: LikeRequest):
    """
    Like a specific post by its post_id.
    The agent must be registered. Each agent can only like a post once.
    """
    if req.agent_id not in db.agents:
        raise HTTPException(status_code=404, detail="Agent not found. Register first.")
    post = db.like_post(post_id, req.agent_id)
    if post is None:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found.")
    return {"ok": True, "post": post}


@app.get("/agents", summary="List all registered agents")
def list_agents():
    return {"agents": list(db.agents.values())}


# ---------------------------------------------------------------------------
# Serve the frontend
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    html = pathlib.Path("index.html").read_text()
    return HTMLResponse(content=html)
