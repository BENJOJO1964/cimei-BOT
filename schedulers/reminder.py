import schedule
import time
from datetime import datetime
from lunarcalendar import Converter, Solar, Lunar
from linebot import LineBotApi
from linebot.models import TextSendMessage
from config.env import LINE_CHANNEL_ACCESS_TOKEN

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 拜拜提醒訊息
REMINDER_MESSAGES = [
    "今天是初一，別忘了帶上麻糬一起祈福，祝你心想事成！",
    "農曆十五拜拜日，次妹提醒你準備好麻糬了嗎？祝福平安順心！",
    "今天適合拜拜，麻糬和祝福都不能少喔！",
    "初一十五拜拜，麻糬是最好的心意，祝你闔家平安！"
]

# 判斷今天是否為農曆初一或十五
def is_lunar_1st_or_15th():
    today = datetime.now()
    solar = Solar(today.year, today.month, today.day)
    lunar = Converter.Solar2Lunar(solar)
    return lunar.day in [1, 15]

# 推播提醒訊息（需有 user_id 列表）
def push_reminder(user_ids):
    import random
    msg = random.choice(REMINDER_MESSAGES)
    for uid in user_ids:
        line_bot_api.push_message(uid, TextSendMessage(text=msg))

# 排程任務
def schedule_reminder(user_ids):
    def job():
        if is_lunar_1st_or_15th():
            push_reminder(user_ids)
    schedule.every().day.at("09:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60) 