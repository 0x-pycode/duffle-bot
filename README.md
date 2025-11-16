# 🐦 Duffle Bot  
Automated multi-account assistant for interacting with the [Duffle.money](https://www.duffle.money/) waitlist system.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Status-Working-success?style=flat-square">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=flat-square">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square">
</p>

Duffle Bot automates:
- Twitter authentication using cookies  
- Privy OAuth pipeline  
- Email submission  
- Social task completion  
- Account statistics collection  
- Multi-account rotation  
- Proxy support  
- Logging  

This repository is designed for educational and research purposes.

---

## ✨ Features

- 🔐 **Twitter login via cookies** (twikit)
- 🔗 **Privy OAuth automation**
- 📩 **Automatic email submission**
- 🧩 **Social tasks completion**
  - Follow on Twitter  
  - Join Telegram  
  - Join Discord  
  - Follow Instagram  
- 📊 **Account statistics**
- 🔄 **Multi-account support**
- 🌐 **Per-account proxies**
- 🎲 **Randomized timing (human-like delays)**
- 📝 **Logs (colored console + logs/bot.log)**

---

## 📁 Project Structure

```
duffle-bot/
│
├── core/
│   ├── twitter.py          # Twitter login & OAuth flow
│   ├── duffle.py           # Duffle API & tasks
│   ├── account.py          # Account model
│   ├── proxies.py          # Proxy loader
│   ├── utils.py            # Utility helpers
│   ├── settings.py         # Config loader
│   ├── tasks.py            # Automation logic
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
├── requirements.txt
├── .gitignore
└── main.py
```

---

## ⚙️ Installation

```bash
git clone https://github.com/0x-pycode/duffle-bot.git
cd duffle-bot

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔧 Configuration

### 1. Create `.env`

Copy example:

```bash
cp .env.example .env
```

Fill in:

```env
PAUSE_FROM=10
PAUSE_TO=15

# Default public Twitter guest bearer token (same for all users, safe to commit)
TWITTER_BEARER_TOKEN=YOUR_TOKEN_HERE

ACCOUNTS=ACC_1,ACC_2
REF_CODES=your_ref_code
```

---

### 2. Configure emails

`data/emails.json`:

```json
{
  "email1@gmail.com": "ACC_1",
  "email2@gmail.com": "ACC_2"
}
```

---

### 3. Configure proxies (optional)

`data/proxies.json`:

```json
{
  "ACC_1": {
    "proxy_host": "123.45.67.89",
    "proxy_port": 8000,
    "login": "proxy_user",
    "passwd": "proxy_pass"
  }
}
```

Leave empty `{}` if not using proxies.

---

### 4. Add Twitter cookies for each account

File name format:

```
data/twitter_cookies/ACC_NAME.json
```

Example:

```json
[
  {"name": "auth_token", "value": "xxx"},
  {"name": "ct0", "value": "yyy"}
]
```

Export cookies from your browser using any cookie extension.

---

## ▶️ Running the Bot

```bash
python main.py
```

Bot will:

- Load accounts  
- Log into Twitter  
- Authenticate via Privy  
- Join the Duffle waitlist  
- Complete tasks  
- Save referral codes  
- Log everything  

---

## 📜 Logging

Logs are stored here:

```
logs/bot.log
```

Console includes colored output for clarity.

---

## 🛡️ `.gitignore`

Sensitive files like:

- `.env`
- `emails.json`
- `proxies.json`
- twitter cookies  
- logs  

…are already ignored and safe.

---

## 📜 License

This project is released under the **MIT License**.  
You are free to fork, modify, and contribute.

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.  
Use responsibly and respect platform rules.
