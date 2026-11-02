import streamlit as st
import cv2
import tempfile
from inference_sdk import InferenceHTTPClient
from PIL import Image

# 頁面基本設定
st.set_page_config(
    page_title="SignLinkage - 香港手語即時翻譯原型",
    page_icon="🖐️",
    layout="centered"
)

st.title("SignLinkage - 前線零售手語動態辨識原型")
st.markdown("支援連續手語影片上傳與 AI 特徵解析，實現無縫零售服務溝通。")

# 初始化 Roboflow Inference Client (使用 @st.cache_resource 快取連線)
@st.cache_resource
def init_roboflow_client():
    client = InferenceHTTPClient.init(
        api_url="https://serverless.roboflow.com",
        api_key="rf_2bFNcWYta0lJXQLZMBhS3CUILj1"  # 你的 Publishable API Key
    )
    return client

# 建立客戶端連線並加入例外防護
client = None
try:
    client = init_roboflow_client()
    st.sidebar.success("AI 引擎連線成功！")
except Exception as e:
    st.sidebar.error(f"AI 引擎連線失敗: {e}")

# 側邊欄參數調整
st.sidebar.header("參數微調")
confidence_threshold = st.sidebar.slider("模型信心閾值 (Confidence %)", 0, 100, 23)
frame_step = st.sidebar.slider("抽幀頻率 (每幾幀分析一次)", 1, 30, 10)

# 檔案上傳介面 (支援連續短片格式)
uploaded_video = st.file_uploader("請上傳手語連續短片 (.mp4, .mov, .avi)", type=["mp4", "mov", "avi"])

if uploaded_video is not None:
    # 建立暫存檔供 OpenCV 讀取 (符合 RAM 與短暫處理合規原則)
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_video.read())
    
    # 在網頁上顯示上傳的影片
    st.video(uploaded_video)
    
    if st.button("開始執行動態手語辨識", type="primary"):
        if client is None:
            st.error("AI 引擎尚未初始化，無法進行預測。")
        else:
            vid = cv2.VideoCapture(tfile.name)
            fps = vid.get(cv2.CAP_PROP_FPS)
            if fps == 0 or fps is None:
                fps = 30.0  # 預設防呆數值
            
            total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results_container = []
            frame_count = 0
            
            # 迴圈讀取影片影格
            while vid.isOpened():
                ret, frame = vid.read()
                if not ret:
                    break
                
                # 依據抽幀頻率取樣，減少 API 負載並確保流暢
                if frame_count % frame_step == 0:
                    temp_frame_path = "temp_frame.jpg"
                    cv2.imwrite(temp_frame_path, frame)
                    
                    try:
                        # 呼叫 Inference SDK 進行預測 (model_id 請帶入你的專案名稱與版本號，例如 sign-linkage/1)
                        prediction = client.infer(temp_frame_path, model_id="sign-linkage/1")
                        
                        timestamp = frame_count / fps
                        results_container.append({
                            "time": timestamp,
                            "prediction": prediction
                        })
                    except Exception as api_err:
                        print(f"API 呼叫錯誤: {api_err}")
                
                frame_count += 1
                if total_frames > 0:
                    progress_bar.progress(min(frame_count / total_frames, 1.0))
                    status_text.text(f"正在分析影片影格：{frame_count} / {total_frames}")
            
            vid.release()
            progress_bar.empty()
            status_text.success("動態手語辨識完成！")
            
            # 呈現時間軸分析結果
            st.subheader("辨識時間軸結果")
            if len(results_container) > 0:
                for item in results_container:
                    t = item["time"]
                    res = item["prediction"]
                    
                    # 根據 inference-sdk 的回傳結構解析預測結果
                    predictions_list = res.get("predictions", [])
                    if predictions_list and len(predictions_list) > 0:
                        top_pred = predictions_list[0].get('class', '未知')
                        conf = predictions_list[0].get('confidence', 0) * 100
                        
                        # 過濾低於信心門檻的結果
                        if conf >= confidence_threshold:
                            st.write(f"⏱️ **{t:.2f} 秒** ➔ 辨識結果：`{top_pred}` (信心指數: {conf:.1f}%)")
                        else:
                            st.write(f"⏱️ **{t:.2f} 秒** ➔ 偵測中（低於信心門檻 {confidence_threshold}%）")
                    else:
                        st.write(f"⏱️ **{t:.2f} 秒** ➔ 畫面靜默或未達標")
            else:
                st.warning("未能在影片中偵測到有效手勢，請嘗試調低側邊欄的信心閾值。")
