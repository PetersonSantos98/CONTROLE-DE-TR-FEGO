import streamlit as st
import pandas as pd
import html
import unicodedata

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

    /* =======================================================
       ESCONDER ELEMENTOS DO STREAMLIT
       ======================================================= */

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


    /* =======================================================
       PÁGINA
       ======================================================= */

    .stApp {
        background-color: #FFFFFF;
    }

    .block-container {
        padding-top: 0.15rem !important;
        padding-bottom: 0.3rem !important;
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.08rem !important;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.7rem !important;
        align-items: flex-start !important;
    }


    /* =======================================================
       CABEÇALHO PRINCIPAL
       ======================================================= */

    .cabecalho-principal {
        width: 100%;
        height: 43px;

        position: relative;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #FFFFFF;

        border-bottom: 7px solid #17365D;

        margin: 0 0 7px 0;
        padding: 0 5px;

        box-sizing: border-box;
    }

    .cabecalho-icone {
        position: absolute;

        left: 7px;
        top: 4px;

        font-size: 27px;
        line-height: 32px;
    }

    .cabecalho-titulo {
        color: #17365D;

        font-family: Arial, sans-serif;

        font-size: 25px;
        font-weight: 800;

        text-align: center;

        line-height: 32px;
    }

    .cabecalho-relogio {
        position: absolute;

        right: 12px;
        top: 7px;

        color: #17365D;

        font-family: Arial, sans-serif;

        font-size: 17px;
        font-weight: 800;

        white-space: nowrap;
    }


    /* =======================================================
       BLOCO DE CADA SETOR
       ======================================================= */

    .bloco-setor {
        width: 100%;

        margin: 0 0 7px 0;
        padding: 0;

        box-sizing: border-box;
    }

    .titulo-setor-tv {
        width: 100%;

        color: #17365D;

        font-family: Arial, sans-serif;

        font-size: 17px;
        font-weight: 800;

        text-align: center;

        line-height: 19px;

        margin: 0;
        padding: 1px 0 2px 0;

        box-sizing: border-box;
    }


    /* =======================================================
       TABELAS
       ======================================================= */

    .tabela-tv {
        width: 100%;

        border-collapse: collapse;
        border-spacing: 0;

        table-layout: fixed;

        font-family: Arial, sans-serif;

        margin: 0;
        padding: 0;
    }

    .tabela-tv thead tr {
        background-color: #17365D;
    }

    .tabela-tv th {
        background-color: #17365D;
        color: #FFFFFF;

        border: 1px solid #FFFFFF;

        padding: 1px 3px;

        height: 17px;

        font-size: 10px;
        font-weight: 700;

        line-height: 12px;

        text-align: center;

        white-space: nowrap;

        box-sizing: border-box;
    }

    .tabela-tv td {
        color: #000000;
        background-color: #FFFFFF;

        border: 1px solid #7F7F7F;

        padding: 1px 3px;

        height: 18px;

        font-size: 10px;
        font-weight: 600;

        line-height: 13px;

        vertical-align: middle;

        box-sizing: border-box;

        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }


    /* =======================================================
       LARGURAS
       ======================================================= */

    .col-frota {
        width: 12%;
        text-align: center !important;
    }

    .col-motivo {
        width: 38%;
        text-align: left !important;
    }

    .col-inicio {
        width: 17%;
        text-align: center !important;
    }

    .col-duracao {
        width: 13%;
        text-align: center !important;
    }

    .col-atividade {
        width: 20%;
        text-align: center !important;
    }


    /* =======================================================
       ATIVIDADE
       ======================================================= */

    td.col-atividade {
        background-color: #A6A6A6;
        color: #000000;

        font-size: 9px;
        font-weight: 700;
    }


    /* =======================================================
       SEM REGISTROS
       ======================================================= */

    .linha-vazia {
        text-align: center !important;
        color: #666666 !important;
        font-weight: 400 !important;
    }


    /* =======================================================
       OUTROS
       ======================================================= */

    .separador-outros {
        width: 100%;
        border-top: 2px solid #17365D;

        margin-top: 6px;
        margin-bottom: 4px;
    }


    /* =======================================================
       RODAPÉ
       ======================================================= */

    .rodape-tv {
        width: 100%;

        border-top: 1px solid #AAAAAA;

        margin-top: 6px;
        padding-top: 3px;

        font-family: Arial, sans-serif;

        font-size: 9px;

        color: #666666;

        text-align: right;
    }


    /* =======================================================
       TELAS GRANDES / TV
       ======================================================= */

    @media (min-width: 1600px) {

        .cabecalho-titulo {
            font-size: 28px;
        }

        .cabecalho-relogio {
            font-size: 19px;
        }

        .titulo-setor-tv {
            font-size: 18px;
        }

        .tabela-tv th {
            font-size: 10px;
        }

        .tabela-tv td {
            font-size: 10px;
        }
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

    st.error("Credenciais do Supabase não encontradas.")

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
# BASE 3026 = DIVERSOS
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

    texto = str(valor).strip().upper()

    return texto


# ============================================================
# NORMALIZAR TEXTO SEM ACENTOS
# ============================================================

def texto_sem_acento(valor):

    texto = normalizar_texto(valor)

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

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
# IDENTIFICAR SETOR
# ============================================================

def identificar_setor(frente):

    texto = texto_sem_acento(frente)


    # ========================================================
    # PLANTIO
    # ========================================================

    if "PLANTIO" in texto:
        return "PLANTIO"


    # ========================================================
    # CONSERVAÇÃO
    # ========================================================

    if (
        "CONSERV" in texto
        or "ESTRADA" in texto
    ):
        return "CONSERVAÇÃO"


    # ========================================================
    # PREPARO DE SOLO
    # ========================================================

    if (
        "PREPARO" in texto
        and "SOLO" in texto
    ):
        return "PREPARO DE SOLO"


    # ========================================================
    # TORTA DE FILTRO
    # ========================================================

    if (
        "TORTA" in texto
        and "FILTRO" in texto
    ):
        return "TORTA DE FILTRO"


    # ========================================================
    # HERBICIDA
    # ========================================================

    if "HERBICIDA" in texto:
        return "HERBICIDA"


    # ========================================================
    # CULTIVO
    # ========================================================

    if "CULTIVO" in texto:
        return "CULTIVO"


    # ========================================================
    # FERTIRRIGAÇÃO
    # ========================================================

    if (
        "FERTIRRIGA" in texto
        or "IRRIGA" in texto
    ):
        return "FERTIRRIGAÇÃO"


    # ========================================================
    # INCÊNDIO
    # ========================================================

    if "INCENDIO" in texto:
        return "INCÊNDIO"


    # ========================================================
    # SERVIÇOS AGRÍCOLAS
    # ========================================================

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

    df = pd.DataFrame(dados)


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
    # FILTRAR BASE
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
    # DATA/HORA
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
    # DURAÇÃO
    # ========================================================

    df["DURAÇÃO"] = (
        df["inicio_dt"]
        .apply(calcular_duracao)
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
    # LOCAL
    # ========================================================

    df["local"] = (
        df["local"]
        .fillna("")
        .astype(str)
        .str.strip()
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
    #
    # Ainda não existe uma coluna de atividade no Supabase.
    # Mantemos "-" até adicionarmos essa informação.
    # ========================================================

    df["ATIVIDADE"] = "-"


    # ========================================================
    # ORDENAÇÃO
    # ========================================================

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
# ESCAPAR TEXTO PARA HTML
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

    if texto == "":
        texto = "-"

    return html.escape(
        texto,
        quote=True
    )


# ============================================================
# CRIAR HTML DA TABELA
# ============================================================

def criar_tabela_html(dataframe):

    partes = []

    partes.append(
        """
        <table class="tabela-tv">

            <thead>

                <tr>

                    <th class="col-frota">
                        FROTA
                    </th>

                    <th class="col-motivo">
                        MOTIVO
                    </th>

                    <th class="col-inicio">
                        INÍCIO
                    </th>

                    <th class="col-duracao">
                        DURAÇÃO
                    </th>

                    <th class="col-atividade">
                        ATIVIDADE
                    </th>

                </tr>

            </thead>

            <tbody>
        """
    )


    # ========================================================
    # SEM REGISTROS
    # ========================================================

    if dataframe.empty:

        partes.append(
            """
            <tr>

                <td class="col-frota linha-vazia">
                    -
                </td>

                <td class="col-motivo linha-vazia">
                    -
                </td>

                <td class="col-inicio linha-vazia">
                    -
                </td>

                <td class="col-duracao linha-vazia">
                    -
                </td>

                <td class="col-atividade linha-vazia">
                    -
                </td>

            </tr>
            """
        )


    # ========================================================
    # REGISTROS
    # ========================================================

    else:

        for _, linha in dataframe.iterrows():

            frota = escapar(
                linha.get("frota", "-")
            )

            motivo = escapar(
                linha.get("motivo", "-")
            )

            inicio = escapar(
                linha.get("INÍCIO", "-")
            )

            duracao = escapar(
                linha.get("DURAÇÃO", "-")
            )

            atividade = escapar(
                linha.get("ATIVIDADE", "-")
            )

            partes.append(
                f"""
                <tr>

                    <td
                        class="col-frota"
                        title="{frota}"
                    >
                        {frota}
                    </td>

                    <td
                        class="col-motivo"
                        title="{motivo}"
                    >
                        {motivo}
                    </td>

                    <td
                        class="col-inicio"
                        title="{inicio}"
                    >
                        {inicio}
                    </td>

                    <td
                        class="col-duracao"
                        title="{duracao}"
                    >
                        {duracao}
                    </td>

                    <td
                        class="col-atividade"
                        title="{atividade}"
                    >
                        {atividade}
                    </td>

                </tr>
                """
            )


    partes.append(
        """
            </tbody>

        </table>
        """
    )

    return "".join(partes)


# ============================================================
# MOSTRAR SETOR
# ============================================================

def mostrar_setor(nome, dataframe):

    tabela_html = criar_tabela_html(
        dataframe
    )

    bloco = f"""
    <div class="bloco-setor">

        <div class="titulo-setor-tv">
            {escapar(nome)}
        </div>

        {tabela_html}

    </div>
    """

    st.markdown(
        bloco,
        unsafe_allow_html=True
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

cabecalho = f"""
<div class="cabecalho-principal">

    <div class="cabecalho-icone">
        🛠️
    </div>

    <div class="cabecalho-titulo">
        CONTROLE DE MANUTENÇÃO - DIVERSOS
    </div>

    <div class="cabecalho-relogio">
        {agora.strftime("%d/%m/%Y %H:%M")}
    </div>

</div>
"""

st.markdown(
    cabecalho,
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
# COLUNA 1
# - Plantio
# - Conservação
# - Preparo de Solo
# - Torta de Filtro
#
# COLUNA 2
# - Herbicida
# - Cultivo
# - Fertirrigação
#
# COLUNA 3
# - Incêndio
# - Serviços Agrícolas
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
# OUTROS / NÃO CLASSIFICADOS
#
# Por enquanto vamos deixar visível.
# Assim conseguimos identificar frentes que ainda precisam
# ser adicionadas ao mapeamento.
# ============================================================

if not outros.empty:

    st.markdown(
        '<div class="separador-outros"></div>',
        unsafe_allow_html=True
    )

    mostrar_setor(
        "OUTROS / NÃO CLASSIFICADOS",
        outros
    )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    f"""
    <div class="rodape-tv">

        IFROTA → Supabase

        &nbsp;&nbsp;|&nbsp;&nbsp;

        BASE 3026

        &nbsp;&nbsp;|&nbsp;&nbsp;

        Tela atualizada em
        {agora.strftime("%d/%m/%Y %H:%M:%S")}

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AUTO REFRESH
#
# Atualiza a página a cada 60 segundos.
# ============================================================

@st.fragment(
    run_every="60s"
)
def auto_refresh():

    st.empty()


auto_refresh()
