import streamlit as st
import pandas as pd

from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Controle de Manutenção - Usina Iracema",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FUSO HORÁRIO
# ============================================================

FUSO_BR = ZoneInfo("America/Sao_Paulo")


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1800px;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .titulo-principal {
        font-size: 27px;
        font-weight: 800;
        color: #FFFFFF;
        background-color: #17365D;
        padding: 10px 14px;
        border-radius: 2px;
        margin-bottom: 5px;
    }

    .linha-azul {
        height: 3px;
        background-color: #17365D;
        margin-top: 4px;
        margin-bottom: 12px;
    }

    .atualizacao {
        font-size: 14px;
        font-weight: 600;
        margin-top: 3px;
        margin-bottom: 8px;
    }

    .cabecalho-grupo {
        background-color: #17365D;
        color: white;
        font-size: 17px;
        font-weight: 800;
        padding: 6px 10px;
        margin-top: 18px;
        margin-bottom: 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .quantidade-grupo {
        font-size: 17px;
        font-weight: 800;
        padding-right: 10px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #536273;
        border-radius: 0px;
    }

    .stButton > button {
        width: 100%;
        font-weight: 600;
    }

    .rodape {
        margin-top: 25px;
        padding-top: 10px;
        border-top: 1px solid #555;
        color: #888;
        font-size: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CREDENCIAIS SUPABASE
# ============================================================

try:

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

except Exception:

    st.error(
        "As credenciais do Supabase não foram configuradas."
    )

    st.info(
        "Configure SUPABASE_URL e SUPABASE_KEY "
        "nos Secrets do Streamlit."
    )

    st.stop()


# ============================================================
# CONEXÃO SUPABASE
# ============================================================

@st.cache_resource
def conectar_supabase():

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


try:

    supabase = conectar_supabase()

except Exception as erro:

    st.error(
        f"Erro ao conectar ao Supabase: {erro}"
    )

    st.stop()


# ============================================================
# BUSCAR MANUTENÇÕES
# ============================================================

@st.cache_data(ttl=30)
def buscar_manutencoes():

    try:

        resposta = (
            supabase
            .table("manutencoes_ifrota")
            .select(
                "tipo_equipamento,"
                "base,"
                "classe,"
                "frente,"
                "local,"
                "frota,"
                "gleba,"
                "inicio,"
                "motivo,"
                "atualizado_em"
            )
            .eq(
                "base",
                2026
            )
            .execute()
        )

        return resposta.data

    except Exception as erro:

        st.error(
            f"Erro ao consultar o Supabase: {erro}"
        )

        return []


# ============================================================
# LIMPAR NÚMERO
# ============================================================

def limpar_numero(valor):

    if valor is None:
        return ""

    try:

        if pd.isna(valor):
            return ""

    except Exception:
        pass

    texto = str(valor).strip()

    if texto == "":
        return ""

    try:

        numero = float(texto)

        if numero.is_integer():

            return str(
                int(numero)
            )

    except Exception:
        pass

    return texto


# ============================================================
# CONVERTER HORÁRIO
# ============================================================

def converter_inicio(valor):

    if valor is None:
        return pd.NaT

    try:

        data = pd.to_datetime(
            valor,
            utc=True,
            errors="coerce"
        )

        if pd.isna(data):
            return pd.NaT

        return data.tz_convert(
            "America/Sao_Paulo"
        )

    except Exception:

        return pd.NaT


# ============================================================
# FORMATAR INÍCIO
# ============================================================

def formatar_inicio(valor):

    if pd.isna(valor):
        return "-"

    return valor.strftime(
        "%d/%m %H:%M"
    )


# ============================================================
# CALCULAR TEMPO
# ============================================================

def calcular_tempo(inicio):

    if pd.isna(inicio):
        return "-"

    agora = pd.Timestamp.now(
        tz="America/Sao_Paulo"
    )

    diferenca = (
        agora - inicio
    )

    segundos = int(
        diferenca.total_seconds()
    )

    if segundos < 0:
        segundos = 0

    minutos_totais = (
        segundos // 60
    )

    horas = (
        minutos_totais // 60
    )

    minutos = (
        minutos_totais % 60
    )

    return (
        f"{horas:02d}:"
        f"{minutos:02d}"
    )


# ============================================================
# NORMALIZAR FRENTE
# ============================================================

def normalizar_frente(valor):

    if valor is None:
        return "-"

    texto = str(valor).strip()

    if texto == "":
        return "-"

    texto_upper = texto.upper()

    if "FRENTE 1" in texto_upper:
        return "FRENTE 1"

    if "FRENTE 2" in texto_upper:
        return "FRENTE 2"

    if "FRENTE 3" in texto_upper:
        return "FRENTE 3"

    if "FRENTE 4" in texto_upper:
        return "FRENTE 4"

    if "FRENTE 5" in texto_upper:
        return "FRENTE 5"

    return texto_upper


# ============================================================
# PREPARAR DATAFRAME
# ============================================================

def preparar_dataframe(dados):

    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados)

    colunas = [
        "tipo_equipamento",
        "base",
        "classe",
        "frente",
        "local",
        "frota",
        "gleba",
        "inicio",
        "motivo",
        "atualizado_em"
    ]

    for coluna in colunas:

        if coluna not in df.columns:
            df[coluna] = None


    # ========================================================
    # BASE
    # ========================================================

    df["base"] = pd.to_numeric(
        df["base"],
        errors="coerce"
    )

    df = df[
        df["base"] == 2026
    ].copy()


    # ========================================================
    # CLASSE
    # ========================================================

    df["classe"] = pd.to_numeric(
        df["classe"],
        errors="coerce"
    )


    # ========================================================
    # TIPO
    # ========================================================

    df["tipo_equipamento"] = (
        df["tipo_equipamento"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )


    # ========================================================
    # FROTA
    # ========================================================

    df["frota"] = (
        df["frota"]
        .apply(limpar_numero)
    )


    # ========================================================
    # GLEBA
    # ========================================================

    df["gleba"] = (
        df["gleba"]
        .apply(limpar_numero)
    )


    # ========================================================
    # INÍCIO
    # ========================================================

    df["inicio_dt"] = (
        df["inicio"]
        .apply(converter_inicio)
    )


    # ========================================================
    # INÍCIO FORMATADO
    # ========================================================

    df["INÍCIO"] = (
        df["inicio_dt"]
        .apply(formatar_inicio)
    )


    # ========================================================
    # TEMPO
    # ========================================================

    df["TEMPO"] = (
        df["inicio_dt"]
        .apply(calcular_tempo)
    )


    # ========================================================
    # FRENTE
    # ========================================================

    df["FRENTE"] = (
        df["frente"]
        .apply(normalizar_frente)
    )


    # ========================================================
    # LOCAL
    # ========================================================

    df["local"] = (
        df["local"]
        .fillna("-")
        .astype(str)
        .str.strip()
    )

    df.loc[
        df["local"] == "",
        "local"
    ] = "-"


    # ========================================================
    # MOTIVO
    # ========================================================

    df["motivo"] = (
        df["motivo"]
        .fillna("-")
        .astype(str)
        .str.strip()
    )


    # ========================================================
    # ORDENAR
    # ========================================================

    df = df.sort_values(
        by=[
            "inicio_dt",
            "frota"
        ],
        ascending=[
            True,
            True
        ],
        na_position="last"
    )

    return df


# ============================================================
# MOSTRAR BLOCO
# ============================================================

def mostrar_bloco(
    titulo,
    dataframe
):

    quantidade = len(
        dataframe
    )

    st.markdown(
        f"""
<div class="cabecalho-grupo">
<span>{titulo}</span>
<span class="quantidade-grupo">{quantidade}</span>
</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # SEM REGISTROS
    # ========================================================

    if dataframe.empty:

        st.info(
            "Nenhum equipamento em manutenção."
        )

        return


    # ========================================================
    # TABELA
    # ========================================================

    tabela = pd.DataFrame({

        "FROTA":
            dataframe["frota"],

        "MOTIVO":
            dataframe["motivo"],

        "INÍCIO":
            dataframe["INÍCIO"],

        "TEMPO":
            dataframe["TEMPO"],

        "FRENTE":
            dataframe["FRENTE"],

        "LOCAL":
            dataframe["local"]

    })


    st.dataframe(
        tabela,
        hide_index=True,
        use_container_width=True,
        row_height=30,

        column_config={

            "FROTA":
                st.column_config.TextColumn(
                    "FROTA",
                    width="small"
                ),

            "MOTIVO":
                st.column_config.TextColumn(
                    "MOTIVO",
                    width="large"
                ),

            "INÍCIO":
                st.column_config.TextColumn(
                    "INÍCIO",
                    width="medium"
                ),

            "TEMPO":
                st.column_config.TextColumn(
                    "TEMPO",
                    width="small"
                ),

            "FRENTE":
                st.column_config.TextColumn(
                    "FRENTE",
                    width="medium"
                ),

            "LOCAL":
                st.column_config.TextColumn(
                    "LOCAL",
                    width="large"
                )

        }
    )


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    """
<div class="titulo-principal">
CONTROLE DE MANUTENÇÃO - USINA IRACEMA
</div>

<div class="linha-azul"></div>
""",
    unsafe_allow_html=True
)


# ============================================================
# CARREGAR DADOS
# ============================================================

dados = buscar_manutencoes()

df = preparar_dataframe(
    dados
)


# ============================================================
# HORÁRIO ATUAL
# ============================================================

agora = datetime.now(
    FUSO_BR
)


# ============================================================
# ATUALIZAÇÃO
# ============================================================

col1, col2 = st.columns(
    [8, 1]
)


with col1:

    st.markdown(
        f"""
<div class="atualizacao">
Última Atualização: {agora.strftime("%d/%m/%Y %H:%M")}
&nbsp;&nbsp; 🟢
</div>
""",
        unsafe_allow_html=True
    )


with col2:

    if st.button(
        "🔄 Atualizar",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()


# ============================================================
# SEPARAR EQUIPAMENTOS
# ============================================================

if df.empty:

    df_colhedoras = pd.DataFrame()
    df_tratores = pd.DataFrame()
    df_carretas = pd.DataFrame()
    df_transporte = pd.DataFrame()

else:

    # ========================================================
    # COLHEDORAS
    # BASE 2026
    # CLASSE 4
    # ========================================================

    df_colhedoras = df[
        (
            df["tipo_equipamento"]
            .eq("MAQUINA")
        )
        |
        (
            df["classe"] == 4
        )
    ].copy()


    # ========================================================
    # TRATORES
    # BASE 2026
    # CLASSE 2
    # ========================================================

    df_tratores = df[
        (
            df["tipo_equipamento"]
            .eq("TRATOR")
        )
        |
        (
            df["classe"] == 2
        )
    ].copy()


    # ========================================================
    # CARRETAS
    # BASE 2026
    # CLASSE 5
    # ========================================================

    df_carretas = df[
        (
            df["tipo_equipamento"]
            .eq("CARRETA")
        )
        |
        (
            df["classe"] == 5
        )
    ].copy()


    # ========================================================
    # TRANSPORTE DE CANA
    # BASE 2026
    # CLASSE 1
    # ========================================================

    df_transporte = df[
        (
            df["tipo_equipamento"]
            .eq("CAMINHAO")
        )
        |
        (
            df["classe"] == 1
        )
    ].copy()


# ============================================================
# COLHEDORAS
# ============================================================

mostrar_bloco(
    "COLHEDORAS",
    df_colhedoras
)


# ============================================================
# TRATORES
# ============================================================

mostrar_bloco(
    "TRATORES",
    df_tratores
)


# ============================================================
# TRANSPORTE DE CANA
# ============================================================

mostrar_bloco(
    "TRANSP. CANA",
    df_transporte
)


# ============================================================
# CARRETAS
# ============================================================

mostrar_bloco(
    "CARRETAS",
    df_carretas
)

# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    f"""
<div class="rodape">
Dados de manutenção: IFROTA → Supabase
&nbsp;&nbsp;|&nbsp;&nbsp;
Tela atualizada em {agora.strftime("%d/%m/%Y %H:%M:%S")}
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# AUTO REFRESH
# ============================================================

@st.fragment(
    run_every="60s"
)
def auto_refresh():

    st.empty()


auto_refresh()
