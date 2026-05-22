import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanças", page_icon="💰", layout="wide")

st.markdown("""
#Boas vindas!
## Nosso APP financeiro!
Espero que você curta a experiência da nossa solução para organização financeira.            
""")

#Widget de upload de arquivo
file_upload = st.file_uploader(label="Faça o upload do seu arquivo CSV", type=["csv"])

#Verifica se algum arquivo foi carregado
if file_upload:
    
    #lê os dados
    df = pd.read_csv(file_upload)
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y").dt.date

    #Exibição dos dados no app
    exp1 = st.expander("Dados Brutos")
    columns_fmt = {"Valor":st.column_config.NumberColumn("Valor", format="R$ %f")}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    #Visão instituição
    exp2 = st.expander("Instituições")
    df_instituicao = df.pivot_table(index="Data", columns="Instituição", values="Valor")

    #Abas para diferentes visualizações
    tab_data, tab_history, tab_share = exp2.tabs(["Dados", "Histórico", "Participação"])

    #Exibe Dataframe
    tab_data.dataframe(df_instituicao)

    #Exibe Histórico
    with tab_history:
        st.line_chart(df_instituicao)

    #Exibe distribuicao
    with tab_share:
        
        #Filtro de data
        date = st.selectbox("Filtro Data", options=df_instituicao.index)

        #Gráfico de distribuição
        st.bar_chart(df_instituicao.loc[date])

    df_data = df.groupby(by="Data")[["Valor"]].sum()
    df_data["lag_1"] = df_data["Valor"].shift(1)
    df_data["Diferença Mensal"] = df_data["Valor"] - df_data["lag_1"]

    st.dataframe(df_data)