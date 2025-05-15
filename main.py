from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage, FollowEvent, JoinEvent, FlexSendMessage, MemberJoinedEvent
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json

from config.env import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
# from handlers.order_flow import handle_order_flow  # 已刪除，不再匯入
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
    # 只回覆明確問 BOT 的訊息
    trigger_keywords = ["@次妹", "BOT", "次妹", "請問", "？", "哪裡擺攤", "明天在哪擺攤", "今天在哪擺攤", "天氣", "遊戲", "陪我聊天", "陪我們聊天", "品牌故事", "保存", "買麻糬", "我要買麻糬", "我們要買麻糬", "到哪買麻糬", "麻糬口味"]
    # 只要有「麻糬」兩字也要回覆
    if not (any(k in user_message for k in trigger_keywords) or "麻糬" in user_message):
        return  # 不是問 BOT 的訊息就不回覆
    # Debug: 回傳群組ID（務必最優先判斷）
    if event.source.type == "group" and user_message.lower() == "gid":
        print("✅ 收到來自群組的訊息")
        print("✅ 群組 ID：", event.source.group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"本群組的 groupId 是：\n{event.source.group_id}")
        )
        return
    # 查詢明天擺攤地點
    if any(k in user_message for k in ["明天在哪擺攤", "明天在哪裡", "明天攤位"]):
        try:
            # Google Sheets API 驗證（用環境變數）
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive',
            ]
            gcp_key_json = os.getenv("GCP_KEY_JSON")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(gcp_key_json), scope)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1
            rows = sheet.get_all_records()
            # 取得明天日期（台灣時區）
            tz_delta = timedelta(hours=8)
            tomorrow = (datetime.utcnow() + tz_delta + timedelta(days=1)).strftime('%A').lower()
            weekday_map = {
                'monday': '星期一', 'tuesday': '星期二', 'wednesday': '星期三', 'thursday': '星期四', 'friday': '星期五', 'saturday': '星期六', 'sunday': '星期日'
            }
            tomorrow_zh = weekday_map.get(tomorrow, tomorrow)
            print(f"[DEBUG] 明天中文星期: {tomorrow_zh}")
            print(f"[DEBUG] 讀到的 rows: {rows}")
            found = False
            for row in rows:
                if tomorrow_zh in str(row.get('星期 weekdays')):
                    location = row.get('擺攤地點 location')
                    timing = row.get('時間 timing')
                    remark = row.get('備註 remark')
                    msg = f"明天（{tomorrow_zh}）擺攤地點：\n地點：{location}\n時間：{timing}"
                    if remark:
                        msg += f"\n備註：{remark}"
                    found = True
                    break
            if not found:
                msg = f"抱歉，明天（{tomorrow_zh}）暫無擺攤資訊，請稍後再查詢或聯絡店家。"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        except Exception as e:
            import traceback
            print(f"[ERROR] 查詢明天擺攤地點失敗: {e}")
            traceback.print_exc()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="抱歉，查詢明天擺攤地點時發生錯誤，請稍後再試！"))
        return
    # 買麻糬相關關鍵字統一回覆
    if any(k in user_message for k in ["買麻糬", "我要買麻糬", "訂購麻糬"]):
        reply = "嗨，感謝您對麻糬的喜愛，歡迎您到我們今天擺攤的位置購買，另外，我們正在建立外送系統喔🍡"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    FAQ_ANSWERS = {
        "品牌故事": "次妹手工麻糬創立於2020年，堅持手作、天然、無添加，陪伴你每一個溫暖時刻。",
        "麻糬保存": "麻糬建議冷藏保存2天內食用完畢，口感最佳。",
        "營業時間": "每日10:00-18:00，歡迎來店選購！",
        "常見問題": "歡迎詢問：品牌故事、麻糬保存、營業時間、訂購方式等。"
    }
    CHAT_RESPONSES = [
        "嗨，我是次妹～有什麼想聊的嗎？不管是麻糬還是生活都可以問我喔！",
        "你知道嗎？麻糬的Q彈口感，其實跟天氣也有點關係呢～想聽更多嗎？",
        "有時候心情不好，吃顆麻糬就會變好一點呢。你今天還好嗎？",
        "除了麻糬，我也喜歡和你聊聊生活小事，歡迎隨時找我喔！",
        "如果你想知道麻糬的故事、吃法或保存方法，都可以問我唷！"
    ]
    # 天氣查詢
    if any(key in user_message for key in ["天氣", "天氣推薦"]):
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
            TextSendMessage(text="您好！我是次妹，想買麻糬嗎？輸入『天氣』『陪我聊聊』體驗更多功能！")
        )
        return

@handler.default()
def default(event):
    print(f"[DEBUG] Unhandled event type: {type(event)} — raw: {event}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001) 