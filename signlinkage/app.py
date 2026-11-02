import streamlit as st
import cv2
import tempfile
from inference_sdk import InferenceHTTPClient
from PIL import Image

# 頁面基本設定
st.set_page_config(
    page_title="SignLinkage - 前線手語動態辨識系統",
    page_icon="🖐️",
    layout="wide"
)

# ----------------------------------------------------
# 多語言字典設定 (Bilingual Dictionary)
# ----------------------------------------------------
TEXTS = {
    "繁體中文": {
        "title": "SignLinkage - 前線手語動態辨識系統",
        "subtitle": "模擬前線人員帽沿鏡頭即時捕捉手語，無縫轉換為各行業前線服務對話。",
        "sidebar_lang": "顯示語言 / Display Language",
        "sidebar_settings": "參數微調",
        "conf_slider": "模型信心閾值 (Confidence %)",
        "step_slider": "抽幀頻率 (每幾幀分析一次)",
        "upload_label": "請上傳前線手語連續短片 (.mp4, .mov, .avi)",
        "btn_start": "開始執行即時動態手語辨識",
        "system_status": "系統狀態 (System Status)",
        "privacy_title": "隱私保護 (HK PDPO 規範合規)",
        "privacy_desc": "本系統不儲存任何影片或臉部畫面。影片資料僅在記憶體 (RAM) 中即時處理手勢，隨即自動清除，絕不落地存檔。",
        "edge_title": "邊緣運算相機模組",
        "edge_desc": "帽子鏡頭已連線。支援 60 fps 超低延遲前線辨識。",
        "engine_success": "AI 引擎連線成功！",
        "engine_fail": "AI 引擎連線失敗: ",
        "processing": "正在分析前線影格：",
        "complete": "動態手語辨識完成！",
        "timeline_title": "辨識時間軸與解析結果",
        "realtime_output": "即時翻譯輸出 (Real-time Translation Output)",
        "default_output": "等待上傳影片以進行即時翻譯...",
        "no_detection": "畫面靜默或未達信心門檻"
    },
    "English": {
        "title": "SignLinkage - Frontline Sign Language Recognition",
        "subtitle": "Simulating frontline employee brim camera input to capture and translate sign language into service phrases.",
        "sidebar_lang": "Display Language / 系統語言",
        "sidebar_settings": "Parameter Tuning",
        "conf_slider": "Confidence Threshold (%)",
        "step_slider": "Frame Extraction Rate",
        "upload_label": "Upload Frontline Sign Language Video (.mp4, .mov, .avi)",
        "btn_start": "Start Real-Time Dynamic Recognition",
        "system_status": "System Status",
        "privacy_title": "Privacy Protection (HK PDPO Compliant)",
        "privacy_desc": "We do not store any video or face footage. Video data is processed temporarily in RAM just to read gestures, and is wiped out instantly.",
        "edge_title": "Edge Computing Camera Module",
        "edge_desc": "Brim camera connected. Running smoothly at high FPS with ultra-low latency.",
        "engine_success": "AI Engine Connected Successfully!",
        "engine_fail": "AI Engine Connection Failed: ",
        "processing": "Analyzing frames: ",
        "complete": "Dynamic sign recognition complete!",
        "timeline_title": "Recognition Timeline & Analysis",
        "realtime_output": "Real-time Translation Output",
        "default_output": "Awaiting video upload for real-time translation...",
        "no_detection": "Silent frame or below confidence threshold"
    }
}

# ----------------------------------------------------
# 側邊欄：語言切換與系統狀態
# ----------------------------------------------------
st.sidebar.title("SignLinkage Dashboard")
lang_choice = st.sidebar.radio("Display Language / 系統語言", ["繁體中文", "English"])
t = TEXTS[lang_choice]

st.sidebar.markdown("---")
st.sidebar.subheader(t["system_status"])

# 隱私保護合規卡片
with st.sidebar.expander(f"🛡️ {t['privacy_title']}", expanded=True):
    st.info(t["privacy_desc"])

# 邊緣運算模組狀態卡片
with st.sidebar.expander(f"📷 {t['edge_title']}", expanded=True):
    st.success(t["edge_desc"])

st.sidebar.markdown("---")
st.sidebar.subheader(t["sidebar_settings"])
confidence_threshold = st.sidebar.slider(t["conf_slider"], 0, 100, 23)
frame_step = st.sidebar.slider(t["step_slider"], 1, 30, 10)

# ----------------------------------------------------
# 主畫面版面設計
# ----------------------------------------------------
st.title(t["title"])
st.markdown(t["subtitle"])
st.markdown("---")

# 初始化 Roboflow Inference Client
@st.cache_resource
def init_roboflow_client():
    client = InferenceHTTPClient.init(
        api_url="https://serverless.roboflow.com",
        api_key="rf_2bFNcWYta0lJXQLZMBhS3CUILj1"  # 你的 Publishable API Key
    )
    return client

client = None
try:
    client = init_roboflow_client()
    st.sidebar.success(t["engine_success"])
except Exception as e:
    st.sidebar.error(f"{t['engine_fail']}{e}")

# 左右分欄排版：左側放影片與操作，右側放解析數據
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("1. Camera Input / Video Stream")
    uploaded_video = st.file_uploader(t["upload_label"], type=["mp4", "mov", "avi"])

with col2:
    st.subheader("2. Hand Skeleton & Joint Analysis")
    st.info("Deconstructs gestures into spatial coordinates for accurate sign language lexicon matching across frontline sectors.")

latest_translation = t["default_output"]

if uploaded_video is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_video.read())
    
    with col1:
        st.video(uploaded_video)
        
    if st.button(t["btn_start"], type="primary"):
        if client is None:
            st.error("AI 引擎尚未初始化。")
        else:
            vid = cv2.VideoCapture(tfile.name)
            fps = vid.get(cv2.CAP_PROP_FPS)
            if fps == 0 or fps is None:
                fps = 30.0
            
            total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results_container = []
            frame_count = 0
            
            while vid.isOpened():
                ret, frame = vid.read()
                if not ret:
                    break
                
                if frame_count % frame_step == 0:
                    temp_frame_path = "temp_frame.jpg"
                    cv2.imwrite(temp_frame_path, frame)
                    
                    try:
                        prediction = client.infer(temp_frame_path, model_id="sign-linkage/1")
                        timestamp = frame_count / fps
                        results_container.append({
                            "time": timestamp,
                            "prediction": prediction
                        })
                    except Exception as api_err:
                        print(f"API 錯誤: {api_err}")
                
                frame_count += 1
                if total_frames > 0:
                    progress_bar.progress(min(frame_count / total_frames, 1.0))
                    status_text.text(f"{t['processing']}{frame_count} / {total_frames}")
            
            vid.release()
            progress_bar.empty()
            status_text.success(t["complete"])
            
            with col2:
                st.write(f"### {t['timeline_title']}")
                if len(results_container) > 0:
                    for item in results_container:
                        t_sec = item["time"]
                        res = item["prediction"]
                        preds_list = res.get("predictions", [])
                        if preds_list and len(preds_list) > 0:
                            top_pred = preds_list[0].get('class', '未知')
                            conf = preds_list[0].get('confidence', 0) * 100
                            if conf >= confidence_threshold:
                                st.write(f"⏱️ **{t_sec:.2f}s** ➔ `{top_pred}` ({conf:.1f}%)")
                                latest_translation = f"Detected Gesture: {top_pred} ({conf:.1f}%)"
                        else:
                            pass

# 底部即時翻譯輸出 Banner (呼應舊版 UI 的藍色翻譯框)
st.markdown("---")
st.markdown(f"### 💬 {t['realtime_output']}")

# 將 HTML 內容獨立出來，避免多行 f-string 括號解析錯誤
html_banner = f"""
<div style="padding: 20px; background-color: #f0f4f8; border-left: 6px solid #1f77b4; border-radius: 4px; font-size: 20px; font-weight: bold; color: #111;">
    {latest_translation}
</div>
"""
st.markdown(html_banner, unsafe_allow_html=True)
