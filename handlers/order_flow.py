from flask import request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    TextSendMessage, FlexSendMessage, QuickReply,
    QuickReplyButton, MessageAction
)
from config.env import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from services.flex_builder import create_flavor_selection, create_quantity_selection, build_order_summary_flex

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Store user order state
user_orders = {}

FLAVORS = ["花生", "紅豆", "棗泥", "芋泥", "芝麻", "咖哩"]
QUANTITIES = ["6", "12", "20"]

def handle_order_flow(event):
    user_id = event.source.user_id
    
    # Initialize user order state if not exists
    if user_id not in user_orders:
        user_orders[user_id] = {
            "step": 1,
            "flavor": None,
            "quantity": None,
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
            return send_customer_info_request(event.reply_token)
        else:
            return send_quantity_selection(event.reply_token)
    
    # Step 3: Collect customer info
    elif current_state["step"] == 3:
        # Parse customer info (assuming format: "Name|Address|Phone")
        try:
            name, address, phone = event.message.text.split("|")
            current_state["customer_info"] = {
                "name": name.strip(),
                "address": address.strip(),
                "phone": phone.strip()
            }
            
            # Create order summary
            summary = build_order_summary_flex({
                "flavor": current_state["flavor"],
                "quantity": current_state["quantity"],
                "name": current_state["customer_info"].get("name", ""),
                "phone": current_state["customer_info"].get("phone", ""),
                "address": current_state["customer_info"].get("address", "")
            })
            
            # Send order summary
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="Order Summary", contents=summary["contents"])
            )
            
            # Clear user state
            del user_orders[user_id]
            
            return jsonify({"status": "success"})
            
        except ValueError:
            return send_customer_info_request(event.reply_token)

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

def send_customer_info_request(reply_token):
    message = TextSendMessage(
        text="請提供您的訂購資訊，格式如下：\n姓名|地址|電話\n例如：王小明|台北市信義區信義路五段7號|0912345678"
    )
    
    line_bot_api.reply_message(reply_token, message)
    return jsonify({"status": "success"}) 