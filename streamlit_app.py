import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Dashboard Financeiro Corporativo",
    layout="wide"
)

# =========================
# CSS
# =========================
st.markdown("""
<style>
.kpi-card {
    padding: 18px;
    border-radius: 18px;
    color: white;
    box-shadow: 0 8px 22px rgba(0,0,0,0.18);
    min-height: 120px;
}

.kpi-title {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 18px;
    font-weight: 800;
    line-height: 1.3;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
def moeda(valor):
    return f"R$ {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def moeda_tooltip(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def percentual(valor):
    return f"{valor:,.1f}%".replace(".", ",")

def card(titulo, valor, cor, tipo="moeda"):
    if tipo == "moeda":
        valor_formatado = moeda(valor)
    else:
        valor_formatado = percentual(valor)

    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg, {cor}, #111827);">
        <div class="kpi-title">{titulo}</div>
        <div class="kpi-value">{valor_formatado}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# TOPO
# =========================
st.markdown("""
# 📊 Dashboard Financeiro Corporativo
### Análise de Orçado x Realizado
""")

st.caption("Fonte: Base financeira | Atualização via GitHub")
st.divider()

# =========================
# DADOS
# =========================
arquivo = "data/seuarquivo.xlsx"

df = pd.read_excel(arquivo)
df.columns = df.columns.str.strip()

df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
df["Tipo"] = df["Tipo"].astype(str).str.strip()

df["Valor_grafico"] = df["Valor"].abs()

if "Data" in df.columns:
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

# =========================
# FILTROS
# =========================
st.sidebar.markdown("## 🎯 Filtros")

if "Nome_cc" in df.columns:
    f1 = st.sidebar.multiselect("Nome_cc", sorted(df["Nome_cc"].dropna().unique()))
    if f1:
        df = df[df["Nome_cc"].isin(f1)]

if "Desc_grupo" in df.columns:
    f2 = st.sidebar.multiselect("Desc_grupo", sorted(df["Desc_grupo"].dropna().unique()))
    if f2:
        df = df[df["Desc_grupo"].isin(f2)]

if "Data" in df.columns:
    datas = df["Data"].dropna()
    if not datas.empty:
        inicio = st.sidebar.date_input("Data inicial", datas.min())
        fim = st.sidebar.date_input("Data final", datas.max())

        df = df[(df["Data"] >= pd.to_datetime(inicio)) &
                (df["Data"] <= pd.to_datetime(fim))]

# =========================
# KPIs
# =========================
orcado = df[df["Tipo"] == "ORÇADO"]["Valor"].sum()
realizado_real = df[df["Tipo"] == "REALIZADO"]["Valor"].sum()
realizado = abs(realizado_real)

saldo = orcado + realizado_real
total = df["Valor"].sum()

execucao = (realizado / orcado * 100) if orcado != 0 else 0

cor_saldo = "#dc2626" if realizado > orcado else "#16a34a"
cor_exec = "#dc2626" if execucao > 100 else "#2563eb"

# alerta
if realizado > orcado:
    st.error("⚠️ Realizado maior que o orçado")
else:
    st.success("✅ Dentro do orçamento")

st.markdown("## 📌 Indicadores principais")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    card("Orçado", orcado, "#2563eb")

with c2:
    card("Realizado", realizado, "#dc2626")

with c3:
    card("Saldo", saldo, cor_saldo)

with c4:
    card("Total Geral", total, "#374151")

with c5:
    card("% Execução", execucao, cor_exec, "percentual")

st.divider()

# =========================
# GRÁFICO ORÇADO X REALIZADO
# =========================
st.markdown("## 📈 Orçado x Realizado")

grafico = df.groupby("Tipo", as_index=False).agg(
    Valor=("Valor", "sum"),
    Valor_grafico=("Valor_grafico", "sum")
)

grafico["Valor_formatado"] = grafico["Valor"].apply(moeda_tooltip)

chart = alt.Chart(grafico).mark_bar().encode(
    x="Tipo:N",
    y="Valor_grafico:Q",
    color="Tipo:N",
    tooltip=[
        alt.Tooltip("Tipo:N"),
        alt.Tooltip("Valor_formatado:N", title="Valor")
    ]
)

st.altair_chart(chart, use_container_width=True)

# =========================
# EVOLUÇÃO MENSAL
# =========================
st.markdown("## 🗓️ Evolução mensal")

if "Data" in df.columns:
    df["Mes"] = df["Data"].dt.to_period("M").astype(str)

    mensal = df.groupby(["Mes", "Tipo"], as_index=False).agg(
        Valor=("Valor", "sum"),
        Valor_grafico=("Valor_grafico", "sum")
    )

    mensal["Valor_formatado"] = mensal["Valor"].apply(moeda_tooltip)

    chart2 = alt.Chart(mensal).mark_line(point=True).encode(
        x="Mes:N",
        y="Valor_grafico:Q",
        color="Tipo:N",
        tooltip=[
            "Mes",
            "Tipo",
            alt.Tooltip("Valor_formatado:N", title="Valor")
        ]
    )

    st.altair_chart(chart2, use_container_width=True)

st.divider()

# =========================
# POR ÁREA
# =========================
if "Area" in df.columns:
    st.markdown("## 🏢 Valor por Área")

    area = df.groupby("Area", as_index=False).agg(
        Valor=("Valor", "sum"),
        Valor_grafico=("Valor_grafico", "sum")
    )

    area["Valor_formatado"] = area["Valor"].apply(moeda_tooltip)

    chart3 = alt.Chart(area).mark_bar().encode(
        x="Valor_grafico:Q",
        y=alt.Y("Area:N", sort="-x"),
        tooltip=[
            "Area",
            alt.Tooltip("Valor_formatado:N", title="Valor")
        ]
    )

    st.altair_chart(chart3, use_container_width=True)

st.divider()

# =========================
# TABELA
# =========================
st.markdown("## 📋 Visão Gerencial")

pivot = df.pivot_table(
    index=["Tipo", "Area", "Conta", "Nome_conta"],
    values="Valor",
    aggfunc="sum"
).reset_index()

st.dataframe(pivot, use_container_width=True, hide_index=True)

# =========================
# BASE
# =========================
with st.expander("🔎 Base completa"):
    st.dataframe(df, use_container_width=True, hide_index=True)
