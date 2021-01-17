from telegram.ext import Updater
from upbitpy import Upbitpy
import time
import datetime
import logging
import os

INTERVAL_MIN_TIME = 1
CHECK_VOLUMN_RATIO = 150.0
CHECK_CHANGE_PRICE_RATIO = 2.0

CHAT_ID = os.environ["CHAT_ID"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

def wait(min) :
    now = datetime.datetime.now()
    remain_second = 60 - now.second
    remain_second += 60 * (min - (now.minute % min + 1))
    time.sleep(remain_second)


def check_remaining_candles_req(upbit) :
    ret = upbit.get_remaining_req()
    if ret is None:
        return
    if 'candles' not in ret.keys():
        return
    if int(ret['candles']['sec']) == 0:
        time.sleep(1)

def main() :
    upbit = Upbitpy()
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # 전체 원화 마켓 조회
    all_market = upbit.get_market_all()
    krw_markets = []
    for i in all_market :
        if i['market'].startswith('KRW') :
            krw_markets.append(i['market'])

    candles_7d = dict()

    # week 거래량
    for i in krw_markets :
        candles_7d[i] = upbit.get_weeks_candles(i, count=1)[0]
        check_remaining_candles_req(upbit)

    while True :
        for i in krw_markets :
            candleData = upbit.get_minutes_candles(1, i, count=1)[0]

            vol = candleData['candle_acc_trade_volume']
            vol_7d = candles_7d[i]['candle_acc_trade_volume']
            vol_7d_avg = (((vol_7d / 7.0)/ 24.0)/ 60.0) * INTERVAL_MIN_TIME
            vol_ratio = format( (vol/vol_7d_avg) * 100.0, '.2f')

            pri = candleData['candle_acc_trade_price']
            pri_7d = candles_7d[i]['candle_acc_trade_price']
            pri_7d_avg = (((pri_7d / 7.0)/ 24.0)/ 60.0) * INTERVAL_MIN_TIME
            pri_ratio = format( (pri/pri_7d_avg) * 100.0, '.2f')

            opening_price = candleData['opening_price']
            trade_price = candleData['trade_price']
            change_price = opening_price - trade_price
            if float(change_price) > 0.00 :
                change_price_ratio = format( (change_price / opening_price) * 100.0, '.2f')

            if float(vol_ratio) >= float(CHECK_VOLUMN_RATIO) and float(change_price_ratio) >= float(CHECK_CHANGE_PRICE_RATIO) :
                text = '({})\n'.format(datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
                text += '[{}] {}% \n -거래량: {}/ 평균: {}/ 비율: {}\n -거래대금: {}/ 평균: {}\n -시가: {}/ 종가: {}/ 변동액: {}\n'.format(
                    i, change_price_ratio,
                    format(vol, '.2f'), format(vol_7d_avg, '.2f'), vol_ratio,
                    format(int(pri), ','), format(int(pri_7d_avg), ','),
                    format(opening_price, ',.2f'), format(trade_price, ',.2f'), format(change_price, ',.2f')
                )
            check_remaining_candles_req(upbit)

        updater.bot.send_message(chat_id = CHAT_ID, text = text)
        wait(INTERVAL_MIN_TIME)


if __name__ == '__main__' :
    logging.basicConfig(level=logging.INFO)
    main()
