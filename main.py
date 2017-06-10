#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import python_filmaffinity
from uuid import uuid4
import os
import re

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
import telegram
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def _return_list_movies(bot, update, service, movies):
    html = ''
    for count, movie in enumerate(movies):
        url = service.url_film + str(movie['id']) + '.html'
        html += "%s.- <a href='%s'>%s</a>\n" % (count + 1, url, movie['title'])

    bot.send_message(
        chat_id=update.message.chat_id,
        text=html,
        parse_mode=telegram.ParseMode.HTML
    )


def top(bot, update):
    service = python_filmaffinity.Filmaffinity()
    movies = service.top_filmaffinity()
    _return_list_movies(bot, update, service, movies)


def netflix(bot, update):
    service = python_filmaffinity.Filmaffinity()
    movies = service.top_netflix()
    _return_list_movies(bot, update, service, movies)


def hbo(bot, update):
    service = python_filmaffinity.Filmaffinity()
    movies = service.top_hbo()
    _return_list_movies(bot, update, service, movies)


def premieres(bot, update):
    service = python_filmaffinity.Filmaffinity()
    movies = service.top_premieres()
    _return_list_movies(bot, update, service, movies)


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()
    service = python_filmaffinity.Filmaffinity()
    movies = service.search(title=query)
    for movie in movies:
        poster = movie['poster']
        poster = poster.replace("https://", "http://")
        url = service.url_film + str(movie['id']) + '.html'
        results.append(InlineQueryResultArticle(id=movie['id'],
                                                title=movie['title'],
                                                url=url,
                                                thumb_url=poster,
                                                input_message_content=InputTextMessageContent(
                                                    url)))

    update.inline_query.answer(results)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    TOKEN = os.environ.get('TOKEN')
    PORT = int(os.environ.get('PORT', '5000'))
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://<appname>.herokuapp.com/" + TOKEN)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("top", top))
    dp.add_handler(CommandHandler("top_netflix", netflix))
    dp.add_handler(CommandHandler("top_hbo", hbo))
    dp.add_handler(CommandHandler("premieres", premieres))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
