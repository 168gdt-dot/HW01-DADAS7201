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

# ฟังก์ชันโหลดข้อมูลอัตโนมัติ (HW1)
@st.cache_data
def load_data():
    current_dir = pathlib.Path(__file__).parent
    found_files = list(current_dir.rglob('SET50_top5_shareholders.csv'))
    if len(found_files) == 0:
        raise FileNotFoundError("❌ หาไฟล์ไม่พบ กรุณาตรวจสอบว่าชื่อไฟล์ถูกต้อง")
    return pd.read_csv(found_files[0])

# ฟังก์ชันโหลดข้อมูล centrality (HW2)
@st.cache_data
def load_centrality():
    current_dir = pathlib.Path(__file__).parent
    found = list(current_dir.rglob('centrality_results.csv'))
    if len(found) == 0:
        raise FileNotFoundError("centrality_results.csv")
    return pd.read_csv(found[0])

@st.cache_data
def load_edges():
    current_dir = pathlib.Path(__file__).parent
    found = list(current_dir.rglob('memetracker_edges.csv'))
    if len(found) == 0:
        return None
    return pd.read_csv(found[0])

# ฟังก์ชันฝังปุ่ม Full Screen (ใช้ร่วมกันทั้ง HW1/HW2)
def inject_fullscreen(html_data):
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
    return html_data.replace("<body>", "<body>" + fullscreen_injector)

# ==========================================
# 📌 เมนูด้านซ้าย (Sidebar Menu)
# ==========================================
st.sidebar.header("📁 เมนูงาน (Homework)")
page = st.sidebar.radio(
    "เลือกงานที่ต้องการดู:",
    ["HW1: SET50 Network", "HW2: MemeTracker Centrality", "HW3: (Coming Soon)"]
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
            with open(html_filename, 'r', encoding='utf-8') as f:
                html_data = f.read()
            html_data = inject_fullscreen(html_data)
            components.html(html_data, height=720, scrolling=False)

            st.markdown("""
            * 🔵 **จุดสีน้ำเงิน** = ชื่อย่อหุ้นในกลุ่ม SET50
            * 🟠 **จุดสีส้ม** = รายชื่อผู้ถือหุ้นรายใหญ่ (ลองสังเกตจุดสีส้มที่มีเส้นกิ่งก้านลากไปหาจุดน้ำเงินหลายๆ อัน นั่นคือ **ผู้ถือหุ้นร่วมรายใหญ่** ของกลุ่มครับ)
            """)
            st.markdown("---")

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
# 📌 หน้าจอ HW2 : MemeTracker Centrality
# ==========================================
elif page == "HW2: MemeTracker Centrality":
    st.title("🌐 MemeTracker Centrality Network")
    st.write("วิเคราะห์ค่า Centrality ของเครือข่ายโดเมนข่าว (คำนวณด้วย Cypher/Neo4j GDS) — HW2")

    # ชื่อ measure ที่อ่านง่าย
    MEASURES = {
        "Betweenness (สะพานเชื่อม)": "betweenness",
        "Degree (จำนวนการเชื่อม)": "degree",
        "Closeness (ความใกล้)": "closeness",
        "Eigenvector (อิทธิพล)": "eigenvector",
        "PageRank (ความสำคัญ)": "pagerank",
    }

    try:
        cent = load_centrality()
        edges = load_edges()

        # ----- การ์ดสรุป -----
        n_nodes = len(cent)
        n_comm = cent['community'].nunique()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("โดเมน (Nodes)", f"{n_nodes:,}")
        c2.metric("ความเชื่อมโยง (Edges)", f"{len(edges):,}" if edges is not None else "—")
        c3.metric("ชุมชน (Communities)", f"{n_comm}")
        c4.metric("Modularity", "0.536")

        st.markdown("---")

        # ----- แผงควบคุม -----
        with st.expander("🎛️ แผงควบคุม: เลือกมุมมอง Centrality และขนาดกราฟ", expanded=True):
            colA, colB = st.columns([2, 1])
            with colA:
                measure_label = st.selectbox(
                    "เลือกค่า Centrality ที่ต้องการวิเคราะห์ (ขนาดจุด = ค่ามาก-เล็ก):",
                    options=list(MEASURES.keys())
                )
            with colB:
                topn = st.slider("แสดง Top N โดเมน:", min_value=20, max_value=150, value=60, step=10)
        measure = MEASURES[measure_label]

        # ----- เลือก top-N -----
        top = cent.nlargest(topn, measure).copy()
        keep = set(top['domain'])

        st.subheader(f"📊 กราฟเครือข่าย — Top {topn} โดเมน เรียงตาม {measure_label}")
        st.info("💡 ขนาดจุด = ค่า Centrality ที่เลือก · สีจุด = ชุมชน (Louvain) · กดปุ่ม **'🔲 ขยายกราฟเต็มจอ'** เพื่อดูเต็มจอ")

        # ----- สร้างกราฟ pyvis -----
        net = Network(height="700px", width="100%", bgcolor="#f8fafc", font_color="#0f172a")
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200, spring_strength=0.04)

        # normalize ขนาด node (10-60) ตามค่า measure
        vals = top[measure].astype(float)
        lo, hi = vals.min(), vals.max()

        # palette สำหรับ community
        palette = ["#2563eb", "#f97316", "#16a34a", "#dc2626", "#9333ea",
                   "#0891b2", "#ca8a04", "#db2777", "#65a30d", "#4f46e5"]

        for _, row in top.iterrows():
            size = 10 + (float(row[measure]) - lo) / (hi - lo + 1e-9) * 50
            comm = int(row['community'])
            color = palette[comm % len(palette)]
            title = (f"{row['domain']}\n"
                     f"betweenness: {row['betweenness']:.0f}\n"
                     f"degree: {row['degree']:.0f}\n"
                     f"pagerank: {row['pagerank']:.3f}\n"
                     f"community: {comm}")
            net.add_node(row['domain'], label=row['domain'], title=title,
                         color=color, size=size)

        # เพิ่มเส้น (เฉพาะที่ทั้ง 2 ฝั่งอยู่ใน top-N)
        if edges is not None:
            sub = edges[edges['source'].isin(keep) & edges['target'].isin(keep)]
            for _, e in sub.iterrows():
                net.add_edge(e['source'], e['target'],
                             value=float(e['weight']), color="#cbd5e1")

        html_filename = "memetracker_network.html"
        net.save_graph(html_filename)
        with open(html_filename, 'r', encoding='utf-8') as f:
            html_data = f.read()
        html_data = inject_fullscreen(html_data)
        components.html(html_data, height=720, scrolling=False)

        st.markdown("---")

        # ----- ตารางจัดอันดับ -----
        st.write(f"### 📋 ตารางจัดอันดับ Top {topn} โดเมน (ตาม {measure_label})")
        show = top[['domain', 'degree', 'betweenness', 'closeness',
                    'eigenvector', 'pagerank', 'community']].reset_index(drop=True)
        show.index = show.index + 1
        # ปัดเลขให้อ่านง่าย
        show['betweenness'] = show['betweenness'].round(0)
        show['degree'] = show['degree'].round(0)
        show['closeness'] = show['closeness'].round(4)
        show['eigenvector'] = show['eigenvector'].round(4)
        show['pagerank'] = show['pagerank'].round(4)
        st.dataframe(show, use_container_width=True)

        st.markdown("""
        **อธิบายค่า Centrality:**
        * **Betweenness** = โดเมนที่เป็น "สะพาน" ให้ข่าว/quote ไหลผ่าน (ตัวกลางสำคัญ)
        * **Degree** = โดเมนที่เชื่อมกับโดเมนอื่นเยอะ
        * **Closeness** = โดเมนที่เข้าถึงโดเมนอื่นได้เร็ว (อยู่ใจกลางเครือข่าย)
        * **Eigenvector** = โดเมนที่เชื่อมกับโดเมนสำคัญอื่นๆ (อิทธิพลสูง)
        * **PageRank** = ความสำคัญแบบเดียวกับที่ Google ใช้จัดอันดับเว็บ
        * **สีจุด** = ชุมชน (community) ที่ Louvain แบ่ง — เว็บที่พูดเรื่องคล้ายกันจะสีเดียวกัน
        """)

    except FileNotFoundError as e:
        st.error(f"❌ ไม่พบไฟล์ '{e}' กรุณาตรวจสอบว่าวางไฟล์ไว้ในโปรเจกต์แล้ว")
        st.info("ไฟล์ที่ต้องมี: `centrality_results.csv` (จำเป็น) และ `memetracker_edges.csv` (สำหรับเส้นเชื่อม)")

# ==========================================
# 📌 หน้าจอ HW3
# ==========================================
elif page == "HW3: (Coming Soon)":
    st.title("📝 Homework 3")
    st.info("รออัปเดตเนื้อหาสำหรับ HW3 ในภายหลังครับ")