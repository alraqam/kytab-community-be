from datetime import datetime

from pydantic import BaseModel


class CreateThread(BaseModel):
    """Request payload for creating a thread."""

    title: str

class UpdateThread(BaseModel):
    """Request payload for updating a thread's title."""

    title: str

class GetThread(BaseModel):
    """Response payload representing a thread."""

    id: int
    session_id: int | None = None
    milestone_id: int | None = None
    is_general: bool
    title: str
    created_by_id: int | None = None
    created_by_username: str | None = None
    is_locked: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

class CreatePost(BaseModel):
    """Request payload for creating a post."""

    parent_post_id: int | None = None
    title: str
    body: str
    is_spoiler: bool

class UpdatePost(BaseModel):
    """Request payload for updating a post's title, body, and/or spoiler flag."""

    title: str | None = None
    body: str | None = None
    is_spoiler: bool | None = None

class GetPost(BaseModel):
    """Response payload representing a post, including its body."""

    id: int
    thread_id: int
    parent_post_id: int | None = None
    author_id: int | None = None
    author_username: str | None = None
    title: str
    body: str
    is_spoiler: bool
    edited_at: datetime | None = None
    deleted_at: datetime | None = None
    created_at: datetime

class GetPostPartial(BaseModel):
    """Response payload representing a post with its body withheld, used for spoiler-safe listings."""

    id: int
    thread_id: int
    parent_post_id: int | None = None
    author_id: int | None = None
    author_username: str | None = None
    title: str
    is_spoiler: bool
    edited_at: datetime | None = None
    deleted_at: datetime | None = None
    created_at: datetime

class CreatePostReaction(BaseModel):
    """Request payload for creating a reaction on a post."""

    emoji: str

class GetPostReaction(BaseModel):
    """Response payload representing a reaction on a post."""

    id: int
    post_id: int
    user_id: int | None = None
    username: str | None = None
    emoji: str
