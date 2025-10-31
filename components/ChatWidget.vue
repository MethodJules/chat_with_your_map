<script>
export default {
    name: "ChatWidget",
    props: {
        isProcessing: {type: Boolean, default: false}
    },
    data () {
        return {
            input: "",
            messages: []
        };
    },
    watch: {
        isProcessing () {
            this.$nextTick(() => {
                this.scrollToBottom();
            });
        }
    },
    methods: {
        async onSubmit () {
            const query = this.input.trim();

            if (!query) {
                return;
            }
            this.messages.push({sender: "user", text: query});
            this.input = "";
            this.scrollToBottom();

            // Tell parent to process the query and provide a callback for the response
            this.$emit("query-submitted", query, this.handleBotResponse);
        },
        handleBotResponse (responseText) {
            this.messages.push({sender: "bot", text: responseText});
            this.scrollToBottom();
        },
        scrollToBottom () {
            this.$nextTick(() => {
                const el = this.$refs.messages;

                if (el) {
                    el.scrollTop = el.scrollHeight;
                }
            });
        }
    }
};
</script>

<template>
    <div class="chat-widget">
        <div class="chat-header">
            <span>Chat with your Map</span>
        </div>
        <div
            ref="messages"
            class="chat-messages"
        >
            <div
                v-for="(msg, idx) in messages"
                :key="idx"
                :class="['chat-message', msg.sender]"
            >
                <span
                    v-if="msg.sender === 'user'"
                    class="user-label"
                >Sie:
                </span>
                <span
                    v-if="msg.sender === 'bot'"
                    class="bot-label"
                >Bot:
                </span>
                <span>{{ msg.text }}</span>
            </div>
            <div
                v-if="isProcessing"
                class="chat-message bot"
            >
                <span
                    class="bot-label"
                >Bot:
                </span>
                <span
                    class="typing-indicator"
                >
                    <span
                        class="dot"
                    />
                    <span
                        class="dot"
                    />
                    <span
                        class="dot"
                    />
                </span>
            </div>
        </div>
        <form
            class="chat-input-row"
            @submit.prevent="onSubmit"
        >
            <input
                v-model="input"
                :disabled="isProcessing"
                type="text"
                placeholder="Ihre Frage an die Karte..."
                class="chat-input"
                @keydown.enter.exact.prevent="onSubmit"
            >
            <button
                :disabled="isProcessing || !input.trim()"
                class="send-btn"
            >
                Senden
            </button>
        </form>
    </div>
</template>

<style scoped>
.chat-widget {
    width: 100%;
    max-width: 400px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    border: 2px solid #004b8d;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

.chat-header {
    background: linear-gradient(90deg, #004b8d 100%, #e2001a 100%);
    color: #fff;
    padding: 14px 18px;
    border-radius: 10px 10px 0 0;
    font-weight: 600;
    font-size: 1.1em;
    letter-spacing: 0.5px;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    background: #f7faff;
    min-height: 220px;
    max-height: 320px;
}

.chat-message {
    margin-bottom: 12px;
    display: flex;
    align-items: flex-end;
}

.chat-message.user {
    justify-content: flex-end;
}

.chat-message.bot {
    justify-content: flex-start;
}

.user-label {
    color: #004b8d;
    font-weight: 500;
    margin-right: 6px;
}

.bot-label {
    color: #e2001a;
    font-weight: 500;
    margin-right: 6px;
}

.chat-message span {
    background: #e6f0fa;
    color: #222;
    padding: 8px 14px;
    border-radius: 18px;
    max-width: 70%;
    word-break: break-word;
    font-size: 1em;
}

.chat-message.user span {
    background: #004b8d;
    color: #fff;
}

.chat-message.bot span {
    background: #fff;
    color: #222;
    border: 1px solid #e2001a;
}

.typing-indicator {
    display: inline-flex;
    align-items: center;
    height: 24px;
    margin-left: 4px;
}

.dot {
    height: 8px;
    width: 8px;
    margin: 0 2px;
    background-color: #e2001a;
    border-radius: 50%;
    display: inline-block;
    animation: blink 1.4s infinite both;
}

.dot:nth-child(2) {
    animation-delay: 0.2s;
}

.dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes blink {

    0%,
    80%,
    100% {
        opacity: 0.2;
    }

    40% {
        opacity: 1;
    }
}

.chat-input-row {
    display: flex;
    border-top: 1px solid #e6e6e6;
    padding: 10px 12px;
    background: #f7faff;
    border-radius: 0 0 10px 10px;
}

.chat-input {
    flex: 1;
    border: 1px solid #004b8d;
    border-radius: 18px;
    padding: 8px 14px;
    font-size: 1em;
    outline: none;
    margin-right: 8px;
    background: #fff;
    color: #222;
    transition: border 0.2s;
}

.chat-input:focus {
    border: 1.5px solid #e2001a;
}

.send-btn {
    background: linear-gradient(90deg, #004b8d 100%, #e2001a 100%);
    color: #fff;
    border: none;
    border-radius: 18px;
    padding: 8px 18px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}

.send-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}
</style>
