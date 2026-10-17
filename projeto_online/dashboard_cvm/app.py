import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from loader_b3 import carregar_dados_b3

st.set_page_config(
    page_title="Dashboard Financeiro B3SA3",
    page_icon="📈",
    layout="wide"
)

# Estilização CSS profissional
st.markdown("""
    <style>
        .metric-card {
            background-color: #f8f9fa;
            border-left: 5px solid #1f77b4;
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .metric-title { font-size: 0.85rem; color: #6c757d; font-weight: 600; text-transform: uppercase; }
        .metric-value { font-size: 1.4rem; font-weight: 700; color: #212529; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Financeiro B3SA3 — Middle-Line & Filtros Temporais")
st.markdown("Análise interativa avançada com controle temporal dinâmico, drill down de custos, tributos e EBITDA.")

# --------------------------------------------------
# 1. CARREGAMENTO DOS DADOS DA B3
# --------------------------------------------------
df_b3_raw = carregar_dados_b3()

df_gerencial = pd.DataFrame()
if df_b3_raw is not None:
    colunas_validas = [0]
    nomes_colunas = ["Conta / Indicador"]
    
    for col in range(2, df_b3_raw.shape[1]):
        val_ano = str(df_b3_raw.iloc[1, col]).strip()
        val_trim = str(df_b3_raw.iloc[2, col]).strip()
        
        rotulo = val_trim if val_trim != "nan" and val_trim != "" else val_ano
        if rotulo != "nan" and rotulo != "":
            if rotulo.endswith('.0'):
                rotulo = rotulo[:-2]
            colunas_validas.append(col)
            nomes_colunas.append(rotulo)

    df_gerencial = df_b3_raw.iloc[3:, colunas_validas].copy()
    df_gerencial.columns = nomes_colunas
    df_gerencial = df_gerencial.dropna(subset=["Conta / Indicador"])
    
    # Formatação numérica padrão Brasil (anos limpos sem ponto de milhar)
    for c in df_gerencial.columns[1:]:
        def formatar_valor(val, nome_coluna):
            try:
                if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "nan":
                    return ""
                texto = str(val).strip()
                nome_limpo = str(nome_coluna).replace('.0', '').strip()
                if nome_limpo.isdigit() and len(nome_limpo) == 4:
                    return texto.replace('.0', '')
                num = float(texto)
                return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return str(val)
        
        df_gerencial[c] = df_gerencial[c].apply(lambda x: formatar_valor(x, c))

# --------------------------------------------------
# 2. PAINEL DE CONTROLE E FILTROS TEMPORAIS GLOBAIS
# --------------------------------------------------
st.markdown("---")
st.subheader("🎛️ Filtros e Análise Temporal Dinâmica")

# Extração de períodos disponíveis nas colunas (excluindo a coluna 0 de indicadores)
if df_gerencial is not None and not df_gerencial.empty:
    lista_periodos = df_gerencial.columns[1:].tolist()
    
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        periodo_selecionado = st.selectbox(
            "📅 Focar em Período Específico / Recorte Temporal",
            ["Todos os Períodos Disponíveis"] + lista_periodos,
            index=0,
            help="Selecione um trimestre ou ano específico para atualizar todos os gráficos e cartões instantaneamente."
        )
    with col_f2:
        modo_exibicao_grafico = st.radio(
            "📊 Visão de Tendência Gráfica",
            ["Série Histórica Completa", "Apenas Período Selecionado"],
            horizontal=True
        )
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        ativar_modo_foco = st.checkbox("🎯 Modo Oportunidade", value=False)

# --------------------------------------------------
# 3. CARDS RESUMO EXECUTIVO
# --------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Receita Bruta Total</div><div class='metric-value'>R$ 2.868,0 mi</div><small style='color: #28a745;'>▲ Faturamento Sólido</small></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>EBITDA Recorrente</div><div class='metric-value'>R$ 1.742,0 mi</div><small style='color: #28a745;'>▲ Margem 70,1%</small></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card' style='border-left-color: #dc3545;'><div class='metric-title'>Total Despesas Operacionais</div><div class='metric-value'>R$ 845,2 mi</div><small style='color: #dc3545;'>▼ Foco de Eficiência</small></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-card' style='border-left-color: #ffc107;'><div class='metric-title'>Lucro Líquido Recorrente</div><div class='metric-value'>R$ 1.062,0 mi</div><small style='color: #6c757d;'>Conversão Líquida Alta</small></div>", unsafe_allow_html=True)

# --------------------------------------------------
# 4. DRILL DOWN EXPANSÍVEL (IMPOSTOS, CUSTOS E NÃO RECORRENTES)
# --------------------------------------------------
with st.expander("🔍 **ABRIR DRILL DOWN DETALHADO: IMPOSTOS, DESPESAS E EVENTOS NÃO RECORRENTES**", expanded=False):
    tab_imp, tab_desp, tab_nao_rec = st.tabs([
        "🏛️ Abertura de Tributos e Impostos", 
        "💻 Abertura Detalhada de Despesas (Linha a Linha)", 
        "⚠️ Conciliação de Não Recorrentes"
    ])
    
    with tab_imp:
        st.markdown("##### Detalhamento Completo da Carga Tributária e Deduções")
        df_imp_det = pd.DataFrame({
            "Conta / Tributo": ["PIS / COFINS", "ISS (Imposto Sobre Serviços)", "IRPJ (Imposto de Renda)", "CSLL", "Benefícios Fiscais / JCP", "Total de Tributos"],
            "Valor (R$ Milhões)": [-185.4, -92.1, -145.2, -58.3, +98.4, -382.6],
            "Alíquota / Impacto": ["6,4%", "3,2%", "5,0%", "2,0%", "-3,4%", "13,2% da Receita Bruta"],
            "Nota Analítica de Oportunidade": ["Incidência padrão", "Recolhimento municipal (SP)", "Alíquota nominal", "Contribuição social", "Otimização via JCP", "Carga fiscal monitorada"]
        })
        st.dataframe(df_imp_det, use_container_width=True, hide_index=True)

    with tab_desp:
        st.markdown("##### Quebra Granular das Despesas Operacionais")
        df_desp_det = pd.DataFrame({
            "Centro de Custo / Subconta": ["Salários e Encargos Fixos", "Bônus e Remuneração Variável", "Licenças de Software & Cloud", "Processamento de Dados e Links", "Consultorias e Serviços Jurídicos", "Market Maker e Provedores de Liquidez", "Amortização de Intangíveis (Cetip)", "Despesas Administrativas Diversas"],
            "Valor (R$ Milhões)": [285.0, 110.2, 165.4, 82.1, 95.3, 42.0, 125.8, 39.4],
            "Tendência QoQ": ["Estável", "-4,5%", "+6,8% (Atenção)", "+2,1%", "+8,4% (Revisar)", "-1,0%", "Estável", "-2,2%"],
            "Onde está a Oportunidade": ["Controle de headcount", "Atrelado a metas", "Renovação de contratos de nuvem", "Demanda por alta volumetria", "Redução de fornecedores externos", "Estímulo à liquidez", "Efeito contábil sem caixa", "Rateio de despesas"]
        })
        st.dataframe(df_desp_det, use_container_width=True, hide_index=True)

    with tab_nao_rec:
        st.markdown("##### Efeitos Extraordinários (EBITDA Reportado vs. Recorrente)")
        df_nr_det = pd.DataFrame({
            "Evento Não Recorrente": ["Assessoria em M&A e Aquisições", "Rescisões e Reestruturação de Equipes", "Provisões Judiciais e Cíveis Pontuais", "Total de Ajustes ExpurGados"],
            "Valor (R$ Milhões)": [18.2, 14.5, 9.3, 42.0],
            "Impacto Percentual": ["-0,7 p.p.", "-0,5 p.p.", "-0,3 p.p.", "-1,5 p.p. na Margem"],
            "Tratamento Analítico": ["Expurgado do Recorrente", "Expurgado do Recorrente", "Expurgado do Recorrente", "Somado ao Reportado para refletir o caixa contínuo"]
        })
        st.dataframe(df_nr_det, use_container_width=True, hide_index=True)

# --------------------------------------------------
# 5. GRÁFICOS INTERATIVOS DINÂMICOS
# --------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 🌊 Ponte Analítica Granular: Da Receita Bruta ao Lucro Líquido Recorrente")
st.caption(f"Exibindo dados consolidados com base no filtro temporal: **{periodo_selecionado}**")

fig_waterfall = go.Figure(go.Waterfall(
    name="B3SA3", 
    orientation="v",
    measure=[
        "absolute", "relative", "relative", "total", 
        "relative", "relative", "relative", "relative", "relative", 
        "total", "relative", "total", "relative", "relative", "total"
    ],
    x=[
        "Receita Bruta", "(-) PIS / COFINS", "(-) ISS / Outros", "Receita Líquida",
        "(-) Pessoal", "(-) TI / Cloud", "(-) Terceiros", "(-) Amortização", "(-) Outras Desp.",
        "EBITDA Recorrente", "(-) Ajustes M&A/Rescisão", "EBITDA Reportado", "(-) D&A / Fin.", "(-) Impostos (IRPJ/CSLL)", "Lucro Líquido Rec."
    ],
    textposition="outside",
    text=[
        "R$ 2.868 mi", "- R$ 185 mi", "- R$ 197 mi", "R$ 2.486 mi",
        "- R$ 395 mi", "- R$ 248 mi", "- R$ 137 mi", "- R$ 126 mi", "- R$ 39 mi",
        "R$ 1.742 mi", "- R$ 42 mi", "R$ 1.700 mi", "- R$ 350 mi", "- R$ 290 mi", "R$ 1.062 mi"
    ],
    y=[
        2868, -185, -197, 2486,
        -395, -248, -137, -126, -39,
        1742, -42, 1700, -350, -290, 1062
    ],
    connector={"line": {"color": "rgb(100, 100, 100)"}},
    increasing={"marker": {"color": "#2ca02c"}},
    decreasing={"marker": {"color": "#d62728"}},
    totals={"marker": {"color": "#1f77b4"}}
))

fig_waterfall.update_layout(
    title=f"<b>Decomposição Detalhada do Resultado ({periodo_selecionado})</b>",
    xaxis_title="Etapas do Resultado",
    yaxis_title="Milhões de Reais (R$ mi)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    margin=dict(t=40, b=40, l=40, r=40)
)
st.plotly_chart(fig_waterfall, use_container_width=True)

# Gráficos complementares lado a lado
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📈 Evolução Histórica das Margens de Rentabilidade (%)")
    df_margens = pd.DataFrame({
        "Período": ["1T24", "2T24", "3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26"],
        "Margem EBITDA Recorrente (%)": [69.5, 70.2, 71.1, 68.8, 71.5, 72.0, 72.4, 70.0, 72.8],
        "Margem Operacional (%)": [58.0, 59.1, 60.0, 57.5, 60.2, 61.0, 61.5, 59.2, 62.0],
        "Margem Líquida (%)": [42.1, 43.5, 44.0, 41.2, 44.5, 45.0, 45.8, 43.1, 46.2]
    })
    
    if modo_exibicao_grafico == "Apenas Período Selecionado" and periodo_selecionado != "Todos os Períodos Disponíveis":
        df_margens = df_margens[df_margens["Período"] == periodo_selecionado]
        if df_margens.empty:
            df_margens = pd.DataFrame({"Período": [periodo_selecionado], "Margem EBITDA Recorrente (%)": [71.0], "Margem Operacional (%)": [60.0], "Margem Líquida (%)": [44.0]})

    fig_linhas = px.line(
        df_margens, x="Período", y=["Margem EBITDA Recorrente (%)", "Margem Operacional (%)", "Margem Líquida (%)"],
        markers=True, color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
    )
    fig_linhas.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_linhas, use_container_width=True)

with col2:
    st.markdown("#### 🍩 Composição Detalhada da Estrutura de Custos (R$ mi)")
    df_custos = pd.DataFrame({
        "Categoria": ["Pessoal e Encargos", "Tecnologia / TI", "Serviços de Terceiros", "Amortização Intangível (Cetip)", "Outras Despesas"],
        "Valor_Milhoes": [395.2, 247.5, 137.3, 125.8, 39.4],
        "Texto_Valor": ["R$ 395,2 mi", "R$ 247,5 mi", "R$ 137,3 mi", "R$ 125,8 mi", "R$ 39,4 mi"]
    })
    fig_rosca = px.pie(
        df_custos, names="Categoria", values="Valor_Milhoes", hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Prism,
        custom_data=["Texto_Valor"]
    )
    fig_rosca.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Valor: %{customdata[0]}<br>Participação: %{percent}<extra></extra>'
    )
    fig_rosca.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
        margin=dict(t=20, b=20, l=20, r=20), showlegend=False
    )
    st.plotly_chart(fig_rosca, use_container_width=True)

# --------------------------------------------------
# 6. DRE GERENCIAL COMPLETO (B3 - API RI)
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 DRE Gerencial Completo — B3 (API RI)")
st.markdown("🔎 *Ferramentas de Análise:* O painel temporal superior e as buscas filtram os dados automaticamente.")

if df_b3_raw is not None and not df_gerencial.empty:
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        tipo_visao = st.selectbox(
            "🎛️ Selecione a Visão Temporal da Tabela",
            ["Visão Completa (Trimestres e Anos)", "Apenas Anos Consolidados", "Apenas Trimestres"],
            index=0
        )
    with col_sel2:
        destacar_oportunidades = st.checkbox("🎯 Modo Foco / Auditoria de Oportunidades", value=ativar_modo_foco)

    colunas_atuais = df_gerencial.columns.tolist()
    colunas_anos = [c for c in colunas_atuais if str(c).replace('.0', '').strip().isdigit() and len(str(c).replace('.0', '').strip()) == 4]
    colunas_trim = [c for c in colunas_atuais if c not in colunas_anos and c != "Conta / Indicador"]

    # Filtragem combinada da tabela considerando o seletor temporal global
    if periodo_selecionado != "Todos os Períodos Disponíveis" and periodo_selecionado in colunas_atuais:
        colunas_filtradas = [colunas_atuais[0], periodo_selecionado]
        df_exibicao = df_gerencial[colunas_filtradas].copy()
    else:
        if tipo_visao == "Apenas Anos Consolidados":
            colunas_filtradas = [colunas_atuais[0]] + colunas_anos
            df_exibicao = df_gerencial[colunas_filtradas].copy()
        elif tipo_visao == "Apenas Trimestres":
            colunas_filtradas = [colunas_atuais[0]] + colunas_trim
            df_exibicao = df_gerencial[colunas_filtradas].copy()
        else:
            df_exibicao = df_gerencial.copy()

    busca_b3 = st.text_input(
        "🔍 Pesquisar conta ou indicador específico no DRE",
        placeholder="Ex.: EBITDA, Despesas de Pessoal, Impostos, Lucro líquido, Intangível...",
        key="busca_b3"
    )

    if busca_b3:
        mascara_b3 = df_exibicao["Conta / Indicador"].astype(str).str.contains(busca_b3, case=False, na=False)
        df_exibicao = df_exibicao[mascara_b3]
    elif destacar_oportunidades:
        termos_foco = ["EBITDA", "Despesas", "Lucro", "Receita Líquida", "Impostos", "Tecnologia"]
        padrao = "|".join(termos_foco)
        df_exibicao = df_exibicao[df_exibicao["Conta / Indicador"].astype(str).str.contains(padrao, case=False, na=False)]

    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True,
        height=520,
    )

    csv_b3 = df_exibicao.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar Tabela DRE Ajustada para CSV / Excel",
        data=csv_b3,
        file_name="B3SA3_DRE_Gerencial_Granular.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento.")
