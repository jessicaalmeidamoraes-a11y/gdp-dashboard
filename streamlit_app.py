import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Dashboard - Gestão Mensal")

arquivo = "Dados/seuarquivo.xlsx"

df = pd.read_excel(arquivo)

df.columns = df.columns.str.strip()

# filtros
st.sidebar.header("Filtros")

for coluna in ["Nome_cc", "Desc_grupo", "Data"]:
    valores = sorted(df[coluna].dropna().unique())
    escolha = st.sidebar.multiselect(coluna, valores)

    if escolha:
        df = df[df[coluna].isin(escolha)]

# valor numérico
df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)

# KPIs
orcado = df[df["Tipo"].str.strip() == "ORÇADO"]["Valor"].sum()
realizado = df[df["Tipo"].str.strip() == "REALIZADO"]["Valor"].sum()
total = df["Valor"].sum()

c1, c2, c3 = st.columns(3)

c1.metric("ORÇADO", f"R$ {orcado:,.2f}")
c2.metric("REALIZADO", f"R$ {realizado:,.2f}")
c3.metric("TOTAL", f"R$ {total:,.2f}")

# tabela
st.subheader("Visão Gerencial")

pivot = df.pivot_table(
    index=["Tipo", "Area", "Conta", "Nome_conta"],
    values="Valor",
    aggfunc="sum"
).reset_index()

st.dataframe(pivot, use_container_width=True)

# gráfico
st.subheader("Orçado x Realizado")

grafico = df.groupby("Tipo")["Valor"].sum().reset_index()

st.bar_chart(grafico, x="Tipo", y="Valor")
