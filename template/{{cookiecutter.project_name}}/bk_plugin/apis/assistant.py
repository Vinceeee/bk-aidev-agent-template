import json
from typing import Optional

from bk_plugin_framework.kit.api import PluginAPIView
from blueapps.core.exceptions import BlueException
from django.http import StreamingHttpResponse
from pydantic.v1 import BaseModel

from bk_plugin.versions.assistant import CommonAgent


class Message(BaseModel):
    role: str
    content: str


class ChatChoice(BaseModel):
    delta: Message


class StreamingResponse(BaseModel):
    type: str = "FinalAnswer"
    choices: list[ChatChoice]
    options: Optional[dict] = None


class AssistantView(PluginAPIView):
    def event_stream(self, data):
        try:
            input = data["inputs"]["input"]
            chat_history = data["inputs"]["chat_history"]
            agent = CommonAgent()
            inputs = agent.Inputs(input=input, chat_history=chat_history)
            agent_e, cfg = agent.create_agent_instance(inputs)
            yield from agent_e.agent.stream_standard_event(
                agent_e, cfg, {"input": inputs.input}, timeout=2
            )
        except Exception as exception:
            ret = {
                "event": "error",
                "code": exception.code if isinstance(exception, BlueException) else 400,
                "message": exception.response_data()
                if isinstance(exception, BlueException)
                else str(exception),
            }
            yield f"data: {json.dumps(ret)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    def post(self, request):
        data = request.data
        sr = StreamingHttpResponse(self.event_stream(data))
        sr.headers["Cache-Control"] = "no-cache"
        sr.headers["X-Accel-Buffering"] = "no"
        sr.headers["content-type"] = "text/event-stream"
        return sr
