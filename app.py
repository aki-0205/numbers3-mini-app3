import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter, deque
from datetime import datetime, time
import json
import os

st.set_page_config(page_title="ナンバーズミニ20口予測", page_icon="🎯", layout="centered")

DATA_FILE = "mini_history.json"
PREDICTION_CACHE = "prediction_cache.json"

# =========================================================
# 初回用：第7050回〜第7099回のミニ数字（下2桁）正確版
# =========================================================
INITIAL_50 = [
    "16", "45", "25", "86", "08", "11", "45", "15", "52", "10",
    "31", "75", "45", "05", "69", "69", "06", "18", "20", "02",
    "26", "39", "87", "56", "82", "66", "88", "29", "53", "88",
    "08", "60", "50", "94", "82", "51", "66", "12", "82", "77",
    "91", "60", "08", "86", "37", "86", "19", "72", "09", "78"
]

def is_zorome(num: str) -> bool:
    return len(num) == 2 and num[0] == num[1]

def get_period_key() -> str:
    now = datetime.now()
    weekday = now.weekday()  # 0=月 ... 6=日
    current_time = now.time()
    
    if weekday <= 4:  # 月〜金
        if current_time < time(20, 0):
            target_date = now.date()
        else:
            target_date = (now + pd.Timedelta(days=1)).date()
    else:  # 土・日 → 次の月曜日まで同じキー
        days_until_monday = (7 - weekday) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        target_date = (now + pd.Timedelta(days=days_until_monday)).date()
    
    return target_date.strftime("%Y-%m-%d")

def load_history() -> deque:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return deque(data, maxlen=50)
        except:
            pass
    return deque(INITIAL_50, maxlen=50)

def save_history(history: deque):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history), f, ensure_ascii=False)

def load_prediction_cache() -> dict:
    if os.path.exists(PREDICTION_CACHE):
        try:
            with open(PREDICTION_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_prediction_cache(cache: dict):
    with open(PREDICTION_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

def calculate_scores(history: list) -> dict:
    counter = Counter(history)
    total = len(history)
    scores = {}
    
    for i in range(100):
        num = f"{i:02d}"
        count = counter.get(num, 0)
        score = count * 10.0
        
        if num in history[-10:]:
            score += 3.0
        if num in history[-5:]:
            score += 2.0
            
        odd_count = sum(1 for h in history if int(h) % 2 == 1)
        even_count = total - odd_count
        if odd_count > even_count + 5 and int(num) % 2 == 0:
            score += 1.5
        elif even_count > odd_count + 5 and int(num) % 2 == 1:
            score += 1.5
            
        scores[num] = score
    return scores

def generate_prediction(history: list) -> list:
    scores = calculate_scores(history)
    latest = history[-1] if history else None
    
    excluded = set()
    if latest and is_zorome(latest):
        for i in range(10):
            excluded.add(f"{i}{i}")
    
    # スコア降順 → 同点時は数字昇順で完全固定
    ranked = sorted(
        scores.keys(),
        key=lambda x: (-scores[x], x)
    )
    
    selected = []
