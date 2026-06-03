"""
模組：退休規劃
"""
import streamlit as st
from utils.calculations import calc_retirement_plan
from utils.charts import (
    area_chart, donut_chart, line_chart, metric_card_html,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_GOLD, BRAND_SUCCESS
)


def render():
    st.markdown('<div class="section-header">🏦 退休財務規劃</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    💡 <b>規劃邏輯：</b>將本金分為兩部分——
    <b>保本部分</b>投入固定利率商品確保到期本金完整，
    <b>投資部分</b>進入投資型基金取得配息與增值。
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**👤 基本設定**")
        principal = st.number_input("本金（萬元）", 100, 10000, 1000, 50)
        years     = st.slider("規劃年數", 10, 50, 35)

    with col2:
        st.markdown("**🔒 保本商品**")
        safe_rate = st.number_input("保本商品年利率 (%)", 1.0, 8.0, 4.15, 0.05,
                                     format="%.2f") / 100
        st.caption(f"保本係數 ≈ {(1+safe_rate)**(years-2):.4f}")

    with col3:
        st.markdown("**📈 投資型基金**")
        invest_rate     = st.number_input("基金年化報酬率 (%)", 1.0, 25.0, 15.76, 0.5,
                                           format="%.2f")
        dist_rate       = st.number_input("基金年化配息率 (%)", 1.0, 25.0, 11.58, 0.5,
                                           format="%.2f") / 100
        cash_fund_ratio = st.slider("配現金基金比例", 0.1, 1.0, 0.6, 0.05)

    calculate = st.button("▶  開始試算")

    if not calculate:
        st.markdown('<div class="warn-box">👆 設定完參數後按「開始試算」</div>',
                    unsafe_allow_html=True)
        return

    result = calc_retirement_plan(
        principal, years, safe_rate,
        invest_rate, cash_fund_ratio, dist_rate
    )

    st.markdown("---")
    st.markdown('<div class="section-header">📊 試算結果摘要</div>', unsafe_allow_html=True)

    cards = [
        metric_card_html("保本投入金額",    f"{result['safe_amount']:,.1f} 萬",
                         f"利率 {safe_rate*100:.2f}%", BRAND_PRIMARY),
        metric_card_html("投資型投入金額",  f"{result['invest_amount']:,.1f} 萬",
                         f"本金 {principal} 萬 – 保本 {result['safe_amount']} 萬", BRAND_ACCENT),
        metric_card_html("每月預估配息",    f"{result['monthly_income']:,.1f} 萬",
                         f"年配息約 {result['annual_income']:,.1f} 萬", BRAND_GOLD),
        metric_card_html("期末總資產",      f"{result['total_value']:,.1f} 萬",
                         f"帳戶 {result['final_account']:,.1f} + 配息 {result['final_income']:,.1f}", BRAND_SUCCESS),
        metric_card_html("年化報酬率",      f"{result['annual_return']:.2f} %",
                         f"{years} 年總結", BRAND_PRIMARY),
    ]
    st.markdown(
        '<div class="metrics-row">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )

    df = result["df"]
    tab1, tab2, tab3 = st.tabs(["📈 資產成長曲線", "💰 配息分析", "📋 逐年明細"])

    with tab1:
        fig = area_chart(df, "年度", ["帳戶價值(萬)", "累積配息(萬)"],
                         "退休資產成長預估", "金額（萬元）")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig2 = line_chart(df, "年度", ["累積配息(萬)", "總資產(萬)"],
                          "累積配息 vs 總資產", "金額（萬元）",
                          [BRAND_GOLD, BRAND_SUCCESS])
        st.plotly_chart(fig2, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig3 = donut_chart(
                ["保本部分", "配現金基金", "配單位基金"],
                [result['safe_amount'],
                 result['invest_amount'] * cash_fund_ratio,
                 result['invest_amount'] * (1 - cash_fund_ratio)],
                "本金配置比例"
            )
            st.plotly_chart(fig3, use_container_width=True)
        with c2:
            fig4 = donut_chart(
                ["期末帳戶價值", "累積已領配息"],
                [result['final_account'], result['final_income']],
                f"第 {years} 年期末資產組成"
            )
            st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.dataframe(
            df.style.format({
                "帳戶價值(萬)": "{:,.2f}",
                "累積配息(萬)": "{:,.2f}",
                "總資產(萬)":   "{:,.2f}",
            }),
            use_container_width=True, height=400
        )
        st.caption("⚠️ 以上試算假設匯率及基金淨值不變，投資有風險。")

    with st.expander("📖 規劃邏輯說明"):
        st.markdown(f"""
**步驟 1：保本計算**
- 保本係數：{result['safe_factor']}
- 需投入保本金額：{result['safe_amount']:.1f} 萬

**步驟 2：投資配置**
- 剩餘 {result['invest_amount']:.1f} 萬投入投資型保單
- 配現金基金：{result['invest_amount']*cash_fund_ratio:.1f} 萬 → 每月配息 {result['monthly_income']:,.1f} 萬

**步驟 3：{years} 年後結果**
- 總價值 {result['total_value']:.1f} 萬
- 年化報酬率 {result['annual_return']:.2f}%
        """)