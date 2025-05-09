import random
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction

# 遊戲題庫
GAME_QUESTIONS = [
    {"question": "哪一種麻糬裡面有紅豆餡？", "answer": "紅豆"},
    {"question": "哪一種麻糬最適合冬天吃？", "answer": "花生"},
    {"question": "哪一種麻糬有紫色外皮？", "answer": "紫米"},
    {"question": "哪一種麻糬有濃郁芝麻香？", "answer": "芝麻"},
    {"question": "哪一種麻糬有芋頭餡？", "answer": "芋頭"}
]

# 遊戲狀態暫存（可用 redis 或 DB 儲存，這裡用記憶體）
user_game_state = {}

# 啟動遊戲
def start_game(event, line_bot_api):
    user_id = event.source.user_id
    q = random.choice(GAME_QUESTIONS)
    user_game_state[user_id] = q
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label=opt, text=opt))
        for opt in ["紅豆", "花生", "芝麻", "芋頭", "紫米"]
    ]
    msg = TextSendMessage(
        text=f"小遊戲開始！\n{q['question']}",
        quick_reply=QuickReply(items=quick_reply_items)
    )
    line_bot_api.reply_message(event.reply_token, msg)

# 處理遊戲回答
def handle_game_answer(event, line_bot_api):
    user_id = event.source.user_id
    if user_id not in user_game_state:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請先輸入『玩遊戲』開始麻糬小遊戲喔！")
        )
        return
    answer = event.message.text.strip()
    correct = user_game_state[user_id]['answer']
    if answer == correct:
        reply = random.choice([
            "啊，答對了，你一定是達人要不就是...吃貨，再來3顆，😁",
            "太厲害了！你果然是麻糬界的神人！🥳",
            "答對啦！你是不是常常偷吃麻糬？😏"
        ])
        del user_game_state[user_id]
    else:
        reply = random.choice([
            f"可惜不是喔～再想想看！提示：答案是{correct[0]}開頭的喔！",
            "還差一點點，再猜猜看吧！",
            "答錯了沒關係，次妹陪你一起玩！"
        ])
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply)) 