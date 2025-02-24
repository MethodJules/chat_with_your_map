<script>
import { MapCommandExecutor } from '../exectutors/map_command_executor';
export default {
    data () {
        return {
            userInput: "",
            messages: [],
            showTypingIndicator: false,
            executor: null
        };
    },
    created() {
      this.executor = new MapCommandExecutor(this.$store);
    },
    methods:
    {
        async sendMessage () {
            if (this.userInput.trim() === "") {
                return;
            }

            // add user message to the chat
            this.messages.push({sender: "user", text: this.userInput});
            

            const result = await this.executor.executeCommand(this.userInput);
            console.log(result);
            this.userInput = "";
            // Simulate bot typing
            this.showTypingIndicator = true;

            // Simulate response delay
            const botResponse = await this.simulateBotResponse();

            this.showTypingIndicator = false;

            // Add bot message to the chat
            this.messages.push({sender: "bot", text: botResponse});
        },
        simulateBotResponse () {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve("This is a bot response!");
                }, 2000);
            });
        }
    }
};
</script>
<template>
    <div class="chat-bot">
        <div class="chat-window">
            <div
                v-for="(message, index) in messages"
                :key="index"
                class="chat-message"
            >
                <span :class="message.sender">{{ message.text }}</span>
            </div>
            <div
                v-if="showTypingIndicator"
                class="typing-indicator"
            >
                <span class="dot" />
                <span class="dot" />
                <span class="dot" />
            </div>
        </div>
        <div>
            <input
                v-model="userInput"
                type="text"
                placeholder="Type your message..."
                @keyup.enter="sendMessage"
            >
            <button @click="sendMessage">
                Send
            </button>
        </div>
    </div>
</template>

<style scoped>
.chat-bot {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  border: 1px solid #ccc;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  background-color: #f9f9f9;
}

.chat-window {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  height: 300px;
  display: flex;
  flex-direction: column;
}

.chat-message {
  margin: 5px 0;
}

.chat-message .user {
  align-self: flex-end;
  background-color: #007bff;
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  max-width: 70%;
  word-wrap: break-word;
}

.chat-message .bot {
  align-self: flex-start;
  background-color: #e9ecef;
  color: black;
  padding: 5px 10px;
  border-radius: 15px;
  max-width: 70%;
  word-wrap: break-word;
}

.chat-input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ccc;
  background-color: white;
}

.chat-input input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.chat-input button {
  margin-left: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}

.chat-input button:hover {
  background-color: #0056b3;
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 5px 0;
}

.dot {
  width: 8px;
  height: 8px;
  margin: 0 3px;
  background-color: #007bff;
  border-radius: 50%;
  animation: jump 1.5s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes jump {
  0%, 80%, 100% {
    transform: scale(1);
  }
  40% {
    transform: scale(1.5);
  }
}
</style>
