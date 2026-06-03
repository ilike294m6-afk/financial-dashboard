"""
模組：房貸試算
"""
import streamlit as st
import plotly.graph_objects as go
from utils.calculations import calc_mortgage
from utils.charts import (
    donut_chart, metric_card_html, line_chart,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_DANGER, BRAND_SUCCESS
)


def render():
    st.markdown('<div class="section-header">🏠 房貸試算</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    💡 採用<b>本利攤還法</b>，每月還款固定，前期利息較高、後期本金比例增加。
    提醒：房屋實際成本還含稅、修繕費，請一併納入規劃。
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        price      = st.number_input("房價（萬元）", 200, 10000, 1500, 100)
        down_ratio = st.slider("頭期款比例", 0.1, 0.5, 0.2, 0.05)
    with col2:
        rate  = st.number_input("年貸款利率 (%)", 0.5, 10.0, 2.3, 0.1, format="%.2f") / 100
        years = st.slider("貸款年數", 5, 40, 30)
    with col3:
        st.markdown("**試算概覽**")
        loan = price * (1 - down_ratio)
        st.metric("貸款金額", f"{loan:,.0f} 萬")
        st.metric("頭期款",   f"{price * down_ratio:,.0f} 萬")

    if not st.button("▶  開始試算", key="mortgage_calc"):
        st.markdown('<div class="warn-box">👆 設定完參數後按「開始試算」</div>',
                    unsafe_allow_html=True)
        return

    result = calc_mortgage(price, down_ratio, rate, years)
    df     = result["df"]

    yearly = df.groupby("年度").agg(
        總還款=("還款金額", "sum"),
        總本金=("本金",     "sum"),
        總利息=("利息",     "sum"),
        期末餘額=("剩餘本金", "last"),
    ).reset_index()

    st.markdown("---")
    cards = [
        metric_card_html("每月還款",    f"{result['monthly']:,.0f} 元",  "等額本利", BRAND_PRIMARY),
        metric_card_html("貸款金額",    f"{result['loan']:,.0f} 萬",     f"房價 {price:,} 萬", BRAND_ACCENT),
        metric_card_html("總還款金額",  f"{result['total_paid']/10000:,.1f} 萬", "", BRAND_DANGER),
        metric_card_html("總利息支出",  f"{result['total_interest']/10000:,.1f} 萬",
                         f"房價的 {result['total_interest']/(price*10000)*100:.1f}%", BRAND_DANGER),
        metric_card_html("實際總成本",
                         f"{(result['total_paid']+price*down_ratio*10000)/10000:,.1f} 萬",
                         "含頭期款", BRAND_PRIMARY),
    ]
    st.markdown('<div class="metrics-row">' + "".join(cards) + "</div>",
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="warn-box">
    ⚠️ 你花了 <b>{result['total_paid']/10000:,.1f} 萬</b> 買下現值
    <b>{price:,} 萬</b> 的房子，另需計算稅費與修繕費。
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 還款結構", "📉 剩餘本金", "📋 逐年明細"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=yearly["年度"], y=yearly["總本金"]/10000,
                             name="還本金（萬）", marker_color=BRAND_SUCCESS))
        fig.add_trace(go.Bar(x=yearly["年度"], y=yearly["總利息"]/10000,
                             name="付利息（萬）", marker_color=BRAND_DANGER))
        fig.update_layout(barmode="stack", title="每年還款結構",
                          xaxis_title="年度", yaxis_title="金額（萬元）",
                          plot_bgcolor="white", paper_bgcolor="white",
                          hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig2 = donut_chart(["本金", "利息"],
                               [result['loan'],
                                result['total_interest']/10000],
                               "總還款組成")
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            st.markdown(f"""
            <br>
            <div class="info-box">
            📌 <b>關鍵數字</b><br><br>
            • 房價：<b>{price:,} 萬</b><br>
            • 頭期款：<b>{price*down_ratio:,.0f} 萬</b>（{down_ratio*100:.0f}%）<br>
            • 實際貸款：<b>{result['loan']:,} 萬</b><br>
            • 利息支出：<b>{result['total_interest']/10000:,.1f} 萬</b><br>
            • 總花費：<b>{result['total_paid']/10000:,.1f} 萬</b><br>
            • 平均月付：<b>{result['monthly']:,.0f} 元</b>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        fig3 = line_chart(yearly, "年度", ["期末餘額"],
                          "剩餘本金走勢（元）", "剩餘本金（元）", [BRAND_DANGER])
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.dataframe(
            yearly.style.format({
                "總還款": "{:,.0f}", "總本金": "{:,.0f}",
                "總利息": "{:,.0f}", "期末餘額": "{:,.0f}",
            }),
            use_container_width=True, height=400
        )