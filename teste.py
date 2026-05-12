import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from datetime import date

st.set_page_config(page_title="Relatório SISATEG - SENAR", layout="wide")

def main():
    st.title("📊 Relatório de Visitas SISATEG (Elasticsearch)")

    with st.sidebar:
        st.header("🔑 Autenticação")
        user_input = st.text_input("Usuário")
        pass_input = st.text_input("Senha", type="password")
        st.divider()
        st.caption("Hostname: api-corp.cna.org.br")

    st.subheader("📅 Período da Consulta")
    col1, col2 = st.columns(2)
    with col1:
        dt_inicio = st.date_input("Data Inicial", value=date(2026, 1, 1))
    with col2:
        dt_fim = st.date_input("Data Final", value=date.today())
    
    if st.button("🔍 Consultar API SENAR"):
        if not user_input or not pass_input:
            st.error("Informe as credenciais na barra lateral.")
        else:
            with st.spinner("Consultando base de dados..."):
                try:
                    # Endpoint de busca do Elasticsearch para a tabela específica
                    # O padrão para busca no Elasticsearch é nome_do_indice/_search
                    endpoint = "https://api-corp.cna.org.br/sisateg_rel_listar_visita/_search"
                    
                    # Estrutura de consulta Elasticsearch (Query DSL) para filtro de período
                    query_json = {
                        "size": 10000,  # Define limite de registros (ajuste conforme necessário)
                        "query": {
                            "range": {
                                "dt_visita": {
                                    "gte": dt_inicio.strftime('%Y-%m-%d'),
                                    "lte": dt_fim.strftime('%Y-%m-%d'),
                                    "format": "yyyy-MM-dd"
                                }
                            }
                        }
                    }

                    response = requests.post(
                        endpoint, 
                        json=query_json,
                        auth=HTTPBasicAuth(user_input, pass_input),
                        timeout=60
                    )

                    if response.status_code == 200:
                        res_data = response.json()
                        # No Elasticsearch, os dados ficam em hits -> hits -> _source
                        hits = res_data.get('hits', {}).get('hits', [])
                        
                        if hits:
                            # Extrai apenas o conteúdo dos documentos (_source)
                            flat_data = [item['_source'] for item in hits]
                            df = pd.DataFrame(flat_data)
                            
                            st.success(f"Conectado! {len(df)} registros encontrados entre {dt_inicio} e {dt_fim}.")
                            
                            # Exibição dos dados
                            st.dataframe(df)

                            # Download CSV
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Baixar Relatório em CSV",
                                data=csv,
                                file_name=f"relatorio_visitas_{dt_inicio}_a_{dt_fim}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("Nenhum dado encontrado para o período selecionado.")
                    
                    elif response.status_code == 401:
                        st.error("Erro 401: Usuário ou Senha inválidos.")
                    else:
                        st.error(f"Erro {response.status_code}: {response.text}")

                except Exception as e:
                    st.error(f"Falha na conexão: {e}")

if __name__ == "__main__":
    main()