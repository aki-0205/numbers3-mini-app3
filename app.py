import streamlit as st
import pandas as pd
import requests
import base64
import json
from datetime import datetime, date, timedelta

# ==========================================
# ページ設定
# ==========================================
st.set_page_config(
    page_title="Numbers 3 Mini 33口予測・的中管理",
    page_icon="🎯",
    layout="centered"
)

# ==========================================
# 予測ロジック（20口を必ず内包した33口選出）
# ==========================================
def generate_predictions(target_date_obj):
    import random
    all_numbers = [f"{i:02d}" for i in range(100)]
    
    date_str = target_date_obj.strftime("%Y%m%d")
    
    # 1. まずベースとなる20口を決定（従来の再現性維持）
    random.seed(int(date_str) + 100)
    base_20 = sorted(random.sample(all_numbers, 20))
    
    # 2. 残りの80個から、さらに13個を追加して合計33口にする
    remaining = [n for n in all_numbers if n not in base_20]
    random.seed(int(date_str) + 200)
    additional_13 = sorted(random.sample(remaining, 13))
    
    # 3. 合併してソート（必ず20口が完全網羅された33口になる）
    selected_33 = sorted(base_20 + additional_13)
    
    return base_20, selected_33

# 本日の日付と言い回し
now = datetime.now()
today = date.today()
base_20, predictions_33 = generate_predictions(today)

# ==========================================
# ヘッダー・タイトル部分
# ==========================================
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    <div class="main-header">
        <h2>🎯 ナンバースミニ 33口予測 ＆ 的中管理</h2>
        <p style="margin:0; font-size: 0.9rem;">確率1/3（33口）体制 ｜ 20口ベース完全網羅型</p>
    </div>
""", unsafe_allow_html=True)

# 状況バー
st.info(f"🕒 時刻 (JST): {now.strftime('%H:%M')} | 📅 対象予測日: **{today.strftime('%m月%d日')}** (ベース20口を完全内包)")

# ==========================================
# タブによる画面切り替え（見やすさ・操作性の改善）
# ==========================================
tab1, tab2, tab3 = st.tabs(["🎯 本日の33口予測", "📊 統計・分析グラフ", "⚙️ 的中実績・設定"])

with tab1:
    st.subheader(f"📅 {today.strftime('%m月%d日')} 抽選向け予測数字（全33口）")
    st.caption("※従来の20口ベースが確実に含まれています。")
    
    # 見やすいボタングリッド風の表示
    cols_per_row = 5
    preds = predictions_33
    for i in range(0, len(preds), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j, col in enumerate(row_cols):
            if i + j < len(preds):
                num = preds[i + j]
                # 20口ベースに含まれているものは色を強調するなどの工夫
                if num in base_20:
                    col.markdown(f"<div style='background-color:#e3f2fd; border:2px solid #2196f3; border-radius:8px; text-align:center; padding:10px; font-weight:bold; color:#0d47a1; margin-bottom:8px;'>{num}</div>", unsafe_allow_html=True)
                else:
                    col.markdown(f"<div style='background-color:#f5f5f5; border:1px solid #ccc; border-radius:8px; text-align:center; padding:10px; font-weight:bold; color:#333; margin-bottom:8px;'>{num}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**【表示の凡例】** 青枠の数字：ベース20口に含まれる番号 / グレー枠：33口拡張用に追加された番号")

with tab2:
    st.subheader("📊 予測分布・統計分析")
    st.markdown("00から99までの全数字における33口の分布状況です。")
    
    chart_df = pd.DataFrame({
        "番号": [f"{i:02d}" for i in range(100)],
        "選択状態": [1 if f"{i:02d}" in predictions_33 else 0 for i in range(100)]
    })
    chart_df.set_index("番号", inplace=True)
    st.bar_chart(chart_df)

with tab3:
    st.subheader("⚙️ 当選数字の登録と実績管理")
    st.markdown("実際の当選数字を入力し、的中率や履歴を記録します。")
    
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

# フッター
st.markdown("---")
st.caption("Numbers 3 Mini Prediction App (33-Port Fully Integrated Version)")
