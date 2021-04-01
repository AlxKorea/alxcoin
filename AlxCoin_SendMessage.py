from telegram.ext import Updater
import logging
import datetime
import base64, hashlib, hmac, json, requests, time, os


API_KEY = os.environ["GOPAX_API_KEY"]
SECRET = os.environ["GOPAX_SECRET"]
MY_ASSET = os.environ["GOPAX_MY_ASSET"]
MyAsset = '/trading-pairs/'+ MY_ASSET + '/ticker'
CHAT_ID = os.environ["CHAT_ID"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
MY_CHECK_ALERT = os.environ["MY_CHECK_ALERT"]

INTERVAL_MIN_TIME = 1


def wait(min) :
    now = datetime.datetime.now()
    remain_second = 60 - now.second
    remain_second += 60 * (min - (now.minute % min + 1))
    time.sleep(remain_second)

def call(need_auth, method, path, body_json=None, recv_window=None) :
    method = method.upper()
    if need_auth :
        timestamp = str(int(time.time() * 1000))
        include_querystring = method == 'GET' and path.startswith('/orders?')
        p = path if include_querystring else path.split('?')[0]
        msg = 't' + timestamp + method + p
        msg += (str(recv_window) if recv_window else '') + (json.dumps(body_json) if body_json else '')
        raw_secret = base64.b64decode(SECRET)
        raw_signature = hmac.new(raw_secret, str(msg).encode('utf-8'), hashlib.sha512).digest()
        signature = base64.b64encode(raw_signature)
        headers = {'api-key' : API_KEY, 'timestamp' : timestamp, 'signature' : signature}

        if recv_window :
            headers['receive-window'] = str(recv_window)

    else :
        headers = {}

    req_func = {
        'GET' : requests.get,
        'POST' : requests.post,
        'DELETE' : requests.delete
    }[method]
    
    resp = req_func(
        url = 'https://api.gopax.co.kr' + path,
        headers = headers,
        json = body_json
    )
    return {
        'statusCode': resp.status_code,
        'body': resp.json(),
        'header': dict(resp.headers),
    }



def main() :

    updater = Updater(TELEGRAM_BOT_TOKEN)
    check_alert_use = True
    regular_interval = 0

    def send_message_func() :
        sendMessage = '({}) '.format(datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
        sendMessage += '{} 현재가 [ {} ] \n + 매도호가 : {}/ {}/ {} \n + 매수호가 : {}/ {}/ {}\n + 24시간거래량 : {} KRW'.format(
            MY_ASSET, receiveTickerBody['price'],
            receiveTickerBody['ask'], receiveTickerBody['askVolume'], format(float(receiveTickerBody['ask'] * receiveTickerBody['askVolume']), ',.2f'),
            receiveTickerBody['bid'], receiveTickerBody['bidVolume'], format(float(receiveTickerBody['bid'] * receiveTickerBody['bidVolume']), ',.2f'),
            format(float(receiveTickerBody['quoteVolume']), ',.2f'),
        )

        #print(sendMessage)
        updater.bot.send_message(chat_id = CHAT_ID, text = sendMessage)

    while True :
        receiveTicker = call(True, 'GET', MyAsset)
        receiveTickerBody = receiveTicker['body']
        #print(receiveTickerBody)

        if receiveTickerBody['price'] > float(MY_CHECK_ALERT) and check_alert_use :
            send_message_func()
            check_alert_use = False

        if receiveTickerBody['price'] < float(MY_CHECK_ALERT) and not check_alert_use :
            check_alert_use = True

        if regular_interval >= 60 :
            send_message_func()
            regular_interval = 0

        regular_interval += 1
        wait(INTERVAL_MIN_TIME)


if __name__ == '__main__' :
    logging.basicConfig(level=logging.INFO)
    main()