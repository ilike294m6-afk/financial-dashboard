"""
財務管理可視化系統
主程式入口
"""
import streamlit as st

st.set_page_config(
    page_title="財務規劃系統",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 載入 CSS
with open("financial_dashboard/assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 修復側邊欄收起後無法打開的問題
st.markdown("""
<style>
[data-testid="collapsedControl"] {
    display: block !important;
}
</style>
""", unsafe_allow_html=True)

# 載入模組
from modules import retirement, mortgage, loan_calculator, insurance, fund_allocation

# 側邊欄
with st.sidebar:
    st.markdown("## 💼 財務規劃系統")
    st.markdown("---")
    page = st.radio(
        "選擇功能模組",
        [
            "🏦 退休規劃",
            "📈 基金配置分析",
            "🛡️ 定期保險試算",
            "🏠 房貸試算",
            "💳 貸款試算",
        ]
    )
    st.markdown("---")
    st.caption("⚠️ 本系統僅供試算參考\n投資有風險，請謹慎評估")

# 主標題
st.markdown("""
<div class="main-title">
    <h1>💼 財務規劃可視化系統</h1>
    <p>退休規劃 · 基金配置 · 保險試算 · 房貸 · 貸款</p>
</div>
""", unsafe_allow_html=True)

# 頁面路由
if page == "🏦 退休規劃":
    retirement.render()
elif page == "📈 基金配置分析":
    fund_allocation.render()
elif page == "🛡️ 定期保險試算":
    insurance.render()
elif page == "🏠 房貸試算":
    mortgage.render()
elif page == "💳 貸款試算":
    loan_calculator.render()
    loan_calculator.render()
