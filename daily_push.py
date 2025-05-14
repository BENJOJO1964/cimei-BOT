import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 讀取環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")
GCP_KEY_PATH = os.getenv("GCP_KEY_PATH", "gcp_key.json")

# Google Sheets API 驗證
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]
creds = ServiceAccountCredentials.from_json_keyfile_name(GCP_KEY_PATH, scope)
client = gspread.authorize(creds)

# 取得今天日期（台灣時區）
tz_delta = timedelta(hours=8)
today = (datetime.utcnow() + tz_delta).strftime('%Y/%m/%d')

# 讀取 Google Sheet
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
rows = sheet.get_all_records()

# 查找今日地點
location_name = address = None
for row in rows:
    if str(row.get('Date')).strip() == today:
        location_name = row.get('Location Name')
        address = row.get('Address')
        break

if location_name and address:
    maps_link = f"https://www.google.com/maps/search/?api=1&query={address}"
    msg = f"📢 今日（{today}）擺攤地點：\n🧋 {location_name}\n📍 地址：{address}\n🗺 地圖：{maps_link}"
else:
    msg = f"今日（{today}）暫無擺攤資訊，請稍後再查詢或聯絡店家。"

# 推播到 LINE 群組
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
if TARGET_GROUP_ID:
    line_bot_api.push_message(TARGET_GROUP_ID, TextSendMessage(text=msg))
else:
    print("[ERROR] TARGET_GROUP_ID not set.") 