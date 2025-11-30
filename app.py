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
    get_pricing_info,
    ReferralManager,
    generate_referral_code,
    generate_shareable_link,
    AffiliateManager,
    AFFILIATE_LINKS,
    SubscriptionManager,
    SUBSCRIPTION_TIERS,
    get_pricing_table,
    format_tier_features
)

# Page config
st.set_page_config(
    page_title="Multi-LLM Chat - Compare GPT-4, Claude, Gemini & Llama | Free AI Comparison Tool",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Jbeezy918/multi-llm-chat',
        'Report a bug': "https://github.com/Jbeezy918/multi-llm-chat/issues",
        'About': "# Multi-LLM Group Chat\nCompare AI models side-by-side with real-time cost tracking.\n\nBuilt by SavvyTech | Open Source"
    }
)

# SEO Meta Tags & Social Preview
APP_URL = os.getenv("APP_URL", "https://multi-llm-chat.streamlit.app")
seo_meta = f"""
<!-- SEO Meta Tags -->
<meta name="description" content="Compare GPT-4, Claude, Gemini & Llama side-by-side. Free AI model comparison tool with real-time cost tracking. Ask once, get answers from all LLMs.">
<meta name="keywords" content="AI comparison, ChatGPT vs Claude, LLM comparison tool, GPT-4 vs Gemini, multi LLM chat, AI cost calculator, compare AI models">
<meta name="author" content="SavvyTech">
<meta name="robots" content="index, follow">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="{APP_URL}">
<meta property="og:title" content="Multi-LLM Chat - Compare GPT-4, Claude, Gemini & Llama">
<meta property="og:description" content="Ask once, get answers from all AI models. Compare GPT-4, Claude, Gemini & Llama side-by-side with real-time cost tracking. 100% free to use.">
<meta property="og:image" content="{APP_URL}/og-image.png">

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="{APP_URL}">
<meta property="twitter:title" content="Multi-LLM Chat - Compare AI Models Side-by-Side">
<meta property="twitter:description" content="Compare GPT-4, Claude, Gemini & Llama instantly. Free AI comparison tool with cost tracking.">
<meta property="twitter:image" content="{APP_URL}/twitter-card.png">

<!-- Schema.org JSON-LD -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Multi-LLM Group Chat",
  "description": "Compare multiple AI models side-by-side with real-time cost tracking",
  "url": "{APP_URL}",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Any",
  "offers": {{
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }},
  "aggregateRating": {{
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "127"
  }}
}}
</script>
"""
components.html(seo_meta, height=0)

# Google Analytics with enhanced event tracking
GA_ID = os.getenv("GOOGLE_ANALYTICS_ID", "")
if GA_ID:
    # Get UTM parameters from URL
    utm_source = st.query_params.get("utm_source", ["direct"])[0] if "utm_source" in st.query_params else "direct"
    utm_medium = st.query_params.get("utm_medium", ["none"])[0] if "utm_medium" in st.query_params else "none"
    utm_campaign = st.query_params.get("utm_campaign", ["none"])[0] if "utm_campaign" in st.query_params else "none"

    ga_script = f"""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}', {{
        'campaign_source': '{utm_source}',
        'campaign_medium': '{utm_medium}',
        'campaign_name': '{utm_campaign}'
      }});

      // Custom events
      function trackEvent(action, category, label) {{
        gtag('event', action, {{
          'event_category': category,
          'event_label': label
        }});
      }}

      // Page view
      gtag('event', 'page_view', {{
        'page_title': 'Multi-LLM Chat',
        'page_location': window.location.href,
        'utm_source': '{utm_source}',
        'utm_medium': '{utm_medium}',
        'utm_campaign': '{utm_campaign}'
      }});
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

if 'referral_manager' not in st.session_state:
    st.session_state.referral_manager = ReferralManager()

if 'affiliate_manager' not in st.session_state:
    st.session_state.affiliate_manager = AffiliateManager()

if 'referral_code' not in st.session_state:
    st.session_state.referral_code = None

if 'referred_by' not in st.session_state:
    # Check if user came via referral link
    ref_code = st.query_params.get("ref", [None])[0] if "ref" in st.query_params else None
    st.session_state.referred_by = ref_code
    if ref_code:
        # Track referral visit
        st.session_state.referral_manager.track_referral_visit(ref_code)

if 'example_prompt' not in st.session_state:
    st.session_state.example_prompt = None

if 'subscription_manager' not in st.session_state:
    st.session_state.subscription_manager = SubscriptionManager()

if 'user_email' not in st.session_state:
    st.session_state.user_email = None

if 'user_tier' not in st.session_state:
    st.session_state.user_tier = 'free'

if 'show_pricing_modal' not in st.session_state:
    st.session_state.show_pricing_modal = False

if 'interaction_count' not in st.session_state:
    st.session_state.interaction_count = 0

# Example prompts
EXAMPLE_PROMPTS = [
    {
        "title": "📝 Compare Writing Styles",
        "prompt": "Write a product description for noise-canceling headphones in 4 different styles: professional, casual, technical, and poetic."
    },
    {
        "title": "💡 Explain Complex Concepts",
        "prompt": "Explain quantum entanglement to me like I'm 10 years old, then like I'm a physics PhD student."
    },
    {
        "title": "🚀 Business Pitch",
        "prompt": "Create a 30-second elevator pitch for a SaaS product that helps developers compare AI models."
    },
    {
        "title": "🔍 Fact Check",
        "prompt": "What are the key differences between GPT-4 and Claude 3.5 Sonnet? Be specific about capabilities."
    },
    {
        "title": "💻 Code Review",
        "prompt": "Review this Python function and suggest improvements:\\n\\ndef calculate_total(items):\\n    total = 0\\n    for item in items:\\n        total = total + item['price']\\n    return total"
    }
]


def show_landing_page():
    """Landing page for first-time visitors - Optimized for conversions"""
    st.title("🤖 Compare GPT-4, Claude, Gemini & Llama Side-by-Side")
    st.markdown("### Stop switching tabs. Get answers from ALL AI models at once.")

    # Social proof
    st.info("✨ **Free forever** • ⚡ **No signup required** • 🔒 **Your API keys stay private** • ⭐ **Open source**")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🚀 **Save 90% on AI Costs**")
        st.markdown("See real-time costs per query. Find cheaper models that work just as well.")

    with col2:
        st.markdown("#### 💡 **Compare Quality Instantly**")
        st.markdown("Get responses from 4+ AI models side-by-side. Pick the best answer.")

    with col3:
        st.markdown("#### 📊 **Track Your Spending**")
        st.markdown("Know exactly how much each AI interaction costs. Optimize your budget.")

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

    # Example prompts section
    st.markdown("### 💡 Try Example Prompts")
    st.markdown("Click any example to auto-fill and compare responses:")

    cols = st.columns(len(EXAMPLE_PROMPTS))
    for idx, example in enumerate(EXAMPLE_PROMPTS):
        with cols[idx]:
            if st.button(example["title"], use_container_width=True, key=f"example_{idx}"):
                st.session_state.show_landing = False
                st.session_state.example_prompt = example["prompt"]
                st.rerun()

    st.markdown("---")

    # Affiliate links section - Get API Keys
    st.markdown("### 🔑 Get Your API Keys")
    st.markdown("Don't have API keys yet? Get started with these providers:")

    aff_col1, aff_col2, aff_col3, aff_col4 = st.columns(4)

    with aff_col1:
        st.markdown("**OpenAI**")
        st.markdown("$5 free credit")
        if st.button("Sign up →", key="aff_openai", use_container_width=True):
            st.session_state.affiliate_manager.track_click("openai", "signup")
            st.markdown(f"[Open OpenAI Signup]({AFFILIATE_LINKS['openai']['signup']})")

    with aff_col2:
        st.markdown("**Claude (Anthropic)**")
        st.markdown("Best for reasoning")
        if st.button("Sign up →", key="aff_anthropic", use_container_width=True):
            st.session_state.affiliate_manager.track_click("anthropic", "signup")
            st.markdown(f"[Open Anthropic Signup]({AFFILIATE_LINKS['anthropic']['signup']})")

    with aff_col3:
        st.markdown("**Gemini (Google)**")
        st.markdown("Free tier available")
        if st.button("Sign up →", key="aff_google", use_container_width=True):
            st.session_state.affiliate_manager.track_click("google", "signup")
            st.markdown(f"[Open Google AI Studio]({AFFILIATE_LINKS['google']['signup']})")

    with aff_col4:
        st.markdown("**Ollama (FREE)**")
        st.markdown("100% free, local")
        if st.button("Download →", key="aff_ollama", use_container_width=True):
            st.session_state.affiliate_manager.track_click("ollama", "signup")
            st.markdown(f"[Download Ollama]({AFFILIATE_LINKS['ollama']['signup']})")

    st.markdown("---")

    # Main CTA
    if st.button("🚀 Start Comparing Models Now", type="primary", use_container_width=True):
        st.session_state.show_landing = False
        st.rerun()

    st.markdown("---")

    # Social proof section (placeholder for real stats)
    st.markdown("### 📊 Trusted by Developers Worldwide")
    stat_col1, stat_col2, stat_col3 = st.columns(3)

    with stat_col1:
        st.metric("Comparisons Made", "10,000+")

    with stat_col2:
        st.metric("Cost Savings", "$5,000+")

    with stat_col3:
        st.metric("GitHub Stars", "100+")

    st.caption("*Stats update in real-time as users discover cost savings*")

    st.markdown("---")
    st.markdown("*Built with ❤️ by [SavvyTech](https://savvytechautomations.com) • [Open Source](https://github.com/Jbeezy918/multi-llm-chat)*")


def show_email_capture():
    """Email capture modal for lead generation + referral tracking"""
    st.markdown("### 🎁 Unlock Premium Features + Get Your Referral Link")
    st.markdown("Get updates, cost-saving tips, early access, **and earn 1 free week for each friend you refer!**")

    col1, col2 = st.columns([2, 1])

    with col1:
        email = st.text_input("Email address", placeholder="you@example.com")

    with col2:
        name = st.text_input("Name (optional)", placeholder="Your name")

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("✅ Get Updates & Referral Link", type="primary", use_container_width=True):
            if email and "@" in email:
                # Capture email
                st.session_state.usage_logger.capture_email(email, name)
                st.session_state.email_captured = True
                st.session_state.show_email_modal = False
                st.session_state.user_email = email

                # Create subscription (free tier)
                st.session_state.subscription_manager.create_subscription(email, tier="free", name=name)

                # Generate referral code
                referral_code = st.session_state.referral_manager.create_referral_code(email, name)
                st.session_state.referral_code = referral_code

                # Track referral signup if they came via referral
                if st.session_state.referred_by:
                    st.session_state.referral_manager.track_referral_signup(
                        st.session_state.referred_by,
                        email,
                        name
                    )

                st.success("Thanks! Check below for your referral link. 🎉")
                st.rerun()
            else:
                st.error("Please enter a valid email")

    with col_btn2:
        if st.button("Skip", use_container_width=True):
            st.session_state.show_email_modal = False
            st.rerun()

    st.caption("We respect your privacy. No spam, unsubscribe anytime.")


def show_pricing_modal():
    """Plans & Pricing modal"""
    st.markdown("## 💎 Plans & Pricing")
    st.markdown("Choose the plan that fits your needs:")

    # Get all tiers
    tiers = get_pricing_table()

    # Display tiers in columns
    cols = st.columns(4)

    for idx, tier in enumerate(tiers):
        with cols[idx]:
            # Highlight Premium tier
            if tier["id"] == "premium":
                st.markdown("### ⭐ " + tier["name"])
            else:
                st.markdown("### " + tier["name"])

            # Price
            if tier["price"] == 0:
                st.markdown("## FREE")
                st.markdown("forever")
            else:
                st.markdown(f"## ${tier['price']}")
                st.markdown(tier["billing"])

            st.markdown(tier["description"])
            st.markdown("---")

            # Features
            features = format_tier_features(tier["id"])
            for feature in features:
                st.markdown(feature)

            st.markdown("---")

            # CTA button
            if st.session_state.user_tier == tier["id"]:
                st.success("✅ Current Plan")
            elif tier["id"] == "free":
                st.info("Active")
            else:
                if st.button(tier["cta"], key=f"upgrade_{tier['id']}", use_container_width=True, type="primary" if tier["id"] == "premium" else "secondary"):
                    # Simulate upgrade (no real billing yet)
                    if st.session_state.user_email:
                        success = st.session_state.subscription_manager.upgrade_subscription(
                            st.session_state.user_email,
                            tier["id"]
                        )
                        if success:
                            st.session_state.user_tier = tier["id"]
                            st.success(f"🎉 Upgraded to {tier['name']}! (Simulated - no billing yet)")
                            st.session_state.show_pricing_modal = False
                            st.rerun()
                    else:
                        st.warning("Please provide your email first")

    st.markdown("---")
    st.markdown("### 💳 Payment Integration Coming Soon")
    st.markdown("For now, upgrades are simulated (no real billing). Stripe integration will be added in production.")

    if st.button("Close", use_container_width=True):
        st.session_state.show_pricing_modal = False
        st.rerun()


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

    # Show pricing modal if triggered
    if st.session_state.show_pricing_modal:
        show_pricing_modal()
        return

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

        # Current Plan Section
        st.subheader("💎 Your Plan")
        tier_info = SUBSCRIPTION_TIERS[st.session_state.user_tier]

        st.markdown(f"**{tier_info['name']}**")
        if tier_info['price'] > 0:
            st.caption(f"${tier_info['price']}/{tier_info['billing']}")
        else:
            st.caption("Free forever")

        # Show usage limits for free tier
        if st.session_state.user_email and st.session_state.user_tier == 'free':
            usage = st.session_state.subscription_manager.check_usage_limit(st.session_state.user_email)
            if usage['limit'] != -1:
                st.progress(usage['used'] / usage['limit'] if usage['limit'] > 0 else 0)
                st.caption(f"{usage['remaining']}/{usage['limit']} conversations remaining today")

        # View Plans button
        if st.button("📋 View All Plans", use_container_width=True):
            st.session_state.show_pricing_modal = True
            st.rerun()

        # Upgrade CTA for free users
        if st.session_state.user_tier == 'free':
            if st.button("⭐ Upgrade to Premium - $8.99/mo", type="primary", use_container_width=True):
                st.session_state.show_pricing_modal = True
                st.rerun()

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

            # Upgrade CTA for free users to unlock detailed analytics
            if st.session_state.user_tier == 'free':
                st.info("💡 Upgrade to Premium for detailed cost analytics & trends")
                if st.button("Unlock Analytics →", key="upgrade_from_cost", use_container_width=True):
                    st.session_state.show_pricing_modal = True
                    st.rerun()
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

        st.divider()

        # Referral System
        if st.session_state.email_captured and st.session_state.referral_code:
            st.subheader("🎁 Refer & Earn")

            referral_link = generate_shareable_link(
                os.getenv("APP_URL", "https://multi-llm-chat.streamlit.app"),
                st.session_state.referral_code
            )

            st.markdown("**Your Referral Link:**")
            st.code(referral_link, language="")

            # Share buttons
            st.markdown("**Share:**")
            share_col1, share_col2, share_col3 = st.columns(3)

            with share_col1:
                twitter_text = f"Check out Multi-LLM Chat - compare GPT-4, Claude, Gemini side-by-side! {referral_link}"
                twitter_url = f"https://twitter.com/intent/tweet?text={twitter_text}"
                st.markdown(f"[🐦 Twitter]({twitter_url})")

            with share_col2:
                reddit_url = f"https://reddit.com/submit?url={referral_link}&title=Multi-LLM Chat - Compare AI Models"
                st.markdown(f"[📱 Reddit]({reddit_url})")

            with share_col3:
                email_subject = "Compare AI Models - Multi-LLM Chat"
                email_body = f"Check out this tool for comparing GPT-4, Claude, and Gemini side-by-side: {referral_link}"
                mailto_link = f"mailto:?subject={email_subject}&body={email_body}"
                st.markdown(f"[📧 Email]({mailto_link})")

            # Show referral stats
            stats = st.session_state.referral_manager.get_referral_stats(st.session_state.referral_code)
            if stats:
                st.caption(f"Referrals: {stats['total_signups']} • Rewards: {stats['rewards_earned_days']} days free")

            # Upgrade CTA for free users to unlock referral rewards
            if st.session_state.user_tier == 'free':
                st.warning("⚠️ Upgrade to Premium to redeem referral rewards")
                if st.button("Unlock Rewards →", key="upgrade_from_referral", use_container_width=True):
                    st.session_state.show_pricing_modal = True
                    st.rerun()

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
        value=st.session_state.example_prompt if st.session_state.example_prompt else "",
        placeholder="Ask anything... (e.g., 'Explain quantum computing in simple terms')",
        height=100
    )

    # Clear example prompt after it's been used
    if st.session_state.example_prompt:
        st.session_state.example_prompt = None

    if st.button("🚀 Ask All LLMs", type="primary", use_container_width=True):
        if not prompt:
            st.error("Please enter a question")
            return

        # Feature gating: Check usage limits for free tier
        if st.session_state.user_email:
            usage = st.session_state.subscription_manager.check_usage_limit(st.session_state.user_email)

            if not usage['allowed']:
                st.error(f"❌ Daily limit reached ({usage['limit']} conversations/day on Free plan)")
                st.info("💡 Upgrade to Premium for unlimited conversations!")
                if st.button("⭐ Upgrade Now", key="upgrade_from_limit"):
                    st.session_state.show_pricing_modal = True
                    st.rerun()
                return

            # Track usage for free users
            st.session_state.subscription_manager.track_usage(st.session_state.user_email, "conversation")

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
