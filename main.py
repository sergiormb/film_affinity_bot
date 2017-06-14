#!/usr/bin/env python
# -*- coding: utf-8 -*-
from botanio import botan
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
BOTAN_TOKEN = os.environ.get('BOTAN_TOKEN')


class FilmaffinityBot:

    def __init__(self):
        self.service = python_filmaffinity.Filmaffinity()

    def start(self, bot, update):
        update.message.reply_text('Hi, it helps you to find any movie in Filmaffinity by just mentioning me @Film_Affinity_bot')

    def help(self, bot, update):
        html = """
        This is a bot for Filmaffinity, you can use any of these commands \n
        /top_filmaffinity - Top from Filmaffinity \n
        /top_hbo - Top movies from HBO \n
        /top_netflix - Top movies from Netflix \n
        /top_tv_series - Top TV Series \n
        /top_dvd - Top new DVD \n
        /premieres - Premieres \n
        /recommend_netflix - Return a movie random in Netflix \n
        /recommend_hbo - Return a movie random in HBO \n
        """
        bot.send_message(chat_id=update.message.chat_id, text=html, parse_mode=telegram.ParseMode.HTML)

    def _search_youtube(self, title):
        video = self.service._get_trailer(title)
        return video

    def _get_poster_url(self, movie):
        poster = movie['poster']
        poster = poster.replace("https://", "http://")
        return poster

    def _return_list_movies(self, bot, update, movies):
        html = ''
        for count, movie in enumerate(movies):
            url = self.service.url_film + str(movie['id']) + '.html'
            html += "%s.- <a href='%s'>%s (%s)</a>\n" % (count + 1, url, movie['title'], movie['rating'])

        bot.send_message(
            chat_id=update.message.chat_id,
            text=html,
            parse_mode=telegram.ParseMode.HTML
        )

    def _return_movie(self, bot, update, movie):
        html = '%s - %s' % (movie['title'], movie['rating'])
        bot.send_message(
            chat_id=update.message.chat_id,
            text=html,
            parse_mode=telegram.ParseMode.HTML
        )
        html = 'Trailer: %s ' % self._search_youtube(movie['title'])
        bot.send_message(
            chat_id=update.message.chat_id,
            text=html,
            parse_mode=telegram.ParseMode.HTML
        )

    def _save_stats(self, bot, update):
        uid = update.message.from_user
        message_dict = update.message.to_dict()
        event_name = update.message.text
        botan.track(BOTAN_TOKEN, uid, message_dict, event_name)

    def top_filmaffinity(self, bot, update):
        self._save_stats(bot, update)
        movies = self.service.top_filmaffinity()
        self._return_list_movies(bot, update, movies)

    def top_netflix(self, bot, update):
        self._save_stats(bot, update)
        movies = self.service.top_netflix()
        self._return_list_movies(bot, update, movies)

    def top_hbo(self, bot, update):
        self._save_stats(bot, update)
        movies = self.service.top_hbo()
        self._return_list_movies(bot, update, movies)

    def top_dvd(self, bot, update):
        self._save_stats(bot, update)
        movies = self.service.top_dvd()
        self._return_list_movies(bot, update, movies)

    def top_tv_series(self, bot, update):
        self._save_stats(bot, update)
        movies = self.service.top_tv_series()
        self._return_list_movies(bot, update, movies)

    def recommend_netflix(self, bot, update):
        self._save_stats(bot, update)
        movie = self.service.recommend_netflix()
        self._return_movie(bot, update, movie)

    def recommend_hbo(self, bot, update):
        self._save_stats(bot, update)
        movie = self.service.recommend_hbo()
        self._return_movie(bot, update, movie)

    def premieres(self, bot, update):
        self._save_stats(bot, update)
        movies = self.service.top_premieres()
        self._return_list_movies(bot, update, movies)

    def inlinequery(self, bot, update):
        query = update.inline_query.query
        results = list()
        movies = self.service.search(title=query)
        for movie in movies:
            poster = self._get_poster_url(movie)
            url = self.service.url_film + str(movie['id']) + '.html'
            title = '%s - (%s)' % (movie['title'], movie['rating'])
            output = '%s - (%s) Show more: %s' % (movie['title'], movie['rating'], url)
            results.append(InlineQueryResultArticle(id=movie['id'],
                                                    title=title,
                                                    url=url,
                                                    hide_url=True,
                                                    thumb_url=poster,
                                                    input_message_content=InputTextMessageContent(output)
                                                    ))

        update.inline_query.answer(results)

    def error(self, bot, update, error):
        logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    TOKEN = os.environ.get('TOKEN')
    PORT = int(os.environ.get('PORT', '5000'))
    # Create the Updater and pass it your bot's token.

    updater = Updater(TOKEN)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://filmaffinitybot.herokuapp.com/" + TOKEN)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    filmaffinity = FilmaffinityBot()
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", filmaffinity.start))
    dp.add_handler(CommandHandler("help", filmaffinity.help))
    dp.add_handler(CommandHandler("top_filmaffinity", filmaffinity.top_filmaffinity))
    dp.add_handler(CommandHandler("top_netflix", filmaffinity.top_netflix))
    dp.add_handler(CommandHandler("top_hbo", filmaffinity.top_hbo))
    dp.add_handler(CommandHandler("top_dvd", filmaffinity.top_dvd))
    dp.add_handler(CommandHandler("top_tv_series", filmaffinity.top_tv_series))
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
