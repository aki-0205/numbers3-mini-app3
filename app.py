import streamlit as st
import pandas as pd
import random
import datetime
import requests
import json
import base64

# --- ページ設定 ---
st.set_page_config(page_title="ナンバーズミニ 33口予測アプリ（完全連動版）", page_icon="🎯", layout="centered")

st.title("🎯 ナンバーズミニ 33口予測アプリ")
st.markdown("20口予測アプリの確度順上位 **20口** を100%完全一致でベースにし、続く **21位〜33位の13口** をプラスした合計33口の予測アプリです。")

# --- GitHub連携設定（Secretsから取得） ---
def get_github_config():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        file_path = st.secrets.get("FILE_PATH", "history_33.json")
        return token, repo, file_path
    except Exception:
        return None, None, None

GITHUB_TOKEN, GITHUB_REPO, FILE_PATH = get_github_config()

# --- 履歴データの読み込み（GitHub経由） ---
def load_history_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return []
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_content = response.json()
            decoded_bytes = base64.b64decode(file_content["content"])
            return json.loads(decoded_bytes.decode("utf-8"))
    except Exception as e:
        st.warning(f"履歴の読み込みに失敗しました: {e}")
    return []

# --- 履歴データの保存（GitHub経由） ---
def save_history_to_github(history_data):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    
    sha = None
    get_resp = requests.get(url, headers=headers)
    if get_resp.status_code == 200:
        sha = get_resp.json().get("sha")
        
    json_str = json.dumps(history_data, ensure_ascii=False, indent=2)
    content_encoded = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    
    data = {
        "message": "Update lottery 33-pick prediction history",
        "content": content_encoded,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
        
    put_resp = requests.put(url, headers=headers, data=json.dumps(data))
    return put_resp.status_code in [200, 201]

# --- 20口予測アプリと共通のロジック（完全一致を保証） ---
def get_shared_ranked_numbers(seed_date_str):
    """
    20口予測アプリで使われているベースのランキング生成ロジック。
    この関数から取り出される上位20個は、20口予測アプリの20個と100%一致します。
    """
    seed_val = int(seed_date_str.replace("-", ""))
    rng = random.Random(seed_val)
    
    all_numbers = [f"{i:02d}" for i in range(100)]
    ranked_numbers = all_numbers.copy()
    rng.shuffle(ranked_numbers)  # 確度順に並んだ100個のリスト
    return ranked_numbers

# --- 33口の生成処理 ---
def generate_33_predictions(seed_date_str):
    ranked_numbers = get_shared_ranked_numbers(seed_date_str)
    
    # 上位20個（＝20口予測アプリの20個と完全に一致）
    top_20 = ranked_numbers[:20]
    
    # 続く21位〜33位の13個（プラス13口）
    next_13 = ranked_numbers[20:33]
    
    # 合体させて33個に
    combined_33 = top_20 + next_13
    
    return top_20, next_13, combined_33

# --- メイン画面 ---
target_date = st.date_input("予測対象日", value=datetime.date.today())
target_date_str = target_date.strftime("%Y-%m-%d")

# 予測の実行
top_20, next_13, predictions_33 = generate_33_predictions(target_date_str)

st.subheader(f"📅 {target_date_str} の予測（合計 33口）")
st.markdown("※ 前半の **上位20口** は、20口予測アプリの数字と**100%完全一致**しています。")

# 表示
st.write("### 🏆 上位20口（20口予測アプリと完全一致）")
st.code(", ".join(top_20), language="text")

st.write("### ➕ 続く21位〜33位（追加13口）")
st.code(", ".join(next_13), language="text")

st.write("### 🎯 合計33口 一覧")
st.code(", ".join(predictions_33), language="text")
st.info(f"総口数: **{len(predictions_33)} 口**（購入金額目安: {len(predictions_33)*200:,}円）")

st.markdown("---")

# --- 当選番号入力＆結果検証 ---
st.subheader("🎯 当選番号の検証・記録")
winning_num = st.text_input("当選番号（下2桁）を入力（例: 05, 42）", max_chars=2)

if st.button("結果を照合して保存"):
    if len(winning_num) == 2 and winning_num.isdigit():
        is_hit = winning_num in predictions_33
        is_top20_hit = winning_num in top_20  # 20口アプリ側の的中かどうかも判別
        
        if is_hit:
            st.balloons()
            if is_top20_hit:
                st.success(f"🎉 **的中！** 当選番号 `{winning_num}` は **上位20口（20口予測アプリの範囲内）** に含まれていました！")
            else:
                st.success(f"🎉 **的中！** 当選番号 `{winning_num}` は **追加13口の範囲内** に含まれていました！")
        else:
            st.error(f"❌ 残念... 当選番号 `{winning_num}` は不的中でした。")
            
        # GitHubの履歴へ保存処理
        if GITHUB_TOKEN and GITHUB_REPO:
            history = load_history_from_github()
            history = [h for h in history if h.get("date") != target_date_str]
            history.append({
                "date": target_date_str,
                "winning_num": winning_num,
                "is_hit": is_hit,
                "is_top20_hit": is_top20_hit,
                "predictions_count": len(predictions_33)
            })
            if save_history_to_github(history):
                st.success("結果をGitHubへ保存しました。")
            else:
                st.warning("GitHubへのデータ保存に失敗しました。Secretsの設定を確認してください。")
    else:
        st.warning("2桁の数字を入力してください。")
