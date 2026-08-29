# 🚀 Hackathon Hunter — 100% Free Hackathon Link Fetcher & Bot

An automated, zero-cost intelligence crawler and bot that fetches real-time links to the latest hackathons across **India** and **Global Online** platforms (Devfolio, Unstop, Devpost, MLH, and HackerEarth) without requiring any paid APIs or subscriptions.

---

## 🌟 Dual Notification Architecture

- 📱 **Personal WhatsApp Alerts (via CallMeBot)**: Sends a daily curated hackathon digest directly to your personal WhatsApp inbox every morning at **8:00 AM IST**.
- 📢 **Telegram Channel Broadcasts**: Broadcasts the latest hackathon opportunities with rich markdown links to your public/private Telegram channel or community group.
- 💻 **Modern Web Dashboard**: Glassmorphic dark UI with live search, platform chips, 1-click apply, copy links, and Google Calendar event sync.
- ⚡ **Zero-Cost 24/7 Cloud Scheduling**: Powered by GitHub Actions to run automatically every day with **zero server costs**.

---

## 📦 Quick Setup (2 Minutes)

### 1. Personal WhatsApp Setup (CallMeBot - 100% Free)
1. Add **`+34 644 44 49 97`** (CallMeBot) to your WhatsApp contacts.
2. Send this exact message on WhatsApp: `I allow callmebot to send me messages`
3. CallMeBot will reply immediately with your free **API Key**.
4. Set in your `.env`:
   ```env
   WHATSAPP_PHONE=+919876543210
   WHATSAPP_APIKEY=your_callmebot_api_key
   ```

### 2. Telegram Broadcast Setup (100% Free)
1. Open Telegram and search for **`@BotFather`**.
2. Send `/newbot` and follow the prompts to get your **Bot Token**.
3. Create your Telegram Channel / Group (e.g. `India Hackathon Alerts`) and add your bot as an **Administrator**.
4. Set in your `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=@your_channel_username
   ```

---

## 🤖 Running the CLI & Bot

```bash
# 1. Interactive Menu
python bot.py -i

# 2. Filter India Hackathons
python bot.py --india

# 3. Filter Global Online Hackathons
python bot.py --online

# 4. Search by Keyword
python bot.py --search "AI"

# 5. Send Personal WhatsApp Alert
python bot.py --notify-whatsapp

# 6. Broadcast to Telegram Channel
python bot.py --notify-telegram

# 7. Send to ALL Channels (WhatsApp + Telegram + Discord)
python bot.py --notify-all
```

---

## 🌐 Running the Web Dashboard

```bash
python app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

---

## ☁️ 100% Free 24/7 Cloud Automation (GitHub Actions)

The workflow file is ready at [`.github/workflows/hackathon_bot.yml`](file://.github/workflows/hackathon_bot.yml).

1. In your GitHub repository (`stefinmathew66-lab/hackathon`), go to **Settings ➔ Secrets and variables ➔ Actions ➔ New repository secret**.
2. Add your secrets:
   - `WHATSAPP_PHONE`
   - `WHATSAPP_APIKEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. **Done!** Every morning at **8:00 AM IST (02:30 UTC)**:
   - Your personal WhatsApp will receive the daily digest.
   - Your Telegram channel will receive the broadcast post.
   - The repository's [`HACKATHONS.md`](file://HACKATHONS.md) will auto-update with fresh live links.
