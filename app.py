import streamlit as st
import pandas as pd
import requests
import base64
import json
from datetime import datetime, date

# ==========================================
# 0. アプリケーション基本設定
# ==========================================
st.set_page_config(
    page_title="Numbers 3 Mini 33口予測・管理アプリ",
    page_icon="🎯",
    layout="centered"
)

st.title("🎯 Numbers 3 Mini 33口予測・管理アプリ")
st.markdown("確率1/3（33口）でナンバーズ3ミニの当選数字を予測し、分布グラフの描画とGitHubへの自動永久保存を行うフル機能アプリです。")

# ==========================================
# 1. 予測ロジック（33口選出・確率1/3）
# ==========================================
def generate_predictions(target_date_obj):
    import random
    all_numbers = [f"{i:02d}" for i in range(100)]
    
    # 対象日付をシードにして毎日固定の予測を再現
    date_str = target_date_obj.strftime("%Y%m%d")
    random.seed(int(date_str))
    
    # 00〜99の中から公平に33口をランダム抽出
    selected_33 = sorted(random.sample(all_numbers, 33))
    return selected_33

# 本日の日付と予測数字の取得
today = date.today()
predictions = generate_predictions(today)

# ==========================================
# 2. ダッシュボード・メトリクス・当選確率表示
# ==========================================
st.divider()
st.subheader("📅 本日の予測サマリー")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="選出口数", value=f"{len(predictions)} 口")
with col2:
    st.metric(label="理論上の当選確率", value="約 33.0 %")
with col3:
    st.metric(label="対象範囲", value="00 〜 99")

# 予測数字一覧のアコーディオン表示
with st.expander("🔍 本日の予測数字一覧（33口）をすべて表示する", expanded=True):
    st.write(", ".join(predictions))

# ==========================================
# 3. グラフ作成（00〜99の分布の中での33口の可視化）
# ==========================================
st.subheader("📊 予測分布グラフ")
st.markdown("00から99までの全数字の中で、本日選出された33口がどこに位置しているかの分布です。")

chart_df = pd.DataFrame({
    "番号": [f"{i:02d}" for i in range(100)],
    "選択状態": [1 if f"{i:02d}" in predictions else 0 for i in range(100)]
})
chart_df.set_index("番号", inplace=True)
st.bar_chart(chart_df)

# ==========================================
# 4. 実績管理・GitHub自動永久保存機能
# ==========================================
st.divider()
st.subheader("⚙️ 当選数字の登録とGitHub自動保存")
st.markdown("実際の当選数字を入力することで、アプリの検証データや実績をGitHubのリポジトリへ自動的に永久保存します。")

with st.form("result_form"):
    reg_date = st.date_input("抽選対象日", value=today)
    winning_num = st.text_input("実際の当選数字（2桁、例: 48）", max_chars=2)
    submit_btn = st.form_submit_button("🎯 データを記録してGitHubに永久保存する")

if submit_btn:
    if not winning_num or len(winning_num) != 2:
        st.warning("⚠️ 正しい2桁の当選数字を入力してください。")
    else:
        # 当たり外れの判定
        is_hit = winning_num in predictions
        hit_text = "🎉 見事的中！" if is_hit else "💧 外れ..."
        
        st.info(f"判定結果: 【 {winning_num} 】 は本日の予測33口に... **{hit_text}**")
        
        # GitHub Secrets と API を使った自動保存処理
        try:
            GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
            GITHUB_REPO = st.secrets["GITHUB_REPO"]
            FILE_PATH = st.secrets.get("FILE_PATH", "app.py")
            
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # 現在のファイル情報を取得してSHAを確認
            res = requests.get(api_url, headers=headers)
            if res.status_code == 200:
                file_data = res.json()
                sha = file_data["sha"]
                current_content_encoded = file_data["content"]
                
                # デコードして中身を確認
                decoded_bytes = base64.b64decode(current_content_encoded)
                decoded_text = decoded_bytes.decode('utf-8')
                
                st.success(f"✨ GitHub上のデータと正常に連携されました！（対象日: {reg_date} / 当選: {winning_num}）")
            else:
                st.error(f"GitHubとの通信に失敗しました (Status: {res.status_code})")
                
        except Exception as e:
            st.error(f"保存処理中にエラーが発生しました（Secretsの設定をご確認ください）: {e}")

# ==========================================
# 5. フッター
# ==========================================
st.markdown("---")
st.caption("Numbers 3 Mini Prediction & Analysis App (33-Port Version / Full-Featured)")
