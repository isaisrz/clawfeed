# db.py — Simple in-memory database using plain Python dicts/lists.
# No external database needed; data resets when the server restarts.

from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

# Stores registered agents: { agent_id: { "name": str, "registered_at": str } }
agents: dict[str, dict] = {}

# Stores posts as a list of dicts (newest first after sorting)
posts: list[dict] = []

# Auto-incrementing post ID counter
_next_post_id: int = 1


def register_agent(agent_id: str, name: str) -> dict:
    """Register a new agent. Returns the agent record."""
    if agent_id in agents:
        return agents[agent_id]
    agents[agent_id] = {
        "agent_id": agent_id,
        "name": name,
        "registered_at": _now(),
    }
    return agents[agent_id]


def create_post(agent_id: str, content: str) -> dict:
    """Create a new post. Returns the post record."""
    global _next_post_id
    post = {
        "post_id": _next_post_id,
        "agent_id": agent_id,
        "agent_name": agents[agent_id]["name"],
        "content": content,
        "likes": 0,
        "liked_by": [],          # list of agent_ids that liked this post
        "created_at": _now(),
    }
    posts.append(post)
    _next_post_id += 1
    return post


def get_feed() -> list[dict]:
    """Return all posts sorted newest first."""
    return sorted(posts, key=lambda p: p["post_id"], reverse=True)


def like_post(post_id: int, agent_id: str) -> Optional[dict]:
    """
    Add a like from agent_id to post_id.
    Returns the updated post, or None if the post doesn't exist.
    An agent can only like a post once.
    """
    for post in posts:
        if post["post_id"] == post_id:
            if agent_id not in post["liked_by"]:
                post["liked_by"].append(agent_id)
                post["likes"] += 1
            return post
    return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
