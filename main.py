from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage, FollowEvent
import os

from config.env import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from handlers.order_flow import handle_order_flow
from handlers.weather import get_weather_and_recommend
from handlers.gpt_chat import chat_with_user

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

print("[DEBUG] Render 啟動時讀到的 OPENAI_API_KEY (main.py) =", repr(os.getenv("OPENAI_API_KEY")))

@app.route("/", methods=['GET'])
def home():
    return "Line Bot Server is running!"

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

@handler.add(FollowEvent)
def handle_follow(event):
    print('[DEBUG] FollowEvent 觸發，發送歡迎詞')
    welcome_text = (
        "🎉 歡迎加入次妹手工麻糬BOT！\n"
        "我是次妹，Q彈的麻糬就像生活裡的小確幸～\n"
        "輸入『買麻糬』開始訂購，或輸入『天氣』『陪我聊聊』體驗更多有趣功能！\n"
        "品牌故事、保存方式、營業時間都可以問我唷！"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_text))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    print(f"[DEBUG] 收到訊息: {user_message}")
    # FAQ/品牌故事快取（可擴充）
    FAQ_ANSWERS = {
        "品牌故事": "次妹手工麻糬創立於2020年，堅持手作、天然、無添加，陪伴你每一個溫暖時刻。",
        "麻糬保存": "麻糬建議冷藏保存2天內食用完畢，口感最佳。",
        "營業時間": "每日10:00-18:00，歡迎來店選購！",
        "常見問題": "歡迎詢問：品牌故事、麻糬保存、營業時間、訂購方式等。"
    }
    # handlers/gpt_chat.py 的預設聊天內容
    CHAT_RESPONSES = [
        "嗨，我是次妹～有什麼想聊的嗎？不管是麻糬還是生活都可以問我喔！",
        "你知道嗎？麻糬的Q彈口感，其實跟天氣也有點關係呢～想聽更多嗎？",
        "有時候心情不好，吃顆麻糬就會變好一點呢。你今天還好嗎？",
        "除了麻糬，我也喜歡和你聊聊生活小事，歡迎隨時找我喔！",
        "如果你想知道麻糬的故事、吃法或保存方法，都可以問我唷！"
    ]
    # 訂購流程（只在明確訂單關鍵字時觸發）
    if user_message in ["我要買麻糬", "買麻糬", "訂購麻糬"]:
        print("[DEBUG] 進入訂單流程（表格填寫）")
        handle_order_flow(event)
        return
    # 天氣查詢
    elif any(key in user_message for key in ["天氣", "天氣推薦"]):
        city = "臺北市"
        for c in ["台北", "新北", "台中", "高雄", "台南", "桃園", "新竹", "基隆", "嘉義", "彰化", "屏東", "宜蘭", "花蓮", "台東", "苗栗", "雲林", "南投"]:
            if c in user_message:
                city = c.replace("台", "臺") + "市"
        reply = get_weather_and_recommend(city)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    # FAQ/品牌故事自動回覆
    elif user_message in FAQ_ANSWERS:
        reply = FAQ_ANSWERS[user_message]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    # 預設聊天內容（本地回覆，不送 GPT）
    elif user_message in CHAT_RESPONSES:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=user_message))
        return
    # 陪聊模式（只有這裡才送 GPT）
    elif user_message in ["陪我聊聊", "聊天", "聊聊"] or len(user_message) > 2:
        reply = chat_with_user(user_message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    else:
        # 預設回應
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="您好！我是次妹，想買麻糬嗎？輸入『買麻糬』開始訂購流程，或輸入『天氣』『陪我聊聊』體驗更多功能！")
        )
        return

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001) 