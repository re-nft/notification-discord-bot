# Notification Discord Bot

Discord bot that sends a Discord and Twitter message when there is a new lending or renting in reNFT.

## Install and run

```bash
poetry install
poetry run python notification_discord_bot/main.py
```

## Format

```bash
poetry run isort .
poetry run black .
```

## Lint

```bash
poetry run pylint --recursive=y
```

## Run tests

```bash
poetry run pytest
```
