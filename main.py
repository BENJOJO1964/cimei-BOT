from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage, FollowEvent, JoinEvent, FlexSendMessage, MemberJoinedEvent
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json
import random

from config.env import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
# from handlers.order_flow import handle_order_flow  # 已刪除，不再匯入
from handlers.weather import get_weather_and_recommend
from handlers.gpt_chat import chat_with_user, analyze_intent_with_gpt

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
    print("[DEBUG] webhook body:", body)  # 印出原始 JSON
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    print('[INFO] FollowEvent triggered')
    welcome_text = (
        "🌿 Welcome to Cimei Handmade Mochi!  \n"
        "This mochi isn't machine-pressed — it's kneaded with time and care.  \n"
        "Type \"買麻糬\" to start your order 🍡"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_text))

@handler.add(JoinEvent)
def handle_join(event):
    print('[INFO] JoinEvent triggered')
    join_text = (
        "👋 Hi everyone, I'm 次妹手工麻糬 BOT!  \n"
        "Type \"買麻糬\" to place a mochi order in this group 🍡"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=join_text))

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    try:
        group_id = event.source.group_id
        user_id = event.joined.members[0].user_id
        profile = line_bot_api.get_group_member_profile(group_id, user_id)
        member_name = profile.display_name
        welcome_text = f"熱烈歡迎 {member_name} 加入《次妹手工麻糬群》🥳\n每天會公佈擺攤地點，也可以直接問「今天在哪擺攤？」，以後我們會建立預訂外送服務唷～📍"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_text))
    except Exception as e:
        print(f"[ERROR] MemberJoinedEvent: {e}")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    print(f"[DEBUG] 收到訊息: {user_message}")
    # FAQ/品牌故事自動回覆（本地判斷）
    FAQ_ANSWERS = {
        "品牌故事": "次妹手工麻糬創立於2020年，堅持手作、天然、無添加，陪伴你每一個溫暖時刻。",
        "麻糬保存": "麻糬建議冷藏保存2天內食用完畢，口感最佳。",
        "營業時間": "每日10:00-18:00，歡迎來店選購！",
        "常見問題": "歡迎詢問：品牌故事、麻糬保存、營業時間、訂購方式等。"
    }
    if user_message in FAQ_ANSWERS:
        reply = FAQ_ANSWERS[user_message]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    # 口味詢問（本地判斷）
    flavor_keywords = ["麻糬口味", "麻薯口味", "口味", "有什麼口味", "有哪些口味"]
    if any(k in user_message for k in flavor_keywords):
        reply = "我們有6種口味：花生、芝麻、芋泥、棗泥、紅豆、咖哩，歡迎選購！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    # 價格詢問（本地判斷）
    price_keywords = ["多少錢", "價格", "一顆多少", "一盒多少", "賣多少", "價錢"]
    if any(k in user_message for k in price_keywords):
        reply = "每顆10元，小盒6顆/60元，大盒12顆/120元。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    # emoji 列表
    EMOJIS = ["🍡", "🥳", "📍", "🧋", "😋", "✨", "🎉", "🍬", "🍀", "🫶"]
    # 其餘訊息交給 GPT 分析意圖
    from handlers.gpt_chat import analyze_intent_with_gpt
    intent_result = analyze_intent_with_gpt(user_message)
    print(f"[DEBUG] GPT 意圖分析結果: {intent_result}")
    reply_list = []
    # 擺攤地點查詢
    def find_stall_info_by_weekday(target_weekday, label=None):
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive',
            ]
            gcp_key_json = os.getenv("GCP_KEY_JSON")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(gcp_key_json), scope)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1
            rows = sheet.get_all_records()
            found = False
            for row in rows:
                if target_weekday in str(row.get('星期 weekdays')) and row.get('擺攤地點 location'):
                    location = row.get('擺攤地點 location')
                    timing = row.get('時間 timing')
                    remark = row.get('備註 remark')
                    msg = f"{label or target_weekday}擺攤地點：\n地點：{location}"
                    if timing:
                        msg += f"\n時間：{timing}"
                    if remark:
                        msg += f"\n備註：{remark}"
                    found = True
                    break
            if not found:
                msg = f"抱歉，{label or target_weekday}暫無擺攤資訊，請稍後再查詢或聯絡店家。"
            return msg
        except Exception as e:
            import traceback
            print(f"[ERROR] 查詢{target_weekday}擺攤地點失敗: {e}")
            traceback.print_exc()
            return f"抱歉，查詢{label or target_weekday}擺攤地點時發生錯誤，請稍後再試！"
    # 解析意圖並組合回覆
    for intent in intent_result.get("intents", []):
        if intent["type"] == "location":
            # 解析日期
            date = intent.get("date")
            if not date:
                tz_delta = timedelta(hours=8)
                today_dt = datetime.utcnow() + tz_delta
                weekday_map = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
                date = weekday_map[today_dt.weekday()]
            msg = find_stall_info_by_weekday(date, label=f"{date}")
            reply_list.append(msg)
        elif intent["type"] == "flavor":
            reply_list.append("我們有6種口味：花生、芝麻、芋泥、棗泥、紅豆、咖哩，歡迎選購！")
        elif intent["type"] == "price":
            reply_list.append("每顆10元，小盒6顆/60元，大盒12顆/120元。")
        elif intent["type"] == "weather":
            from handlers.weather import get_weather, recommend_flavor_by_weather
            city = "臺北市"
            for c in ["台北", "新北", "台中", "高雄", "台南", "桃園", "新竹", "基隆", "嘉義", "彰化", "屏東", "宜蘭", "花蓮", "台東", "苗栗", "雲林", "南投"]:
                if c in user_message:
                    city = c.replace("台", "臺") + "市"
            weather, key, temp = get_weather(city)
            flavor = recommend_flavor_by_weather(key)
            reply = f"{city.replace('市', '')}今天天氣{weather}，很適合來份{flavor}麻糬，讓心情更美好！\n目前溫度：{temp}°C"
            reply_list.append(reply)
        elif intent["type"] == "chat":
            reply_list.append("嗨，我是次妹～有什麼想聊的嗎？不管是麻糬還是生活都可以問我喔！")
        elif intent["type"] in ["order", "buy"]:
            # 買麻糬/訂單意圖自動查詢今天擺攤地點，合併價格與口味
            tz_delta = timedelta(hours=8)
            today_dt = datetime.utcnow() + tz_delta
            weekday_map = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            date = intent.get("date") or weekday_map[today_dt.weekday()]
            msg = find_stall_info_by_weekday(date, label=f"{date}")
            reply = msg
            if "暫無擺攤資訊" not in msg:
                reply += "\n---\n我們有6種口味：花生、芝麻、芋泥、棗泥、紅豆、咖哩。\n每顆10元，小盒6顆/60元，大盒12顆/120元。\n如需訂購請現場洽詢或私訊我們！"
            reply_list.append(reply)
    # 若無法判斷意圖，給預設回覆
    if not reply_list:
        reply_list = ["您好！我是次妹，想買麻糬嗎？輸入『天氣』『陪我聊聊』體驗更多功能！"]
    # 合併所有回覆，最後加 emoji
    reply_text = "\n---\n".join(reply_list)
    reply_text += " " + random.choice(EMOJIS)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    return

@handler.default()
def default(event):
    print(f"[DEBUG] Unhandled event type: {type(event)} — raw: {event}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001) 