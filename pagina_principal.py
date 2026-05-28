import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# 1. Configuração da página
st.set_page_config(page_title="Central SISATEG", layout="wide")

# 2. Inicializa variáveis na sessão
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.session_state.senha = ""

# 3. Função de Validação Leve no Elastic (Ping)
def validar_login_elastic(usuario, senha):
    url_teste = "https://api-corp.cna.org.br/sisateg_pessoa/_search"
    query_leve = {"size": 0} # Pede zero registros, apenas para validar credencial
    
    try:
        response = requests.post(
            url_teste, 
            json=query_leve, 
            auth=HTTPBasicAuth(usuario, senha), 
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False

# 4. Tela de Login
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.title("Acesso ao Sistema 🔐")
        st.write("Insira suas credenciais corporativas para continuar.")
        
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário", placeholder="Ex: fernando.cruz")
            senha_input = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                with st.spinner("Validando credenciais..."):
                    if validar_login_elastic(usuario_input, senha_input):
                        st.session_state.logado = True
                        st.session_state.usuario = usuario_input
                        st.session_state.senha = senha_input
                        st.rerun() 
                    else:
                        st.error("❌ Usuário ou senha incorretos ou sem permissão.")

# 5. Tela Inicial (Boas-vindas pós-login)
def pagina_inicial():
    st.title("Central de Relatórios 🏢")
    st.markdown("---")
    st.write(f"Bem-vindo(a), **{st.session_state.usuario}**! Selecione o relatório desejado no menu lateral.")

# 6. Lógica de Roteamento
if not st.session_state.logado:
    pagina_auth = st.Page(tela_login, title="Login", icon="🔐")
    pg = st.navigation([pagina_auth])
else:
    with st.sidebar:
        # st.logo("https://i.ibb.co/ZzLmGh8X/Logo-Senar-Preferencial-RGB.png")
        st.write(f"👤 Logado como: `{st.session_state.usuario}`")
        if st.button("Sair", use_container_width=True):
            st.session_state.logado = False
            st.session_state.usuario = ""
            st.session_state.senha = ""
            st.rerun()
            
    home = st.Page(pagina_inicial, title="Início", icon="🏠", default=True)
    relatorio_1 = st.Page("rel_listar_visita.py", title="Relatório Listar Visitas", icon="📈")
    relatorio_2 = st.Page("sisateg_pessoa.py", title="Relatório Pessoas", icon="👥")
    
    pg = st.navigation(
        {
            "Navegação": [home],
            "Relatórios": [relatorio_1, relatorio_2]
        }
    )

pg.run()