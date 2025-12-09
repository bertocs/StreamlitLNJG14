# app_lnj_g4.py

import pandas as pd
import streamlit as st
import plotly.express as px
import os

# ----------------------------------
# CONFIGURACIÓN BÁSICA
# ----------------------------------
st.set_page_config(
    page_title="LNJ G4 - Dashboard",
    layout="wide"
)

EXCEL_PATH = "matriz_lnj_g14.xlsx"  # si el script está en la misma carpeta que el Excel
SHEET_STATS = "estadisticas"        # nombre de la hoja con las variables


# ----------------------------------
# CARGA DE DATOS
# ----------------------------------
@st.cache_data
def load_stats(path: str, sheet_name: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encuentra el archivo: {path}")
    df = pd.read_excel(path, sheet_name=sheet_name)
    # nos aseguramos de que 'equipo' es string
    df["equipo"] = df["equipo"].astype(str)
    return df


try:
    df = load_stats(EXCEL_PATH, SHEET_STATS)
except Exception as e:
    st.error(f"Error cargando el Excel: {e}")
    st.stop()

# ----------------------------------
# SIDEBAR: FILTROS
# ----------------------------------
st.sidebar.title("Filtros")

equipos = sorted(df["equipo"].unique())
equipos_seleccionados = st.sidebar.multiselect(
    "Selecciona equipo(s)",
    options=equipos,
    default=equipos
)

metrica_orden = st.sidebar.selectbox(
    "Métrica para ordenar la clasificación",
    options=[
        "puntos_totales",
        "diferencia_goles",
        "goles_total",
        "goles_recibidos_total",
        "goles_por_partido_total",
    ],
    format_func=lambda x: x.replace("_", " ").capitalize()
)

orden_desc = st.sidebar.checkbox("Orden descendente", value=True)

# Aplicar filtro de equipos
df_filtrado = df[df["equipo"].isin(equipos_seleccionados)].copy()

# Orden principal
df_ordenado = df_filtrado.sort_values(by=metrica_orden, ascending=not orden_desc)


# ----------------------------------
# LAYOUT PRINCIPAL
# ----------------------------------
st.title("Liga Nacional Juvenil G4 — Dashboard de Estadísticas")

st.caption(f"Fuente: matriz de resultados procesada desde lapreferente.com")
st.markdown("---")

# ----------------------------------
# KPIs PRINCIPALES
# ----------------------------------
col1, col2, col3 = st.columns(3)

# Equipo con más puntos
eq_max_puntos = df.loc[df["puntos_totales"].idxmax()]
# Equipo más goleador
eq_max_goles = df.loc[df["goles_total"].idxmax()]
# Mejor diferencia de goles
eq_max_dif = df.loc[df["diferencia_goles"].idxmax()]

with col1:
    st.metric(
        "Equipo con más puntos",
        f'{eq_max_puntos["equipo"]}',
        f'{int(eq_max_puntos["puntos_totales"])} pts'
    )
with col2:
    st.metric(
        "Equipo más goleador",
        f'{eq_max_goles["equipo"]}',
        f'{int(eq_max_goles["goles_total"])} goles'
    )
with col3:
    st.metric(
        "Mejor diferencia de goles",
        f'{eq_max_dif["equipo"]}',
        f'{int(eq_max_dif["diferencia_goles"])} DG'
    )

st.markdown("---")

# ----------------------------------
# CLASIFICACIÓN / TABLA
# ----------------------------------
st.subheader("Clasificación según métrica seleccionada")

# Añadimos posición
df_clasificacion = df_ordenado.copy()
df_clasificacion.insert(0, "posicion", range(1, len(df_clasificacion) + 1))

st.dataframe(
    df_clasificacion[
        [
            "posicion",
            "equipo",
            "puntos_totales",
            "puntos_local",
            "puntos_visitante",
            "victorias_local",
            "victorias_visitante",
            "empates_local",
            "empates_visitante",
            "derrotas_local",
            "derrotas_visitante",
            "goles_total",
            "goles_recibidos_total",
            "diferencia_goles",
            "goles_por_partido_total",
            "goles_recibidos_por_partido_total",
        ]
    ],
    use_container_width=True,
)


# ----------------------------------
# GRÁFICOS
# ----------------------------------
st.markdown("---")
st.subheader("Visualizaciones")

# 1) Barras de puntos totales
st.markdown("### Puntos totales por equipo")
fig_pts = px.bar(
    df_ordenado,
    x="equipo",
    y="puntos_totales",
    text="puntos_totales",
    labels={"equipo": "Equipo", "puntos_totales": "Puntos totales"},
)
fig_pts.update_traces(textposition="outside")
fig_pts.update_layout(xaxis_tickangle=-45, margin=dict(l=20, r=20, t=40, b=120))
st.plotly_chart(fig_pts, use_container_width=True)

# 2) Puntos local vs visitante
st.markdown("### Puntos como local vs visitante")
df_pts_lv = df_filtrado.sort_values("puntos_totales", ascending=False)
fig_lv = px.bar(
    df_pts_lv,
    x="equipo",
    y=["puntos_local", "puntos_visitante"],
    barmode="group",
    labels={
        "equipo": "Equipo",
        "value": "Puntos",
        "variable": "Condición",
    },
)
fig_lv.update_layout(xaxis_tickangle=-45, margin=dict(l=20, r=20, t=40, b=120))
st.plotly_chart(fig_lv, use_container_width=True)

# 3) Goles a favor vs goles en contra
st.markdown("### Perfil ofensivo y defensivo")
fig_goles = px.scatter(
    df_filtrado,
    x="goles_recibidos_total",
    y="goles_total",
    size="puntos_totales",
    hover_name="equipo",
    text="equipo",
    labels={
        "goles_total": "Goles a favor (total)",
        "goles_recibidos_total": "Goles en contra (total)",
        "puntos_totales": "Puntos totales",
    },
)
fig_goles.update_traces(textposition="top center")
fig_goles.update_layout(margin=dict(l=20, r=20, t=40, b=40))
st.plotly_chart(fig_goles, use_container_width=True)

# 4) Goles por partido vs goles recibidos por partido
st.markdown("### Eficiencia por partido")
fig_ratio = px.scatter(
    df_filtrado,
    x="goles_recibidos_por_partido_total",
    y="goles_por_partido_total",
    size="puntos_totales",
    color="diferencia_goles",
    color_continuous_scale="RdYlGn",
    hover_name="equipo",
    labels={
        "goles_por_partido_total": "Goles a favor por partido",
        "goles_recibidos_por_partido_total": "Goles en contra por partido",
        "diferencia_goles": "Dif. de goles",
    },
)
fig_ratio.update_layout(margin=dict(l=20, r=20, t=40, b=40))
st.plotly_chart(fig_ratio, use_container_width=True)
