import random

# 多樣化知性溫柔回應
CHAT_RESPONSES = [
    "嗨，我是次妹～有什麼想聊的嗎？不管是麻糬還是生活都可以問我喔！",
    "你知道嗎？麻糬的Q彈口感，其實跟天氣也有點關係呢～想聽更多嗎？",
    "有時候心情不好，吃顆麻糬就會變好一點呢。你今天還好嗎？",
    "除了麻糬，我也喜歡和你聊聊生活小事，歡迎隨時找我喔！",
    "如果你想知道麻糬的故事、吃法或保存方法，都可以問我唷！"
]

def chat_with_user(user_message):
    # 未來可串 GPT，這裡先用隨機回應
    return random.choice(CHAT_RESPONSES) 