from django.urls import path
from .assistant import AssistantView

urlpatterns = [
    path(r"assistant/", AssistantView.as_view()),
]