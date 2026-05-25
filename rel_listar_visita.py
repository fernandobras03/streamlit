import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import io
from datetime import date, timedelta
import time

# ──────────────────────────────────────────────
# Configuração da Página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Relatório listar visita",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização visual (Clean & Light)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #f8fafc; 
    }
    
    section[data-testid="stSidebar"] { 
        background-color: #f1f5f9; 
        border-right: 1px solid #e2e8f0; 
    }
    
    /* Inputs normais */
    .stTextInput input, .stDateInput input, .stSelectbox select {
        background-color: #ffffff !important; 
        border: 1px solid #cbd5e1 !important; 
        color: #1e293b !important; 
        border-radius: 6px;
    }
    
    /* Caixa principal do Multiselect */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px;
    }

    /* A Tag selecionada (A caixinha do "TODOS") */
    span[data-baseweb="tag"] {
        background-color: #e2e8f0 !important;
        color: #0f172a !important; 
        margin-left: 8px !important; 
        border-radius: 4px;
    }

    /* Botões */
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
    
    /* Expanders */
    [data-testid="stExpander"] { 
        background-color: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 8px; 
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Constantes & Base de Dados Oficial
# ──────────────────────────────────────────────
API_URL = "https://api-corp.cna.org.br/sisateg_rel_listar_visita/_search"

COLUNAS = {
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

# Listas extraídas dos CSVs (Usadas nos filtros de consulta inicial)
LISTA_ATIVIDADES = ["TODOS", "AGRICULTURA ANUAL", "AGRICULTURA ORGÂNICA", "AGROINDÚSTRIA DA CANA DE AÇÚCAR", "AGROINDÚSTRIA DE AZEITE DE OLIVA", "AGROINDÚSTRIA DE CERA", "AGROINDÚSTRIA DE DERIVADOS LÁCTEOS", "AGROINDÚSTRIA DE DERIVADOS VEGETAIS", "AGROINDÚSTRIA DE FARINHA E MANDIOCA", "AGROINDÚSTRIA DE OVOS", "AGROINDÚSTRIA DE PANIFICAÇÃO", "AGROINDÚSTRIA DE PESCADO", "AGROINDÚSTRIA DE POLPAS E BEBIDAS", "AGROINDÚSTRIA DE PRODUTOS APÍCOLA", "AGROINDÚSTRIA EMBUTIDO, DEFUMADOS E PROCESSAMENTO DE CARNES", "AGROINDÚSTRIA LÁCTEOS", "APICULTURA", "AVICULTURA", "BOVINOCULTURA DE CORTE", "BOVINOCULTURA DE LEITE", "CACAUICULTURA", "CAFEICULTURA", "CANA DE AÇÚCAR", "CARCINICULTURA", "EQUIDEOCULTURA", "FLORESTA", "FLORICULTURA", "FRUTICULTURA PERENE", "HEVEICULTURA", "MARICULTURA", "OLERICULTURA", "OVINOCAPRINOCULTURA DE CORTE", "OVINOCAPRINOCULTURA DE LEITE", "PIPERICULTURA", "PISCICULTURA", "RIZICULTURA", "SILVICULTURA", "SISALICULTURA", "SISTEMAS INTEGRADOS DE PRODUÇÃO", "SUINOCULTURA", "TURISMO RURAL"]
LISTA_PROJETOS = ["TODOS", "2 FOMENTO A ASSISTENCIA TECNICA E GERENCIAL", "ABC CERRADO", "AGRO CONECTA", "AGRO SENAR", "AGROINDÚSTRIA ANIMAL E VEGETAL", "AGROINDÚSTRIA INCENTIVO DF", "AGROMAIS ALAGOAS", "AGROMARANHÃO", "AGRONORDESTE ASSISTÊNCIA TÉCNICA E GERENCIAL", "AGRONORDESTE II", "AGRONORDESTE III", "AGRONORDESTE III - ALAGOAS", "AGRONORDESTE III - RIO GRANDE DO NORTE", "AGRONORDESTE SEBRAE", "AGRONORDESTE SEBRAE - FASE II", "AGROPEC ALAGOAS", "AGROPIAUI", "AMAZONAS MAIS PRODUTIVO", "ASSISTENCIA TECNICA E GERENCIAL REGIONAL SENAR- AM", "ASSISTÊNCIA TÉCNICA - RECIPROCIDADE", "ASSISTÊNCIA TÉCNICA 2019 -PB", "ASSISTÊNCIA TÉCNICA E GERENCIAL &#150; ATEG MANACAPURU", "ASSISTÊNCIA TÉCNICA E GERENCIAL - AM", "ASSISTÊNCIA TÉCNICA E GERENCIAL - SENAR BA", "ASSISTÊNCIA TÉCNICA E GERENCIAL PARA AGROINDÚSTRIA", "ASSISTÊNCIA TÉCNICA E GERENCIAL PARA PRODUTORES RURAIS DO RIO GRANDE DO SUL", "ATE-G AGROINDÚSTRIA", "ATEG +", "ATEG + AGRO", "ATEG - AGROTURISMO", "ATEG - HORTI", "ATEG - PRÓ-METRÓPOLE FASE 1", "ATEG - RONDÔNIA", "ATEG - SENAR/SEBRAE (02/2020)", "ATEG / SP / 2025", "ATEG / SP 1º SEMESTRE / 2023", "ATEG 2021 - PRÓPRIA", "ATEG 50", "ATEG AGRO +", "ATEG AGRO CAMPO", "ATEG AGROINDUSTRIA", "ATEG AGROINDUSTRIA RJ", "ATEG AGROINDÚSTRIA", "ATEG AGROINDÚSTRIA ARTESANAL RJ", "ATEG AGROINDÚSTRIA II", "ATEG AGROINDÚSTRIA VEGETAL", "ATEG APICULTURA", "ATEG APICULTURA RJ", "ATEG AVES E SUÍNOS", "ATEG AVICULTURA", "ATEG AVICULTURA PB", "ATEG AVICULTURA RJ", "ATEG AÇAÍ/PA", "ATEG BALDE CHEIO", "ATEG BOVINOCULTURA DE CORTE", "ATEG CACAU/PA", "ATEG CAFÉ RJ", "ATEG CAFÉ+FORTE", "ATEG CARCINICULTURA", "ATEG CEARÁ", "ATEG CITRUS", "ATEG CORTE RJ", "ATEG CRIA/PA", "ATEG EGRESSOS", "ATEG EM AGROINDÚSTRIA", "ATEG EM APICULTURA", "ATEG EM AÇÃO", "ATEG EM BOVINOCULTURA DE CORTE", "ATEG EM BOVINOCULTURA DE LEITE", "ATEG EM CANA DE AÇÚCAR", "ATEG EM FLORESTA PLANTADA", "ATEG EM GRÃOS", "ATEG EM HORTICULTURA", "ATEG EM OVINOCULTURA", "ATEG EM PISCICULTURA", "ATEG EXPANSÃO - RIO DE JANEIRO", "ATEG EXPANSÃO - SERGIPE", "ATEG FAMÍLIA RURAL", "ATEG FLORICULTURA", "ATEG FLORICULTURA RJ", "ATEG FRUTICULTURA", "ATEG FRUTICULTURA PB", "ATEG FRUTICULTURA RJ", "ATEG GRÃOS - PROJETO REGIONAL", "ATEG HORTICULTURA PA", "ATEG HORTICULTURA RJ", "ATEG LEITE FASE II – INCENTIVO", "ATEG LEITE PA", "ATEG LEITE PA &#150; BÚFALO", "ATEG LEITE PA - INCENTIVO", "ATEG LEITE PA FASE II", "ATEG LEITE PB", "ATEG LEITE RJ", "ATEG MADEIRA MAMORÉ", "ATEG MAIS CACAU &#150; FRUTICULTURA", "ATEG MAIS CACAU – INCENTIVO", "ATEG MAIS PECUÁRIA &#150; CORTE E LEITE", "ATEG MAIS RENDA", "ATEG MANDIOCULTURA", "ATEG MANDIOCULTURA – INCENTIVO", "ATEG MEL - INCENTIVO", "ATEG MEL II - INCENTIVO", "ATEG MEL PA", "ATEG MEL – INCENTIVO", "ATEG OLERICULTURA", "ATEG OVINOCAPRINOCULTURA DE CORTE", "ATEG OVINOCAPRINOCULTURA DE CORTE RJ", "ATEG OVINOCAPRINOCULTURA DE LEITE", "ATEG OVINOCAPRINOCULTURA DE LEITE RJ", "ATEG OVINOCULTURA - TOCANTINS", "ATEG PECUÁRIA DE CORTE - AC", "ATEG PECUÁRIA DE LEITE E FRUTICULTURA - PROGRAMA DE INCENTIVO SENAR RR", "ATEG PIAUÍ", "ATEG PISCICULTURA", "ATEG PISCICULTURA RJ", "ATEG PISCICULTURA – INCENTIVO", "ATEG PISCICULTURA/PA", "ATEG PREPARA", "ATEG PROCASE", "ATEG PROJETO DE INCENTIVO A BOVINOCULTURA", "ATEG REGIONAL ALAGOAS", "ATEG RO 3", "ATEG RO 3 - REGIONAL", "ATEG RO 4", "ATEG RO 4 - REGIONAL", "ATEG RO 5", "ATEG RO 6", "ATEG RO 6 - REGIONAL", "ATEG RO 7", "ATEG RO 8", "ATEG RO 9", "ATEG SENAR +", "ATEG SENAR - SEBRAE AC (REGIONAL)", "ATEG SENAR SC", "ATEG SENAR SEBRAE  24-26", "ATEG SENAR SERGIPE", "ATEG SENAR/RN", "ATEG SERGIPE", "ATEG SILVICULTURA", "ATEG SUCESSÃO FAMILIAR 2023", "ATEG SUL-MATA MG", "ATEG TOTAL", "ATEG TOTAL II", "ATEG-CORTE PA", "ATEG/SP 2° SEMESTRE/2024", "ATEG2023/PB", "ATER CAFÉ ES", "BALDE CHEIO", "CAFEICULTURA E OLERICULTURA DF 2024", "CAFÉ+FORTE", "CAJUÍNA AGROINDÚSTRIA", "CAMPO INOVADOR", "CAMPO NA CLASSE MÉDIA", "CAMPO PRODUTIVO", "CAPRICORTE BA", "CICLO PÓS ATEG", "COM LEITE: GESTÃO E PRODUTIVIDADE", "CONTRATO SEBRAE", "CONVÊNIO BNB FUNDECI 2021.0004", "CONVÊNIO NESTLE", "DO RURAL A MESA", "EDUCAÇÃO, INOVAÇÃO E ATEG DO DISTRITO FEDERAL.", "EGRESSOS APICULTURA", "EMPREENDER RURAL AMAZONAS (SEBRAE)", "EVOLUI LEITE", "EXPANSÃO ATEG - PERNAMBUCO", "EXPANSÃO ATEG - TOCANTINS 1", "EXPANSÃO ATEG PARANÁ", "FAZENDA EXPERIMENTAL DA UFBA", "FAZENDA PANTANEIRA SUSTENTÁVEL - FPS", "FIP PAISAGENS RURAIS", "FOMENTO À ASSISTÊNCIA TÉCNICA E GERENCIAL", "FORNECEDORES DIVERSOS", "FORTALECENDO O AGRO", "FORTALECIMENTO DA AGRICULTURA FAMILIAR NO AMAZONAS", "FORTALECIMENTO DA CADEIA PRODUTIVA DO SISAL", "FORTALECIMENTO DA GESTÃO NA PROPRIEDADE", "FORTALECIMENTO DA OVINOCULTURA", "FRUTITEC", "FUNDECI BNB FRUTICULTURA DO COCO", "GERALEITE", "HORTIFRUTI DF", "INCENTIVO AL/23 - ALAGOAS", "INCENTIVO ATEG SC", "INCENTIVO CACAU 2", "INCENTIVO PARANÁ - BOVINOCULTURA DE LEITE E OLERICULTURA", "INCENTIVO TRANSFORMAÇÃO ATEG", "INOVA CEARÁ - SENAR/SEBRAE", "JORNADA ATEG", "MAIS ATEG", "MAIS LEITE SAUDÁVEL", "MAIS LEITE SAUDÁVEL - JATICÍNIO JOIA", "MAIS PRODUÇÃO", "MANDIOCULTURA", "MAPA LEITE", "MUNICÍPIO PARCEIRO", "MÉDIO PRODUTOR - PECUÁRIA DE CORTE", "MÉDIO PRODUTOR DF - INCENTIVO", "NCR CICLO 2", "O SENAR COM VOCÊ", "O SENAR EM CAMPO", "OVINOCAP PLANALTO CENTRAL", "PARCERIA SENAR-SEBRAE 2025/2026", "PB AGRO +", "PLANALTO CENTRAL 01", "PLANALTO CENTRAL 02", "PLANEJAMENTO E SUSTENTABILIDADES DO ESTADO DO AMAZONAS &#150;&#150; AM 2022.", "PRO SENAR", "PRODUZIR +", "PRODUZIR NO CAMPO", "PROGRAMA  AGROCONECTA", "PROGRAMA ATEG - CADEIA PRODUTIVA BOVINOCULTURA DE LEITE (BA)", "PROGRAMA ATEG - CADEIA PRODUTIVA CACAU (BA)", "PROGRAMA DE EXPANSÃO PIAUÍ", "PROGRAMA DE INCENTIVO", "PROGRAMA REGIONAL", "PROGRAMA SENAR + PRÓXIMO", "PROJ. AGROINDÚSTRIA", "PROJETO + AGRO", "PROJETO AGROINDÚSTRIA INCENTIVO DF", "PROJETO AQUICULTURA BRASIL", "PROJETO ATEG AVICULTURA - PROGRAMA REGIONAL", "PROJETO ATEG BOVINOCULTURA DE CORTE - PROGRAMA REGIONAL", "PROJETO ATEG CADEIA PRODUTIVA 2025", "PROJETO ATEG CADEIA PRODUTIVA APICULTURA", "PROJETO ATEG CADEIA PRODUTIVA DA OLERICULTURA", "PROJETO ATEG CADEIA PRODUTIVA DE BOVINOCULTURA DE LEITE", "PROJETO ATEG CADEIA PRODUTIVA FRUTICULTURA", "PROJETO ATEG FRUTICULTURA - PROGRAMA REGIONAL", "PROJETO ATEG MAIS CACAU II - PROGRAMA DE INCENTIVO", "PROJETO ATEG REGIONAL II", "PROJETO ATEG SENAR MINAS", "PROJETO BNB", "PROJETO CRESCER NO CAMPO - AP", "PROJETO CRESCER NO CAMPO III", "PROJETO DE ATEG DO SENAR EM MANDIOCULTURA- AC", "PROJETO DE DESENVOLVIMENTO TERRITORIAL - BNB", "PROJETO DIAGNÓSTICO", "PROJETO FRUTICULTURA VALE DO SÃO FRANCISCO", "PROJETO INCENTIVO EXPANSÃO ATEG - MINAS GERAIS", "PROJETO INCENTIVO PARANÁ - BOVINOCULTURA DE LEITE E OLERICULTURA", "PROJETO INCLUSÃO PRODUTIVA", "PROJETO INTEGRA CAMPO ALAGOAS", "PROJETO LEITE AGRESTE", "PROJETO PILOTO PARANÁ", "PROJETO PISCICULTURA ACRE - REGIONAL", "PROJETO PROSPERA AGROPECUÁRIA SEMIÁRIDO - MINAS GERAIS", "PROJETO REGIONAL", "PROJETO REGIONAL_JUNTOS PELO AGRO", "PROJETO RENOVAÇÃO 360º", "PROJETO RETORNO CERTO FASE II", "PROJETO SENAR CENTRAL 2023", "PROJETO SENAR ES (GERAL)", "PROJETO SENAR ES TOTAL", "PROJETO SENAR MAIS PRODUÇÃO - SENAR AC", "PROJETO TECNOLOGIA SUSTENTAVEL CADEIA PRODUTIVA DO LEITE", "PROJETOS DE ASSISTÊNCIA TÉCNICA E GERENCIAL DO SENAR DO MARANHÃO.", "PROSPERA PIAUÍ", "PRÓPRIO SENAR-RO", "PÓS ATEG - CAFÉ", "PÓS ATEG - CORTE", "PÓS ATEG - DERIVADOS LÁCTEOS", "PÓS ATEG - FRUTICULTURA", "PÓS ATEG - LEITE", "RETOMADA ECONÔMICA", "RETORNO CERTO - INCENTIVO ATEG (SENAR MA)", "SEBRAETEC", "SEMIÁRIDO CAPAZ", "SENAR + AGRO", "SENAR ASSISTE", "SENAR CENTRAL 2024", "SENAR EM CAMPO", "SENAR EM CAMPO 2", "SENAR ES CACAU", "SENAR MAIS", "SENAR MAIS - PARCERIAS", "SENAR MAIS -ES", "SENAR MAIS INCENTIVO", "SENAR MAIS INCENTIVO II", "SENAR MAIS INCENTIVO III", "SENAR MAIS/CMOC", "SENAR NACIONAL 2025", "SENAR NACIONAL 2026", "SENAR NO CAMPO", "SENAR NO JALAPÃO", "SENAR TEC LEITE - ETAPA 1", "SENAR-ES", "SENAR/SEBRAE 2023", "SENAR/SEBRAE 2024", "SENARTEC", "SERTÃO EMPREENDEDOR", "SUPERAÇÃO BRUMADINHO", "SUSTENTABILIDADE NO CAMPO", "TERRAS SUSTENTÁVEIS", "TRAVESSIA LEITE", "TREINAMENTO SP"]
LISTA_STATUS = ["TODOS", "ATIVA", "INATIVA"]

# ──────────────────────────────────────────────
# Extração Direto na Fonte (Otimizado via ElasticSearch Filter)
# ──────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def buscar_dados_otimizados(_usuario, _senha, dt_inicio, dt_fim, projeto_sel, atividade_sel, status_sel):
    all_hits = []
    search_after = None
    
    # PAGE_SIZE reduzido para evitar travamento na deserialização
    PAGE_SIZE_OTIMIZADO = 2000 
    
    filtros_elastic = [
        {"range": {"dt_visita": {"gte": dt_inicio, "lte": dt_fim, "format": "yyyy-MM-dd"}}}
    ]

    # Só injeta no Elastic se o usuário optou por pré-filtrar antes da carga
    if projeto_sel and "TODOS" not in projeto_sel:
        filtros_elastic.append({"bool": {"should": [{"match_phrase": {"projeto": p}} for p in projeto_sel], "minimum_should_match": 1}})
    if atividade_sel and "TODOS" not in atividade_sel:
        filtros_elastic.append({"bool": {"should": [{"match_phrase": {"atividade": a}} for a in atividade_sel], "minimum_should_match": 1}})
    if status_sel and "TODOS" not in status_sel:
        filtros_elastic.append({"bool": {"should": [{"match_phrase": {"status_propriedade": s}} for s in status_sel], "minimum_should_match": 1}})

    query_base = {
        "size": PAGE_SIZE_OTIMIZADO,
        "_source": list(COLUNAS.keys()),
        "query": {"bool": {"filter": filtros_elastic}},
        "sort": [{"dt_visita": "asc"}, {"id_visita": "asc"}]
    }

    session = requests.Session()
    session.auth = HTTPBasicAuth(_usuario, _senha)

    progress_bar = st.progress(0, text="Iniciando extração na API...")
    registros_extraidos = 0

    while True:
        if search_after:
            query_base["search_after"] = search_after

        response = session.post(API_URL, json=query_base, timeout=120)

        if response.status_code == 401:
            st.error("❌ Falha de Autenticação. Verifique seu utilizador e senha.")
            return pd.DataFrame()
        if response.status_code != 200:
            st.error(f"❌ Erro na API ({response.status_code}): {response.text}")
            return pd.DataFrame()

        hits = response.json().get("hits", {}).get("hits", [])
        if not hits:
            break

        all_hits.extend([item["_source"] for item in hits])
        search_after = hits[-1].get("sort")
        registros_extraidos += len(hits)
        
        progress_bar.progress(min(registros_extraidos / 500000, 1.0), text=f"⏳ Extraindo... Total obtido: {registros_extraidos:,}")

        if len(hits) < PAGE_SIZE_OTIMIZADO:
            break
            
    progress_bar.empty()
    session.close()

    if not all_hits:
        return pd.DataFrame()

    df = pd.DataFrame(all_hits)
    df = df.rename(columns=COLUNAS)
    
    valores_nulos = ["NAN", "NONE", "", "NULL", "<NA>"]
    
    def limpar_coluna(serie, valor_padrao):
        serie = serie.replace(valores_nulos, pd.NA)
        return serie.fillna(valor_padrao).astype(str).str.strip().str.upper()

    if "Projeto" in df.columns:
        df["Projeto"] = limpar_coluna(df["Projeto"], "NÃO INFORMADO")
        
    if "Status da Propriedade" in df.columns:
        df["Status da Propriedade"] = limpar_coluna(df["Status da Propriedade"], "NI")
        
    if "Atividade" in df.columns:
        df["Atividade"] = limpar_coluna(df["Atividade"], "NÃO INFORMADO")

    return df

# ──────────────────────────────────────────────
# Interface e Funcionalidade
# ──────────────────────────────────────────────
def main():
    with st.sidebar:
        st.image("https://i.ibb.co/ZzLmGh8X/Logo-Senar-Preferencial-RGB.png", width=150)
        st.subheader("🔐 Autenticação")
        usuario = st.text_input("Utilizador", placeholder="Ex: fernando.cruz")
        senha = st.text_input("Senha", type="password")
        st.divider()
        st.caption("Acesso à base `sisateg_rel_listar_visita`.")

    st.title("Relatório de visitas")
    st.markdown("Busque os dados do período na API. Depois de carregados, utilize a seção abaixo para filtrar os resultados instantaneamente.")
    st.markdown("---")

    # 1. Filtros de Data (Servidor)
    st.subheader("🗓️ Filtros de Carga (Servidor)")
    col1, col2 = st.columns(2)
    with col1:
        dt_inicio = st.date_input("Data Inicial", value=None, format="DD/MM/YYYY")
    with col2:
        dt_fim = st.date_input("Data Final", value=None, format="DD/MM/YYYY")

    # Filtros Opcionais (Servidor)
    with st.expander("🎯 Filtros Prévios Específicos (Opcional)", expanded=False):
        st.caption("Filtre antes da carga caso queira trazer APENAS um projeto/atividade específico da API, economizando memória.")
        f1, f2, f3 = st.columns(3)
        with f1:
            projeto_input = st.multiselect("Projeto Prévio:", options=LISTA_PROJETOS, default=["TODOS"])
        with f2:
            atividade_input = st.multiselect("Atividade Prévia:", options=LISTA_ATIVIDADES, default=["TODOS"])
        with f3:
            status_input = st.multiselect("Status Prévio:", options=LISTA_STATUS, default=["TODOS"])

    if st.button("🚀 Iniciar Extração da Base", use_container_width=True):
        
        # ─── VALIDAÇÕES DE SEGURANÇA E PERFORMANCE ───
        if not usuario or not senha:
            st.warning("⚠️ Forneça suas credenciais na barra lateral.")
            st.stop()
        if dt_inicio is None or dt_fim is None:
            st.error("⚠️ As datas Inicial e Final são obrigatórias para não sobrecarregar o servidor.")
            st.stop()
            
        # Validação: Data invertida
        if dt_fim < dt_inicio:
            st.error("⚠️ A **Data Final** não pode ser anterior à **Data Inicial**.")
            st.stop()
            
        # Validação: Limite de 6 meses (183 dias para margem segura)
        dias_selecionados = (dt_fim - dt_inicio).days
        if dias_selecionados > 183:
            st.error(f"⚠️ **Período muito longo!** Você selecionou {dias_selecionados} dias. Para garantir a estabilidade e performance do sistema, o limite máximo de extração por vez é de **6 meses (183 dias)**. Por favor, ajuste as datas.")
            st.stop()
        # ─────────────────────────────────────────────

        try:
            str_inicio = dt_inicio.strftime('%Y-%m-%d')
            str_fim = dt_fim.strftime('%Y-%m-%d')
            
            with st.spinner("Verificando dados em cache ou extraindo da API..."):
                
                # Inicia o cronômetro
                inicio_timer = time.time()
                
                df_result = buscar_dados_otimizados(
                    usuario, senha, str_inicio, str_fim, 
                    projeto_input, atividade_input, status_input
                )
                
                # Para o cronômetro
                fim_timer = time.time()
                tempo_gasto = fim_timer - inicio_timer
            
            st.session_state['df_visitas_otim'] = df_result
            
            if not df_result.empty:
                st.success(f"✅ **Carga concluída em {tempo_gasto:.2f} segundos!** O servidor entregou a base solicitada.")
            else:
                st.warning(f"⚠️ Nenhum registro encontrado para essa combinação (Busca finalizada em {tempo_gasto:.2f} segundos).")
                
        except Exception as e:
            st.error(f"❌ Erro operacional: {e}")

    # ──────────────────────────────────────────────
    # Fluxo pós-carregamento (Filtros Locais Instantâneos)
    # ──────────────────────────────────────────────
    if 'df_visitas_otim' in st.session_state and not st.session_state['df_visitas_otim'].empty:
        df_base = st.session_state['df_visitas_otim']
        
        st.markdown("---")
        st.subheader("🔍 Filtros Locais (Resultados Instantâneos)")
        st.caption("Filtre os dados já extraídos da API. A contagem e a tabela atualizarão imediatamente.")

        # Cria 3 colunas para os filtros locais
        loc1, loc2, loc3 = st.columns(3)
        
        # Usamos .unique() para mostrar apenas opções que realmente vieram na base extraída
        with loc1:
            lista_proj_local = sorted(df_base["Projeto"].dropna().unique().tolist())
            proj_local = st.multiselect("Filtrar Projeto na Tela:", options=lista_proj_local, default=lista_proj_local)
            
        with loc2:
            lista_ativ_local = sorted(df_base["Atividade"].dropna().unique().tolist())
            ativ_local = st.multiselect("Filtrar Atividade na Tela:", options=lista_ativ_local, default=lista_ativ_local)
            
        with loc3:
            lista_status_local = sorted(df_base["Status da Propriedade"].dropna().unique().tolist())
            status_local = st.multiselect("Filtrar Status na Tela:", options=lista_status_local, default=lista_status_local)

        # Aplica a máscara de filtragem do Pandas
        mask = (
            df_base["Projeto"].isin(proj_local) &
            df_base["Atividade"].isin(ativ_local) &
            df_base["Status da Propriedade"].isin(status_local)
        )
        df_filtrado = df_base[mask]

        # Exibe a Contabilização exata dinamicamente
        st.markdown("### 📊 Resumo da Seleção")
        st.metric(label="Registros Encontrados (Filtrados)", value=f"{len(df_filtrado):,}".replace(",", "."))
        
        if not df_filtrado.empty:
            st.markdown(f"**Visualização Amostral** (Exibindo até 100 de {len(df_filtrado):,} registros visíveis)")
            st.dataframe(df_filtrado.head(100), use_container_width=True, height=350)

            # Prepara o CSV apenas com os dados que estão visíveis na tela
            buffer = io.BytesIO()
            df_filtrado.to_csv(buffer, index=False, encoding="utf-8-sig")
            buffer.seek(0)

            st.download_button(
                label=f"📥 Baixar Relatório Filtrado em CSV ({len(df_filtrado):,} linhas)",
                data=buffer,
                file_name=f"relatorio_visitas_filtrado.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Nenhum registro corresponde aos filtros locais selecionados.")

if __name__ == "__main__":
    main()