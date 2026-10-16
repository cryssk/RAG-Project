# Project Human in the loop

Agents built with **LangChain** and **LangGraph** that read Gmail, summarize the emails with **Claude**, and send the result via **Telegram**, with an optional **Human in the Loop** step: you approve, edit, or reject the action before it runs.

The project was built in stages. Each script introduces one LangChain middleware, and the last one combines all of them into a complete agent.

## Scripts

| File | What it does |
|---|---|
| `01_sumarization.py` | `SummarizationMiddleware`: summarizes long conversations (with a Portuguese prompt) to save tokens. |
| `02_fallback.py` | `ModelFallbackMiddleware`: if the main model fails, a backup model responds. |
| `03_email_agent.py` | `HumanInTheLoopMiddleware`: the agent reads the latest email from a sender, writes a reply, and **pauses** so you can approve, edit, or reject it before it is sent via SMTP. |
| `04_daily_email_agent_wapp.py` | Version of the daily summary that sends via WhatsApp (CallMeBot). |
| `05_daily_email_agent_tlg.py` | **Main agent.** Summarizes the unread emails from each period of the day (morning, afternoon, and evening) and sends the summary via **Telegram**. |

## How the Telegram agent (`05`) works

1. It reads the unread emails received during the period through Gmail **IMAP**. The mailbox is opened in read-only mode, so no email is marked as read.
2. **Claude Haiku 4.5** writes one line per email (`• summary — sender`). If it fails, **Claude Sonnet 5.5** takes over (fallback).
3. The agent calls the `enviar_resumo` tool, which sends the text to your chat through the **Telegram Bot API** (`sendMessage`). Messages longer than 4,000 characters are split into parts.
4. With `APROVAR_ANTES_DE_ENVIAR = True`, sending pauses and shows the draft in the terminal so you can approve, edit, or reject it (Human in the Loop).

The schedules, message headers, and cost limits are in the **CONFIGURAÇÃO** block at the top of the file.

### Why Telegram?

The Telegram Bot API is free, official, and doesn't require a business phone number or a third-party service. All you need is a token and the chat ID to send messages with a simple HTTP request.

## Requirements

- Python 3.10 or newer
- An Anthropic API key: https://platform.claude.com/settings/keys
- A Gmail account with **2-Step Verification** and an **app password** (see below)
- A Telegram bot (see below)

## Installation

```bash
pip install python-dotenv requests langchain langgraph langchain-anthropic
```

## Step by step: Gmail app password

Google doesn't accept your regular password in programs that use IMAP/SMTP. You need to generate an **app password**, a 16-letter password that grants access only to email and can be revoked at any time.

1. Go to https://myaccount.google.com and sign in to the account the agent will read.
2. Go to **Security** and turn on **2-Step Verification**. Without it, the app password option doesn't appear.
3. Open https://myaccount.google.com/apppasswords (or search for "App passwords" in the account search bar).
4. Enter a name for the app, for example `Email agent`, and click **Create**.
5. Copy the 16-letter password that appears. It is shown only once.
6. Put the password in `.env` as `GMAIL_APP_PASSWORD`. The spaces can be removed.
7. Make sure IMAP is enabled in Gmail: **Settings (gear) → See all settings → Forwarding and POP/IMAP → Enable IMAP**. It is already enabled on new accounts.

> Work or school accounts (Google Workspace) may have app passwords blocked by the administrator. In that case, use a personal account or ask for access.

To revoke access, go back to https://myaccount.google.com/apppasswords and delete the password.

## Step by step: Telegram bot

1. In Telegram, open a chat with **@BotFather**.
2. Send `/newbot` and choose a name and a username for the bot (the username must end in `bot`).
3. BotFather replies with the bot's **token** (format `123456789:ABC...`). Put it in `TELEGRAM_BOT_TOKEN`.
4. Open the chat with your bot and send any message (e.g. `hi`). The bot can only message people who have messaged it first.
5. Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in your browser and look for `"chat":{"id": ...}`. That number is the `TELEGRAM_CHAT_ID`.


## Security

- The agent only **reads** Gmail (read-only mode) and only sends messages to your chat.
- The prompt tells the model to ignore instructions written inside the emails, to reduce the risk of *prompt injection*.
- If sending to Telegram fails, the error message doesn't show the URL, which contains the bot token.
