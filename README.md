# Duffle Bot

An automated multi-account bot for interacting with the [Duffle.money](https://www.duffle.money/) waitlist system.

The bot logs into Twitter using cookies, authenticates with Privy, submits emails, completes social tasks, and collects account statistics.  
It supports proxies per account, logging to file, randomized timing, and full automation mode.

---

## ✨ Features

- 🔐 **Twitter login using cookies** (twikit)
- 🔗 **Privy OAuth pipeline automated**
- 📩 **Automatic email submission to Duffle waitlist**
- 🧩 **Automatic social tasks completion**
  - Follow on Twitter  
  - Join Telegram  
  - Join Discord  
  - Follow Instagram
- 📊 **Per-account statistics**
- 🌐 **Proxy support per account**
- 📝 **Detailed logs** (colored console + `logs/bot.log`)
- 🚀 **Fully automated multi-account flow**
- 🔄 **Random delays to simulate human behaviour**

---

## 📁 Project Structure

```text
duffle-bot/
│
├── core/
│   ├── twitter.py          # Twitter login & OAuth flow
│   ├── duffle.py           # Duffle API & social tasks
│   ├── account.py          # Account model
│   ├── proxies.py          # Proxy loader
│   ├── utils.py            # Utilities & random delays
│   ├── settings.py         # Config + environment loader
│   ├── tasks.py            # Main automation logic
│   └── logger.py           # Logging system
│
├── data/
│   ├── emails.json
│   ├── proxies.json
│   ├── referral_codes.txt
│   ├── emails.example.json
│   ├── proxies.example.json
│   └── twitter_cookies/
│       └── ACC_1.json
│
├── logs/
│   └── bot.log
│
├── .env.example
├── .gitignore
├── requirements.txt
└── main.py
