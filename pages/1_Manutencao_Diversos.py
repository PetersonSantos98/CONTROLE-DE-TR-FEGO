import streamlit as st
import pandas as pd

from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Controle de Manutenção - Diversos",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FUSO_BR = ZoneInfo("America/Sao_Paulo")


# ============================================================
# CSS - LAYOUT PARA TV
# ============================================================

st.markdown(
    """
    <style>

    /* Oculta menu lateral */
    [data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="collapsedControl"] {
        display: none;
    }

    /* Remove espaços desnecessários */
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        padding-left: 0.6rem;
        padding-right: 0.6rem;
        max-width: 100%;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* Título principal */
    .titulo-principal {
        position: relative;

        background-color: #FFFFFF;
        color: #17365D;

        border-bottom: 7px solid #17365D;

        font-size: 32px;
        font-weight: 800;

        text-align: center;

        padding: 5px 10px 8px 10px;

        margin-bottom: 12px;
    }

    /* Data/hora no canto direito */
    .relogio {
        position: absolute;

        right: 20px;
        top: 7px;

        font-size: 21px;
        font-weight: 800;

        color: #17365D;
    }

    /* Título de cada setor */
    .titulo-setor {

        color: #17365D;

        font-size: 20px;
        font-weight: 800;

        text-align: center;

        margin-top: 5px;
        margin-bottom: 2px;

        line-height: 1.05;
    }

    /* Quantidade */
    .quantidade {
        font-size: 11px;
        color: #555;

        text-align: right;

        margin-top: -18px;
        margin-bottom: 2px;
    }

    /* Reduz espaço entre componentes */
    div[data-testid="stVerticalBlock"] {
        gap: 0.25rem;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #17365D;
        border-radius: 0px;
    }

    /* Rodapé */
    .rodape {
        margin-top: 12px;

        border-top: 1px solid #CCCCCC;

        padding-top: 5px;

        font-size: 10px;

        color: #777777;

        text-align: right;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUPABASE
# ============================================================

try:

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

except Exception:

    st.error(
        "Credenciais do Supabase não encontradas."
    )

    st.info(
        "Configure SUPABASE_URL e SUPABASE_KEY "
        "nos Secrets do Streamlit."
    )

    st.stop()


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

@st.cache_data(ttl=55)
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
                3026
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
# LIMPAR FROTA
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
            return str(int(numero))

    except Exception:
        pass

    return texto


# ============================================================
# CONVERTER DATA DO SUPABASE
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

def formatar_inicio(data):

    if pd.isna(data):
        return "-"

    return data.strftime(
        "%d/%m %H:%M"
    )


# ============================================================
# CALCULAR DURAÇÃO
# ============================================================

def calcular_duracao(inicio):

    if pd.isna(inicio):
        return "-"

    agora = pd.Timestamp.now(
        tz="America/Sao_Paulo"
    )

    diferenca = agora - inicio

    segundos = int(
        diferenca.total_seconds()
    )

    if segundos < 0:
        segundos = 0

    minutos_totais = segundos // 60

    horas = minutos_totais // 60
    minutos = minutos_totais % 60

    return f"{horas:02d}:{minutos:02d}"


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalizar_texto(valor):

    if valor is None:
        return ""

    try:

        if pd.isna(valor):
            return ""

    except Exception:
        pass

    return str(valor).strip().upper()


# ============================================================
# IDENTIFICAR SETOR
# ============================================================

def identificar_setor(frente):

    texto = normalizar_texto(frente)

    # --------------------------------------------------------
    # PLANTIO
    # --------------------------------------------------------

    if "PLANTIO" in texto:
        return "PLANTIO"


    # --------------------------------------------------------
    # CONSERVAÇÃO
    # --------------------------------------------------------

    if (
        "CONSERV" in texto
        or "ESTRADA" in texto
    ):
        return "CONSERVAÇÃO"


    # --------------------------------------------------------
    # PREPARO DE SOLO
    # --------------------------------------------------------

    if (
        "PREPARO" in texto
        and "SOLO" in texto
    ):
        return "PREPARO DE SOLO"


    # --------------------------------------------------------
    # TORTA DE FILTRO
    # --------------------------------------------------------

    if (
        "TORTA" in texto
        and "FILTRO" in texto
    ):
        return "TORTA DE FILTRO"


    # --------------------------------------------------------
    # HERBICIDA
    # --------------------------------------------------------

    if "HERBICIDA" in texto:
        return "HERBICIDA"


    # --------------------------------------------------------
    # CULTIVO
    # --------------------------------------------------------

    if "CULTIVO" in texto:
        return "CULTIVO"


    # --------------------------------------------------------
    # FERTIRRIGAÇÃO
    # --------------------------------------------------------

    if (
        "FERTIRRIGA" in texto
        or "IRRIGA" in texto
    ):
        return "FERTIRRIGAÇÃO"


    # --------------------------------------------------------
    # INCÊNDIO
    # --------------------------------------------------------

    if (
        "INCENDIO" in texto
        or "INCÊNDIO" in texto
    ):
        return "INCÊNDIO"


    # --------------------------------------------------------
    # SERVIÇOS AGRÍCOLAS
    # --------------------------------------------------------

    if (
        "SERVI" in texto
        and "AGRIC" in texto
    ):
        return "SERVIÇOS AGRÍCOLAS"


    # --------------------------------------------------------
    # NÃO IDENTIFICADO
    # --------------------------------------------------------

    return "OUTROS"


# ============================================================
# PREPARAR DATAFRAME
# ============================================================

def preparar_dataframe(dados):

    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados)


    # --------------------------------------------------------
    # GARANTIR COLUNAS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # BASE
    # --------------------------------------------------------

    df["base"] = pd.to_numeric(
        df["base"],
        errors="coerce"
    )

    df = df[
        df["base"] == 3026
    ].copy()


    # --------------------------------------------------------
    # FROTA
    # --------------------------------------------------------

    df["frota"] = (
        df["frota"]
        .apply(limpar_numero)
    )


    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    df["inicio_dt"] = (
        df["inicio"]
        .apply(converter_inicio)
    )


    # --------------------------------------------------------
    # INÍCIO
    # --------------------------------------------------------

    df["INÍCIO"] = (
        df["inicio_dt"]
        .apply(formatar_inicio)
    )


    # --------------------------------------------------------
    # DURAÇÃO
    # --------------------------------------------------------

    df["DURAÇÃO"] = (
        df["inicio_dt"]
        .apply(calcular_duracao)
    )


    # --------------------------------------------------------
    # MOTIVO
    # --------------------------------------------------------

    df["motivo"] = (
        df["motivo"]
        .fillna("-")
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # SETOR
    # --------------------------------------------------------

    df["SETOR"] = (
        df["frente"]
        .apply(identificar_setor)
    )


    # --------------------------------------------------------
    # ATIVIDADE
    #
    # Ainda não temos esse dado no IFROTA/Supabase.
    # --------------------------------------------------------

    df["ATIVIDADE"] = "-"


    # --------------------------------------------------------
    # ORDENAÇÃO
    # --------------------------------------------------------

    df = df.sort_values(
        by=[
            "SETOR",
            "inicio_dt",
            "frota"
        ],
        ascending=[
            True,
            True,
            True
        ],
        na_position="last"
    )

    return df


# ============================================================
# MOSTRAR SETOR
# ============================================================

def mostrar_setor(
    nome,
    dataframe
):

    st.markdown(
        f"""
        <div class="titulo-setor">
            {nome}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # SEM EQUIPAMENTOS
    # --------------------------------------------------------

    if dataframe.empty:

        tabela_vazia = pd.DataFrame(
            [{
                "FROTA": "-",
                "MOTIVO": "-",
                "INÍCIO": "-",
                "DURAÇÃO": "-",
                "ATIVIDADE": "-"
            }]
        )

        st.dataframe(
            tabela_vazia,
            hide_index=True,
            use_container_width=True,
            row_height=26,
            height=62
        )

        return


    # --------------------------------------------------------
    # TABELA
    # --------------------------------------------------------

    tabela = pd.DataFrame({

        "FROTA":
            dataframe["frota"],

        "MOTIVO":
            dataframe["motivo"],

        "INÍCIO":
            dataframe["INÍCIO"],

        "DURAÇÃO":
            dataframe["DURAÇÃO"],

        "ATIVIDADE":
            dataframe["ATIVIDADE"]

    })


    # Altura automática
    altura = (
        36
        + (len(tabela) * 28)
    )

    # Limite
    altura = max(
        62,
        min(
            altura,
            300
        )
    )


    st.dataframe(
        tabela,
        hide_index=True,
        use_container_width=True,
        row_height=26,
        height=altura,

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

            "DURAÇÃO":
                st.column_config.TextColumn(
                    "DURAÇÃO",
                    width="small"
                ),

            "ATIVIDADE":
                st.column_config.TextColumn(
                    "ATIVIDADE",
                    width="medium"
                )
        }
    )


# ============================================================
# CARREGAMENTO
# ============================================================

dados = buscar_manutencoes()

df = preparar_dataframe(
    dados
)


# ============================================================
# DATA/HORA
# ============================================================

agora = datetime.now(
    FUSO_BR
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    f"""
    <div class="titulo-principal">

        🛠️

        CONTROLE DE MANUTENÇÃO - DIVERSOS

        <span class="relogio">
            {agora.strftime("%d/%m/%Y %H:%M")}
        </span>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SEPARAR SETORES
# ============================================================

def pegar_setor(nome):

    if df.empty:
        return pd.DataFrame()

    return df[
        df["SETOR"] == nome
    ].copy()


plantio = pegar_setor(
    "PLANTIO"
)

conservacao = pegar_setor(
    "CONSERVAÇÃO"
)

preparo_solo = pegar_setor(
    "PREPARO DE SOLO"
)

torta_filtro = pegar_setor(
    "TORTA DE FILTRO"
)

herbicida = pegar_setor(
    "HERBICIDA"
)

cultivo = pegar_setor(
    "CULTIVO"
)

fertirrigacao = pegar_setor(
    "FERTIRRIGAÇÃO"
)

incendio = pegar_setor(
    "INCÊNDIO"
)

servicos_agricolas = pegar_setor(
    "SERVIÇOS AGRÍCOLAS"
)

outros = pegar_setor(
    "OUTROS"
)


# ============================================================
# LAYOUT PRINCIPAL
#
# Igual à organização da planilha:
#
# COLUNA 1
# Plantio
# Conservação
# Preparo de Solo
# Torta de Filtro
#
# COLUNA 2
# Herbicida
# Cultivo
# Fertirrigação
#
# COLUNA 3
# Incêndio
# Serviços Agrícolas
# ============================================================

coluna1, coluna2, coluna3 = st.columns(
    [1, 1, 1],
    gap="small"
)


# ============================================================
# COLUNA 1
# ============================================================

with coluna1:

    mostrar_setor(
        "PLANTIO",
        plantio
    )

    mostrar_setor(
        "CONSERVAÇÃO",
        conservacao
    )

    mostrar_setor(
        "PREPARO DE SOLO",
        preparo_solo
    )

    mostrar_setor(
        "TORTA DE FILTRO",
        torta_filtro
    )


# ============================================================
# COLUNA 2
# ============================================================

with coluna2:

    mostrar_setor(
        "HERBICIDA",
        herbicida
    )

    mostrar_setor(
        "CULTIVO",
        cultivo
    )

    mostrar_setor(
        "FERTIRRIGAÇÃO",
        fertirrigacao
    )


# ============================================================
# COLUNA 3
# ============================================================

with coluna3:

    mostrar_setor(
        "INCÊNDIO",
        incendio
    )

    mostrar_setor(
        "SERVIÇOS AGRÍCOLAS",
        servicos_agricolas
    )


# ============================================================
# OUTROS
#
# Importante para não esconder registros caso apareça
# uma frente que ainda não mapeamos.
# ============================================================

if not outros.empty:

    st.divider()

    mostrar_setor(
        "OUTROS / NÃO CLASSIFICADOS",
        outros
    )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    f"""
    <div class="rodape">

        IFROTA → Supabase

        &nbsp;&nbsp;|&nbsp;&nbsp;

        BASE 3026

        &nbsp;&nbsp;|&nbsp;&nbsp;

        Atualizado em
        {agora.strftime("%d/%m/%Y %H:%M:%S")}

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
