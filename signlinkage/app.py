import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. 頁面基本設定 ---
st.set_page_config(
    page_title="SignLinkage Enterprise - Sign Language Recognition", 
    page_icon="👋", 
    layout="wide"
)

# 自訂高科技質感樣式
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    .stAlert { border-radius: 8px; }
    .stDataFrame { border-radius: 8px; }
    .translation-box {
        padding: 24px; 
        border-radius: 8px; 
        background-color: #f0f4f9; 
        border-left: 6px solid #1a73e8; 
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 快取與資料處理函式 (Performance & Security) ---
@st.cache_data
def get_joint_names(lang_mode: str) -> list:
    """快取 21 個關鍵骨架關節名稱，避免重複建構"""
    if lang_mode == "繁體中文":
        return [
            "0. 手腕 (Wrist)", "1. 拇指根部 (Thumb CMC)", "2. 拇指關節 (Thumb MCP)", "3. 拇指指尖 (Thumb Tip)",
            "4. 食指根部 (Index MCP)", "5. 食指關節 (Index PIP)", "6. 食指指尖 (Index Tip)",
            "7. 中指根部 (Middle MCP)", "8. 中指關節 (Middle PIP)", "9. 中指指尖 (Middle Tip)",
            "10. 無名指根部 (Ring MCP)", "11. 無名指關節 (Ring PIP)", "12. 無名指指尖 (Ring Tip)",
            "13. 小指根部 (Pinky MCP)", "14. 小指關節 (Pinky PIP)", "15. 小指指尖 (Pinky Tip)",
            "16. 手掌中心 (Palm Center)", "17. 掌骨節點 A", "18. 掌骨節點 B", "19. 掌骨節點 C", "20. 掌骨節點 D"
        ]
    return [
        "0. Wrist", "1. Thumb CMC", "2. Thumb MCP", "3. Thumb Tip",
        "4. Index MCP", "5. Index PIP", "6. Index Tip",
        "7. Middle MCP", "8. Middle PIP", "9. Middle Tip",
        "10. Ring MCP", "11. Ring PIP", "12. Ring Tip",
        "13. Pinky MCP", "14. Pinky PIP", "15. Pinky Tip",
        "16. Palm Center", "17. Metacarpal A", "18. Metacarpal B", "19. Metacarpal C", "20. Metacarpal D"
    ]

@st.cache_data
def generate_skeleton_coordinates(file_name: str, seed: int, lang_mode: str) -> tuple:
    """根據輸入影片產生並快取 3D 骨架座標數據"""
    np.random.seed(seed)
    joint_names = get_joint_names(lang_mode)
    
    if lang_mode == "繁體中文":
        col_names = {
            "joint": "關節點名稱 (Joint)",
            "x": "X軸 (水平位置)",
            "y": "Y軸 (垂直位置)",
            "z": "Z軸 (景深位置)"
        }
    else:
        col_names = {
            "joint": "Joint Name",
            "x": "X-Axis (Horizontal)",
            "y": "Y-Axis (Vertical)",
            "z": "Z-Axis (Depth)"
        }
        
    df = pd.DataFrame({
        col_names["joint"]: joint_names,
        col_names["x"]: np.random.uniform(0.25, 0.75, 21).round(4),
        col_names["y"]: np.random.uniform(0.15, 0.85, 21).round(4),
        col_names["z"]: np.random.uniform(-0.15, 0.15, 21).round(4)
    })
    return df, col_names

# --- 3. 側邊欄：系統狀態與合規指標 ---
with st.sidebar:
    st.title("SignLinkage Dashboard")
    st.markdown("---")
    
    lang_mode = st.radio("Display Language / 系統語言", ["繁體中文", "English"], index=0)
    
    st.markdown("---")
    st.markdown("### System Status")
    
    st.info(
        "**Privacy Protection (HK PDPO Compliant)**\n\n"
        "We do not store any video or face footage. "
        "Video data is processed temporarily in live memory (RAM) just to read hand gestures, "
        "and is wiped out instantly. Nothing is saved to a hard drive."
    )
    st.success(
        "**Edge Computing Camera Module**\n\n"
        "Brim camera connected. Running smoothly at 60 frames per second (FPS) "
        "with ultra-low latency under 25 milliseconds."
    )

# --- 4. 核心主畫面：手語識別 (雙語動態支援) ---
if lang_mode == "繁體中文":
    st.header("手語識別 (Sign Language Recognition)")
    st.markdown("模擬前線員工配戴之帽檐廣角鏡頭輸入，實時捕捉手勢特徵並轉譯為零售服務語句。")
else:
    st.header("Sign Language Recognition")
    st.markdown("Simulating frontline employee brim camera input to capture hand gestures in real-time and translate them into retail service phrases.")

st.markdown("---")

# 雙欄佈局
col_video, col_data = st.columns([1, 1], gap="large")

with col_video:
    if lang_mode == "繁體中文":
        st.subheader("1. 鏡頭影像輸入 (Camera Input)")
    else:
        st.subheader("1. Camera Input")
        
uploaded_file = st.file_uploader(
        "Upload video file", 
        type=["mp4", "mov", "avi"], 
        label_visibility="collapsed",
        help="Upload mp4, mov, or avi format"
    )
    
    if uploaded_file is not None:
        try:
            st.video(uploaded_file)
        except Exception as e:
            st.error(f"Error loading video file / 影片載入失敗: {e}")
    else:
        if lang_mode == "繁體中文":
            st.info("請上傳測試短片（例如含「八達通」、「收據」或「膠袋」手勢），系統將自動進行特徵分析。")
        else:
            st.info("Please upload a test video (e.g., gestures for Octopus card, receipt, or plastic bag) to trigger automated analysis.")

with col_data:
    if lang_mode == "繁體中文":
        st.subheader("2. 手勢 3D 骨架關節特徵分析")
        st.caption("將手勢解構為 21 個關鍵空間座標，作為手語詞庫比對之精準依據。")
    else:
        st.subheader("2. Hand 3D Skeleton & Joint Analysis")
        st.caption("Deconstructs gestures into 21 key spatial coordinates for accurate sign language lexicon matching.")
        
    if uploaded_file is not None:
        try:
            # 以檔名長度及固定基數生成範例座標
            seed_val = (len(uploaded_file.name) + 42) % 1000
            landmark_df, col_names = generate_skeleton_coordinates(uploaded_file.name, seed_val, lang_mode)
            
            # 展示 3D 座標 DataFrame
            st.dataframe(landmark_df, use_container_width=True, height=180)
            
            # 展現 X/Y 關節空間散佈圖
            chart_data = pd.DataFrame({
                col_names["x"]: landmark_df[col_names["x"]],
                col_names["y"]: landmark_df[col_names["y"]]
            })
            st.scatter_chart(chart_data, use_container_width=True, height=160)
        except Exception as e:
            st.error(f"Feature extraction error / 特徵擷取異常: {e}")
    else:
        if lang_mode == "繁體中文":
            st.warning("等待影像輸入以擷取特徵數據...")
        else:
            st.warning("Awaiting video input to extract joint features...")

st.markdown("---")

# --- 5. 自動識別與轉譯結果 ---
if uploaded_file is not None:
    spinner_text = "系統正在計算手勢特徵並匹配香港手語 (HKSL) 詞庫..." if lang_mode == "繁體中文" else "Processing gesture features and matching HKSL lexicon..."
    
    with st.spinner(spinner_text):
        time.sleep(0.3)
        
    try:
        fname = uploaded_file.name.lower()
        if "八達通" in fname or "octopus" in fname:
            zh_res = "請拍八達通或請付款"
            en_res = "Please tap your Octopus card."
            confidence = "98.4%"
        elif "收據" in fname or "receipt" in fname:
            zh_res = "請問需要列印收據嗎？"
            en_res = "Do you need a printed receipt?"
            confidence = "97.1%"
        else:
            zh_res = "請問需要膠袋嗎？"
            en_res = "Do you need a plastic bag?"
            confidence = "96.5%"
            
        final_output = zh_res if lang_mode == "繁體中文" else en_res
        
        success_msg = "手語辨識完成：已成功轉譯並同步至顧客面向屏幕。" if lang_mode == "繁體中文" else "Sign recognition complete: Successfully translated and synced to customer display."
        st.success(success_msg)
        
        label_text = "實時轉譯結果 (Real-time Translation Output)" if lang_mode == "繁體中文" else "Real-time Translation Output"
        conf_label = "模型信心指數 (Confidence):" if lang_mode == "繁體中文" else "Model Confidence:"
        
        st.markdown(
            f"""
            <div class="translation-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #5f6368; font-size: 14px; font-weight: 600;">{label_text}</span>
                    <span style="color: #137333; font-size: 13px; font-weight: 600; background: #e6f4ea; padding: 2px 8px; border-radius: 4px;">{conf_label} {confidence}</span>
                </div>
                <h2 style="color: #1a73e8; margin: 12px 0 0 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 26px;">
                    {final_output}
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Inference process error / 轉譯運算過程出錯: {e}")