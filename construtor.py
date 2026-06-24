import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items

# Configuração da Página
st.set_page_config(page_title="SISATEG · Construtor de Relatórios", layout="wide")

# Colunas disponíveis na API (Mapeamento oficial)
COLUNAS_DISPONIVEIS = [
    "ano_referencia_visita", "area_propriedade", "cpf_produtor", "dt_visita", 
    "id_visita", "produtor", "projeto", "atividade", "status_propriedade", 
    "tecnico_responsavel", "supervisor_atual"
]

def main():
    st.title("📋 Construtor de Relatórios SISATEG")
    
    # 1. Filtros de Data
    st.subheader("🗓️ Filtros de Período")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dt_inicio = st.date_input("Data Início", value=None, format="DD/MM/YYYY")
    with col_d2:
        dt_fim = st.date_input("Data Fim", value=None, format="DD/MM/YYYY")

    st.markdown("---")

    # 2. Área de Montagem (Drag and Drop)
    st.subheader("🏗️ Seleção de Colunas")
    st.caption("Arraste da esquerda para a direita. A ordem da direita define a ordem das colunas.")
    
    # Inicialização do estado com um nome único para evitar conflito
    if 'colunas_config' not in st.session_state:
        st.session_state.colunas_config = [
            {'header': 'Disponíveis', 'items': COLUNAS_DISPONIVEIS},
            {'header': 'Selecionadas', 'items': []}
        ]

    # Renderiza o componente - passando a lista pura do session_state
    # O sort_items retorna a lista atualizada
    st.session_state.colunas_config = sort_items(
        st.session_state.colunas_config, 
        multi_containers=True, 
        direction='vertical'
    )

    # 3. Ação de Extrair
    if st.button("🚀 Extrair Relatório", use_container_width=True):
        # Acessando os itens do segundo container (Selecionadas)
        colunas_selecionadas = st.session_state.colunas_config[1]['items']
        
        if not colunas_selecionadas:
            st.error("Selecione pelo menos uma coluna arrastando para a área 'Selecionadas'.")
        elif not dt_inicio or not dt_fim:
            st.error("Preencha o período de datas.")
        else:
            # Feedback Visual
            st.info(f"Colunas selecionadas: {', '.join(colunas_selecionadas)}")
            
            # Aqui você deve colocar a lógica de 'requests.post' 
            # usando colunas_selecionadas no '_source' da query.
            st.success("Configuração validada! Lógica de API pronta para integrar.")

if __name__ == "__main__":
    main()