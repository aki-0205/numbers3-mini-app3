import streamlit as st
import pandas as pd
import requests
import base64
import json
from datetime import datetime, date

# ==========================================
# ページ設定
# ==========================================
st.set_page_config(
    page_title="Numbers 3 Mini 33口予測・的中管理",
    page_icon="🎯",
    layout="centered"
)

# ==========================================
# 予測ロジック（大元の20口アプリと完全同一のベース生成）
# ==========================================
def generate_predictions(target_date_obj):
    import random
    all_numbers = [f"{i:02d}" for i in range(100)]
    
    date_str = target_date_obj.strftime("%Y%m%d")
    
    # 【最重要】大元の20口アプリと完全に同じシード値と抽出方法
    random.seed(int(date_str))
    base_20 = sorted(random.sample(all_numbers, 20))
    
    # 残りの80個から、さらに13個を追加して合計33口にする（ベースの20口は100%含まれます）
    remaining = [n for n in all_numbers if n not in base_20]
    
    # 拡張用の13個を選ぶ（こちらは別のシードで固定的に抽出）
    random.seed(int(date_str) + 999)
    additional_13 = sorted(random.sample(remaining, 13))
    
    # 合併してソート
    selected_33 = sorted(base_20 + additional_13)
    
    return base_20, selected_33

# 本日の日付と予測数字の取得
now = datetime.now()
today = date.today()
base_20, predictions_33 = generate_predictions(today)

# ==========================================
# 画面表示
# ==========================================
st.title("🎯 ナンバースミニ 33口予測 ＆ 的中管理")
st.markdown("確率1/3（33口）体制 ｜ **20口ベース完全網羅型**")

st.info(f"🕒 時刻 (JST): {now.strftime('%H:%M')} | 📅 対象予測日: {today.strftime('%m月%d日')} (ベース20口を完全内包)")

tab1, tab2, tab3 = st.tabs(["🎯 本日の33口予測", "📊 統計・分析グラフ", "⚙️ 的中実績・設定"])

with tab1:
    st.subheader(f"📅 {today.strftime('%m月%d日')} 抽選向け予測数字（全33口）")
    st.caption("※大元の20口アプリの数字が完全にすべて含まれています。")
    
    cols_per_row = 5
    preds = predictions_33
    for i in range(0, len(preds), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j, col in enumerate(row_cols):
            if i + j < len(preds):
                num = preds[i + j]
                if num in base_20:
                    col.success(num)  # 大元アプリの20口に含まれる数字（緑）
                else:
                    col.info(num)     # 33口にするための追加数字（青）
    
    st.markdown("---")
    st.markdown("**【表示の凡例】** 緑色：大元の20口アプリと共通の数字 / 青色：33口にするために追加された数字")

with tab2:
    st.subheader("📊 予測分布・統計分析")
    chart_df = pd.DataFrame({
        "番号": [f"{i:02d}" for i in range(100)],
        "選択状態": [1 if f"{i:02d}" in predictions_33 else 0 for i in range(100)]
    })
    chart_df.set_index("番号", inplace=True)
    st.bar_chart(chart_df)

with tab3:
    st.subheader("⚙️ 当選数字の登録と実績管理")
    with st.form("result_form"):
        reg_date = st.date_input("抽選対象日", value=today)
        winning_num = st.text_input("実際の当選数字（2桁、例: 48）", max_chars=2)
        submit_btn = st.form_submit_button("🎯 データを記録する")

    if submit_btn:
        if not winning_num or len(winning_num) != 2:
            st.warning("⚠️ 正しい2桁の当選数字を入力してください。")
        else:
            is_hit = winning_num in predictions_33
            hit_text = "🎉 見事的中！" if is_hit else "💧 外れ..."
            st.success(f"判定結果: 【 {winning_num} 】 は本日の予測33口に... **{hit_text}**")

st.markdown("---")
st.caption("Numbers 3 Mini Prediction App (33-Port Fully Integrated Version)")
