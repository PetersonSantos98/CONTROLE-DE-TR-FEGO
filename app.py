import streamlit as st
import pandas as pd

from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client, Client


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Controle de Tráfego - Usina Iracema",
    page_icon="🚜",
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

    /* -------------------------------------------------------
       PÁGINA
       ------------------------------------------------------- */

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 1800px;
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


    /* -------------------------------------------------------
       TÍTULO PRINCIPAL
       ------------------------------------------------------- */

    .titulo-principal {
        font-size: 28px;
        font-weight: 800;
        color: #17365D;

        margin-bottom: 3px;
        padding-bottom: 5px;

        border-bottom: 3px solid #17365D;
    }


    /* -------------------------------------------------------
       ATUALIZAÇÃO
       ------------------------------------------------------- */

    .ultima-atualizacao {
        font-size: 14px;
        font-weight: 600;

        margin-top: 8px;
        margin-bottom: 18px;
    }


    /* -------------------------------------------------------
       BLOCO
       ------------------------------------------------------- */

    .bloco {
        margin-top: 16px;
        margin-bottom: 18px;
    }


    /* -------------------------------------------------------
       TÍTULO DAS TABELAS
       ------------------------------------------------------- */

    .titulo-tabela {
        background-color: #17365D;
        color: white;

        font-weight: 800;
        font-size: 17px;

        padding: 6px 10px;

        border: 1px solid #17365D;

        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .titulo-tabela-nome {
        display: inline-block;
    }

    .titulo-tabela-qtd {
        display: inline-block;
        text-align: center;
        min-width: 50px;
    }


    /* -------------------------------------------------------
       TABELA
       ------------------------------------------------------- */

    table.tabela-manutencao {
        width: 100%;
        border-collapse: collapse;

        font-size: 14px;

        margin: 0;

        table-layout: auto;
    }


    table.tabela-manutencao thead th {
        background-color: #17365D;
        color: white;

        font-weight: 700;

        text-align: center;

        padding: 5px 7px;

        border: 1px solid #9EA7B3;

        white-space: nowrap;
    }


    table.tabela-manutencao tbody td {
        padding: 5px 8px;

        border: 1px solid #9EA7B3;

        vertical-align: middle;
    }


    table.tabela-manutencao tbody tr:hover {
        background-color: rgba(100, 149, 237, 0.10);
    }


    /* -------------------------------------------------------
       COLUNAS
       ------------------------------------------------------- */

    .col-frota {
        text-align: center;
        font-weight: 700;
        white-space: nowrap;
    }

    .col-motivo {
        text-align: left;
        min-width: 280px;
    }

    .col-inicio {
        text-align: center;
        white-space: nowrap;
    }

    .col-tempo {
        text-align: center;
        font-weight: 700;
        white-space: nowrap;
    }

    .col-frente {
        text-align: center;
        white-space: nowrap;
    }

    .col-local {
        text-align: left;
        min-width: 170px;
    }


    /* -------------------------------------------------------
       SEM REGISTROS
       ------------------------------------------------------- */

    .sem-registros {
        padding: 10px;

        border-left: 1px solid #9EA7B3;
        border-right: 1px solid #9EA7B3;
        border-bottom: 1px solid #9EA7B3;

        font-size: 14px;

        color: #888;
    }


    /* -------------------------------------------------------
       RODAPÉ
       ------------------------------------------------------- */

    .rodape {
        margin-top: 30px;

        padding-top: 10px;

        border-top: 1px solid #555;

        font-size: 12px;

        color: #888;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CREDENCIAIS DO SUPABASE
# ============================================================

try:

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

except Exception:

    st.error(
        "As credenciais do Supabase não foram configuradas."
    )

    st.info(
        "No Streamlit Cloud, abra Settings > Secrets e adicione "
        "SUPABASE_URL e SUPABASE_KEY."
    )

    st.stop()


# ============================================================
# CONEXÃO COM SUPABASE
# ============================================================

@st.cache_resource
def iniciar_supabase():

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


try:

    supabase: Client = iniciar_supabase()

except Exception as erro:

    st.error(
        f"Erro ao conectar ao Supabase: {erro}"
    )

    st.stop()


# ============================================================
# CONSULTAR MANUTENÇÕES
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
            f"Erro ao consultar manutenções: {erro}"
        )

        return []


# ============================================================
# LIMPAR NÚMEROS
#
# Exemplo:
#
# 925.0 -> 925
# 1.0   -> 1
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
# CONVERTER HORÁRIO DO SUPABASE
#
# Supabase:
# UTC
#
# Aplicativo:
# America/Sao_Paulo
# ============================================================

def converter_inicio(valor):

    if valor is None:
        return pd.NaT

    try:

        if pd.isna(valor):
            return pd.NaT

    except Exception:
        pass

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
#
# Exemplo:
#
# 28/09 05:35
# ============================================================

def formatar_inicio(valor):

    if pd.isna(valor):
        return "-"

    return valor.strftime(
        "%d/%m %H:%M"
    )


# ============================================================
# CALCULAR TEMPO EM MANUTENÇÃO
#
# Exemplo:
#
# 00:42
# 05:13
# 148:50
# 1365:54
# ============================================================

def formatar_duracao(inicio):

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
# ESCAPAR HTML
# ============================================================

def escapar_html(valor):

    if valor is None:
        return ""

    texto = str(valor)

    texto = texto.replace(
        "&",
        "&amp;"
    )

    texto = texto.replace(
        "<",
        "&lt;"
    )

    texto = texto.replace(
        ">",
        "&gt;"
    )

    texto = texto.replace(
        '"',
        "&quot;"
    )

    texto = texto.replace(
        "'",
        "&#39;"
    )

    return texto


# ============================================================
# PREPARAR DATAFRAME
# ============================================================

def preparar_dataframe(dados):

    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(
        dados
    )


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


    # --------------------------------------------------------
    # SOMENTE COLHEITA
    # BASE 2026
    # --------------------------------------------------------

    df = df[
        df["base"] == 2026
    ].copy()


    # --------------------------------------------------------
    # TIPO
    # --------------------------------------------------------

    df["tipo_equipamento"] = (
        df["tipo_equipamento"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )


    # --------------------------------------------------------
    # FROTA
    # --------------------------------------------------------

    df["frota"] = (
        df["frota"]
        .apply(limpar_numero)
    )


    # --------------------------------------------------------
    # GLEBA
    # --------------------------------------------------------

    df["gleba"] = (
        df["gleba"]
        .apply(limpar_numero)
    )


    # --------------------------------------------------------
    # INÍCIO
    # --------------------------------------------------------

    df["inicio_dt"] = (
        df["inicio"]
        .apply(converter_inicio)
    )


    # --------------------------------------------------------
    # FRENTE
    # --------------------------------------------------------

    df["frente_exibicao"] = (
        df["frente"]
        .apply(normalizar_frente)
    )


    # --------------------------------------------------------
    # LOCAL
    # --------------------------------------------------------

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
    # TEMPO
    # --------------------------------------------------------

    df["tempo"] = (
        df["inicio_dt"]
        .apply(formatar_duracao)
    )


    # --------------------------------------------------------
    # INÍCIO FORMATADO
    # --------------------------------------------------------

    df["inicio_exibicao"] = (
        df["inicio_dt"]
        .apply(formatar_inicio)
    )


    # --------------------------------------------------------
    # ORDENAR
    #
    # Manutenções mais antigas primeiro.
    # --------------------------------------------------------

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
# GERAR TABELA HTML
# ============================================================

def gerar_tabela(
    dataframe,
    titulo
):

    quantidade = len(
        dataframe
    )


    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    html = f"""
    <div class="bloco">

        <div class="titulo-tabela">

            <span class="titulo-tabela-nome">
                {escapar_html(titulo)}
            </span>

            <span class="titulo-tabela-qtd">
                {quantidade}
            </span>

        </div>
    """


    # --------------------------------------------------------
    # SEM REGISTROS
    # --------------------------------------------------------

    if dataframe.empty:

        html += """
        <div class="sem-registros">
            Nenhum equipamento em manutenção.
        </div>

        </div>
        """

        return html


    # --------------------------------------------------------
    # CABEÇALHO DA TABELA
    # --------------------------------------------------------

    html += """
    <table class="tabela-manutencao">

        <thead>

            <tr>

                <th>FROTA</th>

                <th>MOTIVO</th>

                <th>INÍCIO</th>

                <th>TEMPO</th>

                <th>FRENTE</th>

                <th>LOCAL</th>

            </tr>

        </thead>

        <tbody>
    """


    # --------------------------------------------------------
    # LINHAS
    # --------------------------------------------------------

    for _, linha in dataframe.iterrows():

        frota = escapar_html(
            linha["frota"]
        )

        motivo = escapar_html(
            linha["motivo"]
        )

        inicio = escapar_html(
            linha["inicio_exibicao"]
        )

        tempo = escapar_html(
            linha["tempo"]
        )

        frente = escapar_html(
            linha["frente_exibicao"]
        )

        local = escapar_html(
            linha["local"]
        )


        html += f"""
        <tr>

            <td class="col-frota">
                {frota}
            </td>

            <td class="col-motivo">
                {motivo}
            </td>

            <td class="col-inicio">
                {inicio}
            </td>

            <td class="col-tempo">
                {tempo}
            </td>

            <td class="col-frente">
                {frente}
            </td>

            <td class="col-local">
                {local}
            </td>

        </tr>
        """


    html += """
        </tbody>

    </table>

    </div>
    """


    return html


# ============================================================
# TÍTULO PRINCIPAL
# ============================================================

st.markdown(
    """
    <div class="titulo-principal">

        CONTROLE DE TRÁFEGO - USINA IRACEMA

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LINHA DE ATUALIZAÇÃO
# ============================================================

col_atualizacao, col_botao = st.columns(
    [8, 1]
)


# ============================================================
# BOTÃO ATUALIZAR
# ============================================================

with col_botao:

    if st.button(
        "🔄 Atualizar",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()


# ============================================================
# BUSCAR DADOS
# ============================================================

dados = buscar_manutencoes()


# ============================================================
# PREPARAR DADOS
# ============================================================

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
# MOSTRAR ATUALIZAÇÃO
# ============================================================

with col_atualizacao:

    st.markdown(
        f"""
        <div class="ultima-atualizacao">

            Última Atualização:
            {agora.strftime("%d/%m/%Y %H:%M")}

            &nbsp;&nbsp; 🟢

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DATAFRAMES VAZIOS
# ============================================================

if df.empty:

    df_colhedoras = pd.DataFrame(
        columns=df.columns
    )

    df_tratores = pd.DataFrame(
        columns=df.columns
    )

    df_transporte = pd.DataFrame(
        columns=df.columns
    )


else:

    # ========================================================
    # COLHEDORAS
    #
    # BASE 2026
    # CLASSE 4
    # tipo_equipamento = MAQUINA
    # ========================================================

    df_colhedoras = df[
        df["tipo_equipamento"]
        .eq("MAQUINA")
    ].copy()


    # ========================================================
    # TRATORES
    #
    # BASE 2026
    # CLASSE 2
    # tipo_equipamento = TRATOR
    # ========================================================

    df_tratores = df[
        df["tipo_equipamento"]
        .eq("TRATOR")
    ].copy()


    # ========================================================
    # TRANSPORTE DE CANA
    #
    # BASE 2026
    # CLASSE 1
    # tipo_equipamento = CAMINHAO
    # ========================================================

    df_transporte = df[
        df["tipo_equipamento"]
        .eq("CAMINHAO")
    ].copy()


# ============================================================
# COLHEDORAS
# ============================================================

st.markdown(
    gerar_tabela(
        df_colhedoras,
        "COLHEDORAS"
    ),
    unsafe_allow_html=True
)


# ============================================================
# TRATORES
# ============================================================

st.markdown(
    gerar_tabela(
        df_tratores,
        "TRATORES"
    ),
    unsafe_allow_html=True
)


# ============================================================
# TRANSPORTE DE CANA
# ============================================================

st.markdown(
    gerar_tabela(
        df_transporte,
        "TRANSP. CANA"
    ),
    unsafe_allow_html=True
)


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    f"""
    <div class="rodape">

        Dados de manutenção:
        IFROTA → Supabase

        &nbsp;&nbsp;|&nbsp;&nbsp;

        Tela atualizada em
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
