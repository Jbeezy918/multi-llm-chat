# 🤖 Multi-LLM Group Chat

**Ask once. Get answers from all LLMs.**

A dead-simple Streamlit app that lets you have group conversations with multiple AI models simultaneously.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Configure API Keys

Add your API keys in the sidebar (or set environment variables):

- **OpenAI**: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Claude**: Get from [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
- **Gemini**: Get from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- **Ollama**: Free! Just run `ollama serve` (install from [ollama.com](https://ollama.com))

### 4. Ask Questions

Type your question and click "Ask All LLMs" to get responses from all configured providers side-by-side.

## ✨ Features

- ✅ **Multi-LLM Support**: OpenAI, Claude, Gemini, Ollama
- ✅ **One Input → All Responses**: Ask once, get answers from all LLMs
- ✅ **Easy API Key Management**: Add keys in sidebar or via environment variables
- ✅ **Conversation History**: All exchanges saved in session
- ✅ **Export**: Download conversations as Markdown or JSON
- ✅ **Clean UI**: Simple, fast, no bloat
- ✅ **Modular Backend**: Easy to extend with more providers

## 🏗️ Architecture

```
multi-llm-chat/
├── app.py                    # Main Streamlit app
├── core/
│   ├── llm_providers.py      # LLM integrations (modular)
│   └── conversation.py       # Conversation management
├── requirements.txt          # Dependencies
└── conversations/            # Saved conversations (auto-created)
```

## 🔧 Environment Variables (Optional)

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
```

## 📦 Deployment

### Streamlit Cloud (Free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your repo
4. Add secrets in Streamlit dashboard

### Docker (Coming Soon)

```bash
docker build -t multi-llm-chat .
docker run -p 8501:8501 multi-llm-chat
```

## 🛠️ Adding New Providers

Easy! Just extend `LLMProvider` in `core/llm_providers.py`:

```python
class NewProvider(LLMProvider):
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, stream: bool = False) -> str:
        # Your integration here
        return response
```

Then add to `get_all_providers()` function.

## 💰 Pricing

- **Ollama**: FREE (runs locally)
- **OpenAI**: Pay per token
- **Claude**: Pay per token
- **Gemini**: FREE tier available + pay per token

## 🎯 Roadmap

- [ ] Streaming responses
- [ ] Custom system prompts per LLM
- [ ] Load saved conversations
- [ ] Side-by-side comparison mode
- [ ] Token usage tracking
- [ ] Cost calculator
- [ ] More providers (Cohere, Mistral, etc.)
- [ ] Agent capabilities
- [ ] Memory integration

## 📝 License

MIT License - Ship it and make money! 💰

## 🤝 Contributing

PRs welcome! Keep it simple and fast.

---

**Built for speed. Ship fast, improve after.**
