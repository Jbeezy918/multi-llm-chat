"""Multi-LLM Group Chat - Streamlit MVP
Ship fast, improve after.
"""
import streamlit as st
import streamlit.components.v1 as components
import os
from datetime import datetime
from core import (
    get_all_providers,
    ConversationManager,
    TokenTracker,
    UsageLogger,
    get_pricing_info
)

# Page config
st.set_page_config(
    page_title="Multi-LLM Group Chat - Compare AI Models",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/joebudds/multi-llm-chat',
        'Report a bug': "https://github.com/joebudds/multi-llm-chat/issues",
        'About': "# Multi-LLM Group Chat\nAsk once. Get answers from all LLMs.\n\nBuilt by SavvyTech"
    }
)

# Google Analytics
GA_ID = os.getenv("GOOGLE_ANALYTICS_ID", "")
if GA_ID:
    ga_script = f"""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}');
    </script>
    """
    components.html(ga_script, height=0)

# Initialize session state
if 'conversation_manager' not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()

if 'config' not in st.session_state:
    st.session_state.config = {}

if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True

if 'token_tracker' not in st.session_state:
    st.session_state.token_tracker = TokenTracker()

if 'usage_logger' not in st.session_state:
    st.session_state.usage_logger = UsageLogger()

if 'email_captured' not in st.session_state:
    st.session_state.email_captured = False

if 'show_email_modal' not in st.session_state:
    st.session_state.show_email_modal = False


def show_landing_page():
    """Landing page for first-time visitors"""
    st.title("🤖 Multi-LLM Group Chat")
    st.markdown("### Ask once. Get answers from all LLMs.")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🚀 **Compare Models**")
        st.markdown("Get responses from GPT-4, Claude, Gemini, and Llama side-by-side")

    with col2:
        st.markdown("#### 💰 **Save Money**")
        st.markdown("Find the best model for your use case and optimize costs")

    with col3:
        st.markdown("#### 📊 **Better Insights**")
        st.markdown("See different perspectives and choose the best answer")

    st.markdown("---")

    st.markdown("### 🎯 How It Works")
    st.markdown("""
    1. **Add your API keys** in the sidebar (or use free Ollama)
    2. **Type your question** in the chat box
    3. **Get responses** from all configured LLMs instantly
    4. **Compare & choose** the best answer for your needs
    """)

    st.markdown("---")

    st.markdown("### ✨ Supported Models")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**OpenAI**")
        st.markdown("• GPT-4o\n• GPT-4 Turbo\n• GPT-3.5")

    with col2:
        st.markdown("**Anthropic**")
        st.markdown("• Claude Sonnet\n• Claude Opus\n• Claude Haiku")

    with col3:
        st.markdown("**Google**")
        st.markdown("• Gemini 2.0\n• Gemini 1.5 Pro\n• Gemini Flash")

    with col4:
        st.markdown("**Ollama (FREE)**")
        st.markdown("• Llama 3.2\n• Mistral\n• Qwen")

    st.markdown("---")

    if st.button("🚀 Get Started", type="primary", use_container_width=True):
        st.session_state.show_landing = False
        st.rerun()

    st.markdown("---")
    st.markdown("*Built with ❤️ by [SavvyTech](https://savvytechautomations.com)*")


def show_email_capture():
    """Email capture modal for lead generation"""
    st.markdown("### 🎁 Unlock Premium Features")
    st.markdown("Get updates on new features, cost-saving tips, and early access to premium tiers!")

    col1, col2 = st.columns([2, 1])

    with col1:
        email = st.text_input("Email address", placeholder="you@example.com")

    with col2:
        name = st.text_input("Name (optional)", placeholder="Your name")

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("✅ Get Updates", type="primary", use_container_width=True):
            if email and "@" in email:
                st.session_state.usage_logger.capture_email(email, name)
                st.session_state.email_captured = True
                st.session_state.show_email_modal = False
                st.success("Thanks! We'll keep you updated. 🎉")
                st.rerun()
            else:
                st.error("Please enter a valid email")

    with col_btn2:
        if st.button("Skip", use_container_width=True):
            st.session_state.show_email_modal = False
            st.rerun()

    st.caption("We respect your privacy. No spam, unsubscribe anytime.")


def main():
    """Main app"""

    # Show landing page for first-time visitors
    if st.session_state.show_landing:
        show_landing_page()
        return

    # Show email capture modal if triggered
    if st.session_state.show_email_modal:
        show_email_capture()
        st.divider()

    # Header
    st.title("🤖 Multi-LLM Group Chat")
    st.markdown("**Ask once. Get answers from all LLMs.**")

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.subheader("🔑 API Keys")

        # OpenAI
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Get from: https://platform.openai.com/api-keys"
        )
        if openai_key:
            st.session_state.config['openai_key'] = openai_key
            openai_model = st.selectbox(
                "OpenAI Model",
                ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                index=1
            )
            st.session_state.config['openai_model'] = openai_model

        # Claude
        claude_key = st.text_input(
            "Claude API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            help="Get from: https://console.anthropic.com/settings/keys"
        )
        if claude_key:
            st.session_state.config['claude_key'] = claude_key
            claude_model = st.selectbox(
                "Claude Model",
                ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
                index=0
            )
            st.session_state.config['claude_model'] = claude_model

        # Gemini
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Get from: https://aistudio.google.com/app/apikey"
        )
        if gemini_key:
            st.session_state.config['gemini_key'] = gemini_key
            gemini_model = st.selectbox(
                "Gemini Model",
                ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                index=0
            )
            st.session_state.config['gemini_model'] = gemini_model

        # Ollama
        st.subheader("🆓 Ollama (Free/Local)")
        use_ollama = st.checkbox("Use Ollama", value=True)
        if use_ollama:
            ollama_model = st.text_input("Ollama Model", value="llama3.2")
            st.session_state.config['ollama_model'] = ollama_model
            st.caption("💡 Start Ollama: `ollama serve`")

        st.divider()

        # Cost tracking
        st.subheader("💰 Session Costs")
        total_cost = st.session_state.token_tracker.get_total_cost()

        if total_cost > 0:
            st.metric("Total Spent", f"${total_cost:.4f}")

            # Show savings
            savings, vs_model = st.session_state.token_tracker.get_savings_vs_most_expensive()
            if savings > 0:
                st.success(f"💰 Saved ${savings:.4f} vs using only {vs_model}")

            # Show breakdown by provider
            with st.expander("Cost Breakdown"):
                summary = st.session_state.token_tracker.get_summary()
                for provider, models in summary["by_provider"].items():
                    for model, stats in models.items():
                        st.caption(f"**{provider}/{model}**: ${stats['cost']:.4f} ({stats['requests']} requests)")
        else:
            st.info("No costs yet. Start chatting!")

        st.divider()

        # Conversation management
        st.subheader("💾 Conversations")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.conversation_manager.clear_history()
                st.rerun()

        with col2:
            if st.button("💾 Save", use_container_width=True):
                filepath = st.session_state.conversation_manager.save_conversation()
                st.success(f"Saved: {filepath}")

        # Export
        st.subheader("📤 Export")
        export_format = st.selectbox("Format", ["Markdown", "JSON"])

        if st.button("Download", use_container_width=True):
            if export_format == "Markdown":
                content = st.session_state.conversation_manager.export_markdown()
                filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                st.download_button(
                    "📥 Download MD",
                    content,
                    filename,
                    mime="text/markdown",
                    use_container_width=True
                )
            else:
                content = st.session_state.conversation_manager.export_json()
                filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                st.download_button(
                    "📥 Download JSON",
                    content,
                    filename,
                    mime="application/json",
                    use_container_width=True
                )

    # Main content area
    # Initialize providers
    providers = get_all_providers(st.session_state.config)

    if not providers:
        st.warning("⚠️ No LLM providers configured. Add API keys in the sidebar to get started.")
        st.info("""
        **Quick Start:**
        1. Add at least one API key in the sidebar
        2. Or use Ollama (free) by running: `ollama serve`
        3. Type your question below
        4. Get responses from all configured LLMs
        """)
        return

    # Show active providers
    st.success(f"✅ Active Providers: {', '.join(providers.keys())}")

    # Chat input
    prompt = st.text_area(
        "Your question:",
        placeholder="Ask anything... (e.g., 'Explain quantum computing in simple terms')",
        height=100
    )

    if st.button("🚀 Ask All LLMs", type="primary", use_container_width=True):
        if not prompt:
            st.error("Please enter a question")
            return

        # Get responses from all providers
        responses = {}
        providers_used = []
        tokens_by_provider = {}
        total_interaction_cost = 0.0

        with st.spinner("Getting responses from all LLMs..."):
            cols = st.columns(len(providers))

            for idx, (name, provider) in enumerate(providers.items()):
                with cols[idx]:
                    with st.spinner(f"{name}..."):
                        response = provider.chat(prompt)
                        responses[name] = response

                        # Track tokens and cost
                        if not response.startswith("❌"):  # Only track successful responses
                            providers_used.append(name)
                            st.session_state.token_tracker.track(
                                name.lower(),
                                provider.model,
                                prompt,
                                response
                            )

                            # Get pricing info for display
                            pricing = get_pricing_info(provider.model, name.lower())
                            tokens_by_provider[name] = pricing

        # Calculate total cost for this interaction
        total_interaction_cost = st.session_state.token_tracker.get_total_cost()

        # Log usage
        st.session_state.usage_logger.log_interaction(
            prompt=prompt,
            providers_used=providers_used,
            tokens_used=tokens_by_provider,
            cost=total_interaction_cost
        )

        # Save to conversation history
        st.session_state.conversation_manager.add_message(prompt, responses)

        # Show email capture after 3rd interaction (if not captured)
        session_stats = st.session_state.usage_logger.get_session_stats()
        if session_stats["total_interactions"] >= 3 and not st.session_state.email_captured:
            st.session_state.show_email_modal = True

        st.success(f"✅ All responses received! Cost: ${total_interaction_cost:.4f}")

    # Display conversation history
    st.divider()
    st.subheader("💬 Conversation History")

    history = st.session_state.conversation_manager.get_history()

    if not history:
        st.info("No messages yet. Ask a question above to get started!")
    else:
        for i, entry in enumerate(reversed(history), 1):
            with st.expander(f"**Q{len(history) - i + 1}**: {entry['prompt'][:100]}...", expanded=(i == 1)):
                st.markdown(f"**Time**: {entry['timestamp']}")
                st.markdown(f"**Question**: {entry['prompt']}")

                # Display responses in columns
                response_cols = st.columns(len(entry['responses']))
                for idx, (provider, response) in enumerate(entry['responses'].items()):
                    with response_cols[idx]:
                        st.markdown(f"### {provider}")
                        st.markdown(response)


if __name__ == "__main__":
    main()
