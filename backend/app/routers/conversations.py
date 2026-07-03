import json
import time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Conversation, Feedback, Message, User, utc_now
from ..schemas import (
    AnswerOut,
    ConversationCreate,
    ConversationDetail,
    ConversationOut,
    ConversationUpdate,
    FeedbackIn,
    FeedbackOut,
    MessageOut,
    QuestionIn,
    SourceOut,
)
from ..security import get_current_user
from ..services.providers import ProviderChain, build_grounded_prompt
from ..services.rate_limit import enforce_rate_limit
from ..services.retrieval import retrieve_sources


router = APIRouter(prefix="/conversations", tags=["conversations"])


def owned_conversation(db: Session, conversation_id: UUID, user: User, with_messages=False) -> Conversation:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
    )
    if with_messages:
        statement = statement.options(selectinload(Conversation.messages))
    conversation = db.scalar(statement)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def answer_conversation(
    db: Session, conversation: Conversation, user: User, question: str
) -> AnswerOut:
    enforce_rate_limit(str(user.id))
    sources = retrieve_sources(db, question)
    if not sources:
        raise HTTPException(status_code=503, detail="The knowledge base is still being prepared")

    user_message = Message(conversation_id=conversation.id, role="user", content=question)
    db.add(user_message)
    db.flush()

    started = time.perf_counter()
    generation = ProviderChain().generate(
        build_grounded_prompt(question, conversation.intention, sources)
    )
    latency_ms = int((time.perf_counter() - started) * 1000)
    citations = [
        {
            **source,
            "chunk_id": str(source["chunk_id"]),
            "document_id": str(source["document_id"]),
        }
        for source in sources
    ]
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=generation.text,
        provider=generation.provider,
        citations=citations,
        latency_ms=latency_ms,
    )
    db.add(assistant_message)
    if conversation.title == "New reflection":
        conversation.title = question[:157] + ("..." if len(question) > 157 else "")
    conversation.updated_at = utc_now()
    db.flush()

    return AnswerOut(
        user_message=MessageOut.model_validate(user_message),
        assistant_message=MessageOut.model_validate(assistant_message),
        sources=[SourceOut(**source) for source in sources],
    )


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    include_archived: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = select(Conversation).where(Conversation.user_id == user.id)
    if not include_archived:
        statement = statement.where(Conversation.archived.is_(False))
    return db.scalars(statement.order_by(Conversation.updated_at.desc())).all()


@router.post("", response_model=ConversationOut, status_code=201)
def create_conversation(
    payload: ConversationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = Conversation(user_id=user.id, title=payload.title, intention=payload.intention)
    db.add(conversation)
    db.flush()
    return conversation


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return owned_conversation(db, conversation_id, user, with_messages=True)


@router.patch("/{conversation_id}", response_model=ConversationOut)
def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = owned_conversation(db, conversation_id, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(conversation, field, value)
    db.flush()
    return conversation


@router.delete("/{conversation_id}", status_code=204)
def archive_conversation(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = owned_conversation(db, conversation_id, user)
    conversation.archived = True
    return Response(status_code=204)


@router.post("/{conversation_id}/messages", response_model=AnswerOut)
def ask_question(
    conversation_id: UUID,
    payload: QuestionIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = owned_conversation(db, conversation_id, user)
    return answer_conversation(db, conversation, user, payload.question.strip())


@router.post("/{conversation_id}/messages/stream")
def stream_question(
    conversation_id: UUID,
    payload: QuestionIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = owned_conversation(db, conversation_id, user)
    answer = answer_conversation(db, conversation, user, payload.question.strip())

    def events():
        yield f"event: meta\ndata: {json.dumps({'message_id': str(answer.assistant_message.id), 'provider': answer.assistant_message.provider})}\n\n"
        words = answer.assistant_message.content.split()
        for index in range(0, len(words), 6):
            yield f"event: token\ndata: {json.dumps({'text': ' '.join(words[index:index + 6]) + ' '})}\n\n"
        yield f"event: sources\ndata: {json.dumps([source.model_dump(mode='json') for source in answer.sources])}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.post("/messages/{message_id}/feedback", response_model=FeedbackOut)
def submit_feedback(
    message_id: UUID,
    payload: FeedbackIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = db.scalar(
        select(Message)
        .join(Conversation)
        .where(Message.id == message_id, Conversation.user_id == user.id, Message.role == "assistant")
    )
    if message is None:
        raise HTTPException(status_code=404, detail="Assistant message not found")
    feedback = db.scalar(select(Feedback).where(Feedback.message_id == message.id))
    if feedback is None:
        feedback = Feedback(message_id=message.id, user_id=user.id, rating=payload.rating)
        db.add(feedback)
    feedback.rating = payload.rating
    feedback.comment = payload.comment
    db.flush()
    return FeedbackOut(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        comment=feedback.comment,
    )


@router.get("/{conversation_id}/export")
def export_conversation(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = owned_conversation(db, conversation_id, user, with_messages=True)
    lines = [f"# {conversation.title}", "", f"Intention: {conversation.intention or 'Not specified'}", ""]
    for message in conversation.messages:
        lines.extend([f"## {message.role.title()}", "", message.content, ""])
    return Response(
        content="\n".join(lines),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="gita-gpt-{conversation.id}.md"'},
    )
