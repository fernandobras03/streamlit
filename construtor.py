import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import io
from datetime import date
from streamlit_sortables import sort_items

# ──────────────────────────────────────────────
# Dicionário de Colunas (Alias Amigável)
# ──────────────────────────────────────────────
COLUNAS_MAP = {
    "ano_referencia_visita": "Ano Referência Visita",
    "area_propriedade": "Área da Propriedade",
    "cpf_produtor": "CPF do Produtor",
    "dt_alteracao_geral": "Data Alteração Geral",
    "dt_alteracao_visita": "Data Alteração Visita",
    "dt_checkin": "Data Check-in",
    "dt_checkout": "Data Check-out",
    "dt_exclusao_visita": "Data Exclusão Visita",
    "dt_primeira_visita_projeto": "Data Primeira Visita Projeto",
    "dt_visita": "Data da Visita",
    "dt_visita_min": "Data Visita Min",
    "duracao_visita": "Duração da Visita",
    "email_produtor": "Email do Produtor",
    "flg_primeira_visita": "Flag Primeira Visita",
    "flg_coleta_dados": "Flag Coleta Dados",
    "flg_retorno": "Flag Retorno",
    "flg_visita_remota": "Flag Visita Remota",
    "flg_visita_valida_mov_visita": "Flag Visita Válida Mov.",
    "id_grupo_produtor": "ID Grupo Produtor",
    "grupo_produtor": "Grupo Produtor",
    "id_visita": "ID Visita",
    "numero_visita": "Número da Visita",
    "ordem_visita": "Ordem da Visita",
    "perfil_fundiario": "Perfil Fundiário",
    "produtor": "Produtor",
    "projeto": "Projeto",
    "atividade": "Atividade",
    "tecnico_responsavel": "Técnico Responsável",
    "status_propriedade": "Status da Propriedade",
    "supervisor_atual": "Supervisor Atual",
    "qtd_visitas": "Qtd. Visitas",
    "qtd_visitas_projeto": "Qtd. Visitas Projeto",
    "visita_presencial": "Visita Presencial",
    "visita_retorno": "Visita de Retorno",
    "visita_valida": "Visita Válida",
    "visita_virtual": "Visita Virtual",
    "visita_zero": "Visita Zero"
}

# Criamos um mapa reverso para o sistema saber qual é o nome no banco de dados
REVERSE_MAP = {v: k for k, v in COLUNAS_MAP.items()}
API_URL = "https://api-corp.cna.org.br/sisateg_rel_listar_visita/_search"
PAGE_SIZE = 10_000

# ──────────────────────────────────────────────
# Lógica de Extração
# ──────────────────────────────────────────────
def extrair_relatorio_dinamico(usuario, senha, dt_inicio, dt_fim, colunas_internas, colunas_amigaveis):
    all_hits = []
    search_after = None
    progresso_msg = st.empty()

    filtros_elastic = [
        {
            "range": {
                "dt_visita": {
                    "gte": dt_inicio,
                    "lte": dt_fim,
                    "format": "yyyy-MM-dd"
                }
            }
        }
    ]

    while True:
        query_json = {
            "size": PAGE_SIZE,
            "_source": colunas_internas, # Pede apenas as colunas que o usuário arrastou
            "query": {
                "bool": {
                    "filter": filtros_elastic
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
            st.error(f"❌ Erro na API ({response.status_code}): {response.text}")
            return pd.DataFrame()

        res_data = response.json()
        hits = res_data.get("hits", {}).get("hits", [])

        if not hits:
            break

        all_hits.extend(hits)
        search_after = hits[-1].get("sort")
        
        progresso_msg.info(f"⏳ Extraindo lotes da API... Total até agora: **{len(all_hits):,}** registros.")

        if len(hits) < PAGE_SIZE:
            break

    progresso_msg.empty()

    if not all_hits:
        return pd.DataFrame()

    # Transforma os dados em DataFrame garantindo que todas as colunas requisitadas existam
    flat_data = [item["_source"] for item in all_hits]
    df = pd.DataFrame(flat_data, columns=colunas_internas)
    
    # Renomeia para os nomes amigáveis e reordena conforme a escolha do usuário
    df.rename(columns=COLUNAS_MAP, inplace=True)
    return df[colunas_amigaveis]

# ──────────────────────────────────────────────
# Interface da Página
# ──────────────────────────────────────────────
def main():
    # Estilização visual limpa
    st.markdown("""
    <style>
        .stDateInput input { border-radius: 6px; }
        div.stButton > button {
            background-color: #004a87; color: white !important; font-weight: 600; border-radius: 8px; height: 3em;
        }
        div.stButton > button:hover { background-color: #00356b; }
    </style>
    """, unsafe_allow_html=True)

    st.title("📋 Construtor de Relatórios Dinâmico")
    st.markdown("Monte seu próprio relatório arrastando as colunas desejadas.")
    
    # 1. Filtros de Data
    st.subheader("🗓️ 1. Defina o Período")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dt_inicio = st.date_input("Data Inicial *", value=None, format="DD/MM/YYYY")
    with col_d2:
        dt_fim = st.date_input("Data Final *", value=None, format="DD/MM/YYYY")

    st.markdown("---")

    # 2. Área de Montagem (Drag and Drop)
    st.subheader("🏗️ 2. Seleção e Ordem das Colunas")
    st.caption("Arraste os campos da esquerda para a direita. A ordem na caixa 'Selecionadas' definirá a ordem no seu CSV final.")
    
    # Pega apenas os nomes amigáveis para mostrar na interface
    nomes_amigaveis = list(COLUNAS_MAP.values())

    if 'colunas_config' not in st.session_state:
        st.session_state.colunas_config = [
            {'header': 'Campos Disponíveis', 'items': nomes_amigaveis},
            {'header': 'Colunas Selecionadas (Arraste para cá)', 'items': []}
        ]

    # Renderiza o componente Drag and Drop
    st.session_state.colunas_config = sort_items(
        st.session_state.colunas_config, 
        multi_containers=True, 
        direction='vertical'
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Ação de Extrair
    if st.button("🚀 Gerar e Extrair Relatório", use_container_width=True):
        colunas_amigaveis_selecionadas = st.session_state.colunas_config[1]['items']
        
        # Recupera as credenciais que vieram do login (pagina_principal.py)
        usuario_logado = st.session_state.get('usuario', '')
        senha_logada = st.session_state.get('senha', '')

        # Validações
        if not colunas_amigaveis_selecionadas:
            st.error("⚠️ Selecione pelo menos uma coluna arrastando para a área direita.")
        elif not dt_inicio or not dt_fim:
            st.error("⚠️ As datas Inicial e Final são obrigatórias.")
        else:
            try:
                # Converte as datas para o padrão do Elasticsearch
                str_inicio = dt_inicio.strftime('%Y-%m-%d')
                str_fim = dt_fim.strftime('%Y-%m-%d')
                
                # Traduz de volta os Nomes Amigáveis para os Nomes do Banco de Dados
                colunas_internas_selecionadas = [REVERSE_MAP[nome] for nome in colunas_amigaveis_selecionadas]
                
                # Executa a busca
                df_result = extrair_relatorio_dinamico(
                    usuario_logado, 
                    senha_logada, 
                    str_inicio, 
                    str_fim, 
                    colunas_internas_selecionadas,
                    colunas_amigaveis_selecionadas
                )
                
                st.session_state['df_construtor'] = df_result
                
                if not df_result.empty:
                    st.success(f"✅ Sucesso! Relatório gerado com {len(df_result):,} linhas.")
                else:
                    st.warning("Nenhum registro encontrado para este período.")
                    
            except Exception as e:
                st.error(f"❌ Erro operacional: {e}")

    # 4. Exibição e Download
    if 'df_construtor' in st.session_state and not st.session_state['df_construtor'].empty:
        df_exibir = st.session_state['df_construtor']
        
        st.markdown("---")
        st.markdown(f"**Prévia do Relatório Montado** (Mostrando 100 de {len(df_exibir):,} registros)")
        
        # Exibe o dataframe mantendo a ordem exata que o usuário escolheu
        st.dataframe(df_exibir.head(100), use_container_width=True, height=350)

        buffer = io.BytesIO()
        df_exibir.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)

        st.download_button(
            label=f"📥 Baixar Relatório Customizado em CSV",
            data=buffer,
            file_name=f"relatorio_customizado_{dt_inicio}_a_{dt_fim}.csv",
            mime="text/csv",
            use_container_width=True
        )

# O Streamlit chama a função nativamente ao acessar a página
main()