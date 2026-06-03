"""
統一圖表樣式
"""
import plotly.graph_objects as go
import pandas as pd

BRAND_PRIMARY = "#1B4F72"
BRAND_ACCENT  = "#2E86C1"
BRAND_GOLD    = "#D4AC0D"
BRAND_SUCCESS = "#1E8449"
BRAND_DANGER  = "#C0392B"
BRAND_GRAY    = "#566573"

PALETTE = [BRAND_PRIMARY, BRAND_ACCENT, BRAND_GOLD, BRAND_SUCCESS, BRAND_DANGER]

LAYOUT_BASE = dict(
    font=dict(family="Arial", size=13, color="#2C3E50"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=40, r=30, t=50, b=40),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#DDD", borderwidth=1),
    hovermode="x unified",
)


def line_chart(df, x, y_cols, title, y_label="", colors=None):
    colors = colors or PALETTE
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], name=col,
            mode="lines",
            line=dict(color=colors[i % len(colors)], width=2.5),
            hovertemplate=f"%{{y:,.1f}}<extra>{col}</extra>",
        ))
    fig.update_layout(**LAYOUT_BASE,
                      title=dict(text=title, font=dict(size=16, color=BRAND_PRIMARY)),
                      yaxis_title=y_label, xaxis_title=x)
    return fig


def area_chart(df, x, y_cols, title, y_label=""):
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        c = PALETTE[i % len(PALETTE)]
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], name=col,
            fill="tozeroy" if i == 0 else "tonexty",
            mode="lines",
            line=dict(color=c, width=1.5),
            fillcolor=f"rgba({r},{g},{b},0.15)",
        ))
    fig.update_layout(**LAYOUT_BASE,
                      title=dict(text=title, font=dict(size=16, color=BRAND_PRIMARY)),
                      yaxis_title=y_label, xaxis_title=x)
    return fig


def donut_chart(labels, values, title):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=PALETTE, line=dict(color="white", width=2)),
        hovertemplate="%{label}: %{value:,.1f} (%{percent})<extra></extra>",
        textinfo="label+percent",
    ))
    fig.update_layout(**LAYOUT_BASE,
                      title=dict(text=title, font=dict(size=16, color=BRAND_PRIMARY)))
    return fig


def metric_card_html(label, value, delta="", color=BRAND_PRIMARY):
    delta_html = f'<div style="font-size:13px;color:#7F8C8D;margin-top:2px">{delta}</div>' if delta else ""
    return f"""
    <div style="background:white;border-radius:10px;padding:20px 24px;
                box-shadow:0 2px 8px rgba(0,0,0,0.08);border-left:4px solid {color};
                min-width:140px;">
        <div style="font-size:13px;color:#7F8C8D;margin-bottom:6px">{label}</div>
        <div style="font-size:26px;font-weight:700;color:{color}">{value}</div>
        {delta_html}
    </div>
    """