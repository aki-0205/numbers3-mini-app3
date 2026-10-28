import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter, deque
from datetime import datetime, time, timedelta, date
import json
import os
import pytz   # 日本時間を強制するために追加

st.set_page_config(page_title="ナンバーズミニ20口予測", page_icon="🎯", layout="centered")

INITIAL_50 = [
    "16", "45", "25", "86", "08", "11", "45", "15", "52", "10",
    "31", "75", "45", "05", "69", "69", "06", "18", "20", "02",
    "26", "39", "87", "56", "82", "66", "88", "29", "53", "88",
    "08", "60", "50", "94", "82", "51", "66", "12", "82", "77",
    "91", "60", "08", "86", "37", "86", "19", "72", "09", "78"
]

DATA_FILE = "mini_history.json"
CACHE_FILE = "prediction_cache.json"
HIT_LOG_FILE = "hit_log.json"

def is_zorome(num: str) -> bool:
    return len(num) == 2 and num[0] == num[1]

def get_period_key() -> str:
    # 日本時間で判定
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.now(jst)
    
    current_time = now.time()
    weekday = now.weekday()  # 0=月 ... 6=日

    if current_time >= time(20, 0):
        base_date = now.date() + timedelta(days=1)
        base_weekday = (weekday + 1) % 7
    else:
        base_date = now.date()
        base_weekday = weekday

    if base_weekday >= 5:  # 土日は次の月曜日まで
        days_to_monday = (7 - base_weekday) % 7
        if days_to_monday == 0:
            days_to_monday = 7
        target_date = base_date + timedelta(days=days_to_monday)
    else:
        target_date = base_date

    return target_date.strftime("%Y-%m-%d")

def load_history() -> deque:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return deque(json.load(f), maxlen=50)
        except:
            pass
    return deque(INITIAL_50, maxlen=50)

def save_history(history: deque):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(list(history), f, ensure_ascii=False)
    except:
        pass

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
    except:
        pass

def load_hit_log() -> list:
    if os.path
