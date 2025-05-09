from flask import request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    TextSendMessage, FlexSendMessage, QuickReply,
    QuickReplyButton, MessageAction
)
from config.env import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID
from services.flex_builder import create_flavor_selection, create_quantity_selection, build_order_summary_flex
import requests

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Store user order state
user_orders = {}

FLAVORS = ["花生", "紅豆", "棗泥", "芋泥", "芝麻", "咖哩"]
QUANTITIES = ["6", "12", "20"]
PICKUP_OPTIONS = ["自取", "外送"]
DELIVERY_FEE = 30

def handle_order_flow(event):
    user_id = event.source.user_id
    print(f"[DEBUG] 訂單流程 user_id={user_id} 收到訊息: {event.message.text}")
    # Initialize user order state if not exists
    if user_id not in user_orders:
        user_orders[user_id] = {
            "step": 1,
            "flavor": None,
            "quantity": None,
            "pickup": None,
            "address": None,
            "remark": "",
            "customer_info": {}
        }
    current_state = user_orders[user_id]
    # Step 1: Select flavor
    if current_state["step"] == 1:
        if event.message.text in FLAVORS:
            current_state["flavor"] = event.message.text
            current_state["step"] = 2
            return send_quantity_selection(event.reply_token)
        else:
            return send_flavor_selection(event.reply_token)
    # Step 2: Select quantity
    elif current_state["step"] == 2:
        if event.message.text in QUANTITIES:
            current_state["quantity"] = event.message.text
            current_state["step"] = 3
            return send_pickup_option(event.reply_token)
        else:
            return send_quantity_selection(event.reply_token)
    # Step 3: Select pickup option
    elif current_state["step"] == 3:
        if event.message.text.strip() == "自取":
            current_state["pickup"] = "自取"
            current_state["address"] = ""
            current_state["step"] = 4
            return send_confirm_order(event.reply_token, current_state)
        elif event.message.text.strip() == "外送":
            current_state["pickup"] = "外送"
            current_state["step"] = 31
            return send_address_request(event.reply_token)
        else:
            return send_pickup_option(event.reply_token)
    # Step 3.1: 輸入外送地址
    elif current_state["step"] == 31:
        current_state["address"] = event.message.text.strip()
        current_state["step"] = 4
        return send_confirm_order(event.reply_token, current_state)
    # Step 4: 確認訂單
    elif current_state["step"] == 4:
        if event.message.text.strip() == "確定":
            # 組訂單摘要
            qty = int(current_state["quantity"])
            price = qty * 10
            remark = current_state["remark"]
            if current_state["pickup"] == "外送":
                price += DELIVERY_FEE
                remark += f"（外送加收{DELIVERY_FEE}元）"
            summary = f"口味：{current_state['flavor']}\n數量：{qty} 顆\n取貨方式：{current_state['pickup']}\n地址：{current_state['address']}\n備註：{remark}\n總金額：{price}元"
            # LINE 回覆
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="訂單已送出！感謝您的訂購～"))
            # Telegram 推播
            send_telegram_order_notification(summary)
            # 清除狀態
            del user_orders[user_id]
            return jsonify({"status": "success"})
        else:
            return send_confirm_order(event.reply_token, current_state)

def send_flavor_selection(reply_token):
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label=flavor, text=flavor))
        for flavor in FLAVORS
    ]
    message = TextSendMessage(
        text="請問想品嚐哪一款麻糬呢？每一種都是次妹用心手作，歡迎選擇：",
        quick_reply=QuickReply(items=quick_reply_items)
    )
    line_bot_api.reply_message(reply_token, message)
    return jsonify({"status": "success"})

def send_quantity_selection(reply_token):
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label=f"{q}個", text=q))
        for q in QUANTITIES
    ]
    message = TextSendMessage(
        text="請選擇數量：",
        quick_reply=QuickReply(items=quick_reply_items)
    )
    line_bot_api.reply_message(reply_token, message)
    return jsonify({"status": "success"})

def send_pickup_option(reply_token):
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label=opt, text=opt))
        for opt in PICKUP_OPTIONS
    ]
    message = TextSendMessage(
        text="請選擇取貨方式：",
        quick_reply=QuickReply(items=quick_reply_items)
    )
    line_bot_api.reply_message(reply_token, message)
    return jsonify({"status": "success"})

def send_address_request(reply_token):
    message = TextSendMessage(
        text="請輸入外送地址："
    )
    line_bot_api.reply_message(reply_token, message)
    return jsonify({"status": "success"})

def send_confirm_order(reply_token, state):
    summary = f"口味：{state['flavor']}\n數量：{state['quantity']} 顆\n取貨方式：{state['pickup']}\n地址：{state['address']}\n請確認訂單內容，若正確請點選『確定』。"
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label="確定", text="確定"))
    ]
    message = TextSendMessage(
        text=summary,
        quick_reply=QuickReply(items=quick_reply_items)
    )
    line_bot_api.reply_message(reply_token, message)
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