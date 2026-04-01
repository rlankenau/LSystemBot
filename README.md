# LSystemBot

A Discord bot for generating fractal images using [L-systems](https://en.wikipedia.org/wiki/L-system). Invite it to your server, configure a rule and some parameters, and watch it draw beautiful recursive geometry.

---

## Table of Contents

- [What is an L-system?](#what-is-an-l-system)
- [Bot Commands](#bot-commands)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Running Locally](#running-locally)
  - [Running with GitHub Actions](#running-with-github-actions)
- [Configuration Reference](#configuration-reference)
- [Example L-system Rules](#example-l-system-rules)

---

## What is an L-system?

An L-system (Lindenmayer system) is a recursive rewriting system that can describe complex fractal shapes with a compact rule string. Starting from a simple line segment, the bot repeatedly applies the rule to every segment until it reaches the configured iteration depth, then draws the result.

Each rule is a space-separated sequence of commands:

| Command | Meaning |
|---------|---------|
| `L/<n>` | Draw a line segment scaled by `1/n` |
| `R<deg>` | Rotate the drawing direction by `<deg>` degrees (positive = counter-clockwise) |

**Example** – Koch snowflake edge rule: `L/3 R-60 L/3 R120 L/3 R-60 L/3`

---

## Bot Commands

All commands are prefixed with `!lsys`.

### `!lsys draw`
Generate and post an image using the current parameters.

### `!lsys set <parameter>=<value>`
Change a parameter. Available parameters:

| Parameter | Description | Example value |
|-----------|-------------|---------------|
| `rule` | The L-system rule string | `L/3 R-60 L/3 R120 L/3 R-60 L/3` |
| `iterations` | Recursion depth (0–9) | `4` |
| `size` | Image size preset (see below) | `fhd` |
| `initial_shape` | Starting geometry | `hline` |
| `color` | Line color (name or `start:end` for gradient) | `cyan:magenta` |
| `background_color` | Background fill color | `black` |

#### Available `size` presets

| Preset | Width × Height |
|--------|---------------|
| `bandcamp-min` | 1400 × 1400 |
| `bandcamp` *(default)* | 2000 × 2000 |
| `qsxga` | 2560 × 2000 |
| `wqhd` | 2560 × 1440 |
| `wuxga` | 1920 × 1200 |
| `fhd` / `1080p` | 1920 × 1080 |
| `uhd` | 3440 × 1440 |
| `4k` | 3840 × 2160 |
| `8k` | 7680 × 4320 |
| `svga` | 800 × 600 |
| `vga` | 640 × 480 |

#### Available `initial_shape` values

`hline`, `hline2`, `hline3`, `hline4`, `vline`, `vline2`, `vline3`, `vline4`, `vline5`, `low+wide`, `triangle`, `2`

### `!lsys params`
Show the current parameter settings.

### `!lsys save <name>`
Save the current parameters under `<name>`.

### `!lsys load <name>`
Restore a previously saved set of parameters.

### `!lsys describe <name>`
Show the parameters stored under `<name>`.

### `!lsys catalog`
List all saved parameter sets.

### `!lsys sizes`
Show available image size presets.

---

## Setup

### Prerequisites

- Python 3.10 or newer
- A [Discord application and bot token](https://discord.com/developers/applications)
  - Enable the **Message Content Intent** in the bot settings

### Running Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/rlankenau/LSystemBot.git
   cd LSystemBot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set the bot token**

   ```bash
   export DISCORD_TOKEN="your-discord-bot-token"
   ```

4. **Start the bot**

   ```bash
   python lsysbot.py
   ```

The bot will connect to Discord and print `Ready to roll.` when it is online.

---

### Running with GitHub Actions

The repository includes a workflow (`.github/workflows/run-bot.yml`) that installs dependencies and starts the bot. The workflow runs automatically on every push to `main` and can also be triggered manually from the **Actions** tab.

#### 1. Add the `DISCORD_TOKEN` secret

1. Open your repository on GitHub.
2. Go to **Settings → Secrets and variables → Actions**.
3. Click **New repository secret**.
4. Name it `DISCORD_TOKEN` and paste your bot token as the value.
5. Click **Add secret**.

#### 2. Trigger the workflow

Push a commit to `main` or go to **Actions → Run LSystem Discord Bot → Run workflow**.

> **Note:** GitHub Actions jobs have a maximum runtime of 6 hours. For a long-running bot, consider deploying to a dedicated server, a container platform (e.g. Railway, Fly.io), or using a self-hosted Actions runner.

---

## Configuration Reference

Parameters are persisted between restarts in a local file (`my_params`). If that file is absent the bot starts with sensible defaults:

| Parameter | Default value |
|-----------|--------------|
| `rule` | `R45 L/0.707… R-45 R-45 L/0.707… R45` |
| `iterations` | `1` |
| `initial_shape` | `hline4` |
| `width` | `2000` |
| `height` | `2000` |
| `start_color` | `white` |
| `end_color` | `white` |
| `background_color` | `black` |

Colors accept any name understood by [Pillow's `ImageColor`](https://pillow.readthedocs.io/en/stable/reference/ImageColor.html) (e.g. `red`, `#ff0000`, `rgb(255,0,0)`). Use `start:end` notation to draw a gradient along the line segments.

---

## Example L-system Rules

| Name | Rule | Iterations |
|------|------|-----------|
| Koch curve | `L/3 R-60 L/3 R120 L/3 R-60 L/3` | 4 |
| Lévy C curve | `R45 L/0.70710678118654752440084436210485 R-45 R-45 L/0.70710678118654752440084436210485 R45` | 8 |
| Cantor dust | `L/3 R0 L/3` | 6 |
