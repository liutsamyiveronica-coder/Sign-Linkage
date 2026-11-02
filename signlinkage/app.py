import streamlit as st
import pandas as pd
import numpy as np
import time

# 頁面基本設定
st.set_page_config(
    page_title="SignLinkage - 手語動態辨識系統",
    page_icon="🖐️",
    layout="wide"
)

# ----------------------------------------------------
# 多語言字典設定 (Bilingual Dictionary - 確保 Key 完整對應)
# ----------------------------------------------------
TEXTS = {
    "繁體中文": {
        "title": "SignLinkage - 手語動態辨識系統",
        "subtitle": "模擬前線人員帽沿鏡頭即時捕捉手語，無縫轉換為前線服務對話。",
        "sidebar_status": "系統狀態",
        "privacy_title": "隱私保護 (HK PDPO 規範合規)",
        "privacy_desc": "本系統不儲存任何影片或臉部畫面。影片資料僅在記憶體 (RAM) 中即時處理手勢，隨即自動清除，絕不落地存檔。",
        "edge_title": "邊緣運算相機模組",
        "edge_desc": "帽子鏡頭已連線。支援 60 fps 超低延遲前線辨識。",
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
        "complete": "Sign recognition complete: Successfully translated and synced to customer display.",
        "waiting": "請上傳影片並點擊「開始執行即時動態手語辨識」以啟動 AI 模型分析。"
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
        "complete": "Sign recognition complete: Successfully translated and synced to customer display.",
        "waiting": "Please upload a video and click start recognition to activate AI analysis."
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
st.title(t["title"])
st.caption(t["subtitle"])
st.markdown("---")

# 使用 Streamlit Session State 記錄是否已執行辨識
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

# 左右雙欄配置
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(t["input_header"])
    uploaded_video = st.file_uploader(t["upload_label"], type=["mp4", "mov", "avi"])
    
    if uploaded_video is not None:
        st.video(uploaded_video)
        # 當上傳新影片時重置分析狀態
        if st.button(t["btn_start"], type="primary"):
            with st.spinner("AI 正在解析動態手語與座標..."):
                time.sleep(1.2)  # 模擬流暢的 AI 運算過場
            st.session_state['analyzed'] = True
            st.success(t["complete"])
    else:
        st.session_state['analyzed'] = False

with col2:
    st.subheader(t["joint_header"])
    
    if st.session_state['analyzed'] and uploaded_video is not None:
        st.caption(t["joint_desc"])
        
        # 產生 21 個手部關節模擬數據
        joints = [
            "0. Wrist", "1. Thumb CMC", "2. Thumb MCP", "3. Thumb Tip",
            "4. Index MCP", "5. Index PIP", "6. Index DIP", "7. Index Tip",
            "8. Middle MCP", "9. Middle PIP", "10. Middle DIP", "11. Middle Tip",
            "12. Ring MCP", "13. Ring PIP", "14. Ring DIP", "15. Ring Tip",
            "16. Pinky MCP", "17. Pinky PIP", "18. Pinky DIP", "19. Pinky Tip", "20. Palm Center"
        ]
        np.random.seed(42)
        skeleton_df = pd.DataFrame({
            "Joint Name": joints,
            "X-Axis (Horizontal)": np.round(np.random.uniform(0.2, 0.8, 21), 4),
            "Y-Axis (Vertical)": np.round(np.random.uniform(0.2, 0.8, 21), 4),
            "Z-Axis (Depth)": np.round(np.random.uniform(-0.05, 0.15, 21), 4)
        })
        st.dataframe(skeleton_df.head(5), use_container_width=True)
        st.scatter_chart(skeleton_df, x="X-Axis (Horizontal)", y="Y-Axis (Vertical)", height=160)
    else:
        st.info(t["waiting"])

# ----------------------------------------------------
# 辨識後才顯示的「會動的橫向 Timeline」與翻譯 Output
# ----------------------------------------------------
if st.session_state['analyzed'] and uploaded_video is not None:
    filename = uploaded_video.name.lower()
    
    # 根據檔名決定生成內容
    if "收據" in filename or "receipt" in filename:
        translated_text = "Do you need a printed receipt? / 請問需要列印收據嗎？"
        steps = [
            ("0.5s", "動作解析: 準備手勢", "95.0%"),
            ("1.2s", "特徵比對: 收據/Receipt", "96.8%"),
            ("2.0s", "語意合成: 系統同步完成", "98.5%")
        ]
    elif "會員" in filename or "member" in filename:
        translated_text = "Would you like to join our membership? / 請問要加入會員嗎？"
        steps = [
            ("0.4s", "動作解析: 登記手勢", "96.2%"),
            ("1.1s", "特徵比對: 會員/Member", "97.5%"),
            ("2.2s", "語意合成: 建立檔案", "99.1%")
        ]
    else:
        translated_text = f"Frontline Translation ({uploaded_video.name}): Welcome, how may I assist you?"
        steps = [
            ("0.5s", "動作解析: 準備手勢", "95.0%"),
            ("1.2s", "特徵比對: 前線詞彙庫", "96.8%"),
            ("2.0s", "語意合成: 系統同步完成", "98.5%")
        ]

    st.markdown("---")
    st.markdown(f"### ⏱️ {t['timeline_title']}")

    # 精美且會動的橫向 Timeline CSS 效果
    timeline_html = f"""
    <style>
    @keyframes pulse-glow {{
        0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(31, 119, 180, 0.4); }}
        70% {{ transform: scale(1.05); box-shadow: 0 0 0 10px rgba(31, 119, 180, 0); }}
        100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(31, 119, 180, 0); }}
    }}
    .timeline-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 25px 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-top: 10px;
        margin-bottom: 20px;
    }}
    .timeline-step {{
        text-align: center;
        flex: 1;
        position: relative;
    }}
    .timeline-badge {{
        background: #1f77b4;
        color: white;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        font-weight: bold;
        font-size: 14px;
        animation: pulse-glow 2s infinite;
    }}
    .timeline-time {{
        font-size: 15px;
        font-weight: bold;
        color: #2c3e50;
    }}
    .timeline-desc {{
        font-size: 13px;
        color: #495057;
        margin-top: 4px;
    }}
    .timeline-conf {{
        font-size: 12px;
        color: #28a745;
        font-weight: bold;
        margin-top: 2px;
    }}
    </style>

    <div class="timeline-container">
        <div class="timeline-step">
            <div class="timeline-badge">1</div>
            <div class="timeline-time">{steps[0][0]}</div>
            <div class="timeline-desc">{steps[0][1]}</div>
            <div class="timeline-conf">信心指數: {steps[0][2]}</div>
        </div>
        <div style="flex-grow: 1; height: 3px; background: #1f77b4; margin: 0 10px; margin-bottom: 30px;"></div>
        <div class="timeline-step">
            <div class="timeline-badge">2</div>
            <div class="timeline-time">{steps[1][0]}</div>
            <div class="timeline-desc">{steps[1][1]}</div>
            <div class="timeline-conf">信心指數: {steps[1][2]}</div>
        </div>
        <div style="flex-grow: 1; height: 3px; background: #1f77b4; margin: 0 10px; margin-bottom: 30px;"></div>
        <div class="timeline-step">
            <div class="timeline-badge">3</div>
            <div class="timeline-time">{steps[2][0]}</div>
            <div class="timeline-desc">{steps[2][1]}</div>
            <div class="timeline-conf">信心指數: {steps[2][2]}</div>
        </div>
    </div>
    """
    st.markdown(timeline_html, unsafe_allow_html=True)

    # 底部藍色高質感即時翻譯輸出 Banner
    html_banner = f"""
    <div style="background-color: #e8f4f8; border: 1px solid #bce8f1; border-radius: 8px; padding: 20px; margin-top: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
        <div style="color: #31708f; font-size: 14px; font-weight: bold; margin-bottom: 6px;">Real-time Translation Output</div>
        <div style="color: #004085; font-size: 24px; font-weight: bold;">{translated_text}</div>
    </div>
    """
    st.markdown(html_banner, unsafe_allow_html=True)
