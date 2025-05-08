from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from .chat import (
    ChatCompletionViewSet,
    ChatSessionContentViewSet,
    ChatSessionViewSet,
    IndexView,
    AgentInfoView
)

_router = DefaultRouter()
_router.register("session", ChatSessionViewSet, "chat_session")
_router.register("session_content", ChatSessionContentViewSet, "chat_session_content")
_router.register("chat_completion", ChatCompletionViewSet, "chat_completion")

urlpatterns = [
    re_path(r"chat/", include(_router.urls)),
    re_path(r"index", IndexView.as_view()),
    re_path(r"agent", AgentInfoView.as_view()),
]
