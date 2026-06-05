import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

st.set_page_config(page_title="參加證明生成系統", layout="wide")

# 設定中文字型路徑 (請確保資料夾內有此字型檔，否則中文會變方塊)
FONT_PATH = "NotoSansTC-Regular.ttf"  # 請替換為您實際的字型檔案名稱，如 'msjh.ttc'

def generate_cert(bg_image, course_name, student_name, date_str, hours_str):
    """
    根據背景圖片與輸入資訊生成單張參加證明
    """
    # 複製圖片以免改動到原始背景
    img = bg_image.copy()
    draw = ImageDraw.Draw(img)
    
    try:
        # 設定不同大小的字型 (若無字型檔會報錯，請務必提供)
        font_large = ImageFont.truetype(FONT_PATH, 60)
        font_medium = ImageFont.truetype(FONT_PATH, 48)
        font_small = ImageFont.truetype(FONT_PATH, 36)
    except IOError:
        st.error(f"找不到字型檔 {FONT_PATH}，請確認檔案是否存在！")
        return img

    # 取得圖片寬高以利置中計算
    W, H = img.size

    # --- 文字寫入座標設定 (可依據實際背板微調) ---
    # 課程名稱
    course_text = f"課程名稱：{course_name}"
    _, _, w, h = draw.textbbox((0, 0), course_text, font=font_medium)
    draw.text(((W-w)/2, H*0.35), course_text, font=font_medium, fill=(80, 40, 20))

    # 茲證明
    certify_text = "茲證明"
    _, _, w, h = draw.textbbox((0, 0), certify_text, font=font_small)
    draw.text(((W-w)/2, H*0.43), certify_text, font=font_small, fill=(0, 0, 0))

    # 學員姓名
    _, _, w, h = draw.textbbox((0, 0), student_name, font=font_large)
    draw.text(((W-w)/2, H*0.48), student_name, font=font_large, fill=(80, 20, 20))

    # 先生/女士
    title_text = "先生/女士"
    _, _, w, h = draw.textbbox((0, 0), title_text, font=font_small)
    draw.text(((W-w)/2, H*0.56), title_text, font=font_small, fill=(0, 0, 0))

    # 參加說明
    desc_text = "參加上述課程並完成學習，特發此證以資證明。"
    _, _, w, h = draw.textbbox((0, 0), desc_text, font=font_medium)
    draw.text(((W-w)/2, H*0.62), desc_text, font=font_medium, fill=(0, 0, 0))

    # 日期與時數
    date_display = f"上課日期：{date_str}"
    hours_display = f"修習時數：{hours_str}"
    _, _, w1, h1 = draw.textbbox((0, 0), date_display, font=font_medium)
    _, _, w2, h2 = draw.textbbox((0, 0), hours_display, font=font_medium)
    
    draw.text(((W-w1)/2, H*0.72), date_display, font=font_medium, fill=(50, 50, 50))
    draw.text(((W-w2)/2, H*0.78), hours_display, font=font_medium, fill=(50, 50, 50))

    return img

st.title("🎓 參加證明批次生成系統")

# --- 側邊欄：背板設定 ---
st.sidebar.header("🖼️ 背景圖片設定")
bg_option = st.sidebar.radio("選擇背板來源", ["預設背板 1", "預設背板 2", "預設背板 3", "自行上傳背板"])

# 處理背板圖片載入
bg_image = None
if bg_option == "自行上傳背板":
    uploaded_bg = st.sidebar.file_uploader("上傳背板圖片 (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if uploaded_bg:
        bg_image = Image.open(uploaded_bg)
else:
    # 這裡假設您有 bg1.png, bg2.png, bg3.png 在目錄中
    bg_dict = {"預設背板 1": "bg1.png", "預設背板 2": "bg2.png", "預設背板 3": "bg3.png"}
    bg_path = bg_dict[bg_option]
    if os.path.exists(bg_path):
        bg_image = Image.open(bg_path)
    else:
        st.sidebar.warning(f"找不到預設圖片 {bg_path}，請上傳或補齊檔案。")

# --- 主畫面：功能分頁 ---
tab1, tab2 = st.tabs(["📄 單張生成", "📑 Excel 批次生成"])

# -- 分頁 1：單張生成 --
with tab1:
    st.subheader("個別學員證明生成")
    col1, col2 = st.columns(2)
    
    with col1:
        default_course = "iPAS 初級AI應用規劃師 重點培訓班"
        course = st.text_input("課程名稱", value=default_course)
        name = st.text_input("學員姓名", value="陳思愷")
        date_val = st.text_input("上課日期", value="7/6~7/16")
        hours_val = st.text_input("修習時數", value="共8小時")
    
    if st.button("預覽並生成單張證明", type="primary"):
        if bg_image is None:
            st.error("請先在左側設定有效的背板圖片！")
        else:
            result_img = generate_cert(bg_image, course, name, date_val, hours_val)
            st.image(result_img, caption=f"{name} 的參加證明", use_container_width=True)
            
            # 提供下載
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label="下載圖片",
                data=byte_im,
                file_name=f"{name}_參加證明.png",
                mime="image/png"
            )

# -- 分頁 2：批次生成 --
with tab2:
    st.subheader("批次生成 (上傳 Excel)")
    st.markdown("請上傳包含 `姓名` 欄位的 Excel 檔案。若有 `課程名稱`、`上課日期`、`修習時數` 欄位，系統將自動讀取；若無，則使用下方設定的統一數值。")
    
    col3, col4 = st.columns(2)
    with col3:
        batch_course = st.text_input("統一課程名稱 (若Excel無該欄位)", value="iPAS 初級AI應用規劃師 重點培訓班")
        batch_date = st.text_input("統一上課日期 (若Excel無該欄位)", value="7/6~7/16")
    with col4:
        batch_hours = st.text_input("統一修習時數 (若Excel無該欄位)", value="共8小時")

    uploaded_excel = st.file_uploader("上傳學員名單 Excel", type=["xlsx", "xls"])

    if uploaded_excel and bg_image:
        df = pd.read_excel(uploaded_excel)
        st.write("預覽資料：", df.head())
        
        if '姓名' not in df.columns:
            st.error("Excel 檔案中找不到「姓名」欄位，請檢查檔案格式！")
        else:
            if st.button("開始批次生成並打包下載"):
                # 建立 ZIP 暫存
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    progress_bar = st.progress(0)
                    total = len(df)
                    
                    for index, row in df.iterrows():
                        # 動態讀取欄位，若無則用預設值
                        s_name = str(row['姓名'])
                        s_course = str(row['課程名稱']) if '課程名稱' in df.columns else batch_course
                        s_date = str(row['上課日期']) if '上課日期' in df.columns else batch_date
                        s_hours = str(row['修習時數']) if '修習時數' in df.columns else batch_hours
                        
                        cert_img = generate_cert(bg_image, s_course, s_name, s_date, s_hours)
                        
                        # 將圖片存入 zip
                        img_byte_arr = io.BytesIO()
                        cert_img.save(img_byte_arr, format='PNG')
                        zip_file.writestr(f"{s_name}_參加證明.png", img_byte_arr.getvalue())
                        
                        # 更新進度條
                        progress_bar.progress((index + 1) / total)
                
                st.success("✅ 批次生成完成！請點擊下方按鈕下載壓縮檔。")
                st.download_button(
                    label="📦 下載全部證明 (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="certificates.zip",
                    mime="application/zip"
                )
    elif uploaded_excel and bg_image is None:
        st.warning("請先在左側設定背板圖片才能進行批次生成。")
