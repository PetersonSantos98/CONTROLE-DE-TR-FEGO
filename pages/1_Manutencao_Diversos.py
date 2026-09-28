import streamlit as st
import pandas as pd
import html
import unicodedata

from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Controle de Manutenção - Diversos",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FUSO_BR = ZoneInfo("America/Sao_Paulo")


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   ESCONDER ELEMENTOS DO STREAMLIT
   ============================================================ */

[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

#MainMenu {
    visibility: hidden !important;
}

footer {
    visibility: hidden !important;
}

header {
    visibility: hidden !important;
    height: 0 !important;
}


/* ============================================================
   PÁGINA
   ============================================================ */

.stApp {
    background: white;
}

.block-container {
    padding-top: 3px !important;
    padding-bottom: 5px !important;
    padding-left: 5px !important;
    padding-right: 5px !important;

    max-width: 100% !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.15rem !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    align-items: flex-start !important;
}


/* ============================================================
   CABEÇALHO PRINCIPAL
   ============================================================ */

.cabecalho {
    width: 100%;
    height: 45px;

    position: relative;

    display: flex;
    align-items: center;
    justify-content: center;

    background: white;

    border-bottom: 5px solid #17365D;

    margin-bottom: 12px;

    box-sizing: border-box;
}

.cabecalho-icone {
    position: absolute;
    left: 8px;

    font-size: 28px;

    top: 50%;
    transform: translateY(-50%);
}

.cabecalho-titulo {
    font-family: Arial, sans-serif;

    color: #17365D;

    font-size: 24px;
    font-weight: 800;

    text-align: center;
}

.cabecalho-relogio {
    position: absolute;
    right: 12px;

    top: 50%;
    transform: translateY(-50%);

    font-family: Arial, sans-serif;

    color: #17365D;

    font-size: 18px;
    font-weight: bold;
}


/* ============================================================
   BLOCO DO SETOR
   ============================================================ */

.setor {
    width: 100%;

    margin: 0 0 10px 0;

    padding: 0;

    box-sizing: border-box;
}


/* ============================================================
   TÍTULO DO SETOR
   ============================================================ */

.titulo-setor {
    width: 100%;

    font-family: Arial, sans-serif;

    color: #17365D;

    font-size: 17px;
    font-weight: 800;

    text-align: center;

    line-height: 22px;

    padding: 2px 0 4px 0;

    margin: 0;

    box-sizing: border-box;
}


/* ============================================================
   TABELA
   ============================================================ */

.tabela {
    width: 100%;

    border-collapse: collapse;

    table-layout: fixed;

    font-family: Arial, sans-serif;

    margin: 0;

    padding: 0;
}


/* ============================================================
   CABEÇALHO DA TABELA
   ============================================================ */

.tabela th {
    background: #17365D;

    color: white;

    border: 1px solid white;

    padding: 2px 3px;

    font-size: 10px;
    font-weight: bold;

    line-height: 12px;

    text-align: center;

    white-space: nowrap;
}


/* ============================================================
   CÉLULAS
   ============================================================ */

.tabela td {
    background: white;

    color: black;

    border: 1px solid #777;

    padding: 2px 3px;

    font-size: 10px;
    font-weight: 600;

    line-height: 12px;

    white-space: nowrap;

    overflow: hidden;

    text-overflow: ellipsis;
}


/* ============================================================
   LARGURA DAS COLUNAS
   ============================================================ */

.frota {
    width: 11%;

    text-align: center !important;
}

.motivo {
    width: 39%;

    text-align: left !important;
}

.inicio {
    width: 17%;

    text-align: center !important;
}

.duracao {
    width: 13%;

    text-align: center !important;
}

.atividade {
    width: 20%;

    text-align: center !important;
}


/* ============================================================
   COLUNA ATIVIDADE
   ============================================================ */

.tabela td.atividade {
    background: #A6A6A6;

    font-size: 9px;

    font-weight: bold;
}


/* ============================================================
   OUTROS / NÃO CLASSIFICADOS
   ============================================================ */

.separador {
    border-top: 2px solid #17365D;

    margin-top: 10px;

    margin-bottom: 5px;
}


/* ============================================================
   RODAPÉ
   ============================================================ */

.rodape {
    margin-top: 5px;

    padding-top: 3px;

    border-top: 1px solid #aaa;

    text-align: right;

    font-family: Arial, sans-serif;

    font-size: 9px;

    color: #666;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SUPABASE
# ============================================================

try:

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

except Exception:

    st.error(
        "SUPABASE_URL e SUPABASE_KEY não encontrados nos Secrets."
    )

    st.stop()


@st.cache_resource
def conectar_supabase():

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


supabase = conectar_supabase()


# ============================================================
# CONSULTAR BANCO
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
            f"Erro ao consultar Supabase: {erro}"
        )

        return []


# ============================================================
# LIMPAR NÚMEROS
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

    if not texto:
        return ""

    try:

        numero = float(texto)

        if numero.is_integer():
            return str(int(numero))

    except Exception:
        pass

    return texto


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


def sem_acento(valor):

    texto = normalizar_texto(valor)

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    return "".join(
        c
        for c in texto
        if not unicodedata.combining(c)
    )


# ============================================================
# CONVERTER DATA/HORA
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
# IDENTIFICAR SETOR
# ============================================================

def identificar_setor(frente):

    texto = sem_acento(frente)


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

    if "INCENDIO" in texto:

        return "INCÊNDIO"


    # --------------------------------------------------------
    # SERVIÇOS AGRÍCOLAS
    # --------------------------------------------------------

    if (
        "SERVI" in texto
        and "AGRIC" in texto
    ):

        return "SERVIÇOS AGRÍCOLAS"


    return "OUTROS"


# ============================================================
# PREPARAR DATAFRAME
# ============================================================

def preparar_dataframe(dados):

    if not dados:

        return pd.DataFrame()


    df = pd.DataFrame(
        dados
    )


    # ========================================================
    # GARANTIR COLUNAS
    # ========================================================

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
        df["base"] == 3026
    ].copy()


    # ========================================================
    # FROTA
    # ========================================================

    df["frota"] = (
        df["frota"]
        .apply(limpar_numero)
    )


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
    # FRENTE
    # ========================================================

    df["frente"] = (
        df["frente"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # ========================================================
    # INÍCIO
    # ========================================================

    df["inicio_dt"] = (
        df["inicio"]
        .apply(converter_inicio)
    )


    df["INÍCIO"] = (
        df["inicio_dt"]
        .apply(formatar_inicio)
    )


    # ========================================================
    # DURAÇÃO
    # ========================================================

    df["DURAÇÃO"] = (
        df["inicio_dt"]
        .apply(calcular_duracao)
    )


    # ========================================================
    # SETOR
    # ========================================================

    df["SETOR"] = (
        df["frente"]
        .apply(identificar_setor)
    )


    # ========================================================
    # ATIVIDADE
    # ========================================================

    df["ATIVIDADE"] = "-"


    # ========================================================
    # ORDENAR
    # ========================================================

    df = df.sort_values(
        [
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
# ESCAPAR HTML
# ============================================================

def escapar(valor):

    if valor is None:

        return "-"


    try:

        if pd.isna(valor):

            return "-"

    except Exception:

        pass


    texto = str(valor).strip()


    if not texto:

        texto = "-"


    return html.escape(
        texto,
        quote=True
    )


# ============================================================
# CRIAR TABELA HTML
# ============================================================

def criar_tabela_html(dataframe):

    linhas = ""


    # ========================================================
    # SEM REGISTROS
    # ========================================================

    if dataframe.empty:

        linhas = (
            "<tr>"
            "<td class='frota'>-</td>"
            "<td class='motivo'>-</td>"
            "<td class='inicio'>-</td>"
            "<td class='duracao'>-</td>"
            "<td class='atividade'>-</td>"
            "</tr>"
        )


    # ========================================================
    # COM REGISTROS
    # ========================================================

    else:

        for _, linha in dataframe.iterrows():

            frota = escapar(
                linha.get(
                    "frota",
                    "-"
                )
            )


            motivo = escapar(
                linha.get(
                    "motivo",
                    "-"
                )
            )


            inicio = escapar(
                linha.get(
                    "INÍCIO",
                    "-"
                )
            )


            duracao = escapar(
                linha.get(
                    "DURAÇÃO",
                    "-"
                )
            )


            atividade = escapar(
                linha.get(
                    "ATIVIDADE",
                    "-"
                )
            )


            linhas += (
                "<tr>"
                f"<td class='frota'>{frota}</td>"
                f"<td class='motivo' title='{motivo}'>{motivo}</td>"
                f"<td class='inicio'>{inicio}</td>"
                f"<td class='duracao'>{duracao}</td>"
                f"<td class='atividade' title='{atividade}'>{atividade}</td>"
                "</tr>"
            )


    tabela = (
        "<table class='tabela'>"
        "<thead>"
        "<tr>"
        "<th class='frota'>FROTA</th>"
        "<th class='motivo'>MOTIVO</th>"
        "<th class='inicio'>INÍCIO</th>"
        "<th class='duracao'>DURAÇÃO</th>"
        "<th class='atividade'>ATIVIDADE</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        f"{linhas}"
        "</tbody>"
        "</table>"
    )


    return tabela


# ============================================================
# MOSTRAR SETOR
# ============================================================

def mostrar_setor(nome, dataframe):

    nome_html = escapar(
        nome
    )


    tabela = criar_tabela_html(
        dataframe
    )


    bloco = (
        "<div class='setor'>"
        f"<div class='titulo-setor'>{nome_html}</div>"
        f"{tabela}"
        "</div>"
    )


    st.markdown(
        bloco,
        unsafe_allow_html=True
    )


# ============================================================
# BUSCAR DADOS
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
# CABEÇALHO PRINCIPAL
# ============================================================

cabecalho = (
    "<div class='cabecalho'>"
    "<div class='cabecalho-icone'>🛠️</div>"
    "<div class='cabecalho-titulo'>"
    "CONTROLE DE MANUTENÇÃO - DIVERSOS"
    "</div>"
    "<div class='cabecalho-relogio'>"
    f"{agora.strftime('%d/%m/%Y %H:%M')}"
    "</div>"
    "</div>"
)


st.markdown(
    cabecalho,
    unsafe_allow_html=True
)


# ============================================================
# PEGAR SETOR
# ============================================================

def pegar_setor(nome):

    if df.empty:

        return pd.DataFrame()


    return df[
        df["SETOR"] == nome
    ].copy()


# ============================================================
# DATAFRAMES POR SETOR
# ============================================================

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
# ============================================================

col1, col2, col3 = st.columns(
    3,
    gap="small"
)


# ============================================================
# COLUNA ESQUERDA
# ============================================================

with col1:

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
# COLUNA CENTRAL
# ============================================================

with col2:

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
# COLUNA DIREITA
# ============================================================

with col3:

    mostrar_setor(
        "INCÊNDIO",
        incendio
    )


    mostrar_setor(
        "SERVIÇOS AGRÍCOLAS",
        servicos_agricolas
    )


# ============================================================
# OUTROS / NÃO CLASSIFICADOS
# ============================================================

if not outros.empty:

    st.markdown(
        "<div class='separador'></div>",
        unsafe_allow_html=True
    )


    mostrar_setor(
        "OUTROS / NÃO CLASSIFICADOS",
        outros
    )


# ============================================================
# RODAPÉ
# ============================================================

rodape = (
    "<div class='rodape'>"
    "IFROTA → Supabase"
    "&nbsp;&nbsp;|&nbsp;&nbsp;"
    "BASE 3026"
    "&nbsp;&nbsp;|&nbsp;&nbsp;"
    "Atualizado em "
    f"{agora.strftime('%d/%m/%Y %H:%M:%S')}"
    "</div>"
)


st.markdown(
    rodape,
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
