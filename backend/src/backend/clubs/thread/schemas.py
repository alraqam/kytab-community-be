from datetime import datetime

from pydantic import BaseModel


class CreateThread(BaseModel):
    title: str

class UpdateThread(BaseModel):
    title: str

class GetThread(BaseModel):
    id: int
    session_id: int | None = None
    milestone_id: int | None = None
    is_general: bool
    title: str
    created_by_id: int
    is_locked: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

class CreatePost(BaseModel):
    parent_post_id: int | None = None
    title: str
    body: str
    is_spoiler: bool

class UpdatePost(BaseModel):
    title: str | None = None
    body: str | None = None
    is_spoiler: bool | None = None

class GetPost(BaseModel):
    id: int
    thread_id: int
    parent_post_id: int | None = None
    author_id: int
    title: str
    body: str
    is_spoiler: bool
    edited_at: datetime | None = None
    deleted_at: datetime | None = None
    created_at: datetime

class GetPostPartial(BaseModel):
    id: int
    thread_id: int
    parent_post_id: int | None = None
    author_id: int
    title: str
    is_spoiler: bool
    edited_at: datetime | None = None
    deleted_at: datetime | None = None
    created_at: datetime

class CreatePostReaction(BaseModel):
    emoji: str

class GetPostReaction(BaseModel):
    id: int
    post_id: int
    user_id: int
    emoji: str