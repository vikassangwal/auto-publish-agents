# Digital Product Auto-Publisher & AI Creator Agent (v2.0)

Autonomous End-to-End Digital Product Creator, Packager, and Multi-Platform Publisher.
Connect your Custom GPT, Claude, Gemini, Ollama, or DeepSeek — or let the autonomous engine build products from scratch!

---

## 1. How It Works (Zero-to-Publishing)

1. **You Give an Idea/Prompt:** (e.g. "Real Estate ROI Calculator" or "SaaS Financial Model")
2. **AI Brain Builds the Product:** Generates the real .xlsx, .pdf, .docx, or code files with working formulas, styles, and sample data.
3. **Auto-Packaging:** Bundles the production templates, demo files, and Quickstart PDF into a ready-to-sell ZIP package.
4. **Auto-Copywriter:** Writes high-converting headlines, markdown descriptions, features, pricing ($ USD / INR), and SEO tags.
5. **Multi-Platform Publisher:** Uploads to all 20 marketplaces + 10-50 personal websites simultaneously (via API or Zero-API Browser sessions).

---

## 2. Supported AI Providers (Custom GPT & Beyond)

Configure in `.env`:
```env
# 1. Custom GPT / OpenAI
AI_PROVIDER=openai
AI_API_KEY=sk-...
AI_MODEL=gpt-4o

# 2. Free / Local Offline AI (Ollama / LM Studio)
AI_PROVIDER=ollama
AI_MODEL=llama3
AI_BASE_URL=http://localhost:11434/v1

# 3. Google Gemini
AI_PROVIDER=gemini
AI_API_KEY=AIza...
AI_MODEL=gemini-1.5-flash

# 4. Anthropic Claude
AI_PROVIDER=claude
AI_API_KEY=sk-ant-...
AI_MODEL=claude-3-5-sonnet-20241022

# 5. DeepSeek / Groq (Ultra-fast & cheap)
AI_PROVIDER=deepseek
AI_API_KEY=sk-...
AI_MODEL=deepseek-chat
```

---

## 3. Quick Run Commands

```powershell
# 1. Autonomous Mode: Create product from prompt & publish to all 20 sites + personal sites
python main.py --prompt "Real Estate Rental ROI Calculator" --no-api --auto-approve

# 2. Publish an existing file across all sites
python main.py --product "Ultimate_Investment_Portfolio_Tracker_Pro.xlsx" --no-api --auto-approve

# 3. Dry-Run simulation
python main.py --prompt "SaaS Financial Model" --dry-run
```
