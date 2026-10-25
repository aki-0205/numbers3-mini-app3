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
    return len(num) == 2 and num
