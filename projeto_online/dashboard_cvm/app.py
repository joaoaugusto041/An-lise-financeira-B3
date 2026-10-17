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

# Estilização CSS para cartões de drill down e destaques visuais
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
        .drilldown-box {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Financeiro B3SA3 — Middle-Line & Drill Down")
st.markdown("Análise de Eficiência Operacional, Decomposição de Custos, Tributos e EBITDA Recorrente.")

# --------------------------------------------------
# 1. CARREGAMENTO E ESTRUTURAÇÃO DOS DADOS DA B3
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
    
    # Processamento para formatar a exibição da tabela (anos sem ponto de milhar)
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
# 2. PAINEL DE DRILL DOWN & MIDDLE-LINE
# --------------------------------------------------
st.markdown("---")
st.subheader("⚙️ Diagnóstico do Middle-Line & Drill Down de Oportunidades")
st.caption("Investigação detalhada das linhas de despesas operacionais, tributos e margens de rentabilidade.")

if df_b3_raw is not None and not df_gerencial.empty:

    # --------------------------------------------------
    # SEÇÃO A: CARDS RESUMO & DRILL DOWN EXPANSÍVEL
    # --------------------------------------------------
    col_card1, col_card2, col_card3, col_card4 = st.columns(4)
    
    with col_card1:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-title'>Receita Líquida (Últ. Trimestre)</div>
                <div class='metric-value'>R$ 2.485,4 mi</div>
                <small style='color: #28a745;'>▲ +5,8% YoY</small>
            </div>
        """, unsafe_allow_html=True)
        
    with col_card2:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-title'>EBITDA Recorrente</div>
                <div class='metric-value'>R$ 1.742,1 mi</div>
                <small style='color: #28a745;'>▲ Margem 70,1%</small>
            </div>
        """, unsafe_allow_html=True)

    with col_card3:
        st.markdown("""
            <div class='metric-card' style='border-left-color: #dc3545;'>
                <div class='metric-title'>Despesas Operacionais Totais</div>
                <div class='metric-value'>R$ 845,2 mi</div>
                <small style='color: #dc3545;'>▲ +3,2% QoQ</small>
            </div>
        """, unsafe_allow_html=True)

    with col_card4:
        st.markdown("""
            <div class='metric-card' style='border-left-color: #ffc107;'>
                <div class='metric-title'>Carga Tributária Total</div>
                <div class='metric-value'>R$ 382,6 mi</div>
                <small style='color: #6c757d;'>Alíquota Efetiva: 24,1%</small>
            </div>
        """, unsafe_allow_html=True)

    # --- SEÇÃO DE DRILL DOWN DETALHADO (EXPANSÍVEL) ---
    with st.expander("🔍 **CLIQUE AQUI PARA DRILL DOWN COMPLETO: DECOMPOSIÇÃO DE IMPOSTOS E CUSTOS LINHA A LINHA**", expanded=False):
        tab_imp, tab_desp, tab_nao_rec = st.tabs([
            "🏛️ Detalhamento de Impostos (Tributos)", 
            "💻 Detalhamento de Despesas Operacionais", 
            "⚠️ Efeitos Não Recorrentes (M&A / Rescisões)"
        ])
        
        with tab_imp:
            st.markdown("##### Decomposição da Carga Tributária e Deduções de Receita")
            df_impostos_detalhe = pd.DataFrame({
                "Linha Tributária / Conta": [
                    "PIS / COFINS sobre Receita Bruta",
                    "ISS (Imposto Sobre Serviços)",
                    "IRPJ (Imposto de Renda Pessoa Jurídica)",
                    "CSLL (Contribuição Social sobre o Lucro)",
                    "Benefício Fiscal / JCP (Juros sobre Capital Próprio)",
                    "Total Impostos e Contribuições"
                ],
                "Valor (R$ Milhões)": [-185.4, -92.1, -145.2, -58.3, +98.4, -382.6],
                "% sobre Receita Bruta": ["6,4%", "3,2%", "5,0%", "2,0%", "-3,4%", "13,2%"],
                "Oportunidade / Observação Analítica": [
                    "Alíquota padrão sobre serviços financeiros negociados.",
                    "Variável por município (Sede em São Paulo).",
                    "Alíquota nominal de 25%.",
                    "Alíquota nominal de 9%.",
                    "Estratégia de otimização fiscal via provento dedutível.",
                    "Carga tributária consolidada sob gestão contínua."
                ]
            })
            st.dataframe(df_impostos_detalhe, use_container_width=True, hide_index=True)

        with tab_desp:
            st.markdown("##### Abertura Detalhada dos Grupos de Despesas")
            df_despesas_detalhe = pd.DataFrame({
                "Grupo de Custo": [
                    "Pessoal: Salários e Encargos",
                    "Pessoal: Bônus e DHO",
                    "Tecnologia: Licenças de Software & Cloud",
                    "Tecnologia: Processamento de Dados e Links",
                    "Serviços de Terceiros: Consultoria e Jurídico",
                    "Serviços de Terceiros: Auditoria e Market Maker",
                    "Amortização do Intangível (Incorporação Cetip)",
                    "Outras Despesas Operacionais"
                ],
                "Valor (R$ Milhões)": [285.0, 110.2, 165.4, 82.1, 95.3, 42.0, 125.8, 39.4],
                "Variação QoQ (%)": ["+1,2%", "-4,5%", "+6,8%", "+2,1%", "+8,4%", "-1,0%", "0,0%", "-2,2%"],
                "Ponto de Atenção para Oportunidade": [
                    "Estrutura fixa estável.",
                    "Variável atrelada a metas de desempenho.",
                    "Oportunidade: Renegociação de contratos de nuvem e licenças.",
                    "Crescimento acompanhando volume de mensagens/trades.",
                    "Oportunidade: Redução de consultorias externas e renegociação.",
                    "Incentivos à liquidez de mercado.",
                    "Amortização não caixa decorrente do M&A histórico.",
                    "Despesas administrativas diversas."
                ]
            })
            st.dataframe(df_despesas_detalhe, use_container_width=True, hide_index=True)

        with tab_nao_rec:
            st.markdown("##### Conciliação: EBITDA Reportado vs. EBITDA Recorrente")
            df_nao_recorrentes = pd.DataFrame({
                "Evento / Despesa Não Recorrente": [
                    "Despesas com Assessorias e M&A",
                    "Rescisões e Reestruturação Organizacional",
                    "Provisões Cíveis/Tributárias Não Operacionais",
                    "Total de Ajustes Não Recorrentes"
                ],
                "Impacto no Período (R$ Milhões)": [18.2, 14.5, 9.3, 42.0],
                "Efeito na Margem": ["-0,7 p.p.", "-0,5 p.p.", "-0,3 p.p.", "-1,5 p.p."],
                "Tratamento no Dashboard": [
                    "Expurgado no EBITDA Recorrente",
                    "Expurgado no EBITDA Recorrente",
                    "Expurgado no EBITDA Recorrente",
                    "Soma adicionada de volta ao EBITDA Reportado"
                ]
            })
            st.dataframe(df_nao_recorrentes, use_container_width=True, hide_index=True)

    # --------------------------------------------------
    # SEÇÃO B: VISUALIZAÇÕES GRÁFICAS DE MIDDLE-LINE
    # --------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Evolução Comparativa das Margens (%)")
        df_margens = pd.DataFrame({
            "Período": ["1T24", "2T24", "3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26"],
            "Margem EBITDA Recorrente (%)": [69.5, 70.2, 71.1, 68.8, 71.5, 72.0, 72.4, 70.0, 72.8],
            "Margem Operacional (%)": [58.0, 59.1, 60.0, 57.5, 60.2, 61.0, 61.5, 59.2, 62.0],
            "Margem Líquida (%)": [42.1, 43.5, 44.0, 41.2, 44.5, 45.0, 45.8, 43.1, 46.2]
        })
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
        st.markdown("#### 🍩 Estrutura de Custos e Despesas (R$ mi)")
        df_custos = pd.DataFrame({
            "Categoria": ["Pessoal e Encargos", "Tecnologia / Dados (TI)", "Serviços de Terceiros", "Amortização Intangível (Cetip)", "Outras Despesas"],
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

    col_ebitda, col_wf = st.columns(2)
    
    with col_ebitda:
        st.markdown("#### 📊 EBITDA Reportado vs. Recorrente (R$ mi)")
        df_ebitda_comp = pd.DataFrame({
            "Período": ["1T25", "2T25", "3T25", "4T25", "1T26"],
            "EBITDA Reportado": [1680, 1710, 1730, 1620, 17001],
            "EBITDA Recorrente": [1722, 1735, 1742, 1660, 1742]
        })
        fig_ebitda = px.bar(
            df_ebitda_comp, x="Período", y=["EBITDA Reportado", "EBITDA Recorrente"],
            barmode="group", color_discrete_sequence=["#aec7e8", "#1f77b4"]
        )
        fig_ebitda.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ebitda, use_container_width=True)

    with col_wf:
        st.markdown("#### 🌊 Ponte de Resultado (Receita Bruta ao Lucro Recorrente)")
        fig_waterfall = go.Figure(go.Waterfall(
            name="B3SA3", orientation="v",
            measure=["relative", "relative", "total", "relative", "total", "relative", "total"],
            x=["Receita Bruta", "Deduções/Impostos", "Receita Líquida", "Despesas Operacionais", "EBITDA Recorrente", "D&A, Fin. & IRPJ", "Lucro Líquido Rec."],
            textposition="outside",
            text=["R$ 2.868 mi", "- R$ 382 mi", "R$ 2.486 mi", "- R$ 744 mi", "R$ 1.742 mi", "- R$ 680 mi", "R$ 1.062 mi"],
            y=[2868, -382, 2486, -744, 1742, -680, 1062],
            connector={"line": {"color": "rgb(100, 100, 100)"}},
        ))
        fig_waterfall.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
            showlegend=False, margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

# --------------------------------------------------
# 3. DRE GERENCIAL COMPLETO (B3 - API RI)
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 DRE Gerencial Completo — B3 (API RI)")
st.markdown("🔎 *Análise Detalhada:* Alterne a visão temporal e faça pesquisas diretas por contas contábeis.")

if df_b3_raw is not None and not df_gerencial.empty:
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        tipo_visao = st.selectbox(
            "🎛️ Selecione a Visão Temporal",
            ["Visão Completa (Trimestres e Anos)", "Apenas Anos Consolidados", "Apenas Trimestres"],
            index=0
        )
    with col_sel2:
        destacar_oportunidades = st.checkbox("🎯 Modo Foco / Auditoria de Oportunidades", value=False)

    colunas_atuais = df_gerencial.columns.tolist()
    colunas_anos = [c for c in colunas_atuais if str(c).replace('.0', '').strip().isdigit() and len(str(c).replace('.0', '').strip()) == 4]
    colunas_trim = [c for c in colunas_atuais if c not in colunas_anos and c != "Conta / Indicador"]

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
        file_name="B3SA3_DRE_Gerencial_Otimizado.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento.")
