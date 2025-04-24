"""
通用 assistant agent 插件。

若非定制开发，只修改 assistant_components.py 文件即可，请勿修改本文件。
"""

import os
from threading import RLock
from typing import Dict, List, Optional

from aidev_extend.core.agent.qa import CommonQAAgent
from aidev_extend.core.models.llm_gateway import ChatModel
from aidev_extend.core.resource import get_client_by_username
from bk_plugin_framework.kit import Context, ContextRequire, Field, FormModel, InputsModel, OutputsModel, Plugin
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from langchain_core.stores import InMemoryBaseStore
from langchain_openai.chat_models.base import _convert_message_to_dict

from .assistant_components import (
    chat_model,
    intent_recognition_kwargs,
    knowledge_ids,
    knowledgebase_ids,
    role_prompt,
    tool_ids,
)


class CommonAgent(Plugin):
    class Meta:
        # 固定,不需要修改,一旦修改会影响访问路径
        version = "0.1.24assistant"
        desc = "Common AI agent from AIDev"

    class Inputs(InputsModel):
        input: str
        chat_history: list

    class Outputs(OutputsModel):
        intermediate_steps: list
        chat_history: list
        output: str
        input: str

    class ContextInputs(ContextRequire):
        executor: str = Field(title="任务执行人")

    class InputsForm(FormModel):
        input = {"ui:component": {"name": "bk-input", "props": {"type": "string"}}}
        chat_history = {
            "type": "array",
            "title": "chat_history",
            "items": {
                "type": "object",
                "title": "history",
                "properties": {
                    "role": {"type": "string", "title": "role"},
                    "content": {"type": "string", "title": "content"},
                },
            },
        }

    assets_list: List[Dict] = []
    lock = RLock()
    setup = False

    def __init__(self):
        super().__init__()
        if not self.__class__.setup:
            self.__class__.setup = True

    def create_agent_instance(self, inputs: Optional[Inputs] = None):
        """实例化一个agent"""
        client = get_client_by_username(username=AnonymousUser.username)
        tools = [client.construct_tool(tool_id) for tool_id in tool_ids]
        knowledge_items = [
            client.api.appspace_retrieve_knowledge(path_params={"id": id_})["data"] for id_ in knowledge_ids
        ]
        knowledge_bases = [
            client.api.appspace_retrieve_knowledgebase(path_params={"id": id_})["data"] for id_ in knowledgebase_ids
        ]
        # ====================================================================================================
        # 启用配置项，仅做兼容。deprecated。
        kb_model = ChatModel.get_setup_instance(
            model=os.environ.get("BKAIDEV_AGENT_LLM", "hunyuan-turbo"),
            streaming=True,
            default_query=dict(bk_app_code=settings.BK_APP_CODE, bk_app_secret=settings.BK_APP_SECRET),
        )
        file_store = InMemoryBaseStore()
        doc_store = InMemoryBaseStore()
        # ====================================================================================================
        agent_e, cfg = CommonQAAgent.get_agent_executor(
            chat_model,
            kb_model,
            file_store,
            doc_store,
            role_prompt=role_prompt,
            chat_history=inputs.chat_history if inputs and inputs.chat_history else [],
            assets_list=self.assets_list,
            extra_tools=tools,
            knowledge_items=knowledge_items,
            knowledge_bases=knowledge_bases,
            intent_recognition_kwargs=intent_recognition_kwargs,
        )
        return agent_e, cfg

    def execute(self, inputs: Inputs, context: Context):
        agent_e, cfg = self.create_agent_instance(inputs)
        ret = agent_e.invoke(inputs.dict(), config=cfg)
        ret["chat_history"] = [_convert_message_to_dict(m) for m in ret["chat_history"]]
        context.outputs = ret
