# 🚀 Deployment Guide - Streamlit Cloud

## Quick Deploy (5 Minutes)

### 1. Deploy to Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Select:
   - **Repository**: `Jbeezy918/multi-llm-chat`
   - **Branch**: `master`
   - **Main file path**: `app.py`
4. Click **"Deploy!"**

### 2. Configure Secrets (Optional)

If you want to pre-configure API keys for users:

1. In your app dashboard, click **"⚙️ Settings"** → **"Secrets"**
2. Add your keys:

```toml
GOOGLE_ANALYTICS_ID = "G-XXXXXXXXXX"

# Optional: Pre-configure API keys (users can still add their own)
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
GEMINI_API_KEY = "..."
```

3. Click **"Save"**

### 3. Get Your Public URL

Your app will be live at:
```
https://[your-app-name].streamlit.app
```

## Custom Domain (Optional)

In Streamlit Cloud settings:
1. Go to **Settings** → **General**
2. Set **Custom subdomain**
3. Or point your own domain via CNAME

## Google Analytics Setup

1. Create a Google Analytics 4 property at [analytics.google.com](https://analytics.google.com)
2. Get your Measurement ID (format: `G-XXXXXXXXXX`)
3. Add to Streamlit secrets as `GOOGLE_ANALYTICS_ID`

## Post-Deployment Checklist

- [ ] App deployed successfully
- [ ] Landing page loads correctly
- [ ] Test with at least one LLM provider
- [ ] Google Analytics tracking works
- [ ] Share URL publicly

## Monitoring

- **Analytics**: Google Analytics dashboard
- **Logs**: Streamlit Cloud dashboard → Logs
- **Errors**: Check Streamlit Cloud dashboard for runtime errors

## Updates

To update your deployed app:

```bash
cd ~/Projects/multi-llm-chat
# Make changes
git add .
git commit -m "Update: description of changes"
git push origin master
```

Streamlit Cloud will auto-deploy the changes within 1-2 minutes.

---

**Your app is live! 🎉**

Share it on:
- Twitter/X
- Product Hunt
- Reddit (r/artificial, r/ChatGPT, r/LocalLLaMA)
- Hacker News
