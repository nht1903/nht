import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from threading import Thread
import time
import logging
import schedule

from gamemonetize_bot import fetch_game_links, parse_game_page, post_to_wordpress, GAME_LIST_URL


class TextHandler(logging.Handler):
    """Logging handler that writes to a Tkinter text widget."""

    def __init__(self, text_widget: ScrolledText):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self._append, msg)

    def _append(self, msg):
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.see(tk.END)


def job():
    logging.info("Fetching game data...")
    try:
        links = fetch_game_links(GAME_LIST_URL)
        if not links:
            logging.info("No game links found.")
            return
        game = parse_game_page(links[0])
        post_to_wordpress(game)
        logging.info("Posted game: %s", game['title'])
    except Exception:
        logging.exception("Error while posting game")


def schedule_loop():
    schedule.every().hour.do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("GameMonetize Bot")

        self.start_button = tk.Button(root, text="Start Bot", command=self.start_bot)
        self.start_button.pack(pady=5)

        self.load_button = tk.Button(root, text="Load Game Now", command=self.load_now)
        self.load_button.pack(pady=5)

        self.log_text = ScrolledText(root, height=20, width=80, state="normal")
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        handler = TextHandler(self.log_text)
        logging.basicConfig(
            level=logging.INFO,
            handlers=[logging.FileHandler("bot.log"), handler],
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        self.bot_thread: Thread | None = None

    def start_bot(self):
        if self.bot_thread and self.bot_thread.is_alive():
            logging.info("Bot already running")
            return
        self.bot_thread = Thread(target=schedule_loop, daemon=True)
        self.bot_thread.start()
        logging.info("Scheduled job started")

    def load_now(self):
        Thread(target=job, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
