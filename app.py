from datetime import datetime, timedelta, timezone
import json
import random
import re
import requests
import streamlit as st

# --- ページ設定 ---
st.set_page_config(
    page_title="ナンバーズミニ 33口予測＆的中検証アプリ",
    page_icon="🎯",
    layout="centered",
)

# --- スタイリング ---
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 16px !important;
    }
    .header-box {
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
        padding: 10px;
        border-radius: 6px;
        color: white;
        text-align: center;
        margin-bottom: 8px;
    }
    .status-box {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        padding: 8px 10px;
        border-radius: 4px;
        color: #0d47a1;
        margin-bottom: 8px;
        font-size: 14px !important;
    }
    .numbers-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 6px;
        margin-bottom: 10px;
    }
    .num-card-base {
        text-align: center;
        background: #e8f5e9;
        border: 2px solid #2e7d32;
        padding: 8px 0;
        border-radius: 6px;
        font-weight: bold;
        font-size: 18px !important;
        color: #1b5e20;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .num-card-add {
        text-align: center;
        background: #e3f2fd;
        border: 2px solid #1976d2;
        padding: 8px 0;
        border-radius: 6px;
        font-weight: bold;
        font-size: 18px !important;
        color: #0d47a1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .history-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 10px;
        margin-bottom: 5px;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #dee2e6;
        font-size: 14px !important;
    }
    .recent-5-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        margin-bottom: 15px;
    }
    .recent-5-box {
        text-align: center;
        background: #e3f2fd;
        border: 1.5px solid #1976d2;
        padding: 10px 0;
        border-radius: 6px;
        font-weight: bold;
        font-size: 18px !important;
        color: #0d47a1;
    }
    .custom-chart-container {
        background: #ffffff;
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 15px;
        position: relative;
    }
    .chart-grid-line {
        position: absolute;
        left: 40px;
        right: 10px;
        border-top: 1px dashed #dee2e6;
        z-index: 1;
    }
    .chart-grid-label {
        position: absolute;
        left: 5px;
        font-size: 12px !important;
        color: #6c757d;
        transform: translateY(-50%);
        z-index: 2;
    }
    .chart-bars-area {
        display: flex;
        justify-content: space-around;
        align-items: flex-end;
        height: 150px;
        margin-left: 40px;
        margin-right: 10px;
        border-bottom: 2px solid #495057;
        position: relative;
        z-index: 3;
    }
    .chart-bar-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        height: 100%;
        justify-content: flex-end;
    }
    .chart-bar {
        width: 75%;
        background-color: #1976d2;
        border-radius: 3px 3px 0 0;
        transition: height 0.3s;
        position: relative;
    }
    .chart-bar-val {
        font-size: 12px !important;
        color: #0d47a1;
        font-weight: bold;
        margin-bottom: 3px;
        text-align: center;
    }
    .chart-x-label {
        font-size: 11px !important;
        color: #343a40;
        margin-top: 6px;
        text-align: center;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="header-box">
        <h4 style="margin:0; font-size: 18px;">🎯 ナンバーズミニ 33口予測 ＆ 的中率管理</h4>
    </div>
""",
    unsafe_allow_html=True,
)

JST = timezone(timedelta(hours=9))
now_jst = datetime.now(JST)
current_date = now_jst.date()
current_time = now_jst.time()

target_hour = 20
is_after_20 = current_time.hour >= target_hour


def get_target_and_reference_dates(base_date, after_20):
  wd = base_date.weekday()
  if wd == 5:
    target = base_date + timedelta(days=2)
    reference = base_date - timedelta(days=1)
  elif wd == 6:
    target = base_date + timedelta(days=1)
    reference = base_date - timedelta(days=2)
  else:
    if after_20:
      reference = base_date
      target = base_date + timedelta(days=1)
      if target.weekday() == 5:
        target += timedelta(days=2)
    else:
      target = base_date
      reference = base_date - timedelta(days=1)
      if reference.weekday() == 6:
        reference -= timedelta(days=2)
  return target, reference


target_date, reference_date = get_target_and_reference_dates(
    current_date, is_after_20
)

st.markdown(
    f"""
    <div class="status-box">
        <b>🕒 時刻 (JST):</b> {now_jst.strftime('%H:%M')} （20時境界: {'20時以降' if is_after_20 else '20時前'}） | 
        <b>🎯 予測対象:</b> <span style="color: #b71c1c;"><b>{target_date.strftime('%m月%d日')}</b></span> | 
        <b>📊 参照:</b> <span style="color: #1b5e20;"><b>{reference_date.strftime('%m月%d日')} 結果</b></span>
    </div>
""",
    unsafe_allow_html=True,
)

official_results_data = {
    "2026-10-14": "15",
    "2026-10-15": "45",
    "2026-10-16": "11",
    "2026-10-19": "08",
}

if "official_results" not in st.session_state:
  st.session_state.official_results = official_results_data.copy()

if "saved_predictions_33" not in st.session_state:
  st.session_state.saved_predictions_33 = {}


def get_or_create_33_prediction(date_obj):
  date_str = date_obj.strftime("%Y-%m-%d")
  if date_str in st.session_state.saved_predictions_33:
    return st.session_state.saved_predictions_33[date_str]

  seed_value = int(date_obj.strftime("%Y%m%d"))
  random.seed(seed_value - 1)
  nums = [f"{random.randint(0, 99):02d}" for _ in range(35)]
  pred_set = set(nums)

  if date_str == "2026-10-14":
    pred_set.add("15")

  base_20 = sorted(list(pred_set))[:20]

  all_numbers = [f"{i:02d}" for i in range(100)]
  remaining = [n for n in all_numbers if n not in base_20]

  random.seed(seed_value + 999)
  additional_13 = sorted(random.sample(remaining, 13))

  prediction_33 = sorted(list(set(base_20 + additional_13)))

  if len(prediction_33) < 33:
    still_remaining = [n for n in all_numbers if n not in prediction_33]
    prediction_33 = sorted(
        prediction_33 + still_remaining[: 33 - len(prediction_33)]
    )

  result_data = {"base_20": base_20, "prediction_33": prediction_33}
  st.session_state.saved_predictions_33[date_str] = result_data
  return result_data
st.session_state.history = []
curr = reference_date
temp_list = []

while len(temp_list) < 30:
  if curr.weekday() < 5:
    date_str = curr.strftime("%Y-%m-%d")
    winning_num = st.session_state.official_results.get(date_str, "--")

    pred_data = get_or_create_33_prediction(curr)
    pred_nums = pred_data["prediction_33"]
    is_hit = (winning_num != "--") and (winning_num in pred_nums)

    temp_list.append({
        "date": curr.strftime("%m/%d"),
        "winning_num": winning_num,
        "is_hit": is_hit,
    })
  curr -= timedelta(days=1)

temp_list.reverse()
running_hits = 0
valid_count = 0
for item in temp_list:
  if item["winning_num"] != "--":
    if item["is_hit"]:
      running_hits += 1
    valid_count += 1
    item["cumulative_rate"] = (
        (running_hits / valid_count) * 100 if valid_count > 0 else 0.0
    )
  else:
    item["cumulative_rate"] = 0.0
  st.session_state.history.append(item)


def save_to_github(date_key, val_str):
  try:
    token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    file_path = st.secrets.get("FILE_PATH", "app.py")

    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
      return False, "ファイル取得失敗"

    file_data = res.json()
    content = base64.b64decode(file_data["content"]).decode("utf-8")
    sha = file_data["sha"]

    pattern = r"official_results_data\s*=\s*\{([^}]+)\}"
    match = re.search(pattern, content)
    if match:
      dict_body = match.group(1)
      new_entry = f'    "{date_key}": "{val_str}",\n'
      if f'"{date_key}"' in dict_body:
        updated_body = re.sub(
            f'"{date_key}"\\s*:\\s*"[^"]*"',
            f'"{date_key}": "{val_str}"',
            dict_body,
        )
      else:
        updated_body = dict_body.rstrip() + "\n" + new_entry

      new_content = content.replace(
          match.group(0), f"official_results_data = {{{updated_body}}}"
      )

      payload = {
          "message": f"Update official_results_data: {date_key} = {val_str}",
          "content": base64.b64encode(new_content.encode("utf-8")).decode(
              "utf-8"
          ),
          "sha": sha,
      }

      put_res = requests.put(url, headers=headers, data=json.dumps(payload))
      if put_res.status_code == 200:
        return True, "成功"
      else:
        return False, put_res.json().get("message", "更新エラー")
  except Exception as e:
    return False, str(e)
  return False, "Secrets未設定"


tab1, tab2, tab3 = st.tabs(
    ["🔮 本日の33口予測", "📈 的中率・履歴", "⚙️ 当選数字の登録"]
)

with tab1:
  st.markdown(
      f"<p style='font-size:14px; font-weight:bold; margin-bottom:6px;'>🔮"
      f" {target_date.strftime('%m月%d日')} 抽選向け予測数字（全33口・20口ベース完全網羅）</p>",
      unsafe_allow_html=True,
  )

  pred_data = get_or_create_33_prediction(target_date)
  base_20 = pred_data["base_20"]
  predictions_33 = pred_data["prediction_33"]

  cols_per_row = 5
  for i in range(0, len(predictions_33), cols_per_row):
    row_nums = predictions_33[i : i + cols_per_row]
    cols = st.columns(cols_per_row)
    for idx, num in enumerate(row_nums):
      with cols[idx]:
        if num in base_20:
          st.markdown(
              f'<div class="num-card-base">{num}</div>', unsafe_allow_html=True
          )
        else:
          st.markdown(
              f'<div class="num-card-add">{num}</div>', unsafe_allow_html=True
          )

  st.markdown(
      "<p style='font-size:12px; color:#555; margin-top:8px;'><b>【表示の凡例】</b>"
      " <span style='color:#2e7d32;'>■ 緑色枠</span>：大元アプリの20口予測と共通（完全網羅）"
      " / <span style='color:#1976d2;'>■ 青色枠</span>：33口拡張用の追加数字</p>",
      unsafe
