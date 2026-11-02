import streamlit as st
import pandas as pd
import numpy as np

# 頁面基本設定 (使用 wide 版面完美呈現左右雙欄)
st.set_page_config(
    page_title="SignLinkage - 手語動態辨識系統",
    page_icon="🖐️",
    layout="wide"
)

# ----------------------------------------------------
# 多語言字典設定 (Bilingual Dictionary)
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
        "upload_label": "Upload Sign Language Video (.mp4, .mov, .avi)",
        "btn_start": "Start Real-Time Dynamic Recognition",
        "timeline_title": "Recognition Timeline & Analysis",
        "realtime_output": "Real-time Translation Output",
        "complete": "Sign recognition complete: Successfully translated and synced to customer display."
    }
}

# ----------------------------------------------------
# 側邊欄設計 (最新 UI)
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

# 左右雙欄配置
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(t["input_header"])
    uploaded_video = st.file_uploader(t["upload_label"], type=["mp4", "mov", "avi"])

with col2:
    st.subheader(t["joint_header"])
    st.caption(t["joint_desc"])
    
    # 產生 21 個手部關節模擬數據與散佈圖
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
    st.scatter_chart(skeleton_df, x="X-Axis (Horizontal)", y="Y-Axis (Vertical)", height=180)

# ----------------------------------------------------
# 智慧檔案名稱解析與句子生成邏輯
# ----------------------------------------------------
translated_text = "Do you need a printed receipt? / 請問需要列印收據嗎？"
timeline_items = [
    ("0.5s", "動作解析: 準備手勢", 95.0),
    ("1.2s", "特徵比對: 前線詞彙庫", 96.8),
    ("2.0s", "語意合成: 系統同步完成", 98.5)
]

if uploaded_video is not None:
    with col1:
        st.video(uploaded_video)
    
    filename = uploaded_video.name.lower()
    
    # 根據上載檔案名稱智慧生成對應語句
    if "收據" in filename or "receipt" in filename:
        translated_text = "Do you need a printed receipt? / 請問需要列印收據嗎？"
        timeline_items = [
            ("0.4s", "動作解析: 遞交/Request", 97.2),
            ("1.1s", "詞彙辨識: 收據/Receipt", 98.9),
            ("2.2s", "語意合成: 列印交易憑證", 99.1)
        ]
    elif "會員" in filename or "member" in filename:
        translated_text = "Would you like to join our membership? / 請問要加入會員嗎？"
        timeline_items = [
            ("0.5s", "動作解析: 登記/Register", 96.1),
            ("1.3s", "詞彙辨識: 會員/Member", 98.4),
            ("2.5s", "語意合成: 建立會員檔案", 99.0)
        ]
    elif "找錢" in filename or "change" in filename:
        translated_text = "Here is your change. Thank you! / 這是您的找贖，謝謝！"
        timeline_items = [
            ("0.6s", "動作解析: 金額/Amount", 95.8),
            ("1.5s", "詞彙辨識: 找錢/Change", 97.6),
            ("2.8s", "語意合成: 完成交易對話", 98.8)
        ]
    else:
        # 通用預設動態生成
        translated_text = f"Frontline Service Translation ({uploaded_video.name}): Welcome, how may I assist you?"
        timeline_items = [
            ("0.5s", f"檔案特徵萃取: {uploaded_video.name}", 96.0),
            ("1.4s", "動態影格比對完成", 97.5),
            ("2.3s", "語意同步至前線客戶顯示器", 99.2)
        ]

    if st.button(t["btn_start"], type="primary"):
        st.success(t["complete"])

# 右側即時時間軸呈現
with col2:
    st.markdown(f"### ⏱️ {t['timeline_title']}")
    for t_sec, desc, conf in timeline_items:
        st.write(f"⏱️ **{t_sec}** ➔ `{desc}` (信心指數: {conf}%)")

# ----------------------------------------------------
# 底部即時翻譯輸出 Banner (完全還原原版設計)
# ----------------------------------------------------
st.markdown("---")
html_banner = f"""
<div style="background-color: #e8f4f8; border: 1px solid #bce8f1; border-radius: 6px; padding: 15px; margin-top: 10px;">
    <div style="color: #31708f; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Real-time Translation Output</div>
    <div style="color: #004085; font-size: 22px; font-weight: bold;">{translated_text}</div>
</div>
"""
st.markdown(html_banner, unsafe_allow_html=True)
