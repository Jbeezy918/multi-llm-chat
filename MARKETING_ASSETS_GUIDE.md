# 📸 Marketing Assets Creation Guide

**Purpose**: Create professional visuals for launch campaigns
**Tools Needed**: Screenshot tool, Canva (free), or Figma

---

## 🎨 Asset Checklist

### Priority 1: Must-Have (Create First)
- [ ] App screenshot (full interface)
- [ ] Cost comparison screenshot
- [ ] Demo GIF (15 seconds)
- [ ] Social preview image (1200x630px)

### Priority 2: Launch Week
- [ ] Product Hunt thumbnail (1270x760px)
- [ ] Product Hunt gallery (3-5 images)
- [ ] Twitter header (1500x500px)
- [ ] Quote cards (3-5 variations)

### Priority 3: Post-Launch
- [ ] Blog post featured images
- [ ] Video tutorial
- [ ] User testimonial graphics
- [ ] Comparison charts

---

## 📱 Screenshot Guide

### 1. Full App Screenshot
**What to capture:**
- Landing page with "Get Started" button visible
- OR main chat interface with all providers showing
- OR side-by-side comparison of responses

**How to capture:**
1. Open app in browser
2. Set window to 1440x900px (standard desktop)
3. Use CMD+SHIFT+4 (Mac) or Snipping Tool (Windows)
4. Capture full interface
5. Save as `app-screenshot-full.png`

**Optimization:**
- Make sure UI is clean (no errors, full responses visible)
- Use a real example query like "Explain quantum computing"
- Show all 4 providers if possible

### 2. Cost Comparison Screenshot
**What to capture:**
- Sidebar showing "Session Costs" section
- Multiple LLM queries with costs displayed
- Savings calculator visible

**Text overlay to add:**
- "See exactly how much each AI costs"
- Arrow pointing to cost display

**Save as:** `cost-tracking-screenshot.png`

### 3. Side-by-Side Comparison
**What to capture:**
- Full conversation history view
- Responses from 2-4 different LLMs
- Same question, different answers visible

**Save as:** `comparison-screenshot.png`

---

## 🎬 Demo GIF Creation

### Tools
- **Mac**: Kap (free) - https://getkap.co
- **Windows**: ScreenToGif (free)
- **Online**: Loom (export as GIF)

### Script (15 seconds)
1. Show landing page (2s)
2. Click "Get Started" (1s)
3. Type question in input box (2s)
4. Click "Ask All LLMs" (1s)
5. Show loading state (2s)
6. Reveal all 4 responses side-by-side (5s)
7. Scroll to show cost tracking (2s)

### Settings
- **Size**: 800x600px or 1000x750px
- **FPS**: 10-15 (keeps file size small)
- **Duration**: 10-15 seconds
- **File size**: Under 5MB (for Twitter)

### Optimization
- Use a short, impactful question
- Example: "What is the capital of France?"
- Shows speed and simplicity

**Save as:** `demo.gif`

---

## 🖼️ Social Preview Images

### Open Graph Image (1200x630px)
**Purpose**: Shows when link is shared on Facebook, LinkedIn, Slack

**Design elements:**
- Background: Dark gradient (#0E1117 to #262730)
- Logo: 🤖 icon large and centered
- Headline: "Compare GPT-4, Claude, Gemini & Llama"
- Subheadline: "Free AI Model Comparison Tool"
- Visual: Screenshot or mockup of app
- Badge: "100% Free • Open Source"

**Tools:**
- Canva template: Search "Open Graph"
- Or use: https://www.opengraph.xyz/

**Save as:** `og-image.png`

### Twitter Card (1200x675px)
**Purpose**: Shows when link is shared on Twitter/X

**Design (similar to OG but optimized for Twitter):**
- Same layout as OG image
- Add: "Try it now →" CTA
- Optional: GitHub stars count

**Save as:** `twitter-card.png`

---

## 🏆 Product Hunt Assets

### Thumbnail (1270x760px)
**Required**: This is the main image shown in PH feed

**Design:**
- Clean, professional look
- App logo (🤖) large
- Tagline: "Compare AI Models Side-by-Side"
- Screenshot or mockup in background (subtle)
- High contrast, readable at small sizes

**Text overlay:**
- Main: "Multi-LLM Chat"
- Sub: "GPT-4 • Claude • Gemini • Llama"
- Badge: "Free Forever"

**Save as:** `ph-thumbnail.png`

### Gallery Images (880x440px each, 3-5 images)

**Image 1: Landing Page**
- Screenshot of landing page
- Overlay: "Ask once. Get answers from all LLMs."

**Image 2: Side-by-Side Comparison**
- Screenshot showing multiple responses
- Overlay: "Compare quality instantly"

**Image 3: Cost Tracking**
- Screenshot of cost sidebar
- Overlay: "Know exactly what you're spending"

**Image 4: Provider Support**
- Grid showing logos: OpenAI, Anthropic, Google, Ollama
- Text: "Works with 4+ AI providers"

**Image 5 (Optional): Demo GIF**
- Animated demo of full workflow

**Save as:** `ph-gallery-1.png`, `ph-gallery-2.png`, etc.

---

## 🐦 Twitter Assets

### Header Image (1500x500px)
**Purpose**: Twitter profile header

**Design:**
- Brand name: "Multi-LLM Chat"
- Value prop: "Compare GPT-4, Claude, Gemini & Llama"
- Visual: Subtle app interface in background
- CTA: "Try Free → [URL]"

**Save as:** `twitter-header.png`

### Quote Cards (1080x1080px)

**Card 1: Value Prop**
```
"Stop switching between
ChatGPT, Claude, and Gemini.

Compare all AI models
in ONE place."

multi-llm-chat.streamlit.app
```

**Card 2: Cost Savings**
```
"I saved $50/month
by comparing AI models
before every query."

See your real costs
multi-llm-chat.streamlit.app
```

**Card 3: Feature Highlight**
```
"Ask once.
Get answers from:
✅ GPT-4
✅ Claude
✅ Gemini
✅ Llama

Side-by-side comparison
multi-llm-chat.streamlit.app
```

**Design tips:**
- Use brand colors (dark background)
- Large, readable text
- Emoji for visual interest
- URL at bottom

**Save as:** `quote-card-1.png`, `quote-card-2.png`, `quote-card-3.png`

---

## 📊 Comparison Charts

### Cost Comparison Chart
**Purpose**: Show pricing differences between models

**Data to visualize:**
```
Model              Input (per 1M tokens)  Output (per 1M tokens)
GPT-4 Turbo        $10.00                 $30.00
Claude Opus        $15.00                 $75.00
GPT-4o             $2.50                  $10.00
Claude Sonnet      $3.00                  $15.00
GPT-4o-mini        $0.15                  $0.60
Gemini Flash       $0.08                  $0.30
Ollama (local)     $0.00                  $0.00
```

**Chart type**: Horizontal bar chart
**Tool**: Google Sheets → Export as image

**Callout**: "Save 90% by choosing the right model"

**Save as:** `cost-comparison-chart.png`

---

## 🎬 Video Tutorial (Optional - Week 2)

### Quick Demo Video (60 seconds)
**Script:**
1. "Tired of switching between AI models?" (5s)
2. "Meet Multi-LLM Chat" (3s)
3. Demo: Type question → Get all responses (20s)
4. Highlight: Cost tracking (10s)
5. "Compare GPT-4, Claude, Gemini, Llama" (5s)
6. "Free to use. Try it now." (5s)
7. Show URL (5s)

**Tools:**
- Loom (free, easy)
- Screen recording: OBS (free)
- Editing: iMovie (Mac) or DaVinci Resolve (free)

**Specs:**
- 1080p (1920x1080)
- 60 seconds max
- Upload to YouTube, Twitter, Product Hunt

---

## 🚀 Quick Start: Create Priority Assets in 30 Minutes

### Step 1: Screenshots (10 min)
1. Open app
2. Take 3 screenshots:
   - Full landing page
   - Side-by-side comparison
   - Cost tracking sidebar

### Step 2: Demo GIF (10 min)
1. Install Kap or ScreenToGif
2. Record 15-second demo
3. Export as GIF under 5MB

### Step 3: Social Preview (10 min)
1. Go to Canva.com
2. Search "Open Graph Template"
3. Add screenshot, logo, text
4. Export as PNG (1200x630px)

**Done!** You now have the minimum assets needed for launch.

---

## 📁 File Naming Convention

```
app-screenshot-full.png
app-screenshot-comparison.png
app-screenshot-cost-tracking.png
demo.gif
og-image.png
twitter-card.png
ph-thumbnail.png
ph-gallery-1.png
ph-gallery-2.png
ph-gallery-3.png
twitter-header.png
quote-card-1.png
quote-card-2.png
quote-card-3.png
cost-comparison-chart.png
```

Store in: `~/Projects/multi-llm-chat/assets/`

---

## ✅ Asset Checklist Before Launch

**Day Before Launch:**
- [ ] Full app screenshot captured
- [ ] Demo GIF created (under 5MB)
- [ ] OG image created (1200x630px)
- [ ] PH thumbnail created (1270x760px)
- [ ] 3+ PH gallery images ready

**Launch Day:**
- [ ] Upload to Product Hunt
- [ ] Share on Twitter with images
- [ ] Post to Reddit with screenshot
- [ ] Include in email campaign

---

## 🎨 Brand Guidelines

### Colors
- **Primary**: #FF4B4B (Streamlit red)
- **Background**: #0E1117 (dark)
- **Secondary BG**: #262730 (lighter dark)
- **Text**: #FAFAFA (white)

### Fonts
- **Headings**: Sans-serif, bold
- **Body**: Sans-serif, regular

### Logo
- Emoji: 🤖
- Text: "Multi-LLM Chat"

---

**Need help creating assets?**

Use these free tools:
- **Canva**: Templates for all sizes
- **Figma**: Professional design tool
- **Remove.bg**: Remove backgrounds
- **TinyPNG**: Compress images
- **Kap**: Record screen GIFs (Mac)

**Time budget:** 2-3 hours for all priority assets

**Ready to launch once assets are created!** 🚀
