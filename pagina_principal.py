import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# 1. Configuração da página (DEVE SER O PRIMEIRO COMANDO)
st.set_page_config(page_title="Relatórios DATEG", layout="wide", initial_sidebar_state="collapsed")

# 2. Inicializa variáveis na sessão
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.session_state.senha = ""

# 3. Função de Validação Leve no Elastic (Ping)
def validar_login_elastic(usuario, senha):
    url_teste = "https://api-corp.cna.org.br/sisateg_pessoa/_search"
    query_leve = {"size": 0} 
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

# 4. Tela de Login Redesenhada
def tela_login():
    # Injetando CSS customizado para transformar a interface
    st.markdown("""
    <style>
        /* Esconde o menu lateral, o cabeçalho padrão e o botão de expandir na tela de login */
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stHeader"] { display: none; }
        
        /* Ajusta o fundo da página inteira */
        .stApp {
            background-color: #ffffff;
        }
        
        /* Remove o recuo superior para o cabeçalho colar no topo */
        .block-container {
            padding-top: 2rem !important;
            max-width: 100% !important;
        }

        /* Estilização da caixa do formulário principal */
        div[data-testid="stForm"] {
            border: 1px solid #006C4C !important;
            border-radius: 5px;
            padding: 25px;
            background-color: #ffffff;
        }
        
        /* Ajuste nas caixas de texto (inputs) */
        .stTextInput input {
            border: 1px solid #cccccc !important;
            border-radius: 4px;
        }
        .stTextInput input:focus {
            border-color: #006C4C !important;
            box-shadow: 0 0 0 1px #006C4C !important;
        }

        /* Botão Enviar (Verde Claro) */
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #62B55A !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 500;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #4f9448 !important;
        }
        
        /* Textos estáticos (links falsos e ajuda) */
        .login-links {
            color: #888888;
            font-size: 13px;
            margin-bottom: 5px;
        }
        .login-help {
            color: #666666;
            font-size: 13px;
            line-height: 1.4;
            margin-top: 10px;
        }
        .login-help ul {
            padding-left: 20px;
            margin-bottom: 0;
        }
        
        # /* Linhas pontilhadas (Verde Claro) */
        # .dotted-line {
        #     border-top: 2px dotted #62B55A;
        #     margin: 15px 0;
        }
        
        /* Rodapé fixo escuro */
        .login-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #00281c; /* Tom super escuro da cor principal */
            color: #ffffff;
            text-align: center;
            padding: 12px 0;
            font-size: 12px;
            font-weight: 500;
            z-index: 99999;
        }
    </style>
    """, unsafe_allow_html=True)

    # CABEÇALHO: Logo à esquerda, Título centralizado
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0 40px;">
        <img src="https://i.ibb.co/KkCpC3K/Logo-Senar-ATe-G-Assistencia-Tecnica-e-Gerencial-Preferencial.png" width="220">
        <h1 style="color: #006C4C; margin: 0; position: absolute; left: 50%; transform: translateX(-50%); font-size: 26px; letter-spacing: 1px;">RELATÓRIOS DATEG</h1>
    </div>
    <br><br><br>
    """, unsafe_allow_html=True)

    # CAIXA DE LOGIN: Centralizada com larguras controladas
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.form("form_login"):
            # Linha Superior
            #st.markdown("<div class='login-links'>Primeiro acesso | Esqueci minha senha | Alterar senha</div>", unsafe_allow_html=True)
            st.markdown("<div class='dotted-line'></div>", unsafe_allow_html=True)
            
            # Campos de Login (Ocultamos a label padrão e usamos emojis no placeholder)
            usuario_input = st.text_input("Usuário", placeholder="👤 Informe o usuário...", label_visibility="collapsed")
            senha_input = st.text_input("Senha", placeholder="🔒 Informe a senha...", type="password", label_visibility="collapsed")
            
            # Alinhando o botão à direita usando colunas invisíveis
            c_vazio, c_btn = st.columns([3, 1])
            with c_btn:
                submit = st.form_submit_button("Enviar", use_container_width=True)
            
            # Linha Inferior
            st.markdown("<div class='dotted-line'></div>", unsafe_allow_html=True)
            
            # Lista de Informações
            # st.markdown("""
            # <div class='login-help'>
            #     <ul>
            #         <li>Como acessar os sistemas disponíveis?</li>
            #         <li>Quem tem acesso?</li>
            #         <li>Como conseguir o acesso aos sistemas?</li>
            #         <li>Como entrar em contato?</li>
            #         <li>Como alterar sua senha?</li>
            #     </ul>
            # </div>
            # """, unsafe_allow_html=True)
            
            # Lógica de validação do botão
            if submit:
                with st.spinner("Validando acesso..."):
                    if validar_login_elastic(usuario_input, senha_input):
                        st.session_state.logado = True
                        st.session_state.usuario = usuario_input
                        st.session_state.senha = senha_input
                        st.rerun() 
                    else:
                        st.error("❌ Usuário ou senha incorretos.")

    # RODAPÉ
    st.markdown("""
    <div class='login-footer'>
        DATEG 2026 - Todos os direitos reservados - Suporte/Informações: 1633 - 1325 - 1323
    </div>
    """, unsafe_allow_html=True)

# 5. Tela Inicial (Pós-login)
def pagina_inicial():
    # Retorna o menu lateral para quem estiver logado
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: block !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("Central de Relatórios 🏢")
    st.markdown("---")
    st.write(f"Bem-vindo(a), **{st.session_state.usuario}**! Selecione o relatório desejado no menu lateral à esquerda para iniciar suas extrações.")

# 6. Roteamento Inteligente
if not st.session_state.logado:
    pagina_auth = st.Page(tela_login, title="Login", icon="🔐")
    pg = st.navigation([pagina_auth])
else:
    with st.sidebar:
        # st.logo("https://i.ibb.co/KkCpC3K/Logo-Senar-ATe-G-Assistencia-Tecnica-e-Gerencial-Preferencial.png")
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
            "Relatórios Disponíveis": [relatorio_1, relatorio_2]
        }
    )

pg.run()