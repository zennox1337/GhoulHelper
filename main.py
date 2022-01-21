import asyncio
import datetime
import time
import requests
import urllib3
from TikTokAPI import TikTokAPI
import re
import os
import telebot
import sys


def start(link, chat_id):
    if len(link) > 10:
        print('Получена ссылка: ' + link + " | " + str(datetime.datetime.now()).split('.')[0])
        http = urllib3.PoolManager(10)
        r1 = http.urlopen('GET', link)
        html = str(r1.data)
        P = re.compile("\"id\":\"(\\d+)\"")
        videoId = P.findall(html)
        api = TikTokAPI()
        filename = str(chat_id).replace('-', '') + '_' + videoId[0] + ".mp4"
        api.downloadVideoById(videoId[0], filename)
        return filename
    else:
        return 1


def deleteVideo(videoPath):
    os.remove(os.path.join(os.path.abspath(os.curdir), videoPath))


def sendVideo(bot, m, link):
    filename = start(link, m.chat.id)
    video = open(filename, 'rb')
    bot.send_video(m.chat.id, video, reply_to_message_id=m.message_id)
    video.close()
    deleteVideo(filename)


def checkTikTokUrl(bot, m):
    message_text = str(m.text).strip()
    regxp = re.compile(
        "(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?")
    link = regxp.findall(message_text)
    if len(link) > 0:
        if 'tiktok' in str(link[0]).lower():
            sendVideo(bot, m, str(link[0]))


if __name__ == '__main__':

    username_ping = []

    bot = telebot.TeleBot('TOKEN')
    bot = telebot.TeleBot(sys.argv[1])


    @bot.message_handler(commands=['all'])
    def ping(m):
        if not os.path.exists(str(m.chat.id).strip().replace('-', '') + '.txt'):
            f = open(str(m.chat.id).strip().replace('-', '') + '.txt', 'w')
            f.writelines(m.from_user.username)
            bot.reply_to(m, 'Добавлены в список')
            f.close()
        else:
            f = open(str(m.chat.id).strip().replace('-', '') + '.txt', 'r')
            if m.from_user.username in f.read():
                msg = ''
                f.seek(0)
                for line in f.read().splitlines():
                    msg = msg + ' @' + line
                bot.send_message(m.chat.id, msg)
            else:
                f.close()
                f = open(str(m.chat.id).strip().replace('-', '') + '.txt', 'a+')
                f.writelines(m.from_user.username + '\n')
                f.close()
                bot.reply_to(m, 'Добавлены в список')


    @bot.message_handler(content_types=['text'])
    def send_text(m):
        asyncio.set_event_loop(asyncio.new_event_loop())
        checkTikTokUrl(bot, m)


    while True:
        try:
            bot.polling(none_stop=True, interval=0)

        except Exception as e:
            print(e)
            time.sleep(15)
