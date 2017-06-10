#!/usr/bin/env python
# -*- coding: utf-8 -*-

import python_filmaffinity
import os

from telegram import InlineQueryResultArticle, \
    InputTextMessageContent
import telegram
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class FilmaffinityBot:

    def __init__(self, bot, update):
        self.bot = bot
        self.update = update
        self.service = python_filmaffinity.Filmaffinity()

    def start(self):
        self.update.message.reply_text('Hi!')

    def help(self):
        self.update.message.reply_text('Help!')

    def _get_poster_url(self, movie):
        poster = movie['poster']
        poster = poster.replace("https://", "http://")
        return poster

    def _return_list_movies(self, movies):
        html = ''
        for count, movie in enumerate(movies):
            url = self.service.url_film + str(movie['id']) + '.html'
            html += "%s.- <a href='%s'>%s</a>\n" % (count + 1, url, movie['title'])

        self.bot.send_message(
            chat_id=self.update.message.chat_id,
            text=html,
            parse_mode=telegram.ParseMode.HTML
        )

    def _return_movie(self, movie):
        self.bot.send_photo(chat_id=self.update.message.chat_id, photo=self._get_poster_url(movie))
        html = '%s - %s' % (movie['title'], movie['rating'])
        self.bot.send_message(
            chat_id=self.update.message.chat_id,
            text=html,
            parse_mode=telegram.ParseMode.HTML
        )

    def top(self):
        movies = self.service.top_filmaffinity()
        self._return_list_movies(movies)

    def top_netflix(self):
        movies = self.service.top_netflix()
        self._return_list_movies(movies)

    def top_hbo(self):
        movies = self.service.top_hbo()
        self._return_list_movies(movies)

    def recommend_netflix(self):
        movie = self.service.recommend_netflix()
        self._return_movie(movie)

    def recommend_hbo(self):
        movie = self.service.recommend_hbo()
        self._return_movie(movie)

    def premieres(self):
        movies = self.service.top_premieres()
        self._return_list_movies(movies)

    def inlinequery(self):
        query = self.update.inline_query.query
        results = list()
        movies = self.service.search(title=query)
        for movie in movies:
            poster = self._get_poster_url(movie)
            url = self.service.url_film + str(movie['id']) + '.html'
            results.append(InlineQueryResultArticle(id=movie['id'],
                                                    title=movie['title'],
                                                    url=url,
                                                    thumb_url=poster,
                                                    input_message_content=InputTextMessageContent(
                                                        url)))

        self.update.inline_query.answer(results)

    def error(self, error):
        logger.warning('Update "%s" caused error "%s"' % (self.update, error))


def main():
    TOKEN = os.environ.get('TOKEN')
    PORT = int(os.environ.get('PORT', '5000'))
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://filmaffinitybot.herokuapp.com/" + TOKEN)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    filmaffinity = FilmaffinityBot(bot=updater.bot, update=updater)
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", filmaffinity.start))
    dp.add_handler(CommandHandler("help", filmaffinity.help))
    dp.add_handler(CommandHandler("top", filmaffinity.top))
    dp.add_handler(CommandHandler("top_netflix", filmaffinity.top_netflix))
    dp.add_handler(CommandHandler("top_hbo", filmaffinity.top_hbo))
    dp.add_handler(CommandHandler("recommend_netflix", filmaffinity.recommend_netflix))
    dp.add_handler(CommandHandler("recommend_hbo", filmaffinity.recommend_hbo))
    dp.add_handler(CommandHandler("premieres", filmaffinity.premieres))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(filmaffinity.inlinequery))

    # log all errors
    dp.add_error_handler(filmaffinity.error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
