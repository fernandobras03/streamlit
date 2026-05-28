import streamlit as st

# 1. Configuração da página (deve ser o primeiro comando Streamlit)
st.set_page_config(page_title="Central de Relatórios", layout="wide")

#st.logo("https://i.ibb.co/ZzLmGh8X/Logo-Senar-Preferencial-RGB.png")

# 3. Criar uma função para a página inicial
def pagina_inicial():
    st.title("Central de Relatórios 🏢")
    st.markdown("---")
    st.write("Bem-vindo! Selecione o relatório desejado no menu lateral esquerdo para iniciar suas extrações.")
    
    # Se quiser, pode adicionar dicas de uso ou avisos gerais aqui no futuro
    st.info("💡 Dica: Utilize a barra lateral para navegar entre os módulos do SISATEG.")

# 4. Definir as páginas
# Transformamos a função em uma página e marcamos como default (a primeira que abre)
home = st.Page(pagina_inicial, title="Início", icon="🏠", default=True)
relatorio_1 = st.Page("rel_listar_visita.py", title="Listar Visitas", icon="📈")
relatorio_2 = st.Page("sisateg_pessoa.py", title="Base de Pessoas", icon="👥")

# 5. Criar o menu de navegação agrupado
# Usar um dicionário cria seções (labels) no menu lateral, deixando o UI mais limpo
pg = st.navigation(
    {
        "Navegação": [home],
        "Relatórios Disponíveis": [relatorio_1, relatorio_2]
    }
)

# 6. Executar a aplicação
pg.run()