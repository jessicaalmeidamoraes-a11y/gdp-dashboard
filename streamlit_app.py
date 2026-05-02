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
    valor_formatado = moeda(valor) if tipo == "moeda" else percentual(valor)

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
# FILTROS GLOBAIS
# =========================
st.sidebar.markdown("## 🎯 Filtros")

df_filtrado = df.copy()

if "Nome_cc" in df_filtrado.columns:
    filtro_nome_cc = st.sidebar.multiselect(
        "Nome_cc",
        sorted(df_filtrado["Nome_cc"].dropna().unique())
    )

    if filtro_nome_cc:
        df_filtrado = df_filtrado[df_filtrado["Nome_cc"].isin(filtro_nome_cc)]

if "Desc_grupo" in df_filtrado.columns:
    filtro_desc_grupo = st.sidebar.multiselect(
        "Desc_grupo",
        sorted(df_filtrado["Desc_grupo"].dropna().unique())
    )

    if filtro_desc_grupo:
        df_filtrado = df_filtrado[df_filtrado["Desc_grupo"].isin(filtro_desc_grupo)]

if "Data" in df_filtrado.columns:
    datas = df_filtrado["Data"].dropna()

    if not datas.empty:
        data_inicio = st.sidebar.date_input("Data inicial", datas.min())
        data_fim = st.sidebar.date_input("Data final", datas.max())

        df_filtrado = df_filtrado[
            (df_filtrado["Data"] >= pd.to_datetime(data_inicio)) &
            (df_filtrado["Data"] <= pd.to_datetime(data_fim))
        ]

# daqui pra baixo, tudo usa o mesmo filtro
df_base = df_filtrado.copy()

# =========================
# KPIs
# =========================
orcado = df_base[df_base["Tipo"] == "ORÇADO"]["Valor"].sum()
realizado_real = df_base[df_base["Tipo"] == "REALIZADO"]["Valor"].sum()
realizado_visual = abs(realizado_real)

saldo = orcado + realizado_real
total = df_base["Valor"].sum()

execucao = (realizado_visual / orcado * 100) if orcado != 0 else 0

cor_saldo = "#dc2626" if realizado_visual > orcado else "#16a34a"
cor_exec = "#dc2626" if execucao > 100 else "#2563eb"

if realizado_visual > orcado:
    st.error("⚠️ Realizado maior que o orçado")
else:
    st.success("✅ O realizado está dentro do orçamento")

st.markdown("## 📌 Indicadores principais")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    card("Orçado", orcado, "#2563eb")

with c2:
    card("Realizado", realizado_visual, "#dc2626")

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

grafico_tipo = df_base.groupby("Tipo", as_index=False).agg(
    Valor=("Valor", "sum"),
    Valor_grafico=("Valor_grafico", "sum")
)

grafico_tipo["Valor_formatado"] = grafico_tipo["Valor"].apply(moeda_tooltip)

chart_tipo = alt.Chart(grafico_tipo).mark_bar(
    cornerRadiusTopLeft=6,
    cornerRadiusTopRight=6
).encode(
    x=alt.X("Tipo:N", title="Tipo"),
    y=alt.Y("Valor_grafico:Q", title="Valor"),
    color=alt.Color("Tipo:N", title="Tipo"),
    tooltip=[
        alt.Tooltip("Tipo:N", title="Tipo"),
        alt.Tooltip("Valor_formatado:N", title="Valor")
    ]
)

st.altair_chart(chart_tipo, use_container_width=True)

# =========================
# EVOLUÇÃO MENSAL
# =========================
st.markdown("## 🗓️ Evolução mensal")
st.caption("O gráfico mostra os valores mês a mês. Os cards mostram o total acumulado conforme os filtros aplicados.")

if "Data" in df_base.columns:
    df_mes = df_base.dropna(subset=["Data"]).copy()

    if not df_mes.empty:
        df_mes["Mes"] = df_mes["Data"].dt.to_period("M").astype(str)

        mensal = df_mes.groupby(["Mes", "Tipo"], as_index=False).agg(
            Valor=("Valor", "sum"),
            Valor_grafico=("Valor_grafico", "sum")
        )

        mensal["Valor_formatado"] = mensal["Valor"].apply(moeda_tooltip)

        chart_mes = alt.Chart(mensal).mark_line(point=True).encode(
            x=alt.X("Mes:N", title="Mês"),
            y=alt.Y("Valor_grafico:Q", title="Valor"),
            color=alt.Color("Tipo:N", title="Tipo"),
            tooltip=[
                alt.Tooltip("Mes:N", title="Mês"),
                alt.Tooltip("Tipo:N", title="Tipo"),
                alt.Tooltip("Valor_formatado:N", title="Valor")
            ]
        )

        st.altair_chart(chart_mes, use_container_width=True)

st.divider()

# =========================
# VALOR POR ÁREA
# =========================
if "Area" in df_base.columns:
    st.markdown("## 🏢 Valor por Área")

    area = df_base.groupby(["Area", "Tipo"], as_index=False).agg(
        Valor=("Valor", "sum"),
        Valor_grafico=("Valor_grafico", "sum")
    )

    area["Valor_formatado"] = area["Valor"].apply(moeda_tooltip)

    chart_area = alt.Chart(area).mark_bar().encode(
        x=alt.X("Valor_grafico:Q", title="Valor"),
        y=alt.Y("Area:N", sort="-x", title="Área"),
        color=alt.Color("Tipo:N", title="Tipo"),
        tooltip=[
            alt.Tooltip("Area:N", title="Área"),
            alt.Tooltip("Tipo:N", title="Tipo"),
            alt.Tooltip("Valor_formatado:N", title="Valor")
        ]
    )

    st.altair_chart(chart_area, use_container_width=True)

st.divider()

# =========================
# VISÃO GERENCIAL
# =========================
st.markdown("## 📋 Visão Gerencial")

pivot = df_base.pivot_table(
    index=["Tipo", "Area", "Conta", "Nome_conta"],
    values="Valor",
    aggfunc="sum"
).reset_index()

pivot["Valor"] = pivot["Valor"].apply(moeda_tooltip)

st.dataframe(
    pivot,
    use_container_width=True,
    hide_index=True
)

# =========================
# BASE COMPLETA
# =========================
with st.expander("🔎 Base completa"):
    df_exibir = df_base.copy()
    df_exibir["Valor"] = df_exibir["Valor"].apply(moeda_tooltip)

    st.dataframe(
        df_exibir,
        use_container_width=True,
        hide_index=True
    )
