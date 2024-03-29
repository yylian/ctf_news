from urllib3 import PoolManager
from bs4 import BeautifulSoup
from telegram.ext import Updater
from telegram import ParseMode
from markdownify import markdownify as md
import sys
import time


DESCRIPTION_APPENDIX = ' https://github.com/yylian/ctf_news'


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
    all_entries = get_entries(html_content)
    last_message_date = get_last_message_date(bot, chat_id)

    entries = filter_entries(all_entries, last_message_date)
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

    message = bot.getChat(chat_id=chat_id).description
    last_date = ''

    if message.endswith(DESCRIPTION_APPENDIX):

        position_to_cut_appendix = -1 * len(DESCRIPTION_APPENDIX)
        last_date = message[:position_to_cut_appendix]

    return last_date


def set_last_message_date(bot, message, chat_id):

    date = message.date

    message = date + DESCRIPTION_APPENDIX

    bot.set_chat_description(chat_id, message)


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

        time.sleep(1)


def format_message(message):

    message = md(message)

    return message


if __name__ == '__main__':

    chat_id = -1001346269832
    token = get_telegram_token()
    bot = Updater(token=token, use_context=True).bot

    main(bot, chat_id)
