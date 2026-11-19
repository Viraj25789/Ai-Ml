
"""
RetailIQ Design System
Clean, modern analytics dashboard with consistent light-theme contrast.
"""

# ---------------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------------

INK = "#172B4D"
INK_SOFT = "#52647A"

PAPER = "#F4F7FB"
SURFACE = "#FFFFFF"
RULE = "#DFE6EF"

BRASS = "#2563EB"
BRASS_DARK = "#1D4ED8"
TEAL = "#0F766E"
ROSE = "#DC4C64"

CHART_SEQUENCE = [
    BRASS,
    TEAL,
    "#8B5CF6",
    "#E59B35",
    ROSE,
    "#64748B",
]

# ---------------------------------------------------------
# GLOBAL CSS
# ---------------------------------------------------------

CSS = f"""
<style>

/* ---------- Global application ---------- */

:root {{
    color-scheme: light;
}}

html, body {{
    background-color: {PAPER} !important;
}}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {{
    background-color: {PAPER} !important;
    color: {INK} !important;
}}

[data-testid="stHeader"] {{
    background-color: {PAPER} !important;
}}

.block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}}

/* ---------- Typography ---------- */

html, body, [class*="st-"] {{
    font-family: "Inter", "Segoe UI", sans-serif;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {INK} !important;
    font-weight: 650 !important;
    letter-spacing: -0.025em;
}}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {{
    color: {INK} !important;
    line-height: 1.65;
}}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {{
    color: {INK_SOFT} !important;
}}

/* ---------- Sidebar ---------- */

[data-testid="stSidebar"] {{
    background-color: {SURFACE} !important;
    border-right: 1px solid {RULE};
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {{
    color: {INK} !important;
}}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
    color: {INK_SOFT} !important;
}}

/* ---------- Masthead ---------- */

.riq-masthead {{
    background: linear-gradient(120deg, #FFFFFF 0%, #EFF5FF 100%);
    border: 1px solid {RULE};
    border-left: 5px solid {BRASS};
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.8rem;
}}

.riq-masthead h1 {{
    color: {INK} !important;
    font-size: 2.35rem;
    font-weight: 750;
    margin: 0;
    line-height: 1.2;
}}

.riq-masthead p {{
    color: {INK_SOFT} !important;
    margin: 0.45rem 0 0 0;
    font-size: 1rem;
}}

/* ---------- KPI cards ---------- */

.riq-kpi-row {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin-bottom: 1.8rem;
}}

.riq-kpi {{
    background-color: {SURFACE};
    border: 1px solid {RULE};
    border-top: 4px solid {BRASS};
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    min-width: 0;
    box-shadow: 0 2px 8px rgba(23, 43, 77, 0.04);
}}

.riq-kpi-value {{
    color: {INK} !important;
    font-size: 1.7rem;
    font-weight: 750;
    overflow-wrap: anywhere;
}}

.riq-kpi-label {{
    color: {INK_SOFT} !important;
    font-size: 0.88rem;
    margin-top: 0.35rem;
    font-weight: 500;
}}

/* ---------- Section labels ---------- */

.riq-section-label {{
    color: {INK_SOFT} !important;
    font-size: 0.92rem;
    line-height: 1.6;
    padding: 0.8rem 1rem;
    background-color: #EAF0F8;
    border: 1px solid {RULE};
    border-radius: 9px;
    margin-bottom: 1rem;
}}

/* ---------- Tabs ---------- */

[data-testid="stTabs"] {{
    background: transparent !important;
}}

[data-testid="stTabs"] [role="tablist"] {{
    gap: 0.5rem;
    border-bottom: 1px solid {RULE};
}}

[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important;
    color: {INK_SOFT} !important;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
    padding: 0.75rem 1rem;
}}

[data-testid="stTabs"] button[role="tab"] p {{
    color: {INK_SOFT} !important;
}}

[data-testid="stTabs"] button[aria-selected="true"] {{
    background-color: {SURFACE} !important;
    border-bottom: 3px solid {BRASS} !important;
}}

[data-testid="stTabs"] button[aria-selected="true"] p {{
    color: {BRASS_DARK} !important;
    font-weight: 700;
}}

/* ---------- Buttons ---------- */

.stButton > button,
.stDownloadButton > button {{
    background-color: {BRASS} !important;
    color: #FFFFFF !important;
    border: 1px solid {BRASS} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    min-height: 2.5rem;
    transition: background-color 0.15s ease;
}}

.stButton > button p,
.stDownloadButton > button p {{
    color: #FFFFFF !important;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background-color: {BRASS_DARK} !important;
    border-color: {BRASS_DARK} !important;
}}

.stButton > button:focus-visible {{
    outline: 3px solid #93C5FD !important;
    outline-offset: 2px;
}}

/* ---------- Example question buttons ---------- */

.riq-chip > div > button {{
    background-color: {SURFACE} !important;
    color: {INK} !important;
    border: 1px solid {RULE} !important;
    border-radius: 9px !important;
}}

.riq-chip > div > button p {{
    color: {INK} !important;
}}

.riq-chip > div > button:hover {{
    border-color: {BRASS} !important;
    background-color: #EFF5FF !important;
}}

/* ---------- Text inputs and text areas ---------- */

.stTextInput input,
.stTextArea textarea {{
    background-color: {SURFACE} !important;
    color: {INK} !important;
    -webkit-text-fill-color: {INK} !important;
    border: 1px solid #C8D3E0 !important;
    border-radius: 8px !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: {INK_SOFT} !important;
    -webkit-text-fill-color: {INK_SOFT} !important;
    opacity: 1;
}}

.stTextInput input:focus,
.stTextArea textarea:focus {{
    border-color: {BRASS} !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15) !important;
}}

/* ---------- Select boxes and multiselect ---------- */

[data-baseweb="select"] > div {{
    background-color: {SURFACE} !important;
    border-color: #C8D3E0 !important;
    border-radius: 8px !important;
}}

[data-baseweb="select"] input,
[data-baseweb="select"] span {{
    color: {INK} !important;
}}

/* ---------- Widget labels ---------- */

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stCheckbox"] label,
[data-testid="stToggle"] label {{
    color: {INK} !important;
    font-weight: 550;
}}

/* ---------- Alerts ---------- */

[data-testid="stAlert"] {{
    border-radius: 9px !important;
    border: 1px solid {RULE} !important;
}}

[data-testid="stAlert"] p {{
    color: {INK} !important;
}}

/* ---------- Expanders ---------- */

[data-testid="stExpander"] {{
    background-color: {SURFACE} !important;
    border: 1px solid {RULE} !important;
    border-radius: 9px !important;
}}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {{
    color: {INK} !important;
    font-weight: 600;
}}

/* ---------- Data tables ---------- */

[data-testid="stDataFrame"] {{
    border: 1px solid {RULE};
    border-radius: 9px;
    overflow: hidden;
}}

/* ---------- Metrics ---------- */

[data-testid="stMetric"] {{
    background-color: {SURFACE};
    border: 1px solid {RULE};
    border-radius: 10px;
    padding: 0.9rem;
}}

[data-testid="stMetricValue"] {{
    color: {INK} !important;
    font-weight: 750;
}}

[data-testid="stMetricLabel"] {{
    color: {INK_SOFT} !important;
}}

/* ---------- SQL code blocks ---------- */

.stCodeBlock,
pre {{
    background-color: #172B4D !important;
    border-radius: 9px !important;
}}

.stCodeBlock pre,
.stCodeBlock code,
pre code {{
    color: #F8FAFC !important;
    font-family: "Consolas", monospace !important;
}}

/* ---------- Slider ---------- */

[data-testid="stSlider"] {{
    color: {INK} !important;
}}

/* ---------- Dividers ---------- */

hr {{
    border-color: {RULE} !important;
}}

/* ---------- Responsive layout ---------- */

@media (max-width: 900px) {{
    .riq-kpi-row {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}

    .riq-masthead h1 {{
        font-size: 1.9rem;
    }}
}}

@media (max-width: 520px) {{
    .riq-kpi-row {{
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
    }}

    .riq-kpi {{
        padding: 0.8rem;
    }}

    .riq-kpi-value {{
        font-size: 1.3rem;
    }}

    .block-container {{
        padding-left: 1rem;
        padding-right: 1rem;
    }}
}}

</style>
"""


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def inject():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def masthead(title: str, subtitle: str):
    import streamlit as st
    st.markdown(
        f'<div class="riq-masthead">'
        f'<h1>{title}</h1>'
        f'<p>{subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def kpi_row(items):
    """Render KPI cards from a list of (label, value) tuples."""
    import streamlit as st

    cells = "".join(
        f'<div class="riq-kpi">'
        f'<div class="riq-kpi-value">{value}</div>'
        f'<div class="riq-kpi-label">{label}</div>'
        f'</div>'
        for label, value in items
    )

    st.markdown(
        f'<div class="riq-kpi-row">{cells}</div>',
        unsafe_allow_html=True,
    )


def section_label(text: str):
    import streamlit as st
    st.markdown(
        f'<div class="riq-section-label">{text}</div>',
        unsafe_allow_html=True,
    )


def apply_chart_style(fig, height=380):
    """Apply the RetailIQ palette to Plotly charts."""

    fig.update_layout(
        font_family="Inter, sans-serif",
        font_color=INK,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        title_font_size=18,
        title_font_color=INK,
        title_font_family="Inter, sans-serif",
        margin=dict(l=15, r=15, t=55, b=15),
        height=height,
        colorway=CHART_SEQUENCE,
        legend=dict(
            bgcolor=SURFACE,
            font_color=INK,
        ),
    )

    fig.update_xaxes(
        gridcolor=RULE,
        zerolinecolor=RULE,
        color=INK_SOFT,
    )

    fig.update_yaxes(
        gridcolor=RULE,
        zerolinecolor=RULE,
        color=INK_SOFT,
    )

    return fig
