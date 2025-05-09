from flask import jsonify
from linebot.models import TextSendMessage
from config.env import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID
import requests

DELIVERY_FEE = 30

# 最簡單表格訂單流程

def handle_order_flow(event):
    user_message = event.message.text.strip()
    print(f"[DEBUG] 訂單流程收到訊息: {user_message}")
    parts = user_message.split("|")
    if len(parts) >= 3:
        flavor = parts[0].strip()
        quantity = parts[1].strip()
        pickup = parts[2].strip()
        address = parts[3].strip() if len(parts) > 3 else ""
        try:
            qty = int(quantity)
            price = qty * 10
            remark = ""
            if pickup in ["外送", "派送"]:
                price += DELIVERY_FEE
                remark += f"（外送加收{DELIVERY_FEE}元）"
            summary = f"口味：{flavor}\n數量：{qty} 顆\n取貨方式：{pickup}\n地址：{address}\n備註：{remark}\n總金額：{price}元"
            event.reply_token and event.reply_token
            from linebot import LineBotApi
            from config.env import LINE_CHANNEL_ACCESS_TOKEN
            line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="訂單已送出！感謝您的訂購～"))
            send_telegram_order_notification(summary)
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"[DEBUG] 訂單格式錯誤: {e}")
            return send_order_form(event.reply_token)
    else:
        return send_order_form(event.reply_token)

def send_order_form(reply_token):
    form_text = (
        "請填選下列訊息後按(確定)：\n"
        "格式：口味|數量|自取/派送|地址（自取可省略地址）\n"
        "範例：花生|12|自取\n"
        "或：芝麻|6|派送|台北市信義區信義路五段7號\n"
        "可選口味：花生、紅豆、棗泥、芋泥、芝麻、咖哩"
    )
    from linebot import LineBotApi
    from config.env import LINE_CHANNEL_ACCESS_TOKEN
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=form_text))
    return jsonify({"status": "success"})

def send_telegram_order_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID,
        "text": f"【新訂單通知】\n{message}"
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"[Telegram Error] {e}") 