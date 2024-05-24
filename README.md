# Telegram Bot: Raspberry Pi Controller for WS281x LEDs

This is a Telegram bot that lets users control WS281x LEDs connected to a Raspberry Pi.

## How To Use

### Requirements

#### Hardware

- Raspberry Pi
- WS281x LEDs

#### Software

- `python3` with the following modules:
  - `aiogram`
  - `rpi_ws281x`

#### APIs

- Telegram bot API key (https://core.telegram.org/bots/tutorial)

### Configuration

The following environment variables need to be set:

- `TELEGRAM_BOT_TOKEN`

### Run

For testing, simply run `main.py`

For productive use, install the `telegram-bot-rpi-ws281x.service` systemd unit file.
