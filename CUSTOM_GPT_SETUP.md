# 🤖 Custom GPT Setup Guide — One-Click Auto-Publisher Action

This guide allows you to connect your **ChatGPT Custom GPT** (or any AI App) directly to your Auto-Publisher Agent. 

Once connected, you can simply type in ChatGPT:  
> *"Create a Personal Finance Budget Tracker and publish it everywhere"*  

And your Custom GPT will automatically trigger your agent to build the files, package the ZIP, and upload to all 20 platforms + personal websites!

---

## Step 1: Start Your Agent Server (On Your Computer)

In your terminal, run:

```powershell
cd C:\Users\HP\.gemini\antigravity\scratch\digital_product_autopublisher_agent
python server.py
```

Your server is now active on: `http://localhost:8000`

---

## Step 2: Make It Accessible to ChatGPT (Free 1-Click Public Link)

ChatGPT runs in the cloud, so it needs a secure HTTPS URL to reach your local server. You can use free **Cloudflare Tunnel** or **ngrok**:

### Option A: Cloudflare Tunnel (100% Free, No Login Required)
Run this command in a separate terminal:
```powershell
winget install Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:8000
```
It will give you a public URL like:  
`https://random-words.trycloudflare.com`

### Option B: ngrok (Free)
```powershell
ngrok http 8000
```
It will give you a public URL like:  
`https://your-app.ngrok-free.app`

---

## Step 3: Create Your Custom GPT in ChatGPT

1. Go to **[chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor)** (or click your profile -> **My GPTs** -> **Create a GPT**).
2. Go to the **Configure** tab.

### Fill In These Details:

* **Name:** `AutoPublisher AI Agent`
* **Description:** `Autonomous digital product creator and multi-platform publisher for 20+ marketplaces & websites.`
* **Instructions (Copy-paste this entire block):**
```text
You are AutoPublisher AI Agent, an autonomous digital product publishing assistant.
Your job is to help the user create, package, and publish digital products (Excel spreadsheets, PDF guides, documents, code, templates) across 20+ marketplaces and personal websites.

When the user asks you to create or publish a product:
1. Understand the product concept, format (spreadsheet, document, or code), and target audience.
2. Call the `publish_digital_product` action with:
   - `prompt`: The descriptive title/topic of the product.
   - `format_type`: "spreadsheet" (default), "document", or "code".
   - `no_api`: true (for zero-API browser automation).
   - `auto_approve`: true.
3. Once the action executes, present a neat, structured summary of:
   - Product title and format category.
   - Master deliverable ZIP bundle path.
   - Clickable table of all 20 platforms and status (Gumroad, Lemon Squeezy, Etsy, Whop, Cosmofeed, Instamojo, Product Hunt, etc.).
   - Any manual action items if an OTP or CAPTCHA was flagged.
```

---

## Step 4: Add the GPT Action

1. At the bottom of the GPT configuration page, click **"Create new action"**.
2. In the **Schema** box, paste the contents of `custom_gpt_openapi.json`.
3. In the schema, replace the server URL with your Cloudflare / ngrok public URL:
   ```json
   "servers": [
     {
       "url": "https://your-tunnel-url.trycloudflare.com"
     }
   ]
   ```
4. Click **Save / Publish** (Select "Only me" or "Anyone with link").

---

## 🎯 Done! Now You Can Chat with Your Custom GPT

Whenever you type in ChatGPT on desktop or your mobile phone:

> *"Mujhe ek Real Estate ROI Calculator banana hai aur sabhi jagah publish kar do"*

Your Custom GPT will automatically call the action, your agent on your computer will build the real `.xlsx` file, bundle the documentation, and publish it across **Gumroad, Lemon Squeezy, Etsy, Whop, Payhip, Cosmofeed, Instamojo, Product Hunt, and all your personal websites**!
