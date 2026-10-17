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

# Estilização visual corporativa
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

st.title("📊 Dashboard Financeiro B3SA3 — Drill Down na Ponte (Waterfall)")
st.markdown("Navegue pelos níveis de detalhe da ponte de resultado. Selecione uma macro-etapa para abrir sua composição detalhada.")

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
# 2. PAINEL DE CONTROLE DO DRILL DOWN DA PONTE
# --------------------------------------------------
st.markdown("---")
col_wf_ctrl1, col_wf_ctrl2 = st.columns([2, 2])

with col_wf_ctrl1:
    nivel_drilldown_ponte = st.selectbox(
        "🔍 Nível de Detalhe da Ponte (Drill Down)",
        [
            "1. Visão Macro Consolidada (Padrão)",
            "2. Drill Down da Coluna de Impostos e Tributos",
            "3. Drill Down da Coluna de Despesas Operacionais",
            "4. Drill Down de EBITDA e Ajustes Não Recorrentes"
        ],
        index=0,
        help="Selecione a coluna que deseja abrir em detalhes para reorganizar o gráfico de cascata instantaneamente."
    )

with col_wf_ctrl2:
    lista_periodos = df_gerencial.columns[1:].tolist() if not df_gerencial.empty else []
    periodo_filtro = st.selectbox(
        "📅 Recorte Temporal",
        ["Todos os Períodos"] + lista_periodos,
        index=0
    )

# --------------------------------------------------
# 3. CONSTRUÇÃO DINÂMICA DO WATERFALL COM DRILL DOWN
# --------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

if nivel_drilldown_ponte == "1. Visão Macro Consolidada (Padrão)":
    st.markdown("#### 🌊 Ponte Consolidada do Resultado (Macro)")
    st.caption("Visão geral de ponta a ponta. *Dica:* Use o seletor acima para dar drill down nas colunas de Impostos ou Despesas.")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="B3SA3", orientation="v",
        measure=["absolute", "relative", "relative", "total", "relative", "total", "relative", "total"],
        x=["Receita Bruta", "(-) Deduções/Impostos", "(-) Despesas Operacionais", "EBITDA Recorrente", "(-) Ajustes Não Recorrentes", "EBITDA Reportado", "(-) D&A, Fin. & IRPJ", "Lucro Líquido Rec."],
        textposition="outside",
        text=["R$ 2.868 mi", "- R$ 382 mi", "- R$ 845 mi", "R$ 1.641 mi", "- R$ 42 mi", "R$ 1.599 mi", "- R$ 537 mi", "R$ 1.062 mi"],
        y=[2868, -382, -845, 1641, -42, 1599, -537, 1062],
        connector={"line": {"color": "rgb(100, 100, 100)"}},
        increasing={"marker": {"color": "#2ca02c"}},
        decreasing={"marker": {"color": "#d62728"}},
        totals={"marker": {"color": "#1f77b4"}}
    ))

elif nivel_drilldown_ponte == "2. Drill Down da Coluna de Impostos e Tributos":
    st.markdown("#### 🏛️ Drill Down: Composição Detalhada da Coluna de Impostos")
    st.caption("Abertura exclusiva dos tributos diretos, indiretos e créditos fiscais que compõem o montante de impostos.")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="B3SA3", orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["Receita Bruta", "(-) PIS / COFINS", "(-) ISS Municipal", "(-) IRPJ (Imposto de Renda)", "(-) CSLL", "(+) Benefício Fiscal JCP", "Total Líquido de Tributos"],
        textposition="outside",
        text=["R$ 2.868 mi", "- R$ 185,4 mi", "- R$ 92,1 mi", "- R$ 145,2 mi", "- R$ 58,3 mi", "+ R$ 98,4 mi", "- R$ 382,6 mi"],
        y=[2868, -185.4, -92.1, -145.2, -58.3, 98.4, -382.6],
        connector={"line": {"color": "rgb(100, 100, 100)"}},
        increasing={"marker": {"color": "#2ca02c"}},
        decreasing={"marker": {"color": "#d62728"}},
        totals={"marker": {"color": "#ff7f0e"}}
    ))

elif nivel_drilldown_ponte == "3. Drill Down da Coluna de Despesas Operacionais":
    st.markdown("#### 💻 Drill Down: Composição Detalhada da Coluna de Despesas")
    st.caption("Abertura linha a linha de cada centro de custo operacional (Pessoal, TI, Terceiros e Amortização).")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="B3SA3", orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["Receita Líquida", "(-) Salários Fixos", "(-) Bônus / DHO", "(-) Software & Cloud", "(-) Links e Processamento", "(-) Consultorias/Jurídico", "(-) Market Maker", "(-) Amortização Cetip", "Total Desp. Operacionais"],
        textposition="outside",
        text=["R$ 2.486 mi", "- R$ 285,0 mi", "- R$ 110,2 mi", "- R$ 165,4 mi", "- R$ 82,1 mi", "- R$ 95,3 mi", "- R$ 42,0 mi", "- R$ 125,8 mi", "- R$ 905,8 mi"],
        y=[2486, -285.0, -110.2, -165.4, -82.1, -95.3, -42.0, -125.8, -905.8],
        connector={"line": {"color": "rgb(100, 100, 100)"}},
        increasing={"marker": {"color": "#2ca02c"}},
        decreasing={"marker": {"color": "#d62728"}},
        totals={"marker": {"color": "#d62728"}}
    ))

else:
    st.markdown("#### ⚠️ Drill Down: EBITDA Reportado vs. Recorrente (Ajustes)")
    st.caption("Detalhamento dos efeitos não recorrentes que diferem o EBITDA Contábil do Recorrente.")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="B3SA3", orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["EBITDA Recorrente", "(-) Assessorias M&A", "(-) Rescisões e Reestruturação", "(-) Provisões Cíveis", "EBITDA Reportado Final"],
        textposition="outside",
        text=["R$ 1.641 mi", "- R$ 18,2 mi", "- R$ 14,5 mi", "- R$ 9,3 mi", "R$ 1.599 mi"],
        y=[1641, -18.2, -14.5, -9.3, 1599],
        connector={"line": {"color": "rgb(100, 100, 100)"}},
        increasing={"marker": {"color": "#2ca02c"}},
        decreasing={"marker": {"color": "#d62728"}},
        totals={"marker": {"color": "#1f77b4"}}
    ))

fig_waterfall.update_layout(
    title=f"<b>Ponte Detalhada — {nivel_drilldown_ponte}</b>",
    xaxis_title="Componentes",
    yaxis_title="Milhões de Reais (R$ mi)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    margin=dict(t=40, b=40, l=40, r=40)
)
st.plotly_chart(fig_waterfall, use_container_width=True)

# --------------------------------------------------
# 4. GRÁFICOS COMPLEMENTARES DE APOIO
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 EBITDA Reportado vs. Recorrente")
    df_ebitda_comp = pd.DataFrame({
        "Período": ["1T25", "2T25", "3T25", "4T25", "1T26"],
        "EBITDA Reportado": [1580, 1610, 1630, 1520, 1599],
        "EBITDA Recorrente": [1622, 1635, 1641, 1560, 1641]
    })
    fig_bar = px.bar(
        df_ebitda_comp, x="Período", y=["EBITDA Reportado", "EBITDA Recorrente"],
        barmode="group", color_discrete_sequence=["#aec7e8", "#1f77b4"]
    )
    fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("#### 📈 Evolução das Margens de Rentabilidade (%)")
    df_margens = pd.DataFrame({
        "Período": ["1T24", "2T24", "3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26"],
        "Margem EBITDA Recorrente (%)": [69.5, 70.2, 71.1, 68.8, 71.5, 72.0, 72.4, 70.0, 72.8],
        "Margem Líquida (%)": [42.1, 43.5, 44.0, 41.2, 44.5, 45.0, 45.8, 43.1, 46.2]
    })
    fig_linhas = px.line(
        df_margens, x="Período", y=["Margem EBITDA Recorrente (%)", "Margem Líquida (%)"],
        markers=True, color_discrete_sequence=["#1f77b4", "#2ca02c"]
    )
    fig_linhas.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_linhas, use_container_width=True)

# --------------------------------------------------
# 5. DRE GERENCIAL COMPLETO (B3 - API RI)
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 DRE Gerencial Completo — B3 (API RI)")
st.markdown("🔎 *Ferramentas de Análise:* Filtre períodos, pesquise contas e localize oportunidades de middle-line instantaneamente.")

if df_b3_raw is not None and not df_gerencial.empty:
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        tipo_visao = st.selectbox(
            "🎛️ Visão Temporal da Tabela",
            ["Visão Completa (Trimestres e Anos)", "Apenas Anos Consolidados", "Apenas Trimestres"],
            index=0
        )
    with col_sel2:
        destacar_oportunidades_tabela = st.checkbox("🎯 Modo Foco / Auditoria", value=False)

    colunas_atuais = df_gerencial.columns.tolist()
    colunas_anos = [c for c in colunas_atuais if str(c).replace('.0', '').strip().isdigit() and len(str(c).replace('.0', '').strip()) == 4]
    colunas_trim = [c for c in colunas_atuais if c not in colunas_anos and c != "Conta / Indicador"]

    if periodo_filtro != "Todos os Períodos" and periodo_filtro in colunas_atuais:
        colunas_filtradas = [colunas_atuais[0], periodo_filtro]
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
    elif destacar_oportunidades_tabela:
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
        file_name="B3SA3_DRE_Gerencial_DrillDown.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento.")
