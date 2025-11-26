import telegram
import asyncio


def send_telegram_message(message: str) -> None:
    try:
        bot = telegram.Bot(token="8034275235:AAGq4zP6ueqZVWt-Bo4LHGyO3yoQeoHW2lE")
        asyncio.run(bot.send_message(chat_id=1656262418, text=message))
    except Exception:
        print("Send telegram message failed.")


if __name__ == "__main__":
    send_telegram_message(
        message="Hello, this is a test ✅",
    )
