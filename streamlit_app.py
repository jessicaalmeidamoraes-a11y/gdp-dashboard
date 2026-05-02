import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Dashboard Financeiro Corporativo",
    layout="wide"
)

st.markdown("""
# 📊 Dashboard Financeiro Corporativo
### Análise de Orçado x Realizado
""")

st.caption("Fonte: Base financeira | Atualização via GitHub")
st.divider()

arquivo = "data/seuarquivo.xlsx"

df = pd.read_excel(arquivo)
df.columns = df.columns.str.strip()

df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
df["Tipo"] = df["Tipo"].astype(str).str.strip()

if "Data" in df.columns:
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

# =========================
# FILTROS
# =========================
st.sidebar.markdown("## 🎯 Filtros")

for coluna in ["Nome_cc", "Desc_grupo", "Data"]:
    if coluna in df.columns:
        if coluna == "Data":
            datas = df["Data"].dropna()
            if not datas.empty:
                data_inicio = st.sidebar.date_input("Data inicial", datas.min())
                data_fim = st.sidebar.date_input("Data final", datas.max())

                df = df[
                    (df["Data"] >= pd.to_datetime(data_inicio)) &
                    (df["Data"] <= pd.to_datetime(data_fim))
                ]
        else:
            valores = sorted(df[coluna].dropna().unique())
            escolha = st.sidebar.multiselect(coluna, valores)

            if escolha:
                df = df[df[coluna].isin(escolha)]

# =========================
# CÁLCULOS
# =========================
orcado = df[df["Tipo"] == "ORÇADO"]["Valor"].sum()
realizado = df[df["Tipo"] == "REALIZADO"]["Valor"].sum()
saldo = orcado + realizado
total = df["Valor"].sum()

percentual_execucao = (abs(realizado) / orcado * 100) if orcado != 0 else 0

cor_saldo = "#dc2626" if abs(realizado) > orcado else "#16a34a"
cor_execucao = "#dc2626" if percentual_execucao > 100 else "#2563eb"

def moeda(valor):
    return f"R$ {valor:,.0f}".replace(",", ".")

def percentual(valor):
    return f"{valor:,.1f}%".replace(".", ",")

def card(titulo, valor, cor, tipo="moeda"):
    valor_formatado = moeda(valor) if tipo == "moeda" else percentual(valor)

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
        font-size:24px;
font-weight:800;
line-height:1.2;
white-space:normal;
overflow-wrap:break-word;
        ">
            {valor_formatado}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# ALERTA
# =========================
if abs(realizado) > orcado:
    st.error("⚠️ Atenção: o realizado está maior que o orçado.")
else:
    st.success("✅ O realizado está dentro do orçamento.")

# =========================
# KPIs
# =========================
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
    card("% Execução", percentual_execucao, cor_execucao, tipo="percentual")

st.divider()

# =========================
# GRÁFICO TIPO
# =========================
st.markdown("## 📈 Orçado x Realizado")

grafico_tipo = df.groupby("Tipo", as_index=False)["Valor"].sum()

chart_tipo = alt.Chart(grafico_tipo).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x=alt.X("Tipo:N", title="Tipo"),
    y=alt.Y("Valor:Q", title="Valor"),
    color=alt.Color("Tipo:N", legend=None),
    tooltip=["Tipo", "Valor"]
)

st.altair_chart(chart_tipo, use_container_width=True)

# =========================
# GRÁFICOS AVANÇADOS
# =========================
g1, g2 = st.columns(2)

with g1:
    st.markdown("## 🏢 Valor por Área")

    if "Area" in df.columns:
        grafico_area = df.groupby("Area", as_index=False)["Valor"].sum()
        grafico_area = grafico_area.sort_values("Valor", ascending=False)

        chart_area = alt.Chart(grafico_area).mark_bar().encode(
            x=alt.X("Valor:Q", title="Valor"),
            y=alt.Y("Area:N", sort="-x", title="Área"),
            tooltip=["Area", "Valor"]
        )

        st.altair_chart(chart_area, use_container_width=True)

with g2:
    st.markdown("## 🗓️ Evolução mensal")

    if "Data" in df.columns:
        df_mes = df.dropna(subset=["Data"]).copy()
        df_mes["Mes"] = df_mes["Data"].dt.to_period("M").astype(str)

        grafico_mes = df_mes.groupby(["Mes", "Tipo"], as_index=False)["Valor"].sum()

        chart_mes = alt.Chart(grafico_mes).mark_line(point=True).encode(
            x=alt.X("Mes:N", title="Mês"),
            y=alt.Y("Valor:Q", title="Valor"),
            color="Tipo:N",
            tooltip=["Mes", "Tipo", "Valor"]
        )

        st.altair_chart(chart_mes, use_container_width=True)

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
