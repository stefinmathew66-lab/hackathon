# 🚀 Hackathon Hunter — 100% Free Hackathon Link Fetcher & Bot

An automated, zero-cost intelligence crawler and bot that fetches real-time links to the latest hackathons across **India** and **Global Online** platforms without requiring any paid APIs or subscriptions.

---

## 🌟 Features

- **Multi-Source Aggregation (100% Free Public Feeds & Endpoints)**:
  - **Devfolio**: Top Indian & global Web3/Tech hackathons.
  - **Unstop**: India's largest college and corporate hackathons.
  - **Devpost**: Global virtual hackathons with major prize pools.
  - **Major League Hacking (MLH)**: Official student & global digital hackathons.
  - **HackerEarth**: Global developer & enterprise challenges.
- **Dedicated India & Global Online Categorization**:
  - Filter specifically for **India (In-Person & Online)** or **Global Online (Virtual)**.
- **Dual Interface**:
  - **Interactive CLI & Bot (`bot.py`)**: Rich colored tables, instant direct links, export to CSV/JSON/Markdown, and interactive terminal UI.
  - **Modern Web Dashboard (`app.py`)**: Dark-mode glassmorphic interface with instant search, platform chips, 1-click apply, copy links, and Google Calendar event sync.
- **Free Automated Bot Alerts**:
  - Send direct alerts to your **Telegram Channel/Chat** or **Discord Channel** for free.
  - Pre-configured **GitHub Actions Workflow** for 100% free daily cloud execution.

---

## 📦 Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## 🤖 Running the CLI & Bot

### Interactive Mode:
```bash
python bot.py --interactive
# or
python bot.py -i
```

### Direct CLI Commands:
```bash
# 1. Fetch Latest Hackathons in India
python bot.py --india

# 2. Fetch Global Online Hackathons
python bot.py --online

# 3. Search by Keyword (e.g. AI, Web3, FinTech)
python bot.py --search "AI"

# 4. Filter by Platform (Devfolio, Unstop, Devpost, HackerEarth, MLH)
python bot.py --platform Devfolio

# 5. Export to Markdown, CSV, or JSON
python bot.py --export hackathons.md
python bot.py --export hackathons.csv
python bot.py --export hackathons.json

# 6. Send Free Alerts to Telegram or Discord
python bot.py --notify-telegram
python bot.py --notify-discord
```

---

## 🌐 Running the Web Dashboard

```bash
python app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to view the interactive dashboard.

### Dashboard Highlights:
- 🔍 **Real-time instant search** across titles, tags, and prize amounts.
- 🎯 **Region tabs**: All, 🇮🇳 India, 🌐 Global Online.
- 🏢 **Platform filters**: Devfolio, Unstop, Devpost, HackerEarth, MLH.
- 📋 **1-Click Copy Link & Apply Button**: Direct navigation to application pages.
- 📅 **Add to Google Calendar**: Auto-generate calendar entries.
- 💾 **Export Menu**: Download Markdown, CSV, or JSON directly.

---

## 📢 Setting up Free Telegram & Discord Alerts (Optional)

### Free Telegram Bot:
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the prompts to get your **Bot Token**.
3. Create a channel or chat with the bot, and get your **Chat ID** (or channel `@username`).
4. Set them in `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

### Free Discord Webhook:
1. In Discord, go to **Server Settings -> Integrations -> Webhooks -> New Webhook**.
2. Copy the Webhook URL.
3. Set it in `.env`:
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

---

## ☁️ 100% Free Cloud Scheduling (GitHub Actions)

A workflow file is already included at `.github/workflows/hackathon_bot.yml`.

1. Push this project to your private or public GitHub repository.
2. In GitHub, go to **Settings -> Secrets and variables -> Actions**.
3. Add your `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, or `DISCORD_WEBHOOK_URL`.
4. The bot will automatically run every day at **9:00 AM UTC (2:30 PM IST)** and send new hackathon links to your channel with **zero server costs**!
