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
        
        # 直近ボーナス
        if num in history[-10:]:
            score += 3.0
        if num in history[-5:]:
            score += 2.0
            
        # 奇数偶数平準化（弱め）
        odd_count = sum(1 for h in history if int(h) % 2 == 1)
        even_count = total - odd_count
        if odd_count > even_count + 5 and int(num) % 2 == 0:
            score += 1.5
        elif even_count > odd_count + 5 and int(num) % 2 == 1:
            score += 1.5
            
        scores[num] = score
    return scores

def generate_prediction(history: list) -> list:
    """スコア順に厳密に並べ、同点時は数字の小さい順で完全に安定させる"""
    scores = calculate_scores(history)
    latest = history[-1] if history else None
    
    excluded = set()
    if latest and is_zorome(latest):
        for i in range(10):
            excluded.add(f"{i}{i}")
    
    # 重要：スコア降順 → 同点時は数字昇順 で完全に安定ソート
    ranked = sorted(
        scores.keys(),
        key=lambda x: (-scores[x], x)   # マイナスで降順、同点は文字列昇順
    )
    
    selected = []
    for num in ranked:
        if num not in excluded:
            selected.append(num)
        if len(selected) >= 20:
            break
    
    return selected   # ここではソートし直さない（順位を保持）

# ==================== メイン画面 ====================
st.markdown("""
<div style="background:linear-gradient(135deg,#1a365d,#2b6cb0);padding:16px;border-radius:12px;text-align:center;color:white;margin-bottom:18px;">
    <h2 style="margin:0;font-size:1.35rem;">🎯 ナンバーズ3 ミニ 20口予測</h2>
    <p style="margin:5px 0 0;font-size:0.85rem;opacity:0.9;">直近50回分析ベース（初回は7050〜7099）</p>
</div>
""", unsafe_allow_html=True)

history = load_history()
period_key = get_period_key()
cache = load_prediction_cache()

# キャッシュ優先（ここが最重要）
if period_key in cache and len(cache[period_key]) == 20:
    selected_20 = cache[period_key]
else:
    selected_20 = generate_prediction(list(history))
    cache[period_key] = selected_20
    save_prediction_cache(cache)

st.subheader("本日の予測20口")
st.caption(f"固定期間キー: **{period_key}** ／ 使用データ: 直近{len(history)}回")

# ========== 横5 × 縦4 グリッド ==========
for row in range(4):
    cols = st.columns(5)
    for col_idx in range(5):
        idx = row * 5 + col_idx
        num = selected_20[idx]
        with cols[col_idx]:
            st.markdown(
                f"""
                <div style="
                    background:#ffffff;
                    border:2px solid #2b6cb0;
                    border-radius:10px;
                    text-align:center;
                    padding:10px 4px 12px;
                    margin-bottom:8px;
                    box-shadow:0 1px 3px rgba(0,0,0,0.08);
                ">
                    <div style="font-size:0.72rem;color:#718096;margin-bottom:3px;">口{idx+1}</div>
                    <div style="font-size:1.45rem;font-weight:700;color:#1a365d;letter-spacing:1px;">{num}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# 当選登録
st.markdown("---")
st.subheader("当選数字の登録")
c1, c2 = st.columns([3, 1])
with c1:
    win_input = st.text_input("当選したミニ数字（2桁）", max_chars=2, label_visibility="collapsed", placeholder="例: 16")
with c2:
    if st.button("登録", use_container_width=True):
        if win_input and win_input.isdigit() and len(win_input) == 2:
            history.append(win_input.zfill(2))
            save_history(history)
            # キャッシュを削除して次回から新しいウィンドウで再計算
            if os.path.exists(PREDICTION_CACHE):
                os.remove(PREDICTION_CACHE)
            st.success(f「{win_input}」を登録しました")
            st.rerun()
        else:
            st.error("2桁の数字を入力してください")

# 的中率
if history:
    hits = sum(1 for h in list(history)[-50:] if h in selected_20)
    st.metric("直近履歴での的中数（参考）", f"{hits} / {min(50, len(history))}")

# 棒グラフ
st.markdown("---")
st.subheader("出現分布（10単位）")
if history:
    counter = Counter(history)
    bins = [f"{i:02d}-{i+9:02d}" for i in range(0, 100, 10)]
    values = [sum(counter.get(f"{j:02d}", 0) for j in range(i, i+10)) for i in range(0, 100, 10)]
    chart_df = pd.DataFrame({"レンジ": bins, "回数": values})
    st.bar_chart(chart_df.set_index("レンジ"), height=260)

with st.expander("現在の直近50回履歴を確認"):
    st.write(" → ".join(list(history)))

st.caption("※この予測は参考情報です。当選を保証するものではありません。")
