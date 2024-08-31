# Algorithmic Trading Bot using Upstox API

This repository contains a Python-based algorithmic trading bot that interacts with the Upstox API. The bot is designed to execute option trades based on a customizable trading logic. By default, it utilizes a 14-day moving average (MA) indicator to make trading decisions.

## Features

- **Customizable Trading Logic**: Users can easily modify the trading strategy in the main function to suit their needs.
- **Moving Average Indicator**: The bot uses a 14-day moving average by default to identify trading opportunities.
- **Upstox API Integration**: Seamlessly interacts with Upstox to place buy/sell orders.

## Getting Started

### Prerequisites
- Upstox API access token
- Upstox API Python SDK (`upstox` package)
- numpy
- pandas

### Installation

**Clone the repository:**
```
   git clone https://github.com/Manikumarksr/Algo-trading-bot.git
```
## Usage

**Run the Bot:**

Execute the script to start the trading bot:
```
python run_bot.py
```