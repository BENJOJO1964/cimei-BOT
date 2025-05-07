import requests
import os
from config.env import WEATHER_API_KEY

# 可根據天氣狀況推薦不同口味
WEATHER_TO_FLAVOR = {
    '晴': ['紅豆', '花生'],
    '雨': ['芝麻', '紫米'],
    '陰': ['芋頭', '紫米'],
    '多雲': ['花生', '紅豆'],
    '其他': ['任選都適合']
}

# 多樣化推薦語
RECOMMEND_TEMPLATES = [
    "{city}今天天氣{weather}，很適合來份{flavor}麻糬，讓心情更美好！",
    "{city}現在是{weather}，推薦你試試{flavor}口味的麻糬，Q彈又療癒～",
    "天氣{weather}，{city}的你不妨來點{flavor}麻糬，幸福感up！"
]

# 取得天氣資料（簡化版，僅示範台北市）
def get_weather(city="臺北市"):
    url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={WEATHER_API_KEY}&locationName={city}"
    try:
        res = requests.get(url)
        data = res.json()
        weather = data['records']['location'][0]['weatherElement'][0]['time'][0]['parameter']['parameterName']
        return weather
    except Exception as e:
        return None

def recommend_flavor_by_weather(weather):
    for key in WEATHER_TO_FLAVOR:
        if key in weather:
            return WEATHER_TO_FLAVOR[key][0]
    return WEATHER_TO_FLAVOR['其他'][0]

import random
def get_weather_and_recommend(city="臺北市"):
    weather = get_weather(city)
    if not weather:
        return f"抱歉，次妹暫時查不到{city}的天氣資訊喔！"
    flavor = recommend_flavor_by_weather(weather)
    template = random.choice(RECOMMEND_TEMPLATES)
    return template.format(city=city, weather=weather, flavor=flavor) 