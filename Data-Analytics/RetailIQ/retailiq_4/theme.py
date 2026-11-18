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

/*
  RetailIQ ships one deliberate palette (a warm ledger, not a SaaS default)
  and does not adapt to the browser's Light/Dark/System theme setting.
  Every rule below is paired — background AND text color set together,
  with !important — so switching Streamlit's built-in theme toggle can't
  leave one half updated and the other stuck, which is what causes
  invisible (same-color-as-background) text.
*/

:root {{
    color-scheme: light !important;
}}

html, body {{
    color-scheme: light !important;
}}

/* ---- Global surface + text pairing ---- */
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.main, .block-container {{
    background-color: {PAPER} !important;
    color: {INK} !important;
    font-family: 'IBM Plex Sans', sans-serif;
}}

[data-testid="stHeader"] {{
    background-color: {PAPER} !important;
}}

/* Generic text elements: headings, paragraphs, labels, list items */
h1, h2, h3, h4, h5, h6,
p, span, label, li,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * ,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
[data-testid="stWidgetLabel"] {{
    color: {INK} !important;
}}

/* ---- Sidebar: paired background + text, including its own markdown/caption text ---- */
[data-testid="stSidebar"] {{
    background-color: {SURFACE} !important;
    border-right: 1px solid {RULE};
}}
[data-testid="stSidebar"] * {{
    color: {INK} !important;
}}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{
    color: {INK_SOFT} !important;
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
    color: {INK} !important;
}}
.riq-masthead p {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {INK_SOFT} !important;
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
    color: {INK} !important;
    letter-spacing: -0.01em;
}}
.riq-kpi .riq-kpi-label {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    color: {INK_SOFT} !important;
    margin-top: 0.15rem;
}}

/* ---- Section labels ---- */
.riq-section-label {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.8rem;
    color: {INK_SOFT} !important;
    border-bottom: 1px solid {RULE};
    padding-bottom: 0.4rem;
    margin: 0.2rem 0 1rem 0;
}}

/* ---- Tabs: underline style, no pill chrome ---- */
[data-testid="stTabs"] {{
    background-color: transparent !important;
}}
[data-testid="stTabs"] button, [data-testid="stTabs"] button p {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.95rem;
    color: {INK_SOFT} !important;
    background-color: transparent !important;
}}
[data-testid="stTabs"] [aria-selected="true"], [data-testid="stTabs"] [aria-selected="true"] p {{
    color: {INK} !important;
    font-weight: 600;
    border-bottom: 2px solid {BRASS} !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
    background-color: {BRASS} !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-border"] {{
    background-color: {RULE} !important;
}}

/* ---- Buttons ---- */
.stButton > button, .stDownloadButton > button {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {INK} !important;
    color: {PAPER} !important;
    border: 1px solid {INK} !important;
    border-radius: 3px;
    font-weight: 500;
    padding: 0.4rem 1rem;
}}
.stButton > button p, .stDownloadButton > button p {{
    color: {PAPER} !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    background-color: {BRASS_DARK} !important;
    border-color: {BRASS_DARK} !important;
    color: {SURFACE} !important;
}}
.stButton > button:focus-visible {{
    outline: 2px solid {BRASS};
    outline-offset: 2px;
}}

/* Example-question chips: same shape, quieter, ink-soft text on paper */
.riq-chip > button {{
    background-color: {SURFACE} !important;
    color: {INK_SOFT} !important;
    border: 1px solid {RULE} !important;
    font-size: 0.85rem;
    padding: 0.25rem 0.75rem;
}}
.riq-chip > button p {{
    color: {INK_SOFT} !important;
}}
.riq-chip > button:hover {{
    border-color: {BRASS} !important;
    color: {INK} !important;
    background-color: {SURFACE} !important;
}}
.riq-chip > button:hover p {{
    color: {INK} !important;
}}

/* ---- Inputs ---- */
.stTextInput input, .stTextArea textarea {{
    font-family: 'IBM Plex Mono', monospace;
    background-color: {SURFACE} !important;
    border: 1px solid {RULE} !important;
    color: {INK} !important;
    -webkit-text-fill-color: {INK};
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
    color: {INK_SOFT} !important;
    opacity: 1;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {BRASS} !important;
    box-shadow: 0 0 0 1px {BRASS};
}}

/* ---- Alerts: quieter, rule-bordered instead of tinted pill boxes ---- */
[data-testid="stAlert"] {{
    border-radius: 2px;
    border: 1px solid {RULE} !important;
    background-color: {SURFACE} !important;
}}
[data-testid="stAlert"] * {{
    color: {INK} !important;
}}
[data-testid="stAlertContentInfo"] svg, [data-testid="stAlertContentWarning"] svg,
[data-testid="stAlertContentError"] svg, [data-testid="stAlertContentSuccess"] svg {{
    fill: {INK} !important;
}}

/* ---- Dataframes / tables ---- */
[data-testid="stDataFrame"] {{
    font-family: 'IBM Plex Mono', monospace;
    border: 1px solid {RULE};
}}
[data-testid="stDataFrame"] * {{
    color: {INK} !important;
    background-color: {SURFACE} !important;
}}

/* ---- Code blocks (SQL) — dark chip on purpose, so text must be paper-colored ---- */
.stCodeBlock, pre {{
    background-color: {INK} !important;
}}
.stCodeBlock *, pre code, pre span {{
    font-family: 'IBM Plex Mono', monospace !important;
    color: {PAPER} !important;
}}
:not(pre) > code {{
    color: {INK} !important;
    background-color: {RULE} !important;
}}

/* ---- Expander ---- */
[data-testid="stExpander"] {{
    background-color: {SURFACE} !important;
    border: 1px solid {RULE} !important;
}}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{
    color: {INK} !important;
}}

/* ---- Metric (used sparingly) ---- */
[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace;
    color: {INK} !important;
}}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {INK_SOFT} !important;
}}

/* ---- Sliders ---- */
[data-testid="stSlider"] [role="slider"] {{
    background-color: {BRASS} !important;
}}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {{
    color: {INK_SOFT} !important;
}}

/* ---- Toggle / checkbox ---- */
[data-testid="stToggle"] label p, [data-testid="stCheckbox"] label p {{
    color: {INK} !important;
}}

/* ---- Divider ---- */
hr {{
    border-color: {RULE} !important;
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
    """Applies the shared visual style to a Plotly figure.
    Backgrounds are set explicitly (not transparent) so the chart always
    reads correctly regardless of the page's resolved theme — a transparent
    background would silently inherit whatever's behind it, including a
    dark theme background that'd make our ink-colored text invisible."""
    fig.update_layout(
        font_family="IBM Plex Sans, sans-serif",
        font_color=INK,
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        title_font_family="Fraunces, serif",
        title_font_size=18,
        title_font_color=INK,
        margin=dict(l=10, r=10, t=48, b=10),
        height=height,
        colorway=CHART_SEQUENCE,
        legend=dict(bgcolor=PAPER, font_color=INK),
    )
    fig.update_xaxes(gridcolor=RULE, zerolinecolor=RULE, color=INK)
    fig.update_yaxes(gridcolor=RULE, zerolinecolor=RULE, color=INK)
    return fig
