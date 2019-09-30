from urllib3 import PoolManager
from bs4 import BeautifulSoup
from telegram.ext import Updater
from telegram import ParseMode
from markdownify import markdownify as md
from hashlib import sha256
import sys
import time


class Entry:

    def __init__(self, title, text, date):

        self.title = str(title)
        self.text = str(text)
        self.date = str(date)

    def __str__(self):

        text = ''

        text = text + self.title
        text = text + self.text

        return text


def main(bot, chat_id):

    html_content = get_html_content()
    entries = get_entries(html_content)
    last_message_date = get_last_message_date(bot, chat_id)

    entries = filter_entries(entries, last_message_date)

    print(entries)

    send_messages(entries, bot, chat_id)


def get_telegram_token():

    try:

        token = sys.argv[1]

    except IndexError:

        raise ValueError('No token given')

    return token


def get_html_content():

    manager = PoolManager()
    method = 'GET'
    url = 'https://labs.inf.fh-dortmund.de/ctfd/notifications'

    content = manager.request(method=method, url=url)
    html_content = content.data.decode('utf-8')

    return html_content


def get_entries(html_content):

    entries = []

    soup = BeautifulSoup(html_content, features="html.parser")

    cards = soup.findAll('div', {'class': 'card'})

    for card in cards:

        title = card.find('h3', {'class': 'card-title'}).text
        text = card.find('blockquote', {'class': 'blockquote'})
        time = card.find('small', {'class': 'text-muted'}).text
        entry = Entry(title, text, time)
        entries.append(entry)

    return entries


def get_last_message_date(bot, chat_id):

    last_date = bot.getChat(chat_id=chat_id).description

    return last_date


def set_last_message_date(bot, message, chat_id):

    date = message.date

    bot.set_chat_description(chat_id, date)


def filter_entries(raw_entries, last_message_date):

    entries = []

    for entry in raw_entries:

        date = entry.date

        if date == last_message_date:

            return entries

        entries.append(entry)

    return entries


def send_messages(entries, bot, chat_id):

    if not entries:

        return

    last_message = entries[0]

    set_last_message_date(bot, last_message, chat_id)

    for entry in reversed(entries):

        message = format_message(entry)

        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)

        print(message)

        time.sleep(1)


def format_message(message):

    html_tags_to_be_removed = ['h7']

    message = md(message, strip=html_tags_to_be_removed)

    return message


if __name__ == '__main__':

    fallback_id = 145310771
    chat_id = -1001346269832
    token = get_telegram_token()
    bot = Updater(token=token).bot

    try:

        main(bot, chat_id)

    except Exception as exception:

        text = 'RUB - CHAT:\n'
        text += str(exception)
        text += exception.with_traceback()

        bot.send_message(fallback_id, text)
