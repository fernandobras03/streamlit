import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import io
from streamlit_sortables import sort_items

# ──────────────────────────────────────────────
# Estilização Visual Integrada
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Inputs de texto e datas */
    .stTextInput input, .stDateInput input {
        background-color: #ffffff !important; 
        border: 1px solid #cbd5e1 !important; 
        color: #1e293b !important; 
        border-radius: 6px;
    }
    
    /* Botão Principal */
    div.stButton > button {
        width: 100%; 
        background-color: #004a87; 
        color: #ffffff !important; 
        font-weight: 600; 
        border-radius: 8px; 
        height: 3em;
    }
    div.stButton > button:hover { 
        background-color: #00356b; 
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Configurações e Dicionário de Alias
# ──────────────────────────────────────────────
API_URL = "https://api-corp.cna.org.br/sisateg_rel_listar_visita/_search"
PAGE_SIZE = 10_000

# Mapeamento: "Nome Técnico no Banco" -> "Alias/Nome Amigável"
COLUNAS_MAP = {
    "ano_referencia_visita": "Ano Referência Visita",
    "dt_visita": "Data da Visita",
    "id_visita": "ID Visita",
    "cpf_produtor": "CPF do Produtor",
    "produtor": "Nome do Produtor",
    "projeto": "Projeto",
    "atividade": "Atividade",
    "status_propriedade": "Status da Propriedade",
    "area_propriedade": "Área da Propriedade",
    "tecnico_responsavel": "Técnico Responsável",
    "supervisor_atual": "Supervisor Atual"
}

# ──────────────────────────────────────────────
# Motor de Extração (Elasticsearch)
# ──────────────────────────────────────────────
def extrair_relatorio_dinamico(usuario, senha, dt_inicio, dt_fim, colunas_tecnicas):
    all_hits = []
    search_after = None
    progresso_msg = st.empty()

    # O Elasticsearch permite buscar colunas específicas no '_source'
    # Adicionamos dt_visita e id_visita obrigatoriamente no _source apenas para garantir a ordenação/paginação
    colunas_busca = list(set(colunas_tecnicas + ["dt_visita", "id_visita"]))

    while True:
        query_json = {
            "size": PAGE_SIZE,
            "_source": colunas_busca,
            "query": {
                "range": {
                    "dt_visita": {
                        "gte": dt_inicio,
                        "lte": dt_fim,
                        "format": "yyyy-MM-dd"
                    }
                }
            },
            "sort": [
                {"dt_visita": "asc"},
                {"id_visita": "asc"} 
            ]
        }

        if search_after:
            query_json["search_after"] = search_after

        response = requests.post(API_URL, json=query_json, auth=HTTPBasicAuth(usuario, senha), timeout=120)

        if response.status_code != 200:
            st.error(f"❌ Erro de Comunicação (Status {response.status_code}): {response.text}")
            return pd.DataFrame()

        res_data = response.json()
        hits = res_data.get("hits", {}).get("hits", [])

        if not hits:
            break

        all_hits.extend(hits)
        search_after = hits[-1].get("sort")
        
        progresso_msg.info(f"⏳ Extraindo dados do servidor... Total acumulado: **{len(all_hits):,}** registros.")

        if len(hits) < PAGE_SIZE:
            break

    progresso_msg.empty()

    if not all_hits:
        return pd.DataFrame()

    # Converte os dados brutos num DataFrame
    flat_data = [item["_source"] for item in all_hits]
    df = pd.DataFrame(flat_data)

    # Filtra e ordena o DataFrame EXATAMENTE como o utilizador pediu no arrastar e soltar
    # (Ignora dt_visita e id_visita se eles não tiverem sido selecionados para o relatório final)
    colunas_presentes = [c for c in colunas_tecnicas if c in df.columns]
    df = df[colunas_presentes]

    return df

# ──────────────────────────────────────────────
# Interface da Página
# ──────────────────────────────────────────────
def main():
    # 1. Validação de Segurança Interna
    if "logado" not in st.session_state or not st.session_state.logado:
        st.warning("⚠️ Acesso negado. Por favor, faça o login na página inicial.")
        st.stop()

    st.title("🛠️ Construtor de Relatórios")
    st.markdown("Crie extrações personalizadas escolhendo apenas as colunas que precisa.")
    
    # 2. Filtros de Período
    st.subheader("🗓️ Filtros Obrigatórios")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dt_inicio = st.date_input("Data Início", value=None, format="DD/MM/YYYY")
    with col_d2:
        dt_fim = st.date_input("Data Fim", value=None, format="DD/MM/YYYY")

    st.markdown("---")

    # 3. Área de Montagem (Drag and Drop)
    st.subheader("🏗️ Seleção e Ordenação de Colunas")
    st.caption("Arraste os blocos da esquerda para a área 'Selecionadas' à direita. A ordem na direita definirá a disposição no Excel.")
    
    # Inicializa o state com os NOMES AMIGÁVEIS
    nomes_amigaveis = list(COLUNAS_MAP.values())
    
    if 'colunas_construtor' not in st.session_state:
        st.session_state.colunas_construtor = [
            {'header': '📄 Colunas Disponíveis', 'items': nomes_amigaveis},
            {'header': '✅ Colunas Selecionadas', 'items': []}
        ]

    # Renderiza o componente de arrastar e soltar
    st.session_state.colunas_construtor = sort_items(
        st.session_state.colunas_construtor, 
        multi_containers=True, 
        direction='vertical'
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Ação de Extração
    if st.button("🚀 Iniciar Extração Personalizada", use_container_width=True):
        nomes_selecionados = st.session_state.colunas_construtor[1]['items']
        
        if not nomes_selecionados:
            st.error("⚠️ Arraste pelo menos uma coluna para a área de 'Colunas Selecionadas'.")
            st.stop()
        if dt_inicio is None or dt_fim is None:
            st.error("⚠️ Preencha a Data de Início e a Data de Fim.")
            st.stop()

        try:
            # Tradutor reverso: Pega o nome amigável e descobre o nome técnico no banco
            mapa_reverso = {v: k for k, v in COLUNAS_MAP.items()}
            colunas_tecnicas = [mapa_reverso[nome] for nome in nomes_selecionados]

            str_inicio = dt_inicio.strftime('%Y-%m-%d')
            str_fim = dt_fim.strftime('%Y-%m-%d')
            
            # Chama a API com as credenciais já validadas na página principal
            df_result = extrair_relatorio_dinamico(
                st.session_state.usuario, 
                st.session_state.senha, 
                str_inicio, 
                str_fim, 
                colunas_tecnicas
            )
            
            if not df_result.empty:
                # Renomeia as colunas técnicas para os nomes bonitos (Alias)
                df_result = df_result.rename(columns=COLUNAS_MAP)
                
                # Trata nulos básicos
                df_result = df_result.fillna("NI")

                st.session_state['df_construtor'] = df_result
                st.success(f"✅ Extração finalizada com sucesso!")
            else:
                st.warning("Nenhum registro encontrado para este período.")
                
        except Exception as e:
            st.error(f"❌ Erro operacional: {e}")

    # 5. Visualização e Download (Aparece após o sucesso)
    if 'df_construtor' in st.session_state and not st.session_state['df_construtor'].empty:
        df_exibir = st.session_state['df_construtor']
        
        st.markdown("---")
        st.markdown(f"**Prévia do Relatório Customizado** (Total: {len(df_exibir):,} registros)")
        st.dataframe(df_exibir.head(100), use_container_width=True, height=350)

        # Buffer de exportação
        buffer = io.BytesIO()
        df_exibir.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)

        st.download_button(
            label=f"📥 Baixar Relatório Customizado CSV ({len(df_exibir):,} linhas)",
            data=buffer,
            file_name=f"relatorio_customizado_{dt_inicio}_a_{dt_fim}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Para rodar corretamente quando chamado pelo st.navigation
main()