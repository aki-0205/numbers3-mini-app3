import streamlit as st
import pandas as pd
from collections import Counter, deque
from datetime import datetime, time, timedelta, date
import json
import os

st.set_page_config(page_title="ナンバーズミニ20口予測", page_icon="🎯", layout="centered")

# =========================================================
# 初回データ（第7050回〜第7099回のミニ数字）
# =========================================================
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
    ranked = sorted(scores.keys(), key=lambda x: (-scores[x], x))
    selected = [num for num in ranked if num not in excluded][:20]
    return selected

# ==================== メイン画面 ====================
st.markdown("""
<div style="background:linear-gradient(135deg,#1a365d,#2b6cb0);padding:14px;border-radius:10px;text-align:center;color:white;margin-bottom:12px;">
    <h2 style="margin:0;font-size:1.25rem;">🎯 ナンバーズ3 ミニ 20口予測</h2>
    <p style="margin:4px 0 0;font-size:0.8rem;opacity:0.9;">直近50回分析（初回7050〜7099）</p>
</div>
""", unsafe_allow_html=True)

history = load_history()
period_key = get_period_key()
cache = load_cache()

if period_key in cache and len(cache[period_key]) == 20:
    selected_20 = cache[period_key]
else:
    selected_20 = generate_prediction(list(history))
    cache[period_key] = selected_20
    save_cache(cache)

st.subheader("本日の予測20口")
st.caption(f"固定期間キー: **{period_key}** ／ 使用データ: 直近{len(history)}回")

# ========== コンパクト一覧表示 ==========
st.markdown("### 予測数字一覧")

lines = []
for i in range(0, 20, 5):
    group = selected_20[i:i+5]
    line = "　".join([f"**{num}**" for num in group])
    lines.append(f"口{i+1:2d}〜{i+5:2d}： {line}")

st.markdown("\n\n".join(lines))

st.markdown("---")
compact = "  ".join(selected_20)
st.markdown(
    f"<div style='font-size:1.3rem;font-weight:700;letter-spacing:1px;text-align:center;padding:10px;background:#f0f4f8;border-radius:8px;'>{compact}</div>",
    unsafe_allow_html=True
)

# ========== 当選登録 ==========
st.markdown("---")
st.subheader("当選数字の登録")

draw_date = st.date_input("抽選日", value=date.today(), max_value=date.today(), format="YYYY/MM/DD")

c1, c2 = st.columns([3, 1])
with c1:
    win_input = st.text_input("当選ミニ数字（2桁）", max_chars=2, label_visibility="collapsed", placeholder="例: 16")
with c2:
    if st.button("登録", use_container_width=True):
        if win_input and win_input.isdigit() and len(win_input) == 2:
            history.append(win_input.zfill(2))
            save_history(history)
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
            st.success(f"{draw_date.strftime('%Y/%m/%d')} の {win_input} を登録しました")
            st.rerun()
        else:
            st.error("2桁の数字を入力してください")

# ========== 的中数 + ％表示 ==========
if history:
    hits = sum(1 for h in list(history) if h in selected_20)
    total = len(history)
    rate = (hits / total * 100) if total > 0 else 0
    st.metric("直近履歴での的中数（参考）", f"{hits} / {total}（{rate:.1f}%）")

# ========== 棒グラフ ==========
st.markdown("---")
st.subheader("出現分布（10単位）")
if history:
    counter = Counter(history)
    bins = [f"{i:02d}-{i+9:02d}" for i in range(0, 100, 10)]
    values = [sum(counter.get(f"{j:02d}", 0) for j in range(i, i+10)) for i in range(0, 100, 10)]
    chart_df = pd.DataFrame({"レンジ": bins, "回数": values})
    st.bar_chart(chart_df.set_index("レンジ"), height=220)

with st.expander("現在の直近50回履歴"):
    st.write(" → ".join(list(history)))

st.caption("※この予測は参考情報です。当選を保証するものではありません。")
