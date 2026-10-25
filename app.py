import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta, timezone

# ページ設定
st.set_page_config(page_title="ナンバーズ3 ミニ 予測システム (20口 / 33口比較)", layout="centered")

# 日本標準時（JST = UTC+9）の定義
JST = timezone(timedelta(hours=9))

# 正確な履歴データ（第7099回 〜 第7050回）
INITIAL_DATA = [
    {"draw": 7099, "num": "16"}, {"draw": 7098, "num": "45"}, {"draw": 7097, "num": "25"},
    {"draw": 7096, "num": "86"}, {"draw": 7095, "num": "08"}, {"draw": 7094, "num": "11"},
    {"draw": 7093, "num": "45"}, {"draw": 7092, "num": "15"}, {"draw": 7091, "num": "52"},
    {"draw": 7090, "num": "10"}, {"draw": 7089, "num": "31"}, {"draw": 7088, "num": "75"},
    {"draw": 7087, "num": "45"}, {"draw": 7086, "num": "05"}, {"draw": 7085, "num": "69"},
    {"draw": 7084, "num": "69"}, {"draw": 7083, "num": "06"}, {"draw": 7082, "num": "18"},
    {"draw": 7081, "num": "20"}, {"draw": 7080, "num": "79"}, {"draw": 7079, "num": "46"},
    {"draw": 7078, "num": "35"}, {"draw": 7077, "num": "68"}, {"draw": 7076, "num": "16"},
    {"draw": 7075, "num": "68"}, {"draw": 7074, "num": "46"}, {"draw": 7073, "num": "46"},
    {"draw": 7072, "num": "24"}, {"draw": 7071, "num": "56"}, {"draw": 7070, "num": "15"},
    {"draw": 7069, "num": "09"}, {"draw": 7068, "num": "69"}, {"draw": 7067, "num": "57"},
    {"draw": 7066, "num": "29"}, {"draw": 7065, "num": "24"}, {"draw": 7064, "num": "24"},
    {"draw": 7063, "num": "64"}, {"draw": 7062, "num": "29"}, {"draw": 7061, "num": "09"},
    {"draw": 7060, "num": "09"}, {"draw": 7059, "num": "09"}, {"draw": 7058, "num": "48"},
    {"draw": 7057, "num": "06"}, {"draw": 7056, "num": "16"}, {"draw": 7055, "num": "69"},
    {"draw": 7054, "num": "26"}, {"draw": 7053, "num": "89"}, {"draw": 7052, "num": "89"},
    {"draw": 7051, "num": "07"}, {"draw": 7050, "num": "98"}
]

# セッション状態の初期化
if "history" not in st.session_state:
    st.session_state.history = INITIAL_DATA.copy()

# -------------------------------------------------------------
# 1. 時間固定ロジック
# -------------------------------------------------------------
def get_current_window_info():
    now = datetime.now(JST)
    weekday = now.weekday()
    
    target_date = now.date()
    if now.time() < time(20, 0):
        target_date -= timedelta(days=1)
        weekday = target_date.weekday()
    
    if weekday == 5:
        target_date -= timedelta(days=1)
    elif weekday == 6:
        target_date -= timedelta(days=2)
        
    next_date = target_date + timedelta(days=1)
    if next_date.weekday() == 5:
        next_date += timedelta(days=2)
    elif next_date.weekday() == 6:
        next_date += timedelta(days=1)
        
    window_key = target_date.strftime("%Y-%m-%d")
    prediction_target_str = f"{next_date.month}月{next_date.day}日"
    ref_date_str = f"{target_date.month}月{target_date.day}日"
    
    return window_key, prediction_target_str, ref_date_str

# -------------------------------------------------------------
# 2. 予測・選出ロジック
# -------------------------------------------------------------
def is_zorome(num_str):
    return num_str[0] == num_str[1]

def is_renban(num_str):
    d1 = int(num_str[0])
    d2 = int(num_str[1])
    if abs(d1 - d2) == 1:
        if {d1, d2} == {0, 9}:
            return False
        return True
    return False

def select_top_numbers(history_data, count):
    all_candidates = [f"{i:02d}" for i in range(100)]
    
    df_hist = pd.DataFrame(history_data)
    df_hist['num_int'] = df_hist['num'].astype(int)
    
    freq_map = df_hist['num'].value_counts().to_dict()
    latest_num = history_data[0]['num']
    
    scores = {}
    for num in all_candidates:
        freq = freq_map.get(num, 0)
        base_score = 10.0 - (freq * 1.5) + np.random.uniform(0, 2.0)
        
        val = int(num)
        if val % 2 != 0:
            base_score += 0.2  
            
        scores[num] = base_score

    excluded = set()
    excluded.add(latest_num)
    
    if is_zorome(latest_num):
        for num in all_candidates:
            if is_zorome(num):
                excluded.add(num)
                
    if is_renban(latest_num):
        for num in all_candidates:
            if is_renban(num):
                excluded.add(num)

    valid_candidates = [num for num in all_candidates if num not in excluded]
    valid_candidates.sort(key=lambda x: scores[x], reverse=True)
    
    selected = valid_candidates[:count]
    selected.sort()
    return selected, latest_num

# -------------------------------------------------------------
# 3. Streamlit 画面レイアウト
# -------------------------------------------------------------
st.markdown(
    '<div style="background-color: #2b5c8f; padding: 16px; border-radius: 8px; text-align: center; color: white; margin-bottom: 15px;">'
    '<h2 style="margin: 0; font-size: 1.25rem;">🎯 ナンバーズ3 ミニ 予測システム (20口 / 33口)</h2>'
    '</div>',
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4 = st.tabs(["📊 20口予測表示", "📊 33口予測表示", "📝 当選数字の入力・履歴", "📈 出現傾向 棒グラフ"])

window_key, target_str, ref_str = get_current_window_info()
now_jst = datetime.now(JST)
np.random.seed(hash(window_key + st.session_state.history[0]['num']) % (2**32))

with tab1:
    selected_nums_20, latest_used = select_top_numbers(st.session_state.history, 20)
    st.info(f"🕒 時刻 (JST): {now_jst.strftime('%H:%M')} | 🎯 予測対象: **{target_str}** | 📊 参照: **{ref_str}** 結果 (`{latest_used}`)")
    st.markdown("---")
    st.markdown(f"#### 📌 {target_str} 抽選向け予測数字（全20個）")
    
    grid_html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 20px;">'
    for idx, num in enumerate(selected_nums_20):
        grid_html += (
            '<div style="background-color: #ffffff; border: 2px solid #2b5c8f; border-radius: 8px; padding: 10px 4px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">'
            f'<div style="font-size: 0.7em; color: #555; margin-bottom: 3px; font-weight: bold;">口 {idx+1}</div>'
            f'<div style="font-size: 1.4em; font-weight: bold; color: #111; letter-spacing: 1px;">{num}</div>'
            '</div>'
        )
    grid_html += '</div>'
