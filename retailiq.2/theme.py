"""
theme.py — RetailIQ's design system.

Concept: a shopkeeper's ledger reimagined as a dashboard. Warm paper
background, a serif masthead like a ledger book's title page, monospace
for figures (like a receipt or POS display), hairline rules instead of
card shadows, brass and deep teal as the two accent colors.

Palette
-------
ink        #1C2430   primary text
ink_soft   #5B6472   secondary text / captions
paper      #F6F4EF   app background
surface    #FFFFFF   card / input backgrounds
rule       #DDD6C4   hairline dividers
brass      #B8843A   primary accent (positive emphasis, active states)
teal       #1F6F5C   secondary accent (categories, secondary series)
rose       #A23E48   tertiary accent (alerts, negative values)

Type
----
Display : "Fraunces"      — masthead, section headers
UI      : "IBM Plex Sans" — body text, labels, buttons
Data    : "IBM Plex Mono" — KPI figures, tables, SQL code
"""

INK = "#1C2430"
INK_SOFT = "#5B6472"
PAPER = "#F6F4EF"
SURFACE = "#FFFFFF"
RULE = "#DDD6C4"
BRASS = "#B8843A"
BRASS_DARK = "#96692A"
TEAL = "#1F6F5C"
ROSE = "#A23E48"

CHART_SEQUENCE = [BRASS, TEAL, ROSE, INK_SOFT, "#7A8B99", "#D8B45C"]

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"], [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {INK};
}}

[data-testid="stAppViewContainer"] {{
    background-color: {PAPER};
}}

[data-testid="stHeader"] {{
    background-color: {PAPER};
}}

[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {RULE};
}}

/* ---- Masthead ---- */
.riq-masthead {{
    border-bottom: 2px solid {INK};
    padding-bottom: 0.9rem;
    margin-bottom: 1.6rem;
}}
.riq-masthead h1 {{
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 2.6rem;
    line-height: 1.1;
    margin: 0;
    color: {INK};
}}
.riq-masthead p {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {INK_SOFT};
    font-size: 0.98rem;
    margin: 0.35rem 0 0 0;
}}

/* ---- KPI row ---- */
.riq-kpi-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0;
    margin-bottom: 1.8rem;
}}
.riq-kpi {{
    border-top: 2px solid {INK};
    padding: 0.7rem 1.2rem 0 0;
}}
.riq-kpi .riq-kpi-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.9rem;
    font-weight: 500;
    color: {INK};
    letter-spacing: -0.01em;
}}
.riq-kpi .riq-kpi-label {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    color: {INK_SOFT};
    margin-top: 0.15rem;
}}

/* ---- Section labels ---- */
.riq-section-label {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.8rem;
    color: {INK_SOFT};
    border-bottom: 1px solid {RULE};
    padding-bottom: 0.4rem;
    margin: 0.2rem 0 1rem 0;
}}

/* ---- Tabs: underline style, no pill chrome ---- */
[data-testid="stTabs"] button {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.95rem;
    color: {INK_SOFT};
    background-color: transparent;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    color: {INK} !important;
    font-weight: 600;
    border-bottom: 2px solid {BRASS} !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
    background-color: {BRASS};
}}
[data-testid="stTabs"] [data-baseweb="tab-border"] {{
    background-color: {RULE};
}}

/* ---- Buttons ---- */
.stButton > button, .stDownloadButton > button {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {INK};
    color: {PAPER};
    border: 1px solid {INK};
    border-radius: 3px;
    font-weight: 500;
    padding: 0.4rem 1rem;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    background-color: {BRASS_DARK};
    border-color: {BRASS_DARK};
    color: {SURFACE};
}}
.stButton > button:focus-visible {{
    outline: 2px solid {BRASS};
    outline-offset: 2px;
}}

/* Example-question chips: same shape, quieter, ink-soft text on paper */
.riq-chip > button {{
    background-color: {SURFACE};
    color: {INK_SOFT};
    border: 1px solid {RULE};
    font-size: 0.85rem;
    padding: 0.25rem 0.75rem;
}}
.riq-chip > button:hover {{
    border-color: {BRASS};
    color: {INK};
    background-color: {SURFACE};
}}

/* ---- Inputs ---- */
.stTextInput > div > div > input, .stTextArea textarea {{
    font-family: 'IBM Plex Mono', monospace;
    background-color: {SURFACE};
    border: 1px solid {RULE};
    color: {INK};
}}
.stTextInput > div > div > input:focus, .stTextArea textarea:focus {{
    border-color: {BRASS};
    box-shadow: 0 0 0 1px {BRASS};
}}

/* ---- Alerts: quieter, rule-bordered instead of tinted pill boxes ---- */
[data-testid="stAlert"] {{
    border-radius: 2px;
    border: 1px solid {RULE};
    background-color: {SURFACE};
}}

/* ---- Dataframes / tables ---- */
[data-testid="stDataFrame"] {{
    font-family: 'IBM Plex Mono', monospace;
    border: 1px solid {RULE};
}}

/* ---- Code blocks (SQL) ---- */
.stCodeBlock, pre, code {{
    font-family: 'IBM Plex Mono', monospace !important;
    background-color: {INK} !important;
}}

/* ---- Metric (used sparingly) ---- */
[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace;
    color: {INK};
}}
[data-testid="stMetricLabel"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {INK_SOFT};
}}

/* ---- Sliders ---- */
[data-testid="stSlider"] [role="slider"] {{
    background-color: {BRASS};
}}

/* ---- Divider ---- */
hr {{
    border-color: {RULE};
}}
</style>
"""


def inject():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def masthead(title: str, subtitle: str):
    import streamlit as st
    st.markdown(
        f'<div class="riq-masthead"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def kpi_row(items):
    """items: list of (label, value) tuples."""
    import streamlit as st
    cells = "".join(
        f'<div class="riq-kpi"><div class="riq-kpi-value">{value}</div>'
        f'<div class="riq-kpi-label">{label}</div></div>'
        for label, value in items
    )
    st.markdown(f'<div class="riq-kpi-row">{cells}</div>', unsafe_allow_html=True)


def section_label(text: str):
    import streamlit as st
    st.markdown(f'<div class="riq-section-label">{text}</div>', unsafe_allow_html=True)


def apply_chart_style(fig, height=380):
    """Applies the shared visual style to a Plotly figure."""
    fig.update_layout(
        font_family="IBM Plex Sans, sans-serif",
        font_color=INK,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font_family="Fraunces, serif",
        title_font_size=18,
        title_font_color=INK,
        margin=dict(l=10, r=10, t=48, b=10),
        height=height,
        colorway=CHART_SEQUENCE,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=RULE, zerolinecolor=RULE)
    fig.update_yaxes(gridcolor=RULE, zerolinecolor=RULE)
    return fig
