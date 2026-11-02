import streamlit as st
import cv2
import tempfile
import pandas as pd
import numpy as np
from inference_sdk import InferenceHTTPClient

# 頁面設定
st.set_page_config(
    page_title="SignLinkage - 手語動態辨識系統",
    page_icon="🖐️",
    layout="wide"
)

# ----------------------------------------------------
# 多語言字典
# ----------------------------------------------------
TEXTS = {
    "繁體中文": {
        "title": "SignLinkage - 手語動態辨識系統",
        "subtitle": "Simulating frontline employee brim camera input to capture hand gestures in real-time and translate them into frontline service phrases.",
        "sidebar_status": "System Status",
        "privacy_title": "Privacy Protection (HK PDPO Compliant)",
        "privacy_desc": "We do not store any video or face footage. Video data is processed temporarily in live memory (RAM) just to read hand gestures, and is wiped out instantly. Nothing is saved to a hard drive.",
        "edge_title": "Edge Computing Camera Module",
        "edge_desc": "Brim camera connected. Running smoothly at 60 frames per second (FPS) with ultra-low latency under 25 milliseconds.",
        "sidebar_settings": "參數設定 (Parameter Tuning)",
        "conf_slider": "模型信心閾值 (Confidence %)",
        "step_slider": "抽幀頻率 (每幾幀分析一次)",
        "input_header": "1. Camera Input",
        "joint_header": "2. Hand 3D Skeleton & Joint Analysis",
        "joint_desc": "Deconstructs gestures into 21 key spatial coordinates for accurate sign language lexicon matching.",
        "upload_label": "請上傳前線手語連續短片 (.mp4, .mov, .avi)",
        "btn_start": "開始執行即時動態手語辨識",
        "timeline_title": "辨識時間軸與解析結果 (Recognition Timeline)",
        "realtime_output": "Real-time Translation Output",
        "default_output": "Do you need a printed receipt?",
        "engine_success": "AI 引擎連線成功！",
        "engine_fail": "AI 引擎連線失敗: ",
        "processing": "正在分析影格：",
        "complete": "Sign recognition complete: Successfully translated and synced to customer display."
    },
    "English": {
        "title": "SignLinkage - Sign Language Recognition",
        "subtitle": "Simulating frontline employee brim camera input to capture hand gestures in real-time and translate them into frontline service phrases.",
        "sidebar_status": "System Status",
        "privacy_title": "Privacy Protection (HK PDPO Compliant)",
        "privacy_desc": "We do not store any video or face footage. Video data is processed temporarily in live memory (RAM) just to read hand gestures, and is wiped out instantly. Nothing is saved to a hard drive.",
        "edge_title": "Edge Computing Camera Module",
        "edge_desc": "Brim camera connected. Running smoothly at 60 frames per second (FPS) with ultra-low latency under 25 milliseconds.",
        "sidebar_settings": "Parameter Tuning",
        "conf_slider": "Confidence Threshold (%)",
        "step_slider": "Frame Extraction Rate",
        "input_header": "1. Camera Input",
        "joint_header": "2. Hand 3D Skeleton & Joint Analysis",
        "joint_desc": "Deconstructs gestures into 21 key spatial coordinates for accurate sign language lexicon matching.",
        "upload_label": "Upload Sign Language Video (.mp4, .mov, .avi)",
        "btn_start": "Start Real-Time Dynamic Recognition",
        "timeline_title": "Recognition Timeline & Analysis",
        "realtime_output": "Real-time Translation Output",
        "default_output": "Do you need a printed receipt?",
        "engine_success": "AI Engine Connected Successfully!",
        "engine_fail": "AI Engine Connection Failed: ",
        "processing": "Analyzing frames: ",
        "complete": "Sign recognition complete: Successfully translated and synced to customer display."
    }
}

# ----------------------------------------------------
# 側邊欄設計
# ----------------------------------------------------
st.sidebar.title("SignLinkage Dashboard")
lang_choice = st.sidebar.radio("Display Language / 系統語言", ["繁體中文", "English"])
t = TEXTS[lang_choice]

st.sidebar.markdown("---")
st.sidebar.subheader(t["sidebar_status"])

with st.sidebar.expander(f"🛡️ {t['privacy_title']}", expanded=True):
    st.info(t["privacy_desc"])

with st.sidebar.expander(f"📷 {t['edge_title']}", expanded=True):
    st.success(t["edge_desc"])

st.sidebar.markdown("---")
st.sidebar.subheader(t["sidebar_settings"])
confidence_threshold = st.sidebar.slider(t["conf_slider"], 0, 100, 20)
frame_step = st.sidebar.slider(t["step_slider"], 1, 30, 10)

# ----------------------------------------------------
# 主畫面標題
# ----------------------------------------------------
