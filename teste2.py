import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import io

# ──────────────────────────────────────────────
# Configuração da Página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="CNA · SISATEG (Pessoas)",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Estilos Customizados (UI/UX Clean & Contraste)
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }

    /* Sidebar com melhor contraste para inputs */
    section[data-testid="stSidebar"] {
        background-color: #e2e8f0;
        border-right: 1px solid #cbd5e1;
    }
    
    /* Inputs de texto muito mais visíveis */
    .stTextInput input {
        background-color: #ffffff !important;
        border: 1px solid #64748b !important;
        color: #0f172a !important;
        border-radius: 6px;
        padding: 0.5rem;
    }
    .stTextInput input:focus {
        border-color: #004a87 !important;
        box-shadow: 0 0 0 2px rgba(0, 74, 135, 0.2) !important;
    }

    /* Botão de Ação Principal (Azul CNA) */
    div.stButton > button {
        width: 100%;
        background-color: #004a87;
        color: #ffffff !important;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6em 1em;
        border: none;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 74, 135, 0.2);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #00356b;
        box-shadow: 0 10px 15px -3px rgba(0, 74, 135, 0.3);
        transform: translateY(-1px);
    }

    /* Cards de Métricas Estilizados */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 5px solid #004a87;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #475569;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Constantes de Configuração
# ──────────────────────────────────────────────
API_URL = "https://api-corp.cna.org.br/sisateg_pessoa/_search"
PAGE_SIZE = 10_000

COLUNAS = {
    "categoria_pessoa": "Categoria da Pessoa",
    "celular": "Celular",
    "cep": "CEP",
    "cpf": "CPF",
    "dt_alteracao": "Data da Última Alteração",
    "dt_exclusao": "Data de Exclusão",
    "estado_civil": "Estado Civil",
    "id_pessoa": "ID da Pessoa",
    "nome": "Nome Completo",
    "status_pessoa": "Status pessoa",
    "uf_regional": "UF Regional",
}

# ──────────────────────────────────────────────
# Lógica de Extração
# ──────────────────────────────────────────────
def buscar_todos_os_registros(usuario: str, senha: str) -> pd.DataFrame:
    all_hits = []
    search_after = None

    while True:
        query_json = {
            "size": PAGE_SIZE,
            "_source": list(COLUNAS.keys()),
            "query": {
                "match_all": {}
            },
            "sort": [
                {"id_pessoa": "asc"}
            ],
        }

        if search_after:
            query_json["search_after"] = search_after

        response = requests.post(
            API_URL,
            json=query_json,
            auth=HTTPBasicAuth(usuario, senha),
            timeout=120,
        )

        if response.status_code == 401:
            st.error("❌ Falha de Autenticação. Verifique seu usuário e senha.")
            return pd.DataFrame()

        if response.status_code != 200:
            st.error(f"❌ Erro de Comunicação (Status {response.status_code}): {response.text}")
            return pd.DataFrame()

        res_data = response.json()
        hits = res_data.get("hits", {}).get("hits", [])

        if not hits:
            break

        all_hits.extend(hits)
        search_after = hits[-1].get("sort")

        if len(hits) < PAGE_SIZE:
            break

    if not all_hits:
        return pd.DataFrame()

    flat_data = [item["_source"] for item in all_hits]
    df = pd.DataFrame(flat_data, columns=list(COLUNAS.keys()))
    df = df.rename(columns=COLUNAS)
    
    # Tratamento de dados vazios garantindo que não quebre a interface
    if "Status pessoa" in df.columns:
        df["Status pessoa"] = df["Status pessoa"].fillna("NÃO INFORMADO").astype(str).str.strip().str.upper()
        df.loc[df["Status pessoa"].isin(["NAN", "NONE", "", "NULL"]), "Status pessoa"] = "NÃO INFORMADO"
        
    if "Categoria da Pessoa" in df.columns:
        df["Categoria da Pessoa"] = df["Categoria da Pessoa"].fillna("NÃO INFORMADO").astype(str).str.strip().str.upper()
        df.loc[df["Categoria da Pessoa"].isin(["NAN", "NONE", "", "NULL"]), "Categoria da Pessoa"] = "NI"

    return df

# ──────────────────────────────────────────────
# Interface e Fluxo Principal
# ──────────────────────────────────────────────
def main():
    with st.sidebar:
        st.image(
            "https://i.ibb.co/ZzLmGh8X/Logo-Senar-Preferencial-RGB.png",
            width=160,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔐 Autenticação")
        usuario = st.text_input("Usuário", placeholder="Ex: fernando.cruz")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        st.divider()
        st.caption("Acesso à base corporativa `sisateg_pessoa`")

    st.title("📋 Painel SISATEG — Pessoas")
    st.markdown("Consulte e exporte a base de dados completa de cadastros integrados ao sistema.")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Iniciar Extração Completa", use_container_width=True):
        if not usuario or not senha:
            st.warning("⚠️ Operação interrompida: Credenciais ausentes na barra lateral.")
            st.stop()

        try:
            # Spinner limpo e sem histórico
            with st.spinner("Extraindo informações do servidor. Isso pode levar alguns minutos..."):
                st.session_state['df_pessoas'] = buscar_todos_os_registros(usuario, senha)
            
            if not st.session_state['df_pessoas'].empty:
                st.success("✅ Carga finalizada com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro operacional: {e}")
            st.stop()

    if 'df_pessoas' in st.session_state and not st.session_state['df_pessoas'].empty:
        df_orig = st.session_state['df_pessoas']

        # ── KPI Cards ──
        # st.markdown("### 📊 Indicadores Principais")
        # kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        # total_rows = len(df_orig)
        # kpi1.metric("Total Cadastrado", f"{total_rows:,}".replace(",", "."))
        
        # if "Status Pessoa" in df_orig.columns:
        #     ativos = df_orig["Status pessoa"].eq("ATIVO").sum()
        #     kpi2.metric("Pessoas Ativas", f"{ativos:,}".replace(",", "."))
        # else:
        #     kpi2.metric("Pessoas Ativas", "0")
            
        # if "Categoria da Pessoa" in df_orig.columns:
        #     categorias_distintas = df_orig["Categoria da Pessoa"].nunique()
        #     kpi3.metric("Tipos de categoria", categorias_distintas)
        # else:
        #     kpi3.metric("Tipos de Categoria", "0")
            
        # ── Seção de Filtros Dinâmicos ──
        df_filtrado = df_orig.copy()
        
        with st.expander("🔎 Filtrar Base de Dados", expanded=True):
            f_col1, f_col2 = st.columns(2)
            
            with f_col1:
                if "Status pessoa" in df_orig.columns:
                    opcoes_status = sorted(df_orig["Status pessoa"].unique())
                    status_sel = st.multiselect("Filtrar por Status:", options=opcoes_status, default=opcoes_status)
                    if status_sel:
                        df_filtrado = df_filtrado[df_filtrado["Status pessoa"].isin(status_sel)]
                        
            with f_col2:
                if "Categoria da Pessoa" in df_orig.columns:
                    opcoes_categoria = sorted(df_orig["Categoria da Pessoa"].unique())
                    categoria_sel = st.multiselect("Filtrar por Categoria:", options=opcoes_categoria, default=opcoes_categoria)
                    if categoria_sel:
                        df_filtrado = df_filtrado[df_filtrado["Categoria da Pessoa"].isin(categoria_sel)]

        # ── Data View e Exportação ──
        st.markdown("---")
        st.markdown(f"**Prévia dos Dados** (Exibindo os primeiros 100 de {len(df_filtrado):,} registros filtrados)".replace(",", "."))
        
        st.dataframe(df_filtrado.head(100), use_container_width=True, height=350)

        buffer = io.BytesIO()
        df_filtrado.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)

        st.download_button(
            label=f"📄 Exportar Base Filtrada ({len(df_filtrado):,} linhas)".replace(",", "."),
            data=buffer,
            file_name="exportacao_sisateg_pessoa.csv",
            mime="text/csv",
            use_container_width=True,
        )

if __name__ == "__main__":
    main()