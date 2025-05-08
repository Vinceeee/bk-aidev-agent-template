<template>
  <div class="article">
    <h1>BK AI: Revolutionizing the Future of Artificial Intelligence</h1>
    <p>In the rapidly evolving world of technology, artificial intelligence (AI) has emerged as a game-changer, offering unprecedented capabilities to transform industries and redefine human experiences. Among the various players in this dynamic field, BK AI stands out as a beacon of innovation, dedicated to pushing the boundaries of what AI can achieve.

BK AI was founded with a clear vision: to harness the power of AI to create solutions that are not only intelligent but also intuitive, efficient, and scalable. The company's name, BK, is a nod to its founders' belief in the power of knowledge and its ability to drive progress. BK AI is committed to advancing AI research and development, while also ensuring that its technologies are accessible and beneficial to a wide range of industries and applications.

At the core of BK AI's success is its commitment to research and development. The company boasts a team of world-class researchers and engineers who are dedicated to exploring the latest advancements in AI and machine learning. This team is responsible for developing cutting-edge algorithms, models, and tools that are used to power BK AI's products and services.

One of the key areas where BK AI excels is in natural language processing (NLP). The company's NLP technology is designed to understand and interpret human language, enabling machines to interact with humans in a more natural and intuitive way. This has applications in a wide range of fields, from customer service and support to content creation and translation.

Another area of focus for BK AI is computer vision. The company's computer vision technology enables machines to interpret and understand visual information from the world around them. This has applications in fields such as autonomous vehicles, security, and healthcare, where the ability to accurately analyze and interpret visual data is critical.

BK AI also offers a range of AI-powered solutions for businesses across various industries. These solutions are designed to help companies improve efficiency, reduce costs, and enhance their overall competitiveness. For example, BK AI offers a predictive analytics platform that uses machine learning algorithms to analyze large datasets and identify patterns and insights that can inform business decisions.

In addition to its product offerings, BK AI is also committed to fostering a culture of innovation and collaboration. The company regularly hosts events and workshops to bring together experts and thought leaders from across the AI community. These events provide a platform for knowledge-sharing, idea exchange, and collaboration on new research initiatives.

BK AI's impact extends beyond its own products and services. The company is also dedicated to promoting ethical AI practices and ensuring that its technologies are developed and deployed in a responsible and transparent manner. This includes working closely with policymakers, regulators, and other stakeholders to develop guidelines and best practices for the ethical use of AI.

Looking ahead, BK AI's future looks bright. The company is poised for growth, with a pipeline of innovative products and services in development. As AI continues to transform industries and redefine human experiences, BK AI is well-positioned to be at the forefront of this revolution.

In conclusion, BK AI is a leader in the field of artificial intelligence, dedicated to pushing the boundaries of what AI can achieve. With its commitment to research and development, focus on NLP and computer vision, and range of AI-powered solutions for businesses, BK AI is poised for continued success in the years ahead. As the company continues to innovate and collaborate, it is clear that BK AI will play a pivotal role in shaping the future of artificial intelligence.</p>
  </div>
  <img
    class="fix-image ai-image"
    src="./blueking-ai.png"
    @click="handleShowAi"
  >
  <img
    class="float-image ai-image"
    src="./blueking-ai.png"
    @click="handleShowAi"
  >
  <AIBlueking
    v-model:is-show="isShow"
    :loading="loading"
    :messages="messages"
    @clear="handleClear"
    @send="handleSend"
    @stop="handleStop"
    @close="handleClose"
  />
</template>

<script lang="ts" setup>
import {
  ref,
} from 'vue';
import AIBlueking, { ChatHelper, RoleType, MessageStatus } from '@blueking/ai-blueking';
import '@blueking/ai-blueking/dist/vue3/style.css';

const loading = ref(false);
const messages  = ref([]);
const isShow = ref(false);

// 展示 AI 聊天框
const handleShowAi = () => {
  isShow.value = true;
}

// 关闭 AI 聊天框
const handleClose = () => {
  isShow.value = false;
}

// 聊天开始
const handleStart = (id: number | string) => {
  loading.value = true;
  messages.value.push({
    time: new Date().getTime(),
    role: RoleType.Assistant,
    content: '内容正在生成中...',
    status: MessageStatus.Loading,
  });
}

// 接收消息
const handleReceiveMessage = (message: string, id: number | string) => {
  const currentMessage = messages.value.at(-1);
  if (currentMessage.status === MessageStatus.Loading) {
    // 如果是loading状态，直接覆盖
    currentMessage.content = message;
    currentMessage.status = MessageStatus.Success;
  } else if (currentMessage.status === MessageStatus.Success) {
    // 如果是后续消息，就追加消息
    currentMessage.content += message;
  }
}

// 聊天结束
const handleEnd = (id: number | string, message?: string) => {
  loading.value = false;
  const currentMessage = messages.value.at(-1);
  if (message) {
    // done 的情况下，返回 message，直接覆盖
    currentMessage.content = message;
    currentMessage.status = MessageStatus.Success;
  } else if (currentMessage.status === MessageStatus.Loading) {
    // loading 情况下终止
    currentMessage.content = '聊天内容已中断';
    currentMessage.status = MessageStatus.Error;
  }
}

// 错误处理
const handleError = (message: string, code: string | number, id: number | string) => {
  if (['bk_token is invalid', 'user authentication failed'].some(item => message.includes(item))) {
    // 未登录，跳转登录
    const loginUrl = new URL(process.env.BK_LOGIN_URL);
    loginUrl.searchParams.append('c_url', location.href);
    window.location.href = loginUrl.href;
  } else {
    // 处理错误消息
    const currentMessage = messages.value.at(-1);
    currentMessage.status = MessageStatus.Error;
    currentMessage.content = message;
    loading.value = false;
  }
}

const prefix = process.env.BK_API_URL_TMPL?.replace(
  "{api_name}",
  process.env.BK_API_GATEWAY_NAME
)?.replace("http:", "https:");
const chatHelper = new ChatHelper(
  `${prefix}/prod/bk_plugin/plugin_api/assistant/`,
  handleStart,
  handleReceiveMessage,
  handleEnd,
  handleError
);

// 清空消息
const handleClear = () => {
  messages.value = [];
}

// 发送消息
const handleSend = (args: any) => {
  // 记录当前消息记录
  const chatHistory = [...messages.value];
  // 添加一条消息
  messages.value.push({
    time: new Date().getTime(),
    role: 'user',
    content: args.content,
    cite: args.cite,
  });
  // ai 消息，id是唯一标识当前流，调用 chatHelper.stop 的时候需要传入
  chatHelper.stream(
    {
      inputs: {
        input: args.cite ? `${args.content}: ${args.cite}` : args.content,
        chat_history: chatHistory,
      },
    },
    1,
  );
};

// 暂停聊天
const handleStop = () => {
  chatHelper.stop(1);
};
</script>

<style scoped>
.article {
  padding: 20px;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}
.ai-image {
  position: fixed;
  width: 64px;
  height: 64px;
  cursor: pointer;
}
.fix-image {
  right: 10px;
  bottom: 20px;
}
.float-image {
  bottom: 100px;
  right: -32px;
  transition: right 0.3s;
  &:hover {
    right: 10px;
  }
}
</style>
