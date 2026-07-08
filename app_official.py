
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import base64
from pathlib import Path

# =====================================================
# SBL LOGO - SOLO VISUALE
# =====================================================
def _sbl_logo_src():
    candidates = [
        "/content/logo_sbl.png",
        "logo_sbl.png",
        "/content/logo_sbl.webp",
        "logo_sbl.webp",
    ]

    for name in candidates:
        p = Path(name)
        if p.exists():
            suffix = p.suffix.lower()
            if suffix == ".png":
                mime = "image/png"
            elif suffix == ".webp":
                mime = "image/webp"
            else:
                mime = "image/jpeg"

            with open(p, "rb") as f:
                return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

    return ""

SBL_LOGO_SRC = _sbl_logo_src()
SBL_HEADER_LOGO = (
    f"<img class='sbl-header-logo' src='{SBL_LOGO_SRC}' />"
    if SBL_LOGO_SRC
    else "🏟️"
)
# =====================================================




# =====================================================
# CONFIGURAZIONE PAGINA
# =====================================================

st.set_page_config(
    page_title="SIAE Sport Dashboard",
    page_icon="🏟️",
    layout="wide"
)








# =====================================================
# SBL FORMAT PATCH V2 - MASSIMO 2 DECIMALI, SOLO VISUALE
# =====================================================
def _sbl_to_max_2_decimals_text(text):
    import re

    if not isinstance(text, str):
        return text

    # Converte solo numeri con almeno 3 cifre decimali: 12.3456 -> 12.35
    def repl(match):
        raw = match.group(0)
        try:
            return f"{float(raw):.2f}"
        except Exception:
            return raw

    return re.sub(r"(?<![A-Za-z0-9_])-?\d+\.\d{3,}(?![A-Za-z0-9_])", repl, text)


def _sbl_format_number_max_2(value):
    try:
        import numpy as np

        if isinstance(value, (float, np.floating)):
            if abs(float(value) - round(float(value))) < 1e-9:
                return f"{float(value):,.0f}"
            return f"{float(value):,.2f}"

        return value
    except Exception:
        return value


def _sbl_round_display_object(data):
    try:
        import pandas as pd
        import numpy as np

        if isinstance(data, pd.io.formats.style.Styler):
            return data.format(precision=2, na_rep="")

        if isinstance(data, pd.DataFrame):
            out = data.copy()
            numeric_cols = out.select_dtypes(include=[np.number]).columns
            out[numeric_cols] = out[numeric_cols].round(2)
            return out

        if isinstance(data, pd.Series):
            if pd.api.types.is_numeric_dtype(data):
                return data.round(2)
            return data

        if isinstance(data, float):
            return _sbl_format_number_max_2(data)

        return data

    except Exception:
        return data


def _sbl_fix_plotly_figure_max_2(fig):
    try:
        import re

        def fix_template(s):
            if not isinstance(s, str):
                return s

            s = re.sub(
                r"%\{([a-zA-Z0-9_]+):(,?)\.(\d+)f\}",
                lambda m: f"%{{{m.group(1)}:{m.group(2)}.2f}}" if int(m.group(3)) > 2 else m.group(0),
                s
            )

            s = re.sub(
                r":(,?)\.(\d+)f",
                lambda m: f":{m.group(1)}.2f" if int(m.group(2)) > 2 else m.group(0),
                s
            )

            return s

        for tr in fig.data:
            if hasattr(tr, "hovertemplate"):
                tr.hovertemplate = fix_template(tr.hovertemplate)

            if hasattr(tr, "texttemplate"):
                tr.texttemplate = fix_template(tr.texttemplate)

            # Arrotonda solo le etichette testuali, non i dati del grafico
            if hasattr(tr, "text") and tr.text is not None:
                try:
                    new_text = []
                    for x in tr.text:
                        if isinstance(x, float):
                            new_text.append(_sbl_format_number_max_2(x))
                        else:
                            new_text.append(x)
                    tr.text = new_text
                except Exception:
                    pass

        return fig

    except Exception:
        return fig


if "_SBL_2DEC_PATCH_V2_ACTIVE" not in globals():
    _SBL_2DEC_PATCH_V2_ACTIVE = True

    _original_st_dataframe_2dec_v2 = st.dataframe
    _original_st_table_2dec_v2 = st.table
    _original_st_metric_2dec_v2 = st.metric
    _original_st_markdown_2dec_v2 = st.markdown
    _original_st_write_2dec_v2 = st.write
    _original_st_plotly_chart_2dec_v2 = st.plotly_chart

    def _sbl_dataframe_2dec_v2(data=None, *args, **kwargs):
        return _original_st_dataframe_2dec_v2(_sbl_round_display_object(data), *args, **kwargs)

    def _sbl_table_2dec_v2(data=None, *args, **kwargs):
        return _original_st_table_2dec_v2(_sbl_round_display_object(data), *args, **kwargs)

    def _sbl_metric_2dec_v2(label, value, delta=None, *args, **kwargs):
        value = _sbl_format_number_max_2(value)
        delta = _sbl_format_number_max_2(delta)
        return _original_st_metric_2dec_v2(label, value, delta, *args, **kwargs)

    def _sbl_markdown_2dec_v2(body, *args, **kwargs):
        body = _sbl_to_max_2_decimals_text(body)
        return _original_st_markdown_2dec_v2(body, *args, **kwargs)

    def _sbl_write_2dec_v2(*args, **kwargs):
        args = tuple(_sbl_round_display_object(a) for a in args)
        return _original_st_write_2dec_v2(*args, **kwargs)

    def _sbl_plotly_chart_2dec_v2(fig_or_data, *args, **kwargs):
        fig_or_data = _sbl_fix_plotly_figure_max_2(fig_or_data)
        return _original_st_plotly_chart_2dec_v2(fig_or_data, *args, **kwargs)

    st.dataframe = _sbl_dataframe_2dec_v2
    st.table = _sbl_table_2dec_v2
    st.metric = _sbl_metric_2dec_v2
    st.markdown = _sbl_markdown_2dec_v2
    st.write = _sbl_write_2dec_v2
    st.plotly_chart = _sbl_plotly_chart_2dec_v2
# =====================================================

# =====================================================
# SBL FORMAT PATCH - MASSIMO 2 DECIMALI, SOLO VISUALE
# =====================================================
def _sbl_format_metric_value(value):
    try:
        if isinstance(value, float):
            return f"{value:,.2f}"
        return value
    except Exception:
        return value


def _sbl_round_dataframe_for_display(data):
    try:
        import pandas as pd
        import numpy as np

        if isinstance(data, pd.io.formats.style.Styler):
            return data.format(precision=2, na_rep="")

        if isinstance(data, pd.DataFrame):
            out = data.copy()
            numeric_cols = out.select_dtypes(include=[np.number]).columns
            out[numeric_cols] = out[numeric_cols].round(2)
            return out

        if isinstance(data, pd.Series):
            if pd.api.types.is_numeric_dtype(data):
                return data.round(2)
            return data

        return data

    except Exception:
        return data


if "_SBL_2DEC_PATCH_ACTIVE" not in globals():
    _SBL_2DEC_PATCH_ACTIVE = True

    _original_st_dataframe = st.dataframe
    _original_st_table = st.table
    _original_st_metric = st.metric

    def _sbl_dataframe_2dec(data=None, *args, **kwargs):
        data = _sbl_round_dataframe_for_display(data)
        return _original_st_dataframe(data, *args, **kwargs)

    def _sbl_table_2dec(data=None, *args, **kwargs):
        data = _sbl_round_dataframe_for_display(data)
        return _original_st_table(data, *args, **kwargs)

    def _sbl_metric_2dec(label, value, delta=None, *args, **kwargs):
        value = _sbl_format_metric_value(value)
        delta = _sbl_format_metric_value(delta)
        return _original_st_metric(label, value, delta, *args, **kwargs)

    st.dataframe = _sbl_dataframe_2dec
    st.table = _sbl_table_2dec
    st.metric = _sbl_metric_2dec
# =====================================================

# =====================================================
# SBL UI PATCH - SOLO VISUALE
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
    background: linear-gradient(135deg, #EAF9FD 0%, #B7F1FA 45%, #39BDE8 100%) !important;
    color: #0D2D44 !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    padding-top: 1.6rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: none !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, #0D2D44 0%, #174C67 45%, #03789C 75%, #27BBE8 100%) !important;
    color: #ffffff !important;
    box-shadow: 4px 0 22px rgba(13, 45, 68, 0.25);
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] label {
    color: #D9F8FF !important;
    font-weight: 600 !important;
}

/* BRAND SIDEBAR */
.sbl-sidebar-brand {
    margin-bottom: 1.1rem;
}

.sbl-sidebar-logo {
    width: 100px;
    height: 100px;
    border-radius: 18px;
    background: rgba(255,255,255,0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    overflow: hidden;
}

.sbl-sidebar-logo img {
    width: 90px;
    height: 90px;
    object-fit: contain;
    border-radius: 50%;
    background: #ffffff;
}

.sbl-sidebar-title {
    font-size: 1.35rem;
    font-weight: 800;
    line-height: 1.05;
    color: #ffffff !important;
    margin-bottom: 0.35rem;
}

.sbl-sidebar-sub {
    font-size: 0.82rem;
    color: #D9F8FF !important;
    line-height: 1.35;
}

.sbl-sidebar-sep {
    height: 1px;
    background: rgba(255,255,255,0.22);
    margin: 1.2rem 0;
}

/* RADIO SEZIONI */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.5rem !important;
    width: 100% !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    min-height: 54px !important;
    box-sizing: border-box !important;
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.20) !important;
    border-radius: 10px !important;
    padding: 0.65rem 0.8rem !important;
    margin: 0 !important;
    transition: all 0.15s ease !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.16) !important;
    transform: translateX(2px);
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    margin: 0 !important;
    font-size: 0.98rem !important;
    line-height: 1.2 !important;
    white-space: normal !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label > div {
    width: 100% !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label input {
    margin-right: 0.65rem !important;
    flex-shrink: 0 !important;
}

/* SELECTBOX */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stMultiSelect"] > div > div {
    border-radius: 10px !important;
    border: 1px solid #A5E9F7 !important;
}

section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
}

/* TITOLI */
h1, h2, h3 {
    color: #0D2D44 !important;
    font-weight: 800 !important;
}

p, span, label, div {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
}

/* LOGO NEL TITOLO */
.sbl-header-logo {
    width: 66px;
    height: 66px;
    object-fit: contain;
    vertical-align: middle;
    margin-right: 16px;
    border-radius: 50%;
    background: #ffffff;
    border: 2px solid #F0951D;
    padding: 3px;
    box-shadow: 0 4px 14px rgba(13,45,68,0.18);
}

/* CARD / TABELLE */
div[data-testid="stMetric"],
.kpi-card {
    background: #ffffff !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 24px rgba(13,45,68,0.10) !important;
    border: 1px solid #CDEFF7 !important;
}

[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 8px 24px rgba(13,45,68,0.10) !important;
}

.js-plotly-plot {
    border-radius: 16px !important;
}

/* BOTTONI */
.stButton > button {
    background: #00649C !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #1C9FE8 !important;
    font-weight: 700 !important;
}

.stButton > button:hover {
    background: #03789C !important;
    border-color: #27BBE8 !important;
}
</style>
""", unsafe_allow_html=True)

px.defaults.color_discrete_sequence = [
    "#00649C",
    "#00A2D2",
    "#27BBE8",
    "#10B6E8",
    "#03789C",
    "#E85933",
    "#E8AA05",
]
px.defaults.template = "plotly_white"
# =====================================================

# =====================================================
# FUNZIONI
# =====================================================

@st.cache_data
def load_data():
    df_finale = pd.read_csv("df_finale_siae_sport.csv")
    kpi_regioni = pd.read_csv("kpi_regioni.csv")
    kpi_cards = pd.read_csv("kpi_cards_2021_completa.csv")
    tabella_macroaree = pd.read_csv("tabella_macroaree.csv")
    tabella_categorie_2021 = pd.read_csv("tabella_categorie_2021.csv")

    kpi_cards.columns = [c.lower().strip() for c in kpi_cards.columns]

    if "unita" not in kpi_cards.columns:
        kpi_cards["unita"] = ""

    return df_finale, kpi_regioni, kpi_cards, tabella_macroaree, tabella_categorie_2021


def format_value(value, unit=""):
    if pd.isna(value):
        return "n.d."

    if isinstance(value, str):
        return value

    try:
        value = float(value)
    except:
        return str(value)

    if unit == "%":
        return f"{value:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")

    if unit in ["euro", "euro/evento"]:
        return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

    if unit in ["persone/evento"]:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if abs(value) >= 1000:
        return f"{value:,.0f}".replace(",", ".")

    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_kpi_value(kpi_cards, kpi_name):
    row = kpi_cards[kpi_cards["kpi"] == kpi_name]
    if row.empty:
        return "n.d.", ""
    valore = row.iloc[0]["valore"]
    unita = row.iloc[0]["unita"]
    return valore, unita


def kpi_card(title, value, unit=""):
    value_fmt = format_value(value, unit)

    st.markdown(
        f"""
        <div style="
            background-color:#ffffff;
            padding:20px;
            border-radius:14px;
            box-shadow:0 2px 8px rgba(0,0,0,0.08);
            border:1px solid #eeeeee;
            min-height:120px;
        ">
            <div style="font-size:15px; color:#666666; margin-bottom:10px;">
                {title}
            </div>
            <div style="font-size:28px; font-weight:700; color:#111827;">
                {value_fmt}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def plot_horizontal_bar(df, x_col, y_col, title, x_label):
    df_plot = df[[x_col, y_col]].dropna().copy()
    df_plot = df_plot.sort_values(x_col, ascending=True)

    fig = px.bar(
        df_plot,
        x=x_col,
        y=y_col,
        orientation="h",
        title=title,
        labels={x_col: x_label, y_col: ""}
    )

    fig.update_layout(
        height=650,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# CARICAMENTO DATI
# =====================================================

df_finale, kpi_regioni, kpi_cards, tabella_macroaree, tabella_categorie_2021 = load_data()


# =====================================================
# TITOLO
# =====================================================

st.markdown(f"<h1>{SBL_HEADER_LOGO} SIAE Sport Events Italy Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    """
    Dashboard interattiva per l'analisi degli eventi sportivi SIAE in Italia,
    con focus su distribuzione territoriale, trend temporali, KPI regionali,
    pandemia e dettaglio categorie sportive 2021.
    """
)


# =====================================================
# SIDEBAR
# =====================================================


# =====================================================
# SBL SIDEBAR BRAND - SOLO VISUALE
# =====================================================
if SBL_LOGO_SRC:
    st.sidebar.markdown(f"""
    <div class="sbl-sidebar-brand">
        <div class="sbl-sidebar-logo">
            <img src="{SBL_LOGO_SRC}" alt="SBL Consultancy logo">
        </div>
        <div class="sbl-sidebar-title">SIAE Sport</div>
        <div class="sbl-sidebar-sub">Eventi sportivi in Italia · 2004–2021</div>
    </div>
    <div class="sbl-sidebar-sep"></div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="sbl-sidebar-brand">
        <div class="sbl-sidebar-title">SIAE Sport</div>
        <div class="sbl-sidebar-sub">Eventi sportivi in Italia · 2004–2021</div>
    </div>
    <div class="sbl-sidebar-sep"></div>
    """, unsafe_allow_html=True)
# =====================================================


pagina = st.sidebar.radio(
    "Seleziona sezione",
    [
        "Panoramica nazionale",
        "Trend temporali",
        "Ranking regioni",
        "Mappa Italia",
        "Focus categorie 2021",
        "Scheda singola regione",
        "Tabelle dati"
    ]
)


# =====================================================
# PAGINA 1 - PANORAMICA NAZIONALE
# =====================================================

if pagina == "Panoramica nazionale":

    st.header("Panoramica nazionale 2021")

    st.subheader("KPI principali")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        valore, unita = get_kpi_value(kpi_cards, "Totale spettacoli")
        kpi_card("Totale spettacoli", valore, unita)

    with col2:
        valore, unita = get_kpi_value(kpi_cards, "Totale persone")
        kpi_card("Totale persone", valore, unita)

    with col3:
        valore, unita = get_kpi_value(kpi_cards, "Totale botteghino")
        kpi_card("Totale botteghino", valore, unita)

    with col4:
        valore, unita = get_kpi_value(kpi_cards, "Totale pubblico")
        kpi_card("Totale pubblico", valore, unita)


    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        valore, unita = get_kpi_value(kpi_cards, "Persone medie per spettacolo")
        kpi_card("Persone medie per spettacolo", valore, unita)

    with col6:
        valore, unita = get_kpi_value(kpi_cards, "Botteghino medio per spettacolo")
        kpi_card("Botteghino medio per spettacolo", valore, unita)

    with col7:
        valore, unita = get_kpi_value(kpi_cards, "Variazione YoY spettacoli 2021")
        kpi_card("YoY spettacoli 2021", valore, unita)

    with col8:
        valore, unita = get_kpi_value(kpi_cards, "Indice resilienza medio 2021")
        kpi_card("Indice resilienza medio 2021", valore, unita)


    st.markdown("---")
    st.subheader("KPI cards complete")
    st.dataframe(kpi_cards, use_container_width=True)


# =====================================================
# PAGINA 2 - TREND TEMPORALI
# =====================================================

elif pagina == "Trend temporali":

    st.header("Trend temporali")

    trend_nazionale = df_finale[
        (df_finale["livello_territoriale"] == "totale_nazionale") &
        (df_finale["categoria_sport"] == "Attività sportiva")
    ].copy()

    trend_nazionale = trend_nazionale.sort_values("anno")

    indicatore_trend = st.selectbox(
        "Seleziona indicatore nazionale",
        ["n_spettacoli", "persone"]
    )

    titolo = {
        "n_spettacoli": "Trend nazionale degli spettacoli sportivi",
        "persone": "Trend nazionale delle persone"
    }

    fig = px.line(
        trend_nazionale,
        x="anno",
        y=indicatore_trend,
        markers=True,
        title=titolo[indicatore_trend],
        labels={"anno": "Anno", indicatore_trend: indicatore_trend}
    )

    fig.add_vline(x=2020, line_dash="dash")
    fig.add_vline(x=2021, line_dash="dash")

    st.plotly_chart(fig, use_container_width=True)


    st.subheader("Trend per macroarea")

    indicatore_macroarea = st.selectbox(
        "Seleziona indicatore macroarea",
        ["n_spettacoli", "persone"],
        key="indicatore_macroarea"
    )

    macro = tabella_macroaree.copy()
    macro = macro.sort_values(["territorio", "anno"])

    fig = px.line(
        macro,
        x="anno",
        y=indicatore_macroarea,
        color="territorio",
        markers=True,
        title=f"Trend {indicatore_macroarea} per macroarea",
        labels={"anno": "Anno", indicatore_macroarea: indicatore_macroarea, "territorio": "Macroarea"}
    )

    fig.add_vline(x=2020, line_dash="dash")
    fig.add_vline(x=2021, line_dash="dash")

    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# PAGINA 3 - RANKING REGIONI
# =====================================================

elif pagina == "Ranking regioni":

    st.header("Ranking regioni")

    anni = sorted(kpi_regioni["anno"].unique())

    anno_scelto = st.selectbox(
        "Seleziona anno",
        anni,
        index=len(anni) - 1
    )

    kpi_anno = kpi_regioni[kpi_regioni["anno"] == anno_scelto].copy()

    indicatori_base = {
        "Numero spettacoli": "n_spettacoli",
        "Persone": "persone",
        "Persone medie per spettacolo": "persone_medie_per_spettacolo",
        "Quota spettacoli nazionale": "quota_spettacoli_nazionale",
        "Quota persone nazionale": "quota_persone_nazionale",
        "Variazione YoY spettacoli": "variazione_yoy_spettacoli",
        "Variazione YoY persone": "variazione_yoy_persone"
    }

    if anno_scelto == 2021:
        indicatori_base.update({
            "Botteghino": "botteghino",
            "Pubblico": "pubblico",
            "Botteghino medio per spettacolo": "botteghino_medio_per_spettacolo",
            "Pubblico medio per spettacolo": "pubblico_medio_per_spettacolo",
            "Quota botteghino nazionale": "quota_botteghino_nazionale",
            "Quota pubblico nazionale": "quota_pubblico_nazionale"
        })

    indicatore_nome = st.selectbox(
        "Seleziona indicatore",
        list(indicatori_base.keys())
    )

    indicatore_col = indicatori_base[indicatore_nome]

    plot_horizontal_bar(
        kpi_anno,
        indicatore_col,
        "territorio",
        f"{indicatore_nome} per regione - {anno_scelto}",
        indicatore_nome
    )

    st.subheader("Tabella ranking")

    tabella_ranking = kpi_anno[
        ["territorio", indicatore_col]
    ].sort_values(indicatore_col, ascending=False)

    st.dataframe(tabella_ranking.reset_index(drop=True), use_container_width=True)


# =====================================================
# PAGINA 4 - MAPPA ITALIA
# =====================================================

elif pagina == "Mappa Italia":

    st.header("Mappa Italia")

    anni = sorted(kpi_regioni["anno"].dropna().unique())

    anno_mappa = st.selectbox(
        "Seleziona anno",
        anni,
        index=len(anni) - 1,
        key="anno_mappa"
    )

    dati_mappa = kpi_regioni[kpi_regioni["anno"] == anno_mappa].copy()

    indicatori_mappa = {
        "Numero spettacoli": "n_spettacoli",
        "Persone": "persone",
        "Persone medie per spettacolo": "persone_medie_per_spettacolo",
        "Quota spettacoli nazionale": "quota_spettacoli_nazionale",
        "Quota persone nazionale": "quota_persone_nazionale"
    }

    if anno_mappa == 2021:
        indicatori_mappa.update({
            "Botteghino": "botteghino",
            "Pubblico": "pubblico",
            "Botteghino medio per spettacolo": "botteghino_medio_per_spettacolo"
        })

    indicatore_mappa_nome = st.selectbox(
        "Seleziona indicatore mappa",
        list(indicatori_mappa.keys()),
        key="indicatore_mappa"
    )

    indicatore_mappa = indicatori_mappa[indicatore_mappa_nome]

    if indicatore_mappa not in dati_mappa.columns:
        st.warning(f"L'indicatore '{indicatore_mappa_nome}' non è disponibile per l'anno selezionato.")
        st.stop()

    mappa_nomi_regioni = {
        "Piemonte": "Piemonte",
        "Valle d'Aosta": "Valle d'Aosta/Vallée d'Aoste",
        "Valle d’Aosta": "Valle d'Aosta/Vallée d'Aoste",
        "Lombardia": "Lombardia",
        "Liguria": "Liguria",
        "Trentino-Alto Adige": "Trentino-Alto Adige/Südtirol",
        "Trentino Alto Adige": "Trentino-Alto Adige/Südtirol",
        "Veneto": "Veneto",
        "Friuli- Venezia Giulia": "Friuli-Venezia Giulia",
        "Friuli Venezia Giulia": "Friuli-Venezia Giulia",
        "Friuli-Venezia Giulia": "Friuli-Venezia Giulia",
        "Emilia-Romagna": "Emilia-Romagna",
        "Toscana": "Toscana",
        "Umbria": "Umbria",
        "Marche": "Marche",
        "Lazio": "Lazio",
        "Abruzzo": "Abruzzo",
        "Molise": "Molise",
        "Campania": "Campania",
        "Puglia": "Puglia",
        "Basilicata": "Basilicata",
        "Calabria": "Calabria",
        "Sicilia": "Sicilia",
        "Sardegna": "Sardegna"
    }

    # Mantiene il nome originale se non serve conversione
    dati_mappa["regione_geojson"] = dati_mappa["territorio"].replace(mappa_nomi_regioni)

    try:
        geojson_url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
        geojson_regioni = requests.get(geojson_url, timeout=10).json()

        dati_mappa_plot = dati_mappa.dropna(
            subset=["regione_geojson", indicatore_mappa]
        ).copy()

        if dati_mappa_plot.empty:
            st.warning("Non ci sono dati disponibili per costruire la mappa.")
            st.stop()

        # Scala più equilibrata: evita che una regione estrema renda tutte le altre quasi bianche.
        valore_min = dati_mappa_plot[indicatore_mappa].min()
        valore_max = dati_mappa_plot[indicatore_mappa].quantile(0.95)

        if pd.isna(valore_min) or pd.isna(valore_max):
            st.warning("Valori non disponibili per l'indicatore selezionato.")
            st.stop()

        if valore_min == valore_max:
            valore_max = dati_mappa_plot[indicatore_mappa].max()
            if valore_min == valore_max:
                valore_max = valore_min + 1

        formato_hover = "%{z:,.2f}"
        formato_hover_data = ":,.2f"

        if indicatore_mappa in ["n_spettacoli", "persone", "botteghino", "pubblico"]:
            formato_hover = "%{z:,.0f}"
            formato_hover_data = ":,.0f"

        hover_data_map = {
            indicatore_mappa: formato_hover_data,
            "regione_geojson": False
        }

        if "n_spettacoli" in dati_mappa_plot.columns:
            hover_data_map["n_spettacoli"] = ":,.0f"

        if "persone" in dati_mappa_plot.columns:
            hover_data_map["persone"] = ":,.0f"

        fig = px.choropleth(
            dati_mappa_plot,
            geojson=geojson_regioni,
            locations="regione_geojson",
            featureidkey="properties.reg_name",
            color=indicatore_mappa,
            hover_name="territorio",
            hover_data=hover_data_map,
            color_continuous_scale=[
                "#EAF9FD",
                "#B7F1FA",
                "#39BDE8",
                "#00649C",
                "#0D2D44"
            ],
            range_color=(valore_min, valore_max)
        )

        fig.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator",
            showcountries=False,
            showcoastlines=False,
            showland=False,
            showframe=False
        )

        fig.update_traces(
            marker_line_color="#5F6B73",
            marker_line_width=0.8,
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                + indicatore_mappa_nome
                + ": "
                + formato_hover
                + "<extra></extra>"
            )
        )

        fig.update_layout(
            title=None,
            height=650,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Plus Jakarta Sans, Segoe UI, sans-serif",
                color="#0D2D44"
            ),
            coloraxis_colorbar=dict(
                title=dict(text=indicatore_mappa_nome, font=dict(size=12, color="#0D2D44")),
                thickness=14,
                len=0.75,
                x=1.02,
                tickfont=dict(size=11, color="#0D2D44")
            )
        )

        st.markdown("<div class='sbl-map-spacer'></div>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning("Mappa non caricata. Controlla la connessione o il GeoJSON.")
        st.write(e)
elif pagina == "Focus categorie 2021":

    st.header("Focus categorie sportive 2021")

    livello_focus = st.selectbox(
        "Seleziona livello territoriale",
        ["totale_nazionale", "regione"]
    )

    if livello_focus == "totale_nazionale":
        territorio_focus = "Totale complessivo"
    else:
        regioni = sorted(
            tabella_categorie_2021[
                tabella_categorie_2021["livello_territoriale"] == "regione"
            ]["territorio"].unique()
        )

        territorio_focus = st.selectbox(
            "Seleziona regione",
            regioni
        )

    categorie_focus = tabella_categorie_2021[
        (tabella_categorie_2021["territorio"] == territorio_focus) &
        (tabella_categorie_2021["categoria_sport"] != "Attività sportiva")
    ].copy()

    col1, col2 = st.columns(2)

    with col1:
        plot_horizontal_bar(
            categorie_focus,
            "n_spettacoli",
            "categoria_sport",
            f"Spettacoli per categoria - {territorio_focus} 2021",
            "Numero spettacoli"
        )

    with col2:
        plot_horizontal_bar(
            categorie_focus,
            "persone",
            "categoria_sport",
            f"Persone per categoria - {territorio_focus} 2021",
            "Persone"
        )

    st.subheader("Tabella categorie sportive 2021")
    st.dataframe(categorie_focus.reset_index(drop=True), use_container_width=True)


# =====================================================
# PAGINA 6 - SCHEDA SINGOLA REGIONE
# =====================================================

elif pagina == "Scheda singola regione":

    st.header("Scheda singola regione")

    regioni = sorted(kpi_regioni["territorio"].unique())

    regione_scelta = st.selectbox(
        "Seleziona regione",
        regioni
    )

    dati_regione = kpi_regioni[
        kpi_regioni["territorio"] == regione_scelta
    ].copy()

    dati_regione = dati_regione.sort_values("anno")

    anni = sorted(dati_regione["anno"].unique())

    anno_regione = st.selectbox(
        "Seleziona anno",
        anni,
        index=len(anni) - 1
    )

    riga = dati_regione[dati_regione["anno"] == anno_regione].iloc[0]

    st.subheader(f"KPI principali - {regione_scelta} ({anno_regione})")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card("Spettacoli", riga["n_spettacoli"], "eventi")

    with col2:
        kpi_card("Persone", riga["persone"], "persone")

    with col3:
        kpi_card("Persone medie/spettacolo", riga["persone_medie_per_spettacolo"], "persone/evento")

    with col4:
        kpi_card("Quota spettacoli nazionale", riga["quota_spettacoli_nazionale"], "%")


    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        kpi_card("YoY spettacoli", riga["variazione_yoy_spettacoli"], "%")

    with col6:
        kpi_card("YoY persone", riga["variazione_yoy_persone"], "%")

    with col7:
        kpi_card("Quota persone nazionale", riga["quota_persone_nazionale"], "%")

    with col8:
        kpi_card("Resilienza 2021", riga["indice_resilienza_spettacoli_2021"], "%")


    st.subheader("Serie storiche regione")

    indicatore_regione = st.selectbox(
        "Seleziona indicatore serie storica",
        [
            "n_spettacoli",
            "persone",
            "persone_medie_per_spettacolo",
            "quota_spettacoli_nazionale",
            "quota_persone_nazionale"
        ]
    )

    fig = px.line(
        dati_regione,
        x="anno",
        y=indicatore_regione,
        markers=True,
        title=f"{indicatore_regione} - {regione_scelta}",
        labels={"anno": "Anno", indicatore_regione: indicatore_regione}
    )

    fig.add_vline(x=2020, line_dash="dash")
    fig.add_vline(x=2021, line_dash="dash")

    st.plotly_chart(fig, use_container_width=True)


    st.subheader(f"Focus categorie sportive 2021 - {regione_scelta}")

    categorie_regione = tabella_categorie_2021[
        (tabella_categorie_2021["territorio"] == regione_scelta) &
        (tabella_categorie_2021["categoria_sport"] != "Attività sportiva")
    ].copy()

    if len(categorie_regione) > 0:
        plot_horizontal_bar(
            categorie_regione,
            "n_spettacoli",
            "categoria_sport",
            f"Spettacoli per categoria - {regione_scelta} 2021",
            "Numero spettacoli"
        )

        st.dataframe(categorie_regione.reset_index(drop=True), use_container_width=True)
    else:
        st.info("Categorie sportive non disponibili per questa regione.")


    st.subheader("Tabella storica completa regione")
    st.dataframe(dati_regione.reset_index(drop=True), use_container_width=True)


# =====================================================
# PAGINA 7 - TABELLE DATI
# =====================================================

elif pagina == "Tabelle dati":

    st.header("Tabelle dati")

    tabella_scelta = st.selectbox(
        "Seleziona tabella",
        [
            "Dataset finale",
            "KPI regioni",
            "KPI cards 2021",
            "Macroaree",
            "Categorie 2021"
        ]
    )

    if tabella_scelta == "Dataset finale":
        st.dataframe(df_finale, use_container_width=True)

    elif tabella_scelta == "KPI regioni":
        st.dataframe(kpi_regioni, use_container_width=True)

    elif tabella_scelta == "KPI cards 2021":
        st.dataframe(kpi_cards, use_container_width=True)

    elif tabella_scelta == "Macroaree":
        st.dataframe(tabella_macroaree, use_container_width=True)

    elif tabella_scelta == "Categorie 2021":
        st.dataframe(tabella_categorie_2021, use_container_width=True)