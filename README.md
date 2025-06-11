# GameMonetize WordPress Bot

This repository contains a simple Python script that fetches HTML5 game embed codes
from [GameMonetize.com](https://www.gamemonetize.com/) and publishes them to a
WordPress site automatically.

## Requirements
- Python 3.8+
- `requests`
- `beautifulsoup4`
- `schedule`
- `tkinter` (usually included with Python)
- `pyinstaller` (for building an executable)

Install the dependencies with:

```bash
pip install requests beautifulsoup4 schedule pyinstaller
```

## Configuration
Edit `gamemonetize_bot.py` and update the following placeholders:

- `WP_API_URL` – WordPress REST API endpoint for posts.
- `WP_USERNAME` and `WP_APP_PASSWORD` – your WordPress credentials or application password.
- `GAME_LIST_URL` – GameMonetize page that lists the games you want to fetch.

## Running
Execute the script with Python:

```bash
python gamemonetize_bot.py
```

The bot uses the `schedule` library to run the job once a day at `02:00`. It should
run continuously so the scheduled task can execute each day.

## GUI Application
Run the graphical interface instead if you prefer a windowed app:

```bash
python gamemonetize_gui.py
```

Click **Start Bot** to fetch and post a game every hour, or **Load Game Now** to
immediately fetch one game. Logs appear in the window and are also written to
`bot.log`.

To create a standalone Windows executable:

```bash
pyinstaller --onefile gamemonetize_gui.py
```
The resulting executable will be located in the `dist/` directory.
