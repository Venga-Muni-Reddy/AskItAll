from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    organizations,
    workspaces,
    knowledge_bases,
    documents,
    search,
    chat,
    conversations,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(workspaces.router, tags=["Workspaces"])
api_router.include_router(knowledge_bases.router, tags=["Knowledge Bases"])
api_router.include_router(documents.router, tags=["Documents"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
