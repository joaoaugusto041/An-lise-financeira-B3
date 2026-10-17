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

st.title("📊 Dashboard Financeiro B3SA3 — Drill Down Hierárquico")
st.markdown("Explore os dados financeiros de forma interativa navegando entre os níveis macro e granular.")

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
# 2. PAINEL DE CONTROLE DE DRILL DOWN HIERÁRQUICO
# --------------------------------------------------
st.markdown("---")
st.subheader("🎛️ Painel de Navegação Hierárquica (Drill Down)")

col_h1, col_h2, col_h3 = st.columns(3)
with col_h1:
    nivel_analise = st.selectbox(
        "📂 Nível Hierárquico de Análise",
        [
            "Nível 1: Visão Consolidada (Macro)", 
            "Nível 2: Drill Down de Custos e Despesas", 
            "Nível 3: Drill Down de Tributos e Impostos", 
            "Nível 4: Drill Down de Efeitos Não Recorrentes"
        ],
        index=0,
        help="Selecione o nível de profundidade para transformar instantaneamente os gráficos e tabelas."
    )
with col_h2:
    lista_periodos = df_gerencial.columns[1:].tolist() if not df_gerencial.empty else []
    periodo_filtro = st.selectbox(
        "📅 Recorte Temporal",
        ["Todos os Períodos"] + lista_periodos,
        index=0
    )
with col_h3:
    st.markdown("<br>", unsafe_allow_html=True)
    modo_foco = st.checkbox("🎯 Destacar Oportunidades", value=False)

# --------------------------------------------------
# 3. RENDERIZAÇÃO DINÂMICA BASEADA NO NÍVEL DE DRILL DOWN
# --------------------------------------------------

if nivel_analise == "Nível 1: Visão Consolidada (Macro)":
    st.markdown("#### 🌍 Panorama Geral: Da Receita ao Lucro Líquido")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='metric-card'><div class='metric-title'>Receita Bruta Total</div><div class='metric-value'>R$ 2.868,0 mi</div><small style='color: #28a745;'>▲ Base Sólida</small></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='metric-card'><div class='metric-title'>EBITDA Recorrente</div><div class='metric-value'>R$ 1.742,0 mi</div><small style='color: #28a745;'>▲ Margem 70,1%</small></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='metric-card' style='border-left-color: #dc3545;'><div class='metric-title'>Despesas Operacionais</div><div class='metric-value'>R$ 845,2 mi</div><small style='color: #dc3545;'>▼ Requer Monitoramento</small></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='metric-card' style='border-left-color: #ffc107;'><div class='metric-title'>Lucro Líquido Recorrente</div><div class='metric-value'>R$ 1.062,0 mi</div><small style='color: #6c757d;'>Conversão Forte</small></div>", unsafe_allow_html=True)

    # Gráfico de Ponte Macro
    fig_macro = go.Figure(go.Waterfall(
        name="B3SA3", orientation="v",
        measure=["absolute", "relative", "relative", "total", "relative", "total"],
        x=["Receita Bruta", "Deduções e Impostos", "Despesas Operacionais", "EBITDA Recorrente", "D&A, Fin. e IRPJ", "Lucro Líquido Rec."],
        textposition="outside",
        text=["R$ 2.868 mi", "- R$ 382 mi", "- R$ 845 mi", "R$ 1.742 mi", "- R$ 680 mi", "R$ 1.062 mi"],
        y=[2868, -382, -845, 1742, -680, 1062],
        connector={"line": {"color": "rgb(100, 100, 100)"}},
    ))
    fig_macro.update_layout(title="<b>Ponte Consolidada do Resultado (R$ Milhões)</b>", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_macro, use_container_width=True)

elif nivel_analise == "Nível 2: Drill Down de Custos e Despesas":
    st.markdown("#### 💻 Drill Down Detalhado: Estrutura de Custos e Despesas Operacionais")
    st.caption("Abertura granular dos centros de custo para identificar frentes de otimização e corte.")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        # Gráfico de barras detalhado das despesas
        df_desp_graf = pd.DataFrame({
            "Subconta de Despesa": ["Salários e Encargos", "Bônus / DHO", "Licenças Software & Cloud", "Processamento / Links", "Consultorias", "Market Maker", "Amortização Cetip", "Outras Despesas"],
            "Valor (R$ mi)": [285.0, 110.2, 165.4, 82.1, 95.3, 42.0, 125.8, 39.4]
        })
        fig_bar_desp = px.bar(df_desp_graf, x="Valor (R$ mi)", y="Subconta de Despensa", orientation="h", title="<b>Quebra de Despesas por Subconta (R$ mi)</b>", color="Valor (R$ mi)", color_continuous_scale="Reds")
        fig_bar_desp.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_desp, use_container_width=True)

    with col_d2:
        # Tabela analítica de oportunidades de custos
        df_desp_det = pd.DataFrame({
            "Subconta": ["Licenças Software & Cloud", "Consultorias e Jurídico", "Salários e Encargos", "Amortização Intangível"],
            "Valor (R$ mi)": [165.4, 95.3, 285.0, 125.8],
            "Potencial de Oportunidade": ["Alto (Renovação de Contratos)", "Médio (Redução de Escopo)", "Baixo (Headcount Estrutural)", "Nulo (Efeito Contábil sem Caixa)"]
        })
        st.markdown("##### 🔍 Matriz de Oportunidades em Custos")
        st.dataframe(df_desp_det, use_container_width=True, hide_index=True)

elif nivel_analise == "Nível 3: Drill Down de Tributos e Impostos":
    st.markdown("#### 🏛️ Drill Down Detalhado: Carga Tributária e Deduções")
    st.caption("Abertura dos impostos diretos, indiretos e estratégias de eficiência fiscal.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        df_imp_graf = pd.DataFrame({
            "Tributo": ["PIS / COFINS", "Imposto de Renda (IRPJ)", "ISS", "Contribuição Social (CSLL)", "Benefício Fiscal JCP"],
            "Valor (R$ mi)": [185.4, 145.2, 92.1, 58.3, -98.4]
        })
        fig_imp = px.bar(df_imp_graf, x="Tributo", y="Valor (R$ mi)", title="<b>Composição da Carga Tributária (R$ mi)</b>", color="Valor (R$ mi)", color_continuous_scale="Blues")
        fig_imp.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_imp, use_container_width=True)

    with col_t2:
        st.markdown("##### 💡 Diagnóstico Fiscal")
        st.markdown("""
        * **PIS/COFINS:** Representam a maior fatia das deduções sobre a receita bruta de serviços financeiros.
        * **Otimização via JCP (Juros sobre Capital Próprio):** O ganho fiscal de **R$ 98,4 milhões** demonstra o aproveitamento eficiente de proventos dedutíveis para baixar a alíquota efetiva da companhia.
        """)

else: # Nível 4
    st.markdown("#### ⚠️ Drill Down Detalhado: Efeitos Não Recorrentes")
    st.caption("Conciliação entre o EBITDA Reportado e o EBITDA Recorrente (Expurgo de ruídos contábeis).")
    
    df_nr_vis = pd.DataFrame({
        "Evento Extraordinário": ["Assessoria em M&A", "Rescisões e Reestruturação", "Provisões Cíveis/Tributárias"],
        "Impacto (R$ mi)": [18.2, 14.5, 9.3]
    })
    fig_nr = px.pie(df_nr_vis, names="Evento Extraordinário", values="Impacto (R$ mi)", hole=0.4, title="<b>Distribuição dos Ajustes Não Recorrentes</b>")
    st.plotly_chart(fig_nr, use_container_width=True)

# --------------------------------------------------
# 4. DRE GERENCIAL COMPLETO COM FILTROS DE EXIBIÇÃO
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 DRE Gerencial Completo — B3 (API RI)")
st.markdown("🔎 *Ferramentas de Análise:* Utilize os seletores para auditar todas as contas detalhadas.")

if df_b3_raw is not None and not df_gerencial.empty:
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        tipo_visao = st.selectbox(
            "🎛️ Visão Temporal da Tabela",
            ["Visão Completa (Trimestres e Anos)", "Apenas Anos Consolidados", "Apenas Trimestres"],
            index=0
        )
    with col_sel2:
        destacar_oportunidades = st.checkbox("🎯 Modo Foco / Oportunidade", value=modo_foco)

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
        file_name="B3SA3_DRE_Gerencial_DrillDown.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento.")
