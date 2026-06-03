"""
模組：投資型基金配置分析
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.charts import (
    donut_chart, metric_card_html,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_GOLD, BRAND_SUCCESS, BRAND_DANGER
)


def simulate_fund(invest_amount, years, cash_ratio, cash_yield,
                  unit_yield, mgmt_fee, value_change):
    cash_value = invest_amount * cash_ratio
    unit_value = invest_amount * (1 - cash_ratio)
    cum_income = 0.0
    rows = []

    for y in range(1, years + 1):
        annual_income = cash_value * cash_yield
        cash_value = cash_value * (1 + value_change / 100) * (1 - mgmt_fee)
        unit_value = unit_value  * (1 + unit_yield / 100) * (1 - mgmt_fee)
        cum_income += annual_income
        rows.append({
            "年度":             y,
            "配現金基金價值(萬)": round(cash_value, 2),
            "配單位基金價值(萬)": round(unit_value, 2),
            "累積配息(萬)":      round(cum_income, 2),
            "年配息(萬)":        round(annual_income, 2),
            "總帳戶價值(萬)":    round(cash_value + unit_value, 2),
        })
    return pd.DataFrame(rows)


def render():
    st.markdown('<div class="section-header">📈 投資型基金配置分析</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    💡 模擬投資型保單的<b>配現金</b>與<b>配單位</b>兩類基金的長期表現，
    並可調整管理費、淨值變動等參數進行壓力測試。
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**基本設定**")
        invest_amount = st.number_input("投入金額（萬元）", 10, 5000, 739, 10)
        years         = st.slider("模擬年數", 5, 50, 35)
        cash_ratio    = st.slider("配現金基金比例", 0.1, 1.0, 0.6, 0.05)
    with col2:
        st.markdown("**報酬假設**")
        cash_yield = st.number_input("配現金年化配息率 (%)", 1.0, 25.0, 11.58, 0.5,
                                      format="%.2f") / 100
        unit_yield = st.number_input("配單位年化報酬率 (%)", 1.0, 25.0, 15.76, 0.5,
                                      format="%.2f") / 100
    with col3:
        st.markdown("**費用與壓力測試**")
        mgmt_fee     = st.number_input("年管理費率 (%)", 0.0, 5.0, 1.33, 0.1,
                                        format="%.2f") / 100
        value_change = st.number_input("年淨值變動率 (%，負=下跌)",
                                        -20.0, 20.0, 0.0, 0.5, format="%.1f")

    if not st.button("▶  開始模擬", key="fund_sim"):
        st.markdown('<div class="warn-box">👆 設定完參數後按「開始模擬」</div>',
                    unsafe_allow_html=True)
        return

    df     = simulate_fund(invest_amount, years, cash_ratio, cash_yield,
                           unit_yield, mgmt_fee, value_change)
    final  = df.iloc[-1]
    monthly_income = round(invest_amount * cash_ratio * cash_yield / 12, 1)

    st.markdown("---")
    cards = [
        metric_card_html("每月預估配息",     f"{monthly_income:,.1f} 萬",
                         f"年配息約 {monthly_income*12:,.1f} 萬", BRAND_GOLD),
        metric_card_html("期末帳戶總值",     f"{final['總帳戶價值(萬)']:,.1f} 萬",
                         "", BRAND_PRIMARY),
        metric_card_html("累積已領配息",     f"{final['累積配息(萬)']:,.1f} 萬",
                         "", BRAND_ACCENT),
        metric_card_html("總資產（含配息）",
                         f"{final['總帳戶價值(萬)']+final['累積配息(萬)']:,.1f} 萬",
                         "", BRAND_SUCCESS),
        metric_card_html("投入本金",         f"{invest_amount:,} 萬",
                         "", BRAND_DANGER),
    ]
    st.markdown('<div class="metrics-row">' + "".join(cards) + "</div>",
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 帳戶成長", "🔄 壓力測試", "📋 逐年明細"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["年度"], y=df["配現金基金價值(萬)"],
            name="配現金基金", fill="tozeroy", mode="lines",
            line=dict(color=BRAND_GOLD, width=2),
            fillcolor="rgba(212,172,13,0.12)",
        ))
        fig.add_trace(go.Scatter(
            x=df["年度"], y=df["配單位基金價值(萬)"],
            name="配單位基金", fill="tonexty", mode="lines",
            line=dict(color=BRAND_ACCENT, width=2),
            fillcolor="rgba(46,134,193,0.12)",
        ))
        fig.add_trace(go.Scatter(
            x=df["年度"], y=df["累積配息(萬)"],
            name="累積配息", mode="lines",
            line=dict(color=BRAND_SUCCESS, width=2, dash="dash"),
        ))
        fig.update_layout(
            title="帳戶價值成長模擬",
            xaxis_title="年度", yaxis_title="金額（萬元）",
            plot_bgcolor="white", paper_bgcolor="white",
            hovermode="x unified",
            legend=dict(bgcolor="rgba(255,255,255,0.8)"),
        )
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig2 = donut_chart(
                ["配現金基金", "配單位基金"],
                [invest_amount * cash_ratio, invest_amount * (1 - cash_ratio)],
                "初始配置比例"
            )
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            fig3 = donut_chart(
                ["期末帳戶值", "累積配息"],
                [final["總帳戶價值(萬)"], final["累積配息(萬)"]],
                f"第 {years} 年資產組成"
            )
            st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.markdown("**不同淨值變動率下的期末總資產比較**")
        scenarios = [-10, -5, 0, 5, 10, 15]
        sc_rows = []
        for vc in scenarios:
            df_s = simulate_fund(invest_amount, years, cash_ratio,
                                 cash_yield, unit_yield, mgmt_fee, vc)
            f = df_s.iloc[-1]
            sc_rows.append({
                "淨值年變動率 (%)": vc,
                "期末帳戶值 (萬)":  f["總帳戶價值(萬)"],
                "累積配息 (萬)":    f["累積配息(萬)"],
                "總資產 (萬)":      round(f["總帳戶價值(萬)"] + f["累積配息(萬)"], 1),
            })
        sc_df = pd.DataFrame(sc_rows)

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=sc_df["淨值年變動率 (%)"].astype(str) + "%",
            y=sc_df["總資產 (萬)"],
            marker_color=[BRAND_DANGER if v < 0 else BRAND_SUCCESS
                          for v in sc_df["淨值年變動率 (%)"]],
            hovertemplate="%{x}<br>總資產: %{y:,.1f}萬<extra></extra>",
        ))
        fig4.add_hline(y=invest_amount, line_dash="dash", line_color=BRAND_PRIMARY,
                       annotation_text=f"本金 {invest_amount} 萬")
        fig4.update_layout(
            title="不同淨值情境下期末總資產",
            xaxis_title="淨值年變動率", yaxis_title="總資產（萬元）",
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(sc_df, use_container_width=True)

    with tab3:
        st.dataframe(
            df.style.format({c: "{:,.2f}" for c in df.columns if c != "年度"}),
            use_container_width=True, height=400
        )
        st.caption("⚠️ 投資有風險，以上模擬不代表實際投資績效。")