import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from datetime import date

# Configurações da Página
st.set_page_config(page_title="Relatório SISATEG - CNA", layout="wide")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #004a87;
        color: white;
        font-weight: bold;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📊 Consulta de Visitas SISATEG")
    st.info("Extração de grandes volumes via SearchAfter (id_visita)")

    with st.sidebar:
        st.header("🔑 Credenciais")
        user_input = st.text_input("Usuário")
        pass_input = st.text_input("Senha", type="password")

    st.subheader("📅 Período da Consulta")
    col1, col2 = st.columns(2)
    with col1:
        dt_inicio = st.date_input("Data Inicial", value=date(2026, 1, 1))
    with col2:
        dt_fim = st.date_input("Data Final", value=date.today())

    nomes_amigaveis = {
        "uf_regional": "UF",
        "municipio_propriedade": "Município",
        "grupo_produtor": "Grupo Produtor",
        "id_tecnico_atual": "Id. Técnico Atual",
        "id_produtor": "ID Produtor",
        "id_propriedade": "ID Propriedade",
        "ind_sustentabilidade_1": "Ind. Sustentabilidade 1",
        "ind_sustentabilidade_2": "Ind. Sustentabilidade 2",
        "produtor": "Produtor",
        "cpf_produtor": "CPF",
        "imovel": "Imóvel",
        "area_total": "Área total propriedade",
        "area_produtiva_cadastrada": "Área Total Produtiva",
        "area_arrendada": "Área Arrendada",
        "perfil_fundiario": "Perfil fundiário",
        "dt_visita": "Data da Visita",
        "ordem_visita": "Ordem da Visita no Dia",
        "numero_visita": "Nº da Visita",
        "projeto": "Projeto",
        "qtd_lancamentos": "Lançamentos",
        "qtd_ir": "IR",
        "visita_zero": "Dat. Visita Zero",
        "qtd_visitas": "Qtd. Visitas",
        "dt_primeira_visita_projeto": "Primeira Visita no Projeto",
        "qtd_visitas_projeto": "Qtd. Visitas no Projeto",
        "pendencia_ir": "Pendencia IR",
        "qtd_orientacao": "Orientações na Visita",
        "qtd_planejamento": "Planejamentos",
        "atividade": "Atividade",
        "supervisor_atual": "Supervisor Atual",
        "supervisor_anterior": "Supervisor Anterior",
        "tecnico_atual": "Técnico Atual",
        "tecnico_responsavel": "Técnico Responsável pela Visita",
        "dt_sincronizacao": "Ultima Sincronização",
        "dt_checkin": "Data do Checkin",
        "dt_checkout": "Data do Checkout",
        "duracao_visita": "Duração da Visita",
        "flg_coleta_dados": "Coleta de Dados",
        "visita_retorno": "Visita Retorno",
        "visita_virtual": "Atendimento Remoto",
        "flg_primeira_visita": "Visita Zero",
        "visita_valida": "Visita Válida?",
        "id_visita": "ID Visita Interno" # Adicionado para servir de âncora no SORT
    }
    
    colunas_tecnicas = list(nomes_amigaveis.keys())

    if st.button("🔍 Gerar Relatório"):
        if not user_input or not pass_input:
            st.error("Informe as credenciais.")
        else:
            all_hits = []
            search_after = None
            status_text = st.empty()
            
            try:
                url = "https://api-corp.cna.org.br/sisateg_rel_listar_visita/_search"
                
                while True:
                    query_json = {
                        "size": 10000,
                        "_source": colunas_tecnicas,
                        "query": {
                            "range": {
                                "dt_visita": {
                                    "gte": dt_inicio.strftime('%Y-%m-%d'),
                                    "lte": dt_fim.strftime('%Y-%m-%d'),
                                    "format": "yyyy-MM-dd"
                                }
                            }
                        },
                        "sort": [
                            {"dt_visita": "asc"},
                            {"id_visita": "asc"} # Uso de campo de negócio para ordenação
                        ]
                    }

                    if search_after:
                        query_json["search_after"] = search_after

                    response = requests.post(
                        url, 
                        json=query_json, 
                        auth=HTTPBasicAuth(user_input, pass_input),
                        timeout=120
                    )

                    if response.status_code != 200:
                        st.error(f"Erro na API ({response.status_code}): {response.text}")
                        break

                    res_data = response.json()
                    hits = res_data.get('hits', {}).get('hits', [])
                    
                    if not hits:
                        break
                    
                    all_hits.extend(hits)
                    search_after = hits[-1].get("sort")
                    
                    status_text.text(f"Registros recuperados: {len(all_hits)}...")
                    
                    if len(hits) < 10000:
                        break

                if all_hits:
                    flat_data = [item['_source'] for item in all_hits]
                    df = pd.DataFrame(flat_data)
                    df = df.rename(columns=nomes_amigaveis)

                    st.success(f"✅ Total de {len(df)} registros recuperados.")
                    st.dataframe(df.head(100))

                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar CSV Completo", csv, f"relatorio_{dt_inicio}.csv", "text/csv")
                else:
                    st.warning("Nenhum dado encontrado.")

            except Exception as e:
                st.error(f"Erro: {e}")

if __name__ == "__main__":
    main()