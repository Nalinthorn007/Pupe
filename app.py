"""
Streamlit UI for Chart Generation Workflow
ສ້າງປະສົບການ UI ສຳລັບ workflow: Question → SQL → Table → Chart
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import nodes from existing workflow
from src.Agent.nodes import (
    get_schema_node, 
    sql_agent_node, 
    execute_sql_node, 
    chart_generation_node
)

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="📊 Chart Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# Custom CSS Styling
# ============================
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Card style */
    .stCard {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* SQL Code block */
    .sql-block {
        background: #1e1e3f;
        border-radius: 12px;
        padding: 16px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 14px;
        color: #a8d4ff;
        border: 1px solid #3d3d6b;
        overflow-x: auto;
    }
    
    /* Status badges */
    .badge-success {
        background: linear-gradient(135deg, #00c853, #00e676);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .badge-pending {
        background: linear-gradient(135deg, #ff9800, #ffc107);
        color: #1a1a2e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# Session State Initialization
# ============================
if "step" not in st.session_state:
    st.session_state.step = 0  # 0=input, 1=sql_ready, 2=table_ready, 3=chart_ready

if "question" not in st.session_state:
    st.session_state.question = ""

if "sql_script" not in st.session_state:
    st.session_state.sql_script = ""

if "sql_result" not in st.session_state:
    st.session_state.sql_result = None

if "result_schema" not in st.session_state:
    st.session_state.result_schema = ""

if "chart_html_path" not in st.session_state:
    st.session_state.chart_html_path = ""

# ============================
# Helper Functions
# ============================
def reset_state():
    """Reset all session state to initial values"""
    st.session_state.step = 0
    st.session_state.question = ""
    st.session_state.sql_script = ""
    st.session_state.sql_result = None
    st.session_state.result_schema = ""
    st.session_state.chart_html_path = ""

def cancel_action():
    """Cancel and go back to step 0"""
    st.session_state.step = 0
    st.session_state.sql_result = None
    st.session_state.chart_html_path = ""

# ============================
# Main UI
# ============================
st.title("📊 Chart Generation Workflow")
st.markdown("**ສ້າງ Chart ຈາກຄຳຖາມພາສາທຳມະຊາດ → SQL → ຕາຕະລາງ → Chart**")

st.divider()

# ============================
# Step 1: Question Input
# ============================
st.subheader("1️⃣ ປ້ອນຄຳຖາມຂອງທ່ານ")

col1, col2 = st.columns([4, 1])

with col1:
    question_input = st.text_input(
        "ຄຳຖາມ:",
        value=st.session_state.question,
        placeholder="ເຊັ່ນ: ສະແດງຍອດຂາຍແຕ່ລະປີ, ຂ້ອຍຢາກຮູ້ລາຍລະອຽດຜູ້ໃຊ້ທັງໝົດ...",
        label_visibility="collapsed"
    )

with col2:
    generate_btn = st.button("🔍 Generate SQL", type="primary", use_container_width=True)

# Handle Generate SQL button
if generate_btn and question_input:
    st.session_state.question = question_input
    
    with st.spinner("⏳ ກຳລັງດຶງ Schema ແລະ ສ້າງ SQL..."):
        # Step 1: Get schema
        state = {"question": question_input, "messages": []}
        schema_result = get_schema_node(state)
        st.session_state.result_schema = schema_result.get("result_schema", "")
        
        # Step 2: Generate SQL
        state["result_schema"] = st.session_state.result_schema
        sql_result = sql_agent_node(state)
        st.session_state.sql_script = sql_result.get("sql_script", "")
        
        if st.session_state.sql_script and not st.session_state.sql_script.startswith("--"):
            st.session_state.step = 1
            st.rerun()
        else:
            st.error("❌ ບໍ່ສາມາດສ້າງ SQL ໄດ້. ກະລຸນາລອງຄຳຖາມໃໝ່.")

# ============================
# Step 2: SQL Display
# ============================
if st.session_state.step >= 1 and st.session_state.sql_script:
    st.divider()
    st.subheader("2️⃣ SQL Query ທີ່ສ້າງຂຶ້ນ")
    
    # Display SQL in code block
    st.code(st.session_state.sql_script, language="sql")
    
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        execute_btn = st.button("▶️ Execute SQL", type="primary", use_container_width=True)
    
    with col2:
        cancel_sql_btn = st.button("🔄 ລອງໃໝ່", use_container_width=True)
    
    if cancel_sql_btn:
        reset_state()
        st.rerun()
    
    if execute_btn:
        with st.spinner("⏳ ກຳລັງ Execute SQL..."):
            state = {
                "sql_script": st.session_state.sql_script,
                "messages": []
            }
            result = execute_sql_node(state)
            st.session_state.sql_result = result.get("sql_result", {})
            
            if st.session_state.sql_result and not st.session_state.sql_result.get("error"):
                st.session_state.step = 2
                st.rerun()
            else:
                error_msg = st.session_state.sql_result.get("error", "Unknown error")
                st.error(f"❌ SQL Error: {error_msg}")

# ============================
# Step 3: Table Display with Accept/Cancel
# ============================
if st.session_state.step >= 2 and st.session_state.sql_result:
    st.divider()
    st.subheader("3️⃣ ຜົນລັບຈາກ Database")
    
    rows = st.session_state.sql_result.get("rows", [])
    columns = st.session_state.sql_result.get("columns", [])
    row_count = st.session_state.sql_result.get("row_count", 0)
    
    # Show stats
    st.markdown(f"**📋 ຈຳນວນແຖວ:** {row_count} | **📊 ຈຳນວນ Columns:** {len(columns)}")
    
    # Display as dataframe
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.warning("ບໍ່ມີຂໍ້ມູນ")
    
    # Accept / Cancel buttons
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        accept_btn = st.button("✅ Accept & Generate Chart", type="primary", use_container_width=True)
    
    with col2:
        cancel_btn = st.button("❌ Cancel", type="secondary", use_container_width=True)
    
    if cancel_btn:
        cancel_action()
        st.rerun()
    
    if accept_btn:
        with st.spinner("🎨 ກຳລັງສ້າງ Chart..."):
            state = {
                "question": st.session_state.question,
                "sql_result": st.session_state.sql_result,
                "messages": []
            }
            chart_result = chart_generation_node(state)
            final_report = chart_result.get("final_report", "")
            
            if "ສຳເລັດ" in final_report or "successfully" in final_report.lower():
                # Extract path from result
                # Format: "File 'd:\Pupe\src\Agent\Display\xxx.html' ໄດ້ຖືກສ້າງສຳເລັດແລ້ວ."
                if "'" in final_report:
                    path_start = final_report.index("'") + 1
                    path_end = final_report.index("'", path_start)
                    st.session_state.chart_html_path = final_report[path_start:path_end]
                st.session_state.step = 3
                st.rerun()
            else:
                st.error(f"❌ Chart Error: {final_report}")

# ============================
# Step 4: Display Embedded Chart
# ============================
if st.session_state.step >= 3 and st.session_state.chart_html_path:
    st.divider()
    st.subheader("4️⃣ 📊 Chart ທີ່ສ້າງຂຶ້ນ")
    
    st.success(f"✅ Chart ຖືກສ້າງສຳເລັດ: `{st.session_state.chart_html_path}`")
    
    # Read and embed HTML
    if os.path.exists(st.session_state.chart_html_path):
        with open(st.session_state.chart_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Embed HTML using components
        import streamlit.components.v1 as components
        components.html(html_content, height=1000, scrolling=True)
        
        # Download button
        st.download_button(
            label="📥 Download HTML Chart",
            data=html_content,
            file_name="chart.html",
            mime="text/html"
        )
    else:
        st.error(f"❌ ບໍ່ພົບ file: {st.session_state.chart_html_path}")
    
    # Start over button
    st.divider()
    if st.button("🔄 ເລີ່ມໃໝ່", use_container_width=False):
        reset_state()
        st.rerun()

# ============================
# Sidebar Info
# ============================
with st.sidebar:
    st.markdown("### ℹ️ ຂໍ້ມູນ Workflow")
    st.markdown("""
    **ຂັ້ນຕອນ:**
    1. ປ້ອນຄຳຖາມພາສາລາວ
    2. ລະບົບສ້າງ SQL Query
    3. Execute ແລະ ເບິ່ງຕາຕະລາງ
    4. Accept ເພື່ອສ້າງ Chart
    """)
    
    st.divider()
    
    st.markdown("### 📊 Current State")
    st.markdown(f"**Step:** {st.session_state.step}")
    st.markdown(f"**Question:** {st.session_state.question[:50] + '...' if len(st.session_state.question) > 50 else st.session_state.question or 'N/A'}")
    
    if st.session_state.sql_script:
        st.markdown("**SQL:** ✅ Generated")
    if st.session_state.sql_result:
        st.markdown(f"**Rows:** {st.session_state.sql_result.get('row_count', 0)}")
    if st.session_state.chart_html_path:
        st.markdown("**Chart:** ✅ Created")
