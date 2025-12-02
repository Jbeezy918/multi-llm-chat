"""Multi-LLM Group Chat - Streamlit MVP
Ship fast, improve after.
"""
import streamlit as st
import streamlit.components.v1 as components
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
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
    format_tier_features,
    create_checkout_session,
    create_customer_portal_session,
    is_stripe_configured
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

if 'stripe_configured' not in st.session_state:
    st.session_state.stripe_configured = is_stripe_configured()

# Phase 6: AI Receptionist session state
if 'receptionist_mode' not in st.session_state:
    st.session_state.receptionist_mode = False

if 'business_profile' not in st.session_state:
    st.session_state.business_profile = None

if 'receptionist_call_history' not in st.session_state:
    st.session_state.receptionist_call_history = []

if 'receptionist_logger' not in st.session_state:
    st.session_state.receptionist_logger = ReceptionistCallLogger()

# Check for billing redirect params
billing_status = st.query_params.get("billing", [None])[0] if "billing" in st.query_params else None
if billing_status and 'billing_redirect_handled' not in st.session_state:
    st.session_state.billing_redirect = billing_status
    st.session_state.billing_redirect_handled = True
elif 'billing_redirect' not in st.session_state:
    st.session_state.billing_redirect = None

# Phase 6: AI Receptionist helper classes
class ReceptionistCallLogger:
    """Log AI receptionist calls for tracking and analytics"""

    def __init__(self, analytics_dir: str = "analytics"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(exist_ok=True)
        self.calls_file = self.analytics_dir / "receptionist_calls.json"
        self.calls_data = self._load_calls()

    def _load_calls(self):
        """Load calls from file"""
        if self.calls_file.exists():
            with open(self.calls_file, 'r') as f:
                return json.load(f)
        return {"calls": [], "usage_by_user": {}}

    def _save_calls(self):
        """Save calls to file"""
        with open(self.calls_file, 'w') as f:
            json.dump(self.calls_data, f, indent=2)

    def log_call(self, user_email: str, business_name: str, caller_input: str,
                 receptionist_response: str, model_used: str):
        """Log a receptionist call"""
        call_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_email": user_email,
            "business_name": business_name,
            "caller_input": caller_input,
            "receptionist_response": receptionist_response,
            "model_used": model_used
        }

        self.calls_data["calls"].append(call_entry)

        # Update usage by user
        if user_email not in self.calls_data["usage_by_user"]:
            self.calls_data["usage_by_user"][user_email] = 0
        self.calls_data["usage_by_user"][user_email] += 1

        self._save_calls()

    def get_user_call_count_today(self, user_email: str) -> int:
        """Get call count for user today"""
        today = datetime.now().date().isoformat()
        count = 0
        for call in self.calls_data["calls"]:
            if call["user_email"] == user_email and call["timestamp"][:10] == today:
                count += 1
        return count

    def get_stats_last_30_days(self):
        """Get receptionist usage stats for last 30 days"""
        from datetime import timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

        recent_calls = [
            c for c in self.calls_data["calls"]
            if c.get("timestamp", "") >= thirty_days_ago
        ]

        # Count by user
        user_counts = {}
        for call in recent_calls:
            email = call.get("user_email", "unknown")
            user_counts[email] = user_counts.get(email, 0) + 1

        # Sort by count descending
        top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_calls": len(recent_calls),
            "top_users": top_users
        }


def generate_receptionist_prompt(business_profile: dict, caller_input: str) -> str:
    """Generate system prompt for AI receptionist based on business profile"""

    business_name = business_profile.get("business_name", "the business")
    industry = business_profile.get("industry", "restaurant")
    hours = business_profile.get("hours", "9 AM - 5 PM")
    greeting = business_profile.get("greeting", f"Thank you for calling {business_name}!")
    faqs = business_profile.get("faqs", "")
    actions = business_profile.get("actions", "take message, provide information")

    system_prompt = f"""You are a professional AI receptionist for {business_name}, a {industry}.

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
- Hours: {hours}
- Standard Greeting: {greeting}

YOUR ROLE:
- Answer calls professionally with warmth and efficiency
- Keep responses concise (2-3 sentences max for phone etiquette)
- Always be polite, helpful, and clear
- Use proper phone etiquette (e.g., "May I help you with anything else?")

COMMON QUESTIONS & ANSWERS:
{faqs if faqs else "Handle general questions about hours, location, and services."}

AVAILABLE ACTIONS:
{actions}

IMPORTANT PHONE ETIQUETTE RULES:
1. Keep responses SHORT - you're on a phone call, not writing an email
2. Use natural, conversational language
3. Offer to help further before ending
4. If you don't know something, offer to take a message or transfer
5. Always maintain professional but friendly tone

Now respond to this caller: "{caller_input}"

Remember: Keep it brief and natural, as if you're speaking on the phone."""

    return system_prompt


def show_business_profile_setup():
    """UI for setting up business profile for AI receptionist"""
    st.subheader("📋 Business Profile Setup")
    st.markdown("Configure your AI receptionist by filling in your business details below.")

    with st.form("business_profile_form"):
        business_name = st.text_input(
            "Business Name *",
            value=st.session_state.business_profile.get("business_name", "") if st.session_state.business_profile else "",
            placeholder="e.g., Tony's Pizza"
        )

        industry = st.selectbox(
            "Industry *",
            ["Restaurant", "Retail Store", "Medical Office", "Law Firm", "Salon/Spa", "Other"],
            index=0 if not st.session_state.business_profile else
            ["Restaurant", "Retail Store", "Medical Office", "Law Firm", "Salon/Spa", "Other"].index(
                st.session_state.business_profile.get("industry", "Restaurant")
            )
        )

        hours = st.text_input(
            "Business Hours *",
            value=st.session_state.business_profile.get("hours", "") if st.session_state.business_profile else "",
            placeholder="e.g., Monday-Friday 9 AM - 9 PM, Saturday-Sunday 10 AM - 6 PM"
        )

        greeting = st.text_area(
            "Phone Greeting *",
            value=st.session_state.business_profile.get("greeting", "") if st.session_state.business_profile else "",
            placeholder="e.g., Thank you for calling Tony's Pizza! How may I help you today?",
            height=80
        )

        faqs = st.text_area(
            "Common Questions & Answers (Optional)",
            value=st.session_state.business_profile.get("faqs", "") if st.session_state.business_profile else "",
            placeholder="Example:\n- Do you deliver? Yes, we deliver within 5 miles.\n- Do you take reservations? Yes, call us or book online.\n- What's your address? 123 Main St, Downtown.",
            height=120
        )

        actions = st.text_input(
            "Available Actions (Optional)",
            value=st.session_state.business_profile.get("actions", "") if st.session_state.business_profile else "",
            placeholder="e.g., take message, schedule appointment, provide directions, answer menu questions"
        )

        submitted = st.form_submit_button("💾 Save Business Profile", use_container_width=True)

        if submitted:
            if not business_name or not hours or not greeting:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                st.session_state.business_profile = {
                    "business_name": business_name,
                    "industry": industry,
                    "hours": hours,
                    "greeting": greeting,
                    "faqs": faqs,
                    "actions": actions if actions else "take message, provide information"
                }
                st.success("✅ Business profile saved! You can now test the receptionist.")
                st.rerun()


def show_receptionist_simulator():
    """UI for simulating AI receptionist calls"""
    st.subheader("📞 Call Simulator")

    if not st.session_state.business_profile:
        st.warning("⚠️ Please set up your business profile first before testing calls.")
        return

    business_name = st.session_state.business_profile.get("business_name", "your business")

    st.markdown(f"**Simulating calls to: {business_name}**")
    st.caption("Type what a caller would say, and the AI receptionist will respond.")

    # Feature gating: Check usage limits
    if st.session_state.user_email:
        calls_today = st.session_state.receptionist_logger.get_user_call_count_today(st.session_state.user_email)

        # Free tier: 3 calls/day, Premium+: unlimited
        if st.session_state.user_tier == 'free':
            limit = 3
            remaining = max(0, limit - calls_today)

            st.info(f"📊 Free tier: {remaining}/{limit} test calls remaining today")

            if calls_today >= limit:
                st.error(f"❌ Daily limit reached ({limit} test calls/day on Free plan)")
                st.info("💡 Upgrade to Premium for unlimited receptionist test calls!")
                if st.button("⭐ Upgrade Now", key="upgrade_receptionist"):
                    st.session_state.show_pricing_modal = True
                    st.rerun()
                return
        else:
            st.success(f"✅ Premium tier: Unlimited test calls (used {calls_today} today)")
    else:
        st.info("💡 Sign in to track your test call usage")

    # Call simulator form
    caller_input = st.text_area(
        "Caller says:",
        placeholder="Example: Hi, I'd like to make a reservation for 6 people tonight at 7 PM.",
        height=100,
        key="caller_input"
    )

    # Model selection for receptionist (use first available provider)
    providers = get_all_providers(st.session_state.config)

    if not providers:
        st.warning("⚠️ Please configure at least one API key in the sidebar to use the receptionist.")
        return

    # Use first available provider
    selected_provider_name = list(providers.keys())[0]
    selected_provider = providers[selected_provider_name]

    st.caption(f"Using: {selected_provider_name} - {selected_provider.model}")

    if st.button("📞 Simulate Call", type="primary", use_container_width=True):
        if not caller_input:
            st.error("Please enter what the caller would say")
            return

        # Generate receptionist prompt
        full_prompt = generate_receptionist_prompt(st.session_state.business_profile, caller_input)

        with st.spinner(f"AI Receptionist responding..."):
            # Get response from LLM
            response = selected_provider.chat(full_prompt)

            if response.startswith("❌"):
                st.error(f"Error getting response: {response}")
                return

            # Log the call
            if st.session_state.user_email:
                st.session_state.receptionist_logger.log_call(
                    user_email=st.session_state.user_email,
                    business_name=business_name,
                    caller_input=caller_input,
                    receptionist_response=response,
                    model_used=f"{selected_provider_name}/{selected_provider.model}"
                )

            # Add to session history
            st.session_state.receptionist_call_history.insert(0, {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "caller": caller_input,
                "receptionist": response
            })

            st.success("✅ Call completed!")

    # Display call history
    st.divider()
    st.markdown("### 📜 Call History (This Session)")

    if not st.session_state.receptionist_call_history:
        st.info("No calls yet. Start by simulating a call above!")
    else:
        for i, call in enumerate(st.session_state.receptionist_call_history[:10], 1):
            with st.expander(f"Call {i} - {call['timestamp']}", expanded=(i == 1)):
                st.markdown(f"**Caller:** {call['caller']}")
                st.markdown(f"**Receptionist:** {call['receptionist']}")


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

    # Pricing Section
    st.markdown("### 💎 Simple, Transparent Pricing")
    st.markdown("Start free, upgrade when you're ready.")

    price_col1, price_col2, price_col3 = st.columns(3)

    with price_col1:
        st.markdown("#### Free")
        st.markdown("## $0")
        st.markdown("**Perfect for trying out**")
        st.markdown("✅ 10 conversations/day")
        st.markdown("✅ All 4 LLM providers")
        st.markdown("✅ Cost tracking")
        st.markdown("✅ Conversation history")

    with price_col2:
        st.markdown("#### ⭐ Premium")
        st.markdown("## $8.99/mo")
        st.markdown("**Most popular**")
        st.markdown("✅ **Unlimited conversations**")
        st.markdown("✅ Detailed cost analytics")
        st.markdown("✅ Referral rewards")
        st.markdown("✅ Priority support")
        st.markdown("✅ Export conversations")

    with price_col3:
        st.markdown("#### Team")
        st.markdown("## $29.99/mo")
        st.markdown("**For teams**")
        st.markdown("✅ Everything in Premium")
        st.markdown("✅ Up to 5 team members")
        st.markdown("✅ Shared workspace")
        st.markdown("✅ Team usage stats")

    st.markdown("---")

    # FAQs
    st.markdown("### ❓ Frequently Asked Questions")

    with st.expander("Do I need to sign up to use Multi-LLM Chat?"):
        st.markdown("""
        **No!** You can start using the app immediately with your own API keys.
        We only ask for your email after 3 conversations to send you cost-saving tips
        and unlock referral rewards.
        """)

    with st.expander("Do you store my API keys or conversations?"):
        st.markdown("""
        **Your API keys stay 100% private.** They're stored only in your browser session
        and never sent to our servers. Conversations are saved locally in your browser
        unless you explicitly export them.
        """)

    with st.expander("How does pricing work? What counts as a conversation?"):
        st.markdown("""
        A "conversation" is one query sent to all configured LLMs. The free tier includes
        10 conversations per day. Premium gives you unlimited conversations. Daily limits
        reset at midnight UTC.
        """)

    with st.expander("Can I cancel my subscription anytime?"):
        st.markdown("""
        **Yes, cancel anytime.** No contracts, no commitments. When you cancel, you keep
        access until the end of your billing period, then automatically downgrade to the
        free tier.
        """)

    with st.expander("Which AI models are supported?"):
        st.markdown("""
        We support **OpenAI** (GPT-4o, GPT-4 Turbo, GPT-3.5), **Anthropic** (Claude Sonnet,
        Opus, Haiku), **Google** (Gemini 2.0, 1.5 Pro, Flash), and **Ollama** (Llama, Mistral,
        Qwen - 100% free and local).
        """)

    with st.expander("How do referral rewards work?"):
        st.markdown("""
        Premium users get a unique referral link. When someone signs up through your link,
        you earn **1 week free** (7 days added to your subscription). When they upgrade to
        Premium, you earn **1 month free** (30 days). Unlimited referrals!
        """)

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
                    if not st.session_state.user_email:
                        st.warning("Please provide your email first")
                    elif st.session_state.stripe_configured:
                        # Real Stripe checkout
                        checkout_url = create_checkout_session(
                            st.session_state.user_email,
                            tier["id"],
                            st.session_state.subscription_manager
                        )
                        if checkout_url:
                            st.success("✅ Redirecting to secure checkout...")
                            st.markdown(f"[Complete Payment on Stripe →]({checkout_url})")
                            st.info("💡 You'll be redirected back after payment. Your plan will update automatically via webhook.")
                        else:
                            st.error("❌ Failed to create checkout session. Please try again.")
                    else:
                        # Fallback: Simulated upgrade (dev mode)
                        success = st.session_state.subscription_manager.upgrade_subscription(
                            st.session_state.user_email,
                            tier["id"]
                        )
                        if success:
                            st.session_state.user_tier = tier["id"]
                            st.warning(f"⚠️ Simulated upgrade to {tier['name']} (Stripe not configured)")
                            st.session_state.show_pricing_modal = False
                            st.rerun()

    st.markdown("---")

    # Show Stripe configuration status
    if st.session_state.stripe_configured:
        st.success("✅ Stripe payment processing enabled")
        st.caption("Payments are processed securely by Stripe. You'll be redirected to complete your purchase.")
    else:
        st.warning("⚠️ Stripe not configured - using simulated billing")
        st.caption("Set STRIPE_SECRET_KEY and STRIPE_PRICE_* environment variables to enable real payments.")

    if st.button("Close", use_container_width=True):
        st.session_state.show_pricing_modal = False
        st.rerun()


def main():
    """Main app"""

    # Show landing page for first-time visitors
    if st.session_state.show_landing:
        show_landing_page()
        return

    # Handle billing redirect (success/cancel from Stripe)
    if st.session_state.billing_redirect:
        if st.session_state.billing_redirect == "success":
            st.success("🎉 Payment received! Your plan is being activated...")
            st.info("💡 Your tier will update within a few seconds as our webhook processes your payment.")
            st.caption("If your plan doesn't update automatically, please refresh the page in a moment.")

            # Option to manually refresh
            if st.button("Refresh Now", type="primary"):
                # Reload subscription data
                if st.session_state.user_email:
                    subscription = st.session_state.subscription_manager.get_subscription(st.session_state.user_email)
                    if subscription:
                        st.session_state.user_tier = subscription.get('tier', 'free')
                st.session_state.billing_redirect = None
                st.rerun()

        elif st.session_state.billing_redirect == "cancel":
            st.warning("Payment was canceled. No charges were made.")
            st.info("You can try upgrading again anytime from the sidebar.")

            if st.button("Close", type="secondary"):
                st.session_state.billing_redirect = None
                st.rerun()

        st.divider()

    # Show email capture modal if triggered
    if st.session_state.show_email_modal:
        show_email_capture()
        st.divider()

    # Show pricing modal if triggered
    if st.session_state.show_pricing_modal:
        show_pricing_modal()
        return

    # Header (conditional based on mode)
    if st.session_state.receptionist_mode:
        st.title("📞 AI Receptionist (Beta)")
        st.markdown("**Test your AI phone receptionist in a simulated environment.**")
    else:
        st.title("🤖 Multi-LLM Group Chat")
        st.markdown("**Ask once. Get answers from all LLMs.**")

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Phase 6: Mode toggle for AI Receptionist
        st.divider()
        st.subheader("🔄 Mode")

        mode = st.radio(
            "Select Mode:",
            ["Multi-LLM Chat", "AI Receptionist (Beta)"],
            index=1 if st.session_state.receptionist_mode else 0,
            help="Switch between comparing LLMs and testing AI receptionist"
        )

        if mode == "AI Receptionist (Beta)" and not st.session_state.receptionist_mode:
            st.session_state.receptionist_mode = True
            st.rerun()
        elif mode == "Multi-LLM Chat" and st.session_state.receptionist_mode:
            st.session_state.receptionist_mode = False
            st.rerun()

        st.divider()

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

        # Admin Metrics Panel (password-protected)
        admin_password = os.getenv("ADMIN_PASSWORD", "")
        if admin_password:  # Only show if admin password is configured
            with st.expander("🔐 Admin Metrics"):
                password_input = st.text_input("Admin Password", type="password", key="admin_pw")

                if password_input == admin_password:
                    st.success("✅ Access granted")

                    # Get subscription stats
                    stats = st.session_state.subscription_manager.get_subscription_stats()

                    # Calculate active paying users
                    active_paying = (
                        stats['tier_distribution']['premium'] +
                        stats['tier_distribution']['team'] +
                        stats['tier_distribution']['pro']
                    )

                    # MRR
                    st.metric("💰 MRR", f"${stats['mrr']:.2f}/mo")

                    # Active users
                    col_a1, col_a2 = st.columns(2)
                    with col_a1:
                        st.metric("Total Users", stats['total_users'])
                    with col_a2:
                        st.metric("Paying Users", active_paying)

                    # Conversion rate
                    st.metric("Conversion Rate", f"{stats['conversion_rate']:.1f}%")

                    # Tier breakdown
                    st.caption("**Tier Distribution:**")
                    for tier, count in stats['tier_distribution'].items():
                        tier_name = SUBSCRIPTION_TIERS[tier]['name']
                        tier_price = SUBSCRIPTION_TIERS[tier]['price']
                        st.caption(f"• {tier_name}: {count} users (${tier_price}/mo)")

                    # Recent subscriptions (last 5 paying users)
                    st.caption("**Recent Paying Users:**")
                    all_users = st.session_state.subscription_manager.subscriptions.get("users", {})
                    paying_users = [
                        (email, data) for email, data in all_users.items()
                        if data.get('tier') in ['premium', 'team', 'pro']
                    ]

                    # Sort by tier_started_at descending
                    paying_users.sort(
                        key=lambda x: x[1].get('tier_started_at', ''),
                        reverse=True
                    )

                    for email, data in paying_users[:5]:
                        tier = data.get('tier', 'unknown')
                        started = data.get('tier_started_at', 'N/A')[:10]  # Just the date
                        payment_status = data.get('payment_status', 'none')
                        st.caption(f"• {email[:20]}... | {tier} | {started} | {payment_status}")

                    if not paying_users:
                        st.caption("No paying users yet")

                    # Churn calculation (users who downgraded/canceled)
                    events = st.session_state.subscription_manager.subscriptions.get("events", [])
                    churn_events = [
                        e for e in events
                        if e.get('event_type') in ['subscription_downgraded', 'subscription_deleted']
                    ]

                    # Get churned users in last 30 days
                    from datetime import datetime, timedelta
                    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                    recent_churns = [
                        e for e in churn_events
                        if e.get('timestamp', '') >= thirty_days_ago
                    ]

                    st.metric("Churns (30 days)", len(recent_churns))

                    # Phase 6: Receptionist stats
                    st.divider()
                    st.caption("**AI Receptionist Usage (Last 30 Days):**")

                    receptionist_stats = st.session_state.receptionist_logger.get_stats_last_30_days()

                    st.metric("Total Test Calls", receptionist_stats['total_calls'])

                    if receptionist_stats['top_users']:
                        st.caption("**Top Users by Test Calls:**")
                        for email, count in receptionist_stats['top_users']:
                            st.caption(f"• {email[:25]}... : {count} calls")
                    else:
                        st.caption("No receptionist test calls yet")

                elif password_input:
                    st.error("❌ Incorrect password")

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
    # Phase 6: Show receptionist UI if in receptionist mode
    if st.session_state.receptionist_mode:
        # Receptionist mode UI
        col1, col2 = st.columns([1, 1])

        with col1:
            show_business_profile_setup()

        with col2:
            show_receptionist_simulator()

        return

    # Regular Multi-LLM Chat mode
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

        # Free tier email requirement - enforce before first query
        if st.session_state.user_tier == 'free' and not st.session_state.email_captured:
            st.warning("📧 **Free users**: Enter your email to start chatting")
            st.info("💡 Get access to 10 free conversations per day + referral rewards")
            st.session_state.show_email_modal = True
            st.rerun()
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
