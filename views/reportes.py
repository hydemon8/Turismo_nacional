import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_turismo_data

# Cargar los datos
@st.cache_data
def cargar_datos():
    return load_turismo_data()

def show():
    st.title("📄 Reportes Dinámicos por Departamento")
    df = cargar_datos()

    st.markdown("""
    Explora los datos turísticos filtrando por **departamento**.  
    Los reportes incluyen estadísticas, gráficos y tablas detalladas con los registros correspondientes.
    """)

    st.markdown("---")

    # Filtros dinámicos
    deptos = sorted(df['Departamento'].dropna().unique())
    depto_sel = st.selectbox("Selecciona un Departamento", deptos)

    # Filtrar por departamento
    df_filtrado = df[df["Departamento"] == depto_sel]

    st.markdown(f"### 🔍 {len(df_filtrado)} registros encontrados en {depto_sel}")

    # Métricas básicas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Visitantes", int(df_filtrado["Visitantes"].sum()))
    with col2:
        st.metric("Promedio por registro", int(df_filtrado["Visitantes"].mean()))

    st.markdown("---")

    # Gráfico de barras por destino
    if not df_filtrado.empty:
        st.subheader("📊 Visitantes por Destino")
        fig = px.bar(df_filtrado, x="Destino", y="Visitantes", title=f"Visitantes por destino en {depto_sel}",
                     labels={"destino": "Destino", "visitantes": "Número de Visitantes"})
        st.plotly_chart(fig, use_container_width=True)

        # Mostrar tabla
        st.subheader("📋 Detalle de registros")
        st.dataframe(df_filtrado.sort_values("Visitantes", ascending=False), use_container_width=True)
    else:
        st.warning("No hay datos para los filtros seleccionados.")
