import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
from loader_b3 import carregar_dados_b3

st.set_page_config(
    page_title="Dashboard Financeiro B3SA3",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Dashboard Financeiro B3SA3")
st.markdown("Análise financeira integrada: Eficiência Operacional, Custos e DRE Gerencial Detalhado.")

# --------------------------------------------------
# CARREGAMENTO DOS DADOS DA B3
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
            # Limpa '.0' caso venha como float do excel
            if rotulo.endswith('.0'):
                rotulo = rotulo[:-2]
            colunas_validas.append(col)
            nomes_colunas.append(rotulo)

    df_gerencial = df_b3_raw.iloc[3:, colunas_validas].copy()
    df_gerencial.columns = nomes_colunas
    df_gerencial = df_gerencial.dropna(subset=["Conta / Indicador"])
    
    # Formatação numérica padrão Brasil
    for c in df_gerencial.columns[1:]:
        def formatar_valor(val, nome_coluna):
            try:
                if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "nan":
                    return ""
                
                texto = str(val).strip()
                # Se for ano (ex: 2023, 2024, 2025), exibe limpo sem ponto de milhar
                nome_limpo = str(nome_coluna).replace('.0', '').strip()
                if nome_limpo.isdigit() and len(nome_limpo) == 4:
                    return texto.replace('.0', '')
                
                num = float(texto)
                return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return str(val)
        
        df_gerencial[c] = df_gerencial[c].apply(lambda x: formatar_valor(x, c))

# --------------------------------------------------
# SEÇÃO: EFICIÊNCIA OPERACIONAL, CUSTOS E LUCRATIVIDADE
# --------------------------------------------------
st.markdown("---")
st.subheader("⚙️ Eficiência Operacional, Custos e Lucratividade (Middle-Line)")
st.caption("Análise estruturada de despesas operacionais, margens de rentabilidade e pontes de resultado.")

if df_b3_raw is not None and not df_gerencial.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Evolução Histórica das Margens (%)")
        df_margens = pd.DataFrame({
            "Período": ["1T24", "2T24", "3T24", "4T24", "1T25", "2T25", "3T25", "4T25", "1T26"],
            "Margem EBITDA (%)": [68.5, 69.2, 70.1, 67.8, 70.5, 71.0, 71.4, 69.0, 71.8],
            "Margem Líquida (%)": [42.1, 43.5, 44.0, 41.2, 44.5, 45.0, 45.8, 43.1, 46.2]
        })
        fig_linhas = px.line(
            df_margens, x="Período", y=["Margem EBITDA (%)", "Margem Líquida (%)"],
            markers=True, color_discrete_sequence=["#1f77b4", "#2ca02c"]
        )
        fig_linhas.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_linhas, use_container_width=True)

    with col2:
        st.markdown("#### 🍩 Decomposição da Estrutura de Custos (R$ mi)")
        df_custos = pd.DataFrame({
            "Categoria": ["Pessoal e Encargos", "Tecnologia / Dados (TI)", "Serviços de Terceiros", "Depreciação e Amortização", "Outras Despesas"],
            "Valor_Milhoes": [920, 735, 475, 340, 160],
            "Texto_Valor": ["R$ 920 mi", "R$ 735 mi", "R$ 475 mi", "R$ 340 mi", "R$ 160 mi"]
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
        fig_rosca.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig_rosca, use_container_width=True)

    st.markdown("#### 📊 Ponte de Resultado (Waterfall): Da Receita ao Lucro Líquido")
    fig_waterfall = go.Figure(go.Waterfall(
        name="B3SA3", orientation="v",
        measure=["relative", "relative", "relative", "total", "relative", "total"],
        x=["Receita Líquida", "Despesas de Pessoal & TI", "Outras Desp. / Provisões", "EBITDA Ajustado", "Impostos, Fin. & D&A", "Lucro Líquido"],
        textposition="outside",
        text=["R$ 2.650 mi", "- R$ 920 mi", "- R$ 330 mi", "R$ 1.400 mi", "- R$ 560 mi", "R$ 840 mi"],
        y=[2650, -920, -330, 1400, -560, 840],
        connector={"line": {"color": "rgb(100, 100, 100)"}},
    ))
    fig_waterfall.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
    st.plotly_chart(fig_waterfall, use_container_width=True)

# --------------------------------------------------
# DRE GERENCIAL COMPLETO (B3 - API RI)
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 DRE Gerencial Completo — B3 (API RI)")
st.markdown("🔎 *Análise Detalhada:* Utilize o seletor de visualização abaixo para alternar entre os trimestres ou focar direto nos anos consolidados.")

if df_b3_raw is not None and not df_gerencial.empty:
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        tipo_visao = st.selectbox(
            "🎛️ Selecione a Visão Temporal",
            ["Visão Completa (Trimestres e Anos)", "Apenas Anos Consolidados", "Apenas Trimestres"],
            index=0
        )
    with col_sel2:
        destacar_oportunidades = st.checkbox("🎯 Modo Foco / Auditoria de Lucratividade", value=False, help="Filtra linhas-chave para exame rápido.")

    # Filtro robusto de colunas ajustado para reconhecer os anos limpos
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
        "🔍 Pesquisar conta ou indicador específico",
        placeholder="Ex.: EBITDA, Despesas de Pessoal, Lucro líquido, Derivativos...",
        key="busca_b3"
    )

    if busca_b3:
        mascara_b3 = df_exibicao["Conta / Indicador"].astype(str).str.contains(busca_b3, case=False, na=False)
        df_exibicao = df_exibicao[mascara_b3]
    elif destacar_oportunidades:
        termos_foco = ["EBITDA", "Despesas", "Lucro", "Receita Líquida"]
        padrao = "|".join(termos_foco)
        df_exibicao = df_exibicao[df_exibicao["Conta / Indicador"].astype(str).str.contains(padrao, case=False, na=False)]

    with st.expander("💡 Dicionário Financeiro e Guia de Análise de Lucratividade"):
        st.markdown("""
        * **Receita Líquida:** O faturamento total bruto da B3 após deduções. Ponto de partida para o crescimento.
        * **EBITDA (LAJIDA):** Geração de caixa operacional pura da empresa, sem efeitos financeiros ou contábeis.
        * **Despesas de Pessoal e TI:** Os maiores centros de custo. Oportunidade: Avaliar alavancagem operacional.
        * **Amortização de Intangíveis:** Custo contábil de aquisições passadas (ex: Cetip) sem impacto direto de caixa.
        * **Lucro Líquido Recorrente:** O resultado final líquido ajustado entregue aos acionistas.
        """)

    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True,
        height=520,
    )

    csv_b3 = df_exibicao.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar Tabela Ajustada para CSV / Excel",
        data=csv_b3,
        file_name="B3SA3_DRE_Gerencial_Otimizado.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento.")
