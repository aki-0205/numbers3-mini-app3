import streamlit as st
import pandas as pd
from collections import Counter, deque
from datetime import datetime, time, timedelta, date
import json
import os

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

def is_zorome(num: str) -> bool:
    return len(num) == 2 and num[0] == num[1]

def get_period_key() -> str:
    now = datetime.now()
    weekday = now.weekday()
    current_time = now.time()
    if weekday <= 4:
        if current_time < time(20, 0):
            target = now.date()
        else:
            target = (now + timedelta(days=1)).date()
    else:
        days_to_monday = (7 - weekday) % 7 or 7
        target = (now + timedelta(days=days_to_monday)).date()
    return target.strftime("%Y-%m-%d")

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

def calculate_scores(history: list) -> dict:
    counter = Counter(history)
    total = len(history)
    scores = {}
    for i in range(100):
        num = f"{i:02d}"
        count = counter.get(num, 0)
        score = count * 10.0
        if num in history[-10:]: score += 3.0
        if num in history[-5:]: score += 2.0
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
    ranked = sorted(scores.keys(), key=lambda x: (-scores[x], x))
    selected = [num for num in
