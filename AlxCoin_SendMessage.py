from telegram.ext import Updater
from upbitpy import Upbitpy
import time
import datetime
import logging
import os

INTERVAL_MIN_TIME = 60
CHAT_ID = os.environ["chat_id"]
TELEGRAM_BOT_TOKEN = os.environ["telegram_bot_tokrn"]

def wait(min) :
    now = datetime.datetime.now()
    remain_second = 60 - now.second
    remain_second += 60 * (min - (now.minute % min + 1))
    time.sleep(remain_second)

def main() :
    upbit = Upbitpy()
    updater = Updater(TELEGRAM_BOT_TOKEN)

    while True :
        krw_btc_ticker = upbit.get_ticker(['KRW-BTC'])[0]
        krw_eth_ticker = upbit.get_ticker(['KRW-ETH'])[0]
        krw_btc_price_str = format(int(krw_btc_ticker['trade_price']), ',')
        krw_eth_price_str = format(int(krw_eth_ticker['trade_price']), ',')
        text = '({})\n'.format(datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
        text += '+ 비트코인 : {} 원\n'.format(krw_btc_price_str)
        text += '+ 이더리움 : {} 원'.format(krw_eth_price_str)
        updater.bot.send_message(chat_id = CHAT_ID, text = text)
        wait(INTERVAL_MIN_TIME)


if __name__ == '__main__' :
    logging.basicConfig(level=logging.INFO)
    main()
