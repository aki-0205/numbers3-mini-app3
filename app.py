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
    "16",  # 7099  216
    "45",  # 7098  645
    "25",  # 7097  725
    "86",  # 7096  986
    "08",  # 7095  208
    "11",  # 7094  011
    "45",  # 7093  745
    "15",  # 7092  215
    "52",  # 7091  552
    "10",  # 7090  910
    "31",  # 7089  431
    "75",  # 7088  175
    "45",  # 7087  045
    "05",  # 7086  105
    "69",  # 7085  869
    "69",  # 7084  869
    "06",  # 7083  606
    "18",  # 7082  518
    "20",  # 7081  320
    "02",  # 7080  702
    "26",  # 7079  426
    "39",  # 7078  539
    "87",  # 7077  187
    "56",  # 7076  056
    "82",  # 7075  682
    "66",  # 7074  766
    "88",  # 7073  188
    "29",  # 7072  229
    "53",  # 7071  553
    "88",  # 7070  188
    "08",  # 7069  908
    "60",  # 7068  960
    "50",  # 7067  650
    "94",  # 7066  294
    "82",  # 7065  282
    "51",  # 7064  251
    "66",  # 7063  166
    "12",  # 7062  212
    "82",  # 7061  882
    "77",  # 7060  877
    "91",  # 7059  191
    "60",  # 7058  460
    "08",  # 7057  708
    "86",  # 7056  186
    "37",  # 7055  937
    "86",  # 7054  286
    "19",  # 7053  919
    "72",  # 7052  872
    "09",  # 7051  409
    "78",  # 7050  978
]

def is_zorome(num: str) -> bool:
    return len(num) == 2 and num[0] == num[1]

def get_period_key() -> str:
    now = datetime.now()
    weekday = now.weekday()
    current_time = now.time()
    if weekday <= 4:  # 月〜金
        if current_time < time(20, 0):
            target_date = now.date()
        else:
            target_date = (now + pd.Timedelta(days=1)).date()
    else:  # 土日 → 次の月曜まで
        days_until_monday = (7 - weekday) % 7 or 7
        target_date = (now + pd.Timedelta(days=days_until_monday)).date()
    return target_date.strftime("%Y-%m-%d")

def load_history() -> deque:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return deque(data, maxlen=50)
    # 初回はINITIAL_50を使う
    return deque(INITIAL_50, maxlen=50)

def save_history(history: deque):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history), f, ensure_ascii=False)

def load_prediction_cache() -> dict:
    if os.path.exists(PREDICTION_CACHE):
        with open(PREDICTION_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_prediction_cache(cache: dict):
    with open(PREDICTION_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

def calculate_scores(history: list) -> dict:
    if not history:
        return {f"{i:02d}": 0 for i in range(100)}
    counter = Counter(history)
    total = len(history)
    scores = {}
    for i in range(100):
        num = f"{i:02d}"
        count = counter.get(num, 0)
        score = count * 10
        if num in history[-10:]:
            score += 3
        if num in history[-5:]:
            score += 2
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
    if len(history) < 5:
        candidates = [f"{i:02d}" for i in range(100)]
        np.random.shuffle(candidates)
        return sorted(candidates[:20])

    scores = calculate_scores(history)
    latest = history[-1] if history else None
    excluded = set()

    # ゾロ目連続禁止
    if latest and is_zorome(latest):
        for i in range(10):
            excluded.add(f"{i}{i}")

    ranked = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    selected = []
    for num in ranked:
        if num not in excluded:
            selected.append(num)
        if len(selected) >= 20:
            break

    while len(selected) < 20:
        for i in range(100):
            num = f"{i:02d}"
            if num not in selected and num not in excluded:
                selected.append(num)
            if len(selected) >= 20:
                break
    return sorted(selected[:20])

# ==================== メイン画面 ====================
st.markdown("""
<div style="background:linear-gradient(135deg,#1a365d,#2b6cb0);padding:18px;border-radius:12px;text-align:center;color:white;margin-bottom:20px;">
    <h2 style="margin:0;font-size:1.4rem;">🎯 ナンバーズ3 ミニ 20口予測システム</h2>
    <p style="margin:6px 0 0;font-size:0.9rem;opacity:0.9;">直近50回分析ベース（初回は7050〜7099）</p>
</div>
""", unsafe_allow_html=True)

history = load_history()
period_key = get_period_key()
cache = load_prediction_cache()

if period_key in cache:
    selected_20 = cache[period_key]
else:
    selected_20 = generate_prediction(list(history))
    cache[period_key] = selected_20
    save_prediction_cache(cache)

st.subheader("本日の予測20口")
st.caption(f"固定期間キー: {period_key} ／ 使用データ: 直近{len(history)}回")

# 5×4マス表示
cols = st.columns(5)
for idx, num in enumerate(selected_20):
    with cols[idx % 5]:
        st.markdown(f"""
        <div style="background:#edf2f7;border:2px solid #2b6cb0;border-radius:10px;
                    text-align:center;padding:14px 0;margin-bottom:10px;
                    font-size:1.4rem;font-weight:bold;color:#1a365d;">
            {num}
        </div>
        """, unsafe_allow_html=True)

# 当選入力
st.markdown("---")
st.subheader("当選数字の登録（ウィンドウが1つずれます）")
col1, col2 = st.columns([2, 1])
with col1:
    win_input = st.text_input("当選したミニ数字（2桁）", max_chars=2)
with col2:
    if st.button("登録する", use_container_width=True):
        if win_input and win_input.isdigit() and len(win_input) == 2:
            history.append(win_input.zfill(2))
            save_history(history)
            # キャッシュをクリアして再予測させる
            if os.path.exists(PREDICTION_CACHE):
                os.remove(PREDICTION_CACHE)
            st.success(f"{win_input} を登録しました。ウィンドウが更新されます。")
            st.rerun()
        else:
            st.error("2桁の数字を入力してください")

if history:
    hits = sum(1 for h in history if h in selected_20)
    st.metric("直近履歴での的中率（参考）", f"{hits/len(history)*100:.1f}%", f"{hits}/{len(history)}")

# 棒グラフ
st.markdown("---")
st.subheader("当選数字の出現分布（10単位）")
if history:
    counter = Counter(history)
    bins = [f"{i:02d}-{i+9:02d}" for i in range(0, 100, 10)]
    values = [sum(counter.get(f"{j:02d}", 0) for j in range(i, i+10)) for i in range(0, 100, 10)]
    chart_df = pd.DataFrame({"レンジ": bins, "出現回数": values})
    st.bar_chart(chart_df.set_index("レンジ"), height=280)

with st.expander("現在の直近50回履歴"):
    st.write(" → ".join(list(history)))

st.caption("※参考情報です。当選を保証するものではありません。")
