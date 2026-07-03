from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    display_name: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class DevLoginIn(BaseModel):
    email: str = Field(default="admin@gitagpt.local", max_length=320)
    display_name: str = Field(default="Arjuna", min_length=1, max_length=120)


class GoogleLoginIn(BaseModel):
    credential: str = Field(min_length=20)


class RuntimeConfigOut(BaseModel):
    auth_mode: str
    google_client_id: str
    providers: list[str]
    features: list[str]


class ConversationCreate(BaseModel):
    title: str = Field(default="New reflection", min_length=1, max_length=160)
    intention: str = Field(default="", max_length=500)


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    archived: bool | None = None


class SourceOut(BaseModel):
    chunk_id: UUID
    document_id: UUID
    title: str
    translation: str
    page_number: int | None
    excerpt: str
    score: float


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    provider: str | None
    citations: list[dict]
    latency_ms: int | None
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    intention: str
    archived: bool
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]


class QuestionIn(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


class AnswerOut(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    sources: list[SourceOut]


class FeedbackIn(BaseModel):
    rating: int = Field(ge=-1, le=1)
    comment: str = Field(default="", max_length=1000)


class FeedbackOut(BaseModel):
    id: UUID
    message_id: UUID
    rating: int
    comment: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    translation: str
    filename: str
    checksum: str
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime


class BookmarkCreate(BaseModel):
    chunk_id: UUID
    note: str = Field(default="", max_length=500)


class BookmarkOut(BaseModel):
    id: UUID
    chunk_id: UUID
    note: str
    created_at: datetime
    source: SourceOut


class DailyWisdomOut(BaseModel):
    source: SourceOut
    reflection: str
