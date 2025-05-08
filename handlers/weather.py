import requests
import os
from config.env import WEATHER_API_KEY

# 可根據天氣狀況推薦不同口味
WEATHER_TO_FLAVOR = {
    'sunny': ['紅豆', '花生'],
    'clear': ['紅豆', '花生'],
    'rain': ['芝麻', '紫米'],
    'cloud': ['花生', '紅豆'],
    'overcast': ['芋頭', '紫米'],
    'snow': ['芝麻', '紫米'],
    'other': ['任選都適合']
}

# 多樣化推薦語
RECOMMEND_TEMPLATES = [
    "{city}今天天氣{weather}，很適合來份{flavor}麻糬，讓心情更美好！",
    "{city}現在是{weather}，推薦你試試{flavor}口味的麻糬，Q彈又療癒～",
    "天氣{weather}，{city}的你不妨來點{flavor}麻糬，幸福感up！"
]

# 取得天氣資料（簡化版，僅示範台北市）
def get_weather(city="Taipei"):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=zh_tw"
    try:
        res = requests.get(url)
        data = res.json()
        weather = data['current']['condition']['text']
        code = data['current']['condition']['code']
        # 英文關鍵字分類
        lower_text = data['current']['condition']['text'].lower()
        if '晴' in weather or 'sunny' in lower_text or 'clear' in lower_text:
            key = 'sunny'
        elif '雨' in weather or 'rain' in lower_text:
            key = 'rain'
        elif '雲' in weather or 'cloud' in lower_text:
            key = 'cloud'
        elif '陰' in weather or 'overcast' in lower_text:
            key = 'overcast'
        elif '雪' in weather or 'snow' in lower_text:
            key = 'snow'
        else:
            key = 'other'
        return weather, key
    except Exception as e:
        print(f"[WeatherAPI Error] {str(e)}")
        return None, None

def recommend_flavor_by_weather(weather_key):
    return WEATHER_TO_FLAVOR.get(weather_key, WEATHER_TO_FLAVOR['other'])[0]

import random
def get_weather_and_recommend(city="Taipei"):
    weather, key = get_weather(city)
    if not weather:
        return f"抱歉，次妹暫時查不到{city}的天氣資訊喔！"
    flavor = recommend_flavor_by_weather(key)
    template = random.choice(RECOMMEND_TEMPLATES)
    return template.format(city=city, weather=weather, flavor=flavor) 