import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Dashboard Financeiro",
    layout="wide"
)

# =========================
# TOPO CORPORATIVO
# =========================
st.markdown("""
# 📊 Dashboard Financeiro Corporativo
### Análise de Orçado x Realizado
""")

st.caption("Fonte: Base financeira | Atualização via GitHub")

st.divider()

# =========================
# CARREGAR DADOS
# =========================
arquivo = "data/seuarquivo.xlsx"

df = pd.read_excel(arquivo)
df.columns = df.columns.str.strip()

df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
df["Tipo"] = df["Tipo"].astype(str).str.strip()

# =========================
# FILTROS
# =========================
st.sidebar.markdown("## 🎯 Filtros")

for coluna in ["Nome_cc", "Desc_grupo", "Data"]:
    if coluna in df.columns:
        valores = sorted(df[coluna].dropna().unique())
        escolha = st.sidebar.multiselect(coluna, valores)

        if escolha:
            df = df[df[coluna].isin(escolha)]

# =========================
# KPIs
# =========================
orcado = df[df["Tipo"] == "ORÇADO"]["Valor"].sum()
realizado = df[df["Tipo"] == "REALIZADO"]["Valor"].sum()
saldo = orcado + realizado
total = df["Valor"].sum()

st.markdown("## 📌 Indicadores principais")

def moeda(valor):
    return f"R$ {valor:,.0f}".replace(",", ".")

def card(titulo, valor, cor):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {cor}, #111827);
        padding:18px;
        border-radius:18px;
        color:white;
        box-shadow:0 8px 22px rgba(0,0,0,0.18);
        border-left:6px solid rgba(255,255,255,0.6);
        min-height:135px;
    ">
        <div style="font-size:15px; opacity:0.85; margin-bottom:14px;">
            {titulo}
        </div>
        <div style="
            font-size:22px;
            font-weight:800;
            line-height:1.25;
            word-break:break-word;
        ">
            {moeda(valor)}
        </div>
    </div>
    """, unsafe_allow_html=True)

# saldo positivo ou negativo
saldo = orcado + realizado

# cor do saldo: vermelho se realizado passar do orçado
cor_saldo = "#dc2626" if abs(realizado) > orcado else "#16a34a"

c1, c2, c3, c4 = st.columns(4)

with c1:
    card("Orçado", orcado, "#2563eb")

with c2:
    card("Realizado", realizado, "#dc2626")

with c3:
    card("Saldo", saldo, cor_saldo)

with c4:
    card("Total Geral", total, "#374151")
st.divider()

# =========================
# GRÁFICO
# =========================
st.markdown("## 📈 Orçado x Realizado")

grafico = df.groupby("Tipo", as_index=False)["Valor"].sum()

chart = alt.Chart(grafico).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
    x=alt.X("Tipo:N", title="Tipo"),
    y=alt.Y("Valor:Q", title="Valor"),
    color=alt.Color("Tipo:N", legend=None),
    tooltip=["Tipo", "Valor"]
)

st.altair_chart(chart, use_container_width=True)

st.divider()

# =========================
# TABELA GERENCIAL
# =========================
st.markdown("## 📋 Visão Gerencial")

pivot = df.pivot_table(
    index=["Tipo", "Area", "Conta", "Nome_conta"],
    values="Valor",
    aggfunc="sum"
).reset_index()

st.dataframe(
    pivot,
    use_container_width=True,
    hide_index=True
)

# =========================
# BASE DETALHADA
# =========================
with st.expander("🔎 Ver base detalhada"):
    st.dataframe(df, use_container_width=True, hide_index=True)
