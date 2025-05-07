from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage

from config.env import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from handlers.order_flow import handle_order_flow
from handlers.weather import get_weather_and_recommend
from handlers.game import start_game, handle_game_answer
from handlers.gpt_chat import chat_with_user

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/", methods=['GET'])
def home():
    return "Line Bot Server is running!"

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    # 訂購流程
    if user_message in ["我要買麻糬", "買麻糬", "訂購麻糬"]:
        handle_order_flow(event)
    # 天氣查詢
    elif any(key in user_message for key in ["天氣", "天氣推薦"]):
        city = "臺北市"
        for c in ["台北", "新北", "台中", "高雄", "台南", "桃園", "新竹", "基隆", "嘉義", "彰化", "屏東", "宜蘭", "花蓮", "台東", "苗栗", "雲林", "南投"]:
            if c in user_message:
                city = c.replace("台", "臺") + "市"
        reply = get_weather_and_recommend(city)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    # 小遊戲
    elif user_message in ["玩遊戲", "麻糬遊戲", "猜口味"]:
        start_game(event, line_bot_api)
    elif user_message in ["紅豆", "花生", "芝麻", "芋頭", "紫米"]:
        handle_game_answer(event, line_bot_api)
    # 陪聊模式
    elif user_message in ["陪我聊聊", "聊天", "聊聊"] or len(user_message) > 2:
        reply = chat_with_user(user_message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    else:
        # 預設回應
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="您好！我是次妹，想買麻糬嗎？輸入『我要買麻糬』開始訂購流程，或輸入『天氣』『玩遊戲』『陪我聊聊』體驗更多功能！")
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001) 