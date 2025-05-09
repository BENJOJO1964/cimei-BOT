import os
import random
import openai
from config.env import OPENAI_API_KEY

print("[DEBUG] Render 啟動時讀到的 OPENAI_API_KEY =", repr(OPENAI_API_KEY))

# 多樣化知性溫柔回應
CHAT_RESPONSES = [
    "嗨，我是次妹～有什麼想聊的嗎？不管是麻糬還是生活都可以問我喔！",
    "你知道嗎？麻糬的Q彈口感，其實跟天氣也有點關係呢～想聽更多嗎？",
    "有時候心情不好，吃顆麻糬就會變好一點呢。你今天還好嗎？",
    "除了麻糬，我也喜歡和你聊聊生活小事，歡迎隨時找我喔！",
    "如果你想知道麻糬的故事、吃法或保存方法，都可以問我唷！"
]

def optimize_prompt(user_message):
    # 根據常見需求自動優化 prompt
    prompt = user_message
    if any(kw in user_message for kw in ["三句話", "三句內", "三句以內", "三句話介紹", "簡短", "精簡", "一句話"]):
        prompt = f"請用簡短、重點式的方式回答：{user_message}"
    return prompt

def chat_with_user(user_message):
    if not OPENAI_API_KEY:
        return random.choice(CHAT_RESPONSES)
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    print(f"[DEBUG] OPENAI_API_KEY={repr(OPENAI_API_KEY)}")
    try:
        system_prompt = "你是次妹手工麻糬BOT，品牌形象知性溫柔，善於用溫暖、療癒、生活化的語氣陪伴用戶聊天，並適時分享麻糬、天氣、生活小知識。請用繁體中文回答。"
        model_name = "gpt-3.5-turbo"
        print(f"[DEBUG] 使用的模型：{model_name}")
        # 自動優化 prompt
        optimized_user_message = optimize_prompt(user_message)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": optimized_user_message}
            ],
            max_tokens=60,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[OpenAI API Error] {str(e)}")
        return random.choice(CHAT_RESPONSES) 