"""
模組：一般貸款試算
"""
import streamlit as st
import plotly.graph_objects as go
from utils.calculations import calc_loan
from utils.charts import (
    metric_card_html, line_chart,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_GOLD, BRAND_DANGER, BRAND_SUCCESS
)


def render():
    st.markdown('<div class="section-header">💳 貸款試算（利率 · 年期 · 費用）</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    💡 支援<b>等額本利</b>（每月固定）與<b>等額本金</b>（前期較高、後期遞減）
    兩種還款方式，並可加入手續費等費用計算實際資金成本。
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**貸款基本設定**")
        amount  = st.number_input("貸款金額（萬元）", 10, 5000, 200, 10)
        rate    = st.number_input("年利率 (%)", 0.1, 20.0, 3.5, 0.1, format="%.2f") / 100
        years   = st.slider("還款年數", 1, 30, 5)
        method  = st.selectbox("還款方式", ["等額本利", "等額本金"])
    with col2:
        st.markdown("**額外費用**")
        fee_rate   = st.number_input("手續費 / 開辦費 (%)", 0.0, 5.0, 0.5, 0.1,
                                      format="%.2f") / 100
        annual_fee = st.number_input("每年管理費（元）", 0, 100000, 0, 500)

    if not st.button("▶  開始試算", key="loan_calc"):
        st.markdown('<div class="warn-box">👆 設定完參數後按「開始試算」</div>',
                    unsafe_allow_html=True)
        return

    result   = calc_loan(amount, rate, years, method)
    df       = result["df"]
    fee_amt  = round(amount * 10000 * fee_rate, 0)
    total_annual_fees = annual_fee * years
    true_cost = result["total_paid"] + fee_amt + total_annual_fees
    apr = (true_cost - amount * 10000) / (amount * 10000) / years * 100

    st.markdown("---")
    cards = [
        metric_card_html("首月還款",        f"{result['monthly_first']:,.0f} 元",
                         method, BRAND_PRIMARY),
        metric_card_html("總還款金額",       f"{result['total_paid']/10000:,.1f} 萬",
                         "", BRAND_ACCENT),
        metric_card_html("總利息",           f"{result['total_interest']/10000:,.1f} 萬",
                         f"本金的 {result['total_interest']/(amount*10000)*100:.1f}%", BRAND_DANGER),
        metric_card_html("一次性費用",       f"{fee_amt:,.0f} 元",
                         f"手續費 {fee_rate*100:.1f}%", BRAND_GOLD),
        metric_card_html("實際年利率 (APR)", f"{apr:.2f} %",
                         "含所有費用", BRAND_DANGER),
    ]
    st.markdown('<div class="metrics-row">' + "".join(cards) + "</div>",
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 兩種方案比較", "📉 還款結構", "📋 逐月明細"])

    with tab1:
        r_a = calc_loan(amount, rate, years, "等額本利")
        r_p = calc_loan(amount, rate, years, "等額本金")

        fig = go.Figure()
        fig.add_trace(go.Bar(name="等額本利－利息",
                             x=["等額本利"], y=[r_a["total_interest"]/10000],
                             marker_color=BRAND_DANGER))
        fig.add_trace(go.Bar(name="等額本利－本金",
                             x=["等額本利"], y=[amount],
                             marker_color=BRAND_SUCCESS))
        fig.add_trace(go.Bar(name="等額本金－利息",
                             x=["等額本金"], y=[r_p["total_interest"]/10000],
                             marker_color="#E74C3C"))
        fig.add_trace(go.Bar(name="等額本金－本金",
                             x=["等額本金"], y=[amount],
                             marker_color="#27AE60"))
        fig.update_layout(barmode="stack", title="兩種還款方式總成本比較（萬元）",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="info-box">
            <b>等額本利</b><br>
            首月還款：{r_a['monthly_first']:,.0f} 元<br>
            總利息：{r_a['total_interest']/10000:,.2f} 萬<br>
            總還款：{r_a['total_paid']/10000:,.2f} 萬
            </div>
            """, unsafe_allow_html=True)
        with c2:
            saved = (r_a['total_interest'] - r_p['total_interest']) / 10000
            st.markdown(f"""
            <div class="info-box">
            <b>等額本金</b><br>
            首月還款：{r_p['monthly_first']:,.0f} 元<br>
            總利息：{r_p['total_interest']/10000:,.2f} 萬（省 {saved:,.2f} 萬）<br>
            總還款：{r_p['total_paid']/10000:,.2f} 萬
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        yearly = df.groupby("年度").agg(
            總本金=("本金", "sum"),
            總利息=("利息", "sum"),
        ).reset_index()
        yearly["總本金"] /= 10000
        yearly["總利息"] /= 10000

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=yearly["年度"], y=yearly["總本金"],
                              name="還本金（萬）", marker_color=BRAND_SUCCESS))
        fig2.add_trace(go.Bar(x=yearly["年度"], y=yearly["總利息"],
                              name="付利息（萬）", marker_color=BRAND_DANGER))
        fig2.update_layout(barmode="stack", title="每年還款結構",
                           plot_bgcolor="white", paper_bgcolor="white",
                           hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.dataframe(
            df.head(120).style.format({
                "還款金額": "{:,.0f}", "本金": "{:,.0f}",
                "利息": "{:,.0f}", "剩餘本金": "{:,.0f}",
            }),
            use_container_width=True, height=400
        )
        st.caption(f"顯示前 {min(120, len(df))} 筆（共 {len(df)} 筆）")