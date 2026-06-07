import streamlit as st
import pandas as pd
import pathlib
from pyvis.network import Network
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าเว็บกว้าง (Wide mode) - ต้องอยู่บรรทัดบนสุดเสมอ
st.set_page_config(layout="wide", page_title="DADS7201 Homework")

# 🎨 ปรับแต่ง CSS สำหรับป้ายกำกับชื่อหุ้น (Tags)
st.markdown("""
    <style>
    span[data-baseweb="tag"] {
        font-size: 12px !important;
        background-color: #f1f5f9 !important;
        color: #334155 !important;
        border: 1px solid #e2e8f0 !important;
        padding: 2px 6px !important;
        margin: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันโหลดข้อมูลอัตโนมัติ
@st.cache_data
def load_data():
    current_dir = pathlib.Path(__file__).parent
    found_files = list(current_dir.rglob('SET50_top5_shareholders.csv'))
    if len(found_files) == 0:
        raise FileNotFoundError("❌ หาไฟล์ไม่พบ กรุณาตรวจสอบว่าชื่อไฟล์ถูกต้อง")
    return pd.read_csv(found_files[0])

# ==========================================
# 📌 เมนูด้านซ้าย (Sidebar Menu)
# ==========================================
st.sidebar.header("📁 เมนูงาน (Homework)")
page = st.sidebar.radio(
    "เลือกงานที่ต้องการดู:", 
    ["HW1: SET50 Network", "HW2: (Coming Soon)", "HW3: (Coming Soon)"]
)

# ==========================================
# 📌 หน้าจอ HW1
# ==========================================
if page == "HW1: SET50 Network":
    st.title("🕸️ SET50 Shareholder Interactive Network")
    st.write("กราฟเครือข่ายความเชื่อมโยงผู้ถือหุ้นรายใหญ่ (HW1)")
    
    try:
        df = load_data()
        all_tickers = sorted(df['สัญลักษณ์'].unique())
        
        # 💡 ย้ายกล่องค้นหาหุ้นมาไว้ที่ส่วนหลัก (Main Area)
        with st.expander("🔍 แผงควบคุม: เลือกรายชื่อหุ้น SET50 (คลิกเพื่อ ย่อ/ขยาย)", expanded=True):
            st.write("คุณสามารถพิมพ์ค้นหาชื่อหุ้น หรือกดกากบาท (x) เพื่อเอาออกได้เลยครับ:")
            selected_tickers = st.multiselect(
                "หุ้นที่เลือกอยู่ ทั้งหมด:",
                options=all_tickers,
                default=all_tickers
            )
            
        if selected_tickers:
            filtered_df = df[df['สัญลักษณ์'].isin(selected_tickers)]
            
            st.subheader(f"📊 ผังเครือข่ายแบบ Interactive (กำลังแสดงผล {len(selected_tickers)} บริษัท)")
            st.info("💡 ทริกการใช้งาน: ใช้ลูกกลิ้งเมาส์เพื่อซูมเข้า-ออก / ลากจุดได้ / และสามารถกดปุ่ม **'🔲 ขยายกราฟเต็มจอ'** ที่มุมซ้ายบนของตัวกราฟได้เลย!")
            
            # สร้างกราฟ Interactive ด้วย Pyvis
            net = Network(height="700px", width="100%", bgcolor="#f8fafc", font_color="#0f172a")
            net.barnes_hut(gravity=-4000, central_gravity=0.3, spring_length=150, spring_strength=0.05)
            
            for _, row in filtered_df.iterrows():
                ticker = row['สัญลักษณ์']
                shareholder = row['ชื่อผู้ถือหุ้น']
                pct = row['ร้อยละ (%)']
                
                net.add_node(ticker, label=ticker, title=f"หุ้น: {ticker}", color="#2563eb", size=25)
                net.add_node(shareholder, label=shareholder, title=f"ผู้ถือหุ้น: {shareholder}", color="#f97316", size=15)
                net.add_edge(ticker, shareholder, value=pct, title=f"ถือหุ้นอยู่: {pct}%", color="#cbd5e1")
                
            html_filename = "shareholder_network.html"
            net.save_graph(html_filename)
            
            # ฝังปุ่มกด Full Screen
            with open(html_filename, 'r', encoding='utf-8') as f:
                html_data = f.read()
                
            fullscreen_injector = """
            <style>
            .fullscreen-btn {
                position: absolute;
                top: 15px; left: 15px; z-index: 99999;
                padding: 10px 18px; background-color: #2563eb; color: white;
                font-weight: bold; border: none; border-radius: 8px; cursor: pointer;
                box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
                font-family: system-ui, -apple-system, sans-serif; font-size: 14px;
                transition: background-color 0.2s, transform 0.1s;
            }
            .fullscreen-btn:hover { background-color: #1d4ed8; transform: scale(1.03); }
            .fullscreen-btn:active { transform: scale(0.98); }
            :-webkit-full-screen #mynetwork { height: 100vh !important; width: 100vw !important; background-color: #f8fafc !important; }
            :fullscreen #mynetwork { height: 100vh !important; width: 100vw !important; background-color: #f8fafc !important; }
            </style>
            <button class="fullscreen-btn" onclick="toggleGraphFullScreen();">🔲 ขยายกราฟเต็มจอ (Full Screen)</button>
            <script>
            function toggleGraphFullScreen() {
                var elem = document.getElementById("mynetwork");
                if (!document.fullscreenElement && !document.webkitFullscreenElement) {
                    if (elem.requestFullscreen) { elem.requestFullscreen(); } 
                    else if (elem.webkitRequestFullscreen) { elem.webkitRequestFullscreen(); }
                } else {
                    if (document.exitFullscreen) { document.exitFullscreen(); } 
                    else if (document.webkitExitFullscreen) { document.webkitExitFullscreen(); }
                }
            }
            </script>
            """
            
            html_data = html_data.replace("<body>", "<body>" + fullscreen_injector)
            components.html(html_data, height=720, scrolling=False)
            
            st.markdown("""
            * 🔵 **จุดสีน้ำเงิน** = ชื่อย่อหุ้นในกลุ่ม SET50
            * 🟠 **จุดสีส้ม** = รายชื่อผู้ถือหุ้นรายใหญ่ (ลองสังเกตจุดสีส้มที่มีเส้นกิ่งก้านลากไปหาจุดน้ำเงินหลายๆ อัน นั่นคือ **ผู้ถือหุ้นร่วมรายใหญ่** ของกลุ่มครับ)
            """)
            st.markdown("---")
            
            # ตารางข้อมูล
            st.write("### 📋 รายละเอียดข้อมูลผู้ถือหุ้นในระบบ")
            show_df = (
                filtered_df[['สัญลักษณ์', 'อันดับ', 'ชื่อผู้ถือหุ้น', 'จำนวนหุ้น', 'ร้อยละ (%)']]
                .sort_values(by=['สัญลักษณ์', 'อันดับ'])
                .reset_index(drop=True)
            )
            show_df.index = show_df.index + 1
            st.dataframe(show_df, use_container_width=True)
            
        else:
            st.warning("⚠️ กรุณาเลือกชื่อหุ้นอย่างน้อย 1 ตัว เพื่อให้ระบบคำนวณกราฟครับ")

    except FileNotFoundError:
        st.error("❌ ไม่พบไฟล์ชื่อ 'SET50_top5_shareholders.csv' กรุณาตรวจสอบตำแหน่งไฟล์")

# ==========================================
# 📌 หน้าจอ HW2
# ==========================================
elif page == "HW2: (Coming Soon)":
    st.title("📝 Homework 2")
    st.info("รออัปเดตเนื้อหาสำหรับ HW2 ในภายหลังครับ")

# ==========================================
# 📌 หน้าจอ HW3
# ==========================================
elif page == "HW3: (Coming Soon)":
    st.title("📝 Homework 3")
    st.info("รออัปเดตเนื้อหาสำหรับ HW3 ในภายหลังครับ")