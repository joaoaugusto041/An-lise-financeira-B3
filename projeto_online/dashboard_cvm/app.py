import streamlit as st
import pandas as pd
import zipfile
from pathlib import Path
from loader_b3 import carregar_dados_b3

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------
st.set_page_config(
    page_title="B3SA3 | Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Caminho da pasta dados
PASTA = Path(__file__).resolve().parent / "dados"
COD_CVM = 21610
PERIODOS_ANUAIS = [str(a) for a in range(2020, 2026)]
PERIODOS = PERIODOS_ANUAIS + ["1T26"]

# --------------------------------------------------
# VISUAL
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: #0b1120;
    color: #e5e7eb;
}
[data-testid="stHeader"] {
    background: rgba(11, 17, 32, 0.95);
}
[data-testid="stSidebar"] {
    background: #111827;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #f8fafc !important;
}
p, label, span {
    color: #cbd5e1;
}
.kicker {
    color: #60a5fa;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
}
.metric-card {
    background: linear-gradient(145deg, #172238, #111827);
    border: 1px solid #29364c;
    border-radius: 14px;
    padding: 20px;
    min-height: 132px;
}
.metric-label {
    color: #94a3b8;
    font-size: 0.82rem;
    margin-bottom: 12px;
}
.metric-value {
    color: #f8fafc;
    font-size: clamp(1.2rem, 2vw, 1.8rem);
    font-weight: 750;
    line-height: 1.25;
}
.metric-code {
    color: #60a5fa;
    font-size: 0.75rem;
    margin-top: 10px;
}
.section-card {
    background: #111827;
    border: 1px solid #29364c;
    border-radius: 14px;
    padding: 18px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
}
div[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #29364c;
    padding: 14px;
    border-radius: 12px;
}
hr {
    border-color: #29364c;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CARREGAMENTO DOS DADOS CVM
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def carregar_dados():
    registros = []

    for ano in range(2020, 2026):
        arquivo = PASTA / f"dfp_cia_aberta_{ano}.zip"
        if not arquivo.exists():
            continue

        nome_csv = f"dfp_cia_aberta_DRE_con_{ano}.csv"
        with zipfile.ZipFile(arquivo) as z:
            with z.open(nome_csv) as f:
                df = pd.read_csv(
                    f,
                    sep=";",
                    encoding="latin1",
                    dtype={"CD_CONTA": str},
                )

        df["CD_CVM"] = pd.to_numeric(df["CD_CVM"], errors="coerce")
        df = df[df["CD_CVM"] == COD_CVM].copy()

        df["DT_INI_EXERC"] = pd.to_datetime(df["DT_INI_EXERC"], errors="coerce")
        df["DT_FIM_EXERC"] = pd.to_datetime(df["DT_FIM_EXERC"], errors="coerce")

        df = df[
            (df["DT_FIM_EXERC"].dt.year == ano)
            & (df["DT_FIM_EXERC"].dt.month == 12)
        ].copy()

        if df.empty:
            continue

        ordem = df["ORDEM_EXERC"].astype(str).str.upper().str.strip()
        df["_prioridade"] = ordem.map({
            "ÚLTIMO": 0, "ULTIMO": 0,
            "PENÚLTIMO": 1, "PENULTIMO": 1,
        }).fillna(2)

        df = df.sort_values("_prioridade")
        df = df.drop_duplicates("CD_CONTA", keep="first")

        df["Periodo"] = str(ano)
        df["Valor"] = pd.to_numeric(df["VL_CONTA"], errors="coerce")
        registros.append(df)

    arquivo_itr = PASTA / "itr_cia_aberta_2026.zip"
    if arquivo_itr.exists():
        nome_csv = "itr_cia_aberta_DRE_con_2026.csv"
        with zipfile.ZipFile(arquivo_itr) as z:
            with z.open(nome_csv) as f:
                itr = pd.read_csv(
                    f,
                    sep=";",
                    encoding="latin1",
                    dtype={"CD_CONTA": str},
                )

        itr["CD_CVM"] = pd.to_numeric(itr["CD_CVM"], errors="coerce")
        itr = itr[itr["CD_CVM"] == COD_CVM].copy()

        itr["DT_INI_EXERC"] = pd.to_datetime(itr["DT_INI_EXERC"], errors="coerce")
        itr["DT_FIM_EXERC"] = pd.to_datetime(itr["DT_FIM_EXERC"], errors="coerce")

        itr = itr[
            (itr["DT_INI_EXERC"] == pd.Timestamp("2026-01-01"))
            & (itr["DT_FIM_EXERC"] == pd.Timestamp("2026-03-31"))
        ].copy()

        if not itr.empty:
            ordem = itr["ORDEM_EXERC"].astype(str).str.upper().str.strip()
            itr["_prioridade"] = ordem.map({
                "ÚLTIMO": 0, "ULTIMO": 0,
                "PENÚLTIMO": 1, "PENULTIMO": 1,
            }).fillna(2)

            itr = itr.sort_values("_prioridade")
            itr = itr.drop_duplicates("CD_CONTA", keep="first")
            itr["Periodo"] = "1T26"
            itr["Valor"] = pd.to_numeric(itr["VL_CONTA"], errors="coerce")
            registros.append(itr)

    if not registros:
        return pd.DataFrame()

    dados = pd.concat(registros, ignore_index=True)
    dados["CD_CONTA"] = dados["CD_CONTA"].astype(str).str.strip()
    dados["DS_CONTA"] = dados["DS_CONTA"].astype(str).str.strip()

    return dados


with st.spinner("Carregando demonstrações financeiras da CVM..."):
    dados = carregar_dados()

# --------------------------------------------------
# TRATAMENTO
# --------------------------------------------------
if dados.empty:
    # Cria uma tabela vazia de DRE CVM para o app não quebrar online
    tabela = pd.DataFrame(columns=["CD_CONTA", "DS_CONTA"] + PERIODOS)
    st.info("💡 **Modo Online:** Os dados padronizados da CVM exigem os arquivos locais. Exibindo abaixo o **DRE Gerencial Completo obtido via API da B3**.")
else:
    tabela = dados.pivot_table(
        index=["CD_CONTA", "DS_CONTA"],
        columns="Periodo",
        values="Valor",
        aggfunc="first",
    ).reset_index()

    for periodo in PERIODOS:
        if periodo not in tabela.columns:
            tabela[periodo] = float("nan")

    tabela = tabela[["CD_CONTA", "DS_CONTA"] + PERIODOS].copy()
    tabela.columns.name = None


tabela = dados.pivot_table(
    index=["CD_CONTA", "DS_CONTA"],
    columns="Periodo",
    values="Valor",
    aggfunc="first",
).reset_index()

for periodo in PERIODOS:
    if periodo not in tabela.columns:
        tabela[periodo] = float("nan")

tabela = tabela[["CD_CONTA", "DS_CONTA"] + PERIODOS].copy()
tabela.columns.name = None

# --------------------------------------------------
# FUNÇÕES AUXILIARES
# --------------------------------------------------
def valor_conta(codigo, periodo):
    linhas = tabela[tabela["CD_CONTA"] == codigo]
    if linhas.empty or periodo not in tabela.columns:
        return None
    valor = linhas.iloc[0][periodo]
    if pd.isna(valor):
        return None
    return float(valor)

def formatar_mil(valor):
    if valor is None:
        return "Sem dado"
    sinal = "-" if valor < 0 else ""
    absoluto = abs(valor)
    if absoluto >= 1_000_000:
        return f"{sinal}R$ {absoluto / 1_000_000:.2f} bi"
    if absoluto >= 1_000:
        return f"{sinal}R$ {absoluto / 1_000:.1f} mi"
    return f"{sinal}R$ {absoluto:.0f} mil"

def serie_conta(codigo, periodos):
    linhas = tabela[tabela["CD_CONTA"] == codigo]
    if linhas.empty:
        return pd.Series(dtype="float64")
    linha = linhas.iloc[0]
    valores = {
        periodo: linha[periodo]
        for periodo in periodos
        if periodo in linha.index and pd.notna(linha[periodo])
    }
    return pd.Series(valores, dtype="float64")

# --------------------------------------------------
# CABEÇALHO
# --------------------------------------------------
st.markdown('<div class="kicker">FINANCIAL INTELLIGENCE</div>', unsafe_allow_html=True)
st.title("B3SA3 | Dashboard Financeiro")
st.markdown(
    '<div class="subtitle">Análise histórica de resultados • Fonte: CVM • Valores originais em R$ mil</div>',
    unsafe_allow_html=True,
)

st.write("")

periodo_selecionado = st.selectbox(
    "Período dos indicadores",
    PERIODOS,
    index=PERIODOS.index("2025"),
)

st.caption("Os cartões mostram o período selecionado. O 1T26 corresponde a janeiro–março e não é diretamente comparável a um ano completo.")

# --------------------------------------------------
# CARTÕES
# --------------------------------------------------
indicadores = [
    ("Receita", "3.01"),
    ("Resultado bruto", "3.03"),
    ("Resultado operacional*", "3.05"),
    ("Lucro líquido", "3.11"),
]

colunas = st.columns(4)

for coluna, (nome, codigo) in zip(colunas, indicadores):
    valor = valor_conta(codigo, periodo_selecionado)
    texto_valor = formatar_mil(valor) if valor is not None else "Sem dado"

    with coluna:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{nome}</div>
                <div class="metric-value">{texto_valor}</div>
                <div class="metric-code">Conta CVM {codigo}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption("*Resultado antes do resultado financeiro e dos tributos, conforme a classificação padronizada da DRE.")

st.write("")
st.divider()

# --------------------------------------------------
# GRÁFICOS
# --------------------------------------------------
st.subheader("Evolução financeira")
st.caption("Comparação anual de 2020 a 2025. O 1T26 fica separado.")

receita = serie_conta("3.01", PERIODOS_ANUAIS)
lucro = serie_conta("3.11", PERIODOS_ANUAIS)
bruto = serie_conta("3.03", PERIODOS_ANUAIS)

col_grafico1, col_grafico2 = st.columns(2)

with col_grafico1:
    st.markdown("#### Receita")
    if not receita.empty:
        grafico_receita = receita.rename("Receita").to_frame()
        grafico_receita.index.name = "Ano"
        st.line_chart(grafico_receita, height=300)
    else:
        st.info("Não há dados de receita para exibir.")

with col_grafico2:
    st.markdown("#### Lucro líquido")
    if not lucro.empty:
        grafico_lucro = lucro.rename("Lucro líquido").to_frame()
        grafico_lucro.index.name = "Ano"
        st.bar_chart(grafico_lucro, height=300)
    else:
        st.info("Não há dados de lucro para exibir.")

st.write("")
st.markdown("#### Comparativo de resultados anuais")

comparativo = pd.DataFrame({
    "Receita": receita,
    "Resultado bruto": bruto,
    "Lucro líquido": lucro,
})
comparativo.index.name = "Ano"
comparativo = comparativo.dropna(how="all")

if not comparativo.empty:
    st.dataframe(
        comparativo,
        use_container_width=True,
        column_config={
            coluna: st.column_config.NumberColumn(coluna, format="localized")
            for coluna in comparativo.columns
        },
    )

st.divider()

# --------------------------------------------------
# TABELA HISTÓRICA CVM
# --------------------------------------------------
st.subheader("Demonstração de resultado — histórico completo (CVM)")
st.caption("Valores em R$ mil. Células vazias indicam que a conta não possui valor disponível naquele período.")

busca = st.text_input(
    "Pesquisar conta ou código",
    placeholder="Ex.: receita, despesas, pessoal, 3.01...",
)

visual = tabela.rename(columns={
    "CD_CONTA": "Código",
    "DS_CONTA": "Descrição",
}).copy()

if busca:
    mascara = (
        visual["Código"].astype(str).str.contains(busca, case=False, na=False)
        | visual["Descrição"].astype(str).str.contains(busca, case=False, na=False)
    )
    visual = visual[mascara]

st.dataframe(
    visual,
    use_container_width=True,
    hide_index=True,
    height=400,
    column_config={
        "Código": st.column_config.TextColumn("Código", width="small"),
        "Descrição": st.column_config.TextColumn("Descrição", width="large"),
        **{
            periodo: st.column_config.NumberColumn(
                periodo,
                format="localized",
                help="Valor reportado pela CVM, em R$ mil.",
            )
            for periodo in PERIODOS
        },
    },
)

csv = visual.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
st.download_button(
    "⬇️ Exportar tabela CVM para Excel (CSV)",
    data=csv,
    file_name="B3SA3_DRE_CVM.csv",
    mime="text/csv",
)

st.divider()

# --------------------------------------------------
# DRE GERENCIAL COMPLETO (B3 - API RI)
# --------------------------------------------------
st.subheader("DRE Gerencial Completo — B3 (API RI)")
st.caption("Detalhamento completo (Receitas, Despesas, EBITDA, Ajustes, Hedge) obtido diretamente da planilha de resultados da B3 (Aba 'IS (New Seg)'). Valores em R$ mil.")

df_b3_raw = carregar_dados_b3()

if df_b3_raw is not None:
    colunas_validas = [0]
    nomes_colunas = ["Conta / Indicador"]
    
    for col in range(2, df_b3_raw.shape[1]):
        val_ano = str(df_b3_raw.iloc[1, col]).strip()
        val_trim = str(df_b3_raw.iloc[2, col]).strip()
        
        rotulo = val_trim if val_trim != "nan" and val_trim != "" else val_ano
        if rotulo != "nan" and rotulo != "":
            colunas_validas.append(col)
            nomes_colunas.append(rotulo)

    # Pega da linha 3 até o final
    df_gerencial = df_b3_raw.iloc[3:, colunas_validas].copy()
    df_gerencial.columns = nomes_colunas
    df_gerencial = df_gerencial.dropna(subset=["Conta / Indicador"])
    
    # Converte todas as colunas de valores para string/objeto para evitar erro do Arrow no Streamlit
    for c in df_gerencial.columns[1:]:
        df_gerencial[c] = df_gerencial[c].astype(str).str.replace('nan', '')

    # Campo de busca para filtrar rapidamente
    busca_b3 = st.text_input(
        "Pesquisar no DRE Gerencial da B3",
        placeholder="Ex.: EBITDA, Despesas, Lucro recorrente, Mercados...",
        key="busca_b3"
    )

    if busca_b3:
        mascara_b3 = df_gerencial["Conta / Indicador"].astype(str).str.contains(busca_b3, case=False, na=False)
        df_gerencial = df_gerencial[mascara_b3]

    st.dataframe(
        df_gerencial,
        use_container_width=True,
        hide_index=True,
        height=550,
    )

    csv_b3 = df_gerencial.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar DRE Gerencial B3 para CSV",
        data=csv_b3,
        file_name="B3SA3_DRE_Gerencial_Completo_B3.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Não foi possível carregar os dados gerenciais da B3 no momento (verifique a conexão com a API de RI).")
