from telegram.ext import Updater
from upbitpy import Upbitpy
import time
import datetime
import logging
import os

INTERVAL_MIN_TIME = 5

MY_MARKETS = [os.environ["MY_MARKETS"]]
CHAT_ID = os.environ["CHAT_ID"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

def wait(min) :
    now = datetime.datetime.now()
    remain_second = 60 - now.second
    remain_second += 60 * (min - (now.minute % min + 1))
    time.sleep(remain_second)

def main() :
    upbit = Upbitpy()
    updater = Updater(TELEGRAM_BOT_TOKEN)

    print(MY_MARKETS)

    while True :
        ticker = upbit.get_ticker(MY_MARKETS)

        sendMessage = '({}) \n'.format(datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
        
        for market_list in ticker :
            market_name = market_list['market']

            if market_list['market'].startswith('KRW') :
                trade_price = format(float(market_list['trade_price']), ',.2f')
                closing_price = format(float(market_list['prev_closing_price']), ',.2f')
            elif market_list['market'].startswith('BTC') :
                trade_price = format(float(market_list['trade_price']), ',.8f') + ' BTC'
                closing_price = format(float(market_list['prev_closing_price']), ',.8f') + ' BTC'
            else :
                pass

            change_rate = format(float(market_list['signed_change_rate']) * 100, '.2f') + '%'
            
            sendMessage += '[{}] {} ({} /{})\n'.format(
                market_name, trade_price, closing_price, change_rate
            )

        #print(sendMessage)
        updater.bot.send_message(chat_id = CHAT_ID, text = sendMessage)

        wait(INTERVAL_MIN_TIME)


if __name__ == '__main__' :
    logging.basicConfig(level=logging.INFO)
    main()
