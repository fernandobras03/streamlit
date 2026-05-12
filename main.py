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
    exp2.dataframe(df_instituicao)
    exp2.line_chart(df_instituicao)

    #obtem a última data de dados
    last_dt = df_instituicao.sort_index().iloc[-1]
    exp2.bar_chart(last_dt)
