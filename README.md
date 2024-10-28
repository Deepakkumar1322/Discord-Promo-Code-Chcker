# Discord Promo Code Checker

Welcome to the **Discord Promo Code Checker**! This project allows you to validate a list of Discord promotional links, checking if they are expired or still valid. The tool is efficient, scalable, and capable of handling rate limits, while tracking the status of each checked link and providing detailed logs in a color-coded console output.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logging](#logging)
- [Output Files](#output-files)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Multi-Token Support**: Rotate between multiple tokens to avoid rate limits.
- **Asynchronous Processing**: Uses `aiohttp` and `tasksio` for handling multiple promo code checks concurrently.
- **Rate Limit Management**: Automatically handles rate limits and retries requests.
- **Color-Coded Logging**: Provides clear visual feedback using ANSI color codes.
- **Efficient Duplicate Checking**: Prevents saving duplicate promo codes.
- **Detailed Logs**: Logs status and errors with timestamps and categories.
- **Configurable Settings**: Adjustable parameters through a `config.json` file.

## Prerequisites

Ensure you have the following installed:

- Python 3.7+
- All dependencies listed in `requirements.txt`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/discord-promo-code-checker.git
cd discord-promo-code-checker
