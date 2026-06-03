"""
模組：定期保險試算
"""
import streamlit as st
import plotly.graph_objects as go
from utils.calculations import calc_insurance
from utils.charts import (
    metric_card_html,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_GOLD, BRAND_DANGER
)


def render():
    st.markdown('<div class="section-header">🛡️ 定期保險試算</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    💡 定期壽險費率隨年齡增加，以下試算採<b>逐年重新計算</b>費率，
    協助了解長期保費負擔與保障規劃。
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        age    = st.number_input("投保年齡", 20, 70, 30)
        gender = st.selectbox("性別", ["男", "女"])
    with col2:
        coverage = st.number_input("保額（萬元）", 100, 5000, 500, 100)
        years    = st.slider("投保年數", 1, 40, 20)
    with col3:
        monthly_budget = st.number_input("月預算上限（元，0=不限）", 0, 100000, 0, 500)
        st.caption(f"投保至 {age + years} 歲")

    if not st.button("▶  開始試算", key="ins_calc"):
        st.markdown('<div class="warn-box">👆 設定完參數後按「開始試算」</div>',
                    unsafe_allow_html=True)
        return

    result = calc_insurance(age, coverage, years, monthly_budget)
    df     = result["df"]

    st.markdown("---")
    cards = [
        metric_card_html("保額",       f"{coverage:,} 萬",
                         "壽險保障", BRAND_PRIMARY),
        metric_card_html("總保費",      f"{result['total_premium']:,.0f} 元",
                         f"{years} 年累計", BRAND_ACCENT),
        metric_card_html("平均月保費",  f"{result['avg_monthly']:,.0f} 元",
                         "", BRAND_GOLD),
        metric_card_html("CP 值",
                         f"{coverage * 10000 / result['total_premium']:.1f}x",
                         "保額 ÷ 總保費", BRAND_PRIMARY),
    ]
    st.markdown('<div class="metrics-row">' + "".join(cards) + "</div>",
                unsafe_allow_html=True)

    if monthly_budget > 0:
        over = df[df["月保費"] > monthly_budget]
        if not over.empty:
            st.markdown(f"""
            <div class="warn-box">
            ⚠️ 第 <b>{int(over.iloc[0]['年度'])}</b> 年起
            （年齡 {int(over.iloc[0]['年齡'])} 歲），
            月保費 <b>{int(over.iloc[0]['月保費']):,} 元</b>
            將超過您的月預算 {monthly_budget:,} 元，
            建議提前規劃轉換商品或調整保額。
            </div>
            """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📈 保費趨勢", "📋 逐年明細"])

    with tab1:
        colors = [
            BRAND_DANGER if (monthly_budget > 0 and row["月保費"] > monthly_budget)
            else BRAND_ACCENT
            for _, row in df.iterrows()
        ]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["年度"], y=df["年保費"],
            name="年保費",
            marker_color=colors,
            hovertemplate="第%{x}年 | 年齡%{customdata}歲<br>年保費: %{y:,.0f}元<extra></extra>",
            customdata=df["年齡"],
        ))
        if monthly_budget > 0:
            fig.add_hline(
                y=monthly_budget * 12,
                line_dash="dash", line_color=BRAND_DANGER,
                annotation_text=f"預算上限 {monthly_budget:,}元/月",
                annotation_position="top left"
            )
        fig.update_layout(
            title="逐年保費趨勢",
            xaxis_title="投保年度", yaxis_title="年保費（元）",
            plot_bgcolor="white", paper_bgcolor="white",
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.dataframe(
            df.style.format({
                "月費率(‰)": "{:.3f}",
                "月保費":    "{:,.0f}",
                "年保費":    "{:,.0f}",
                "保額(萬)":  "{:,.0f}",
            }),
            use_container_width=True, height=400
        )