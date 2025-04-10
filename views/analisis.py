import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_turismo_data

# Configurar la página de análisis
def show():
    st.title("📈 Análisis Exploratorio de Datos Turísticos")

    # Cargar datos
    df = load_turismo_data()

    # Sidebar con filtros
    with st.sidebar:
        st.header("🔍 Filtros de Análisis")

        selected_dept = st.multiselect(
            "Departamentos:",
            options=df['Departamento'].unique(),
            default=df['Departamento'].unique()[:3]
        )

        selected_dest = st.multiselect(
            "Tipo de Destino:",
            options=df['Destino'].unique(),
            default=df['Destino'].unique()
        )

        temp_range = st.slider(
            "Rango de Visitantes:",
            min_value=int(df['Visitantes'].min()),
            max_value=int(df['Visitantes'].max()),
            value=(1000, 10000)
        )

    # Aplicar filtros
    filtered_df = df[
        (df['Departamento'].isin(selected_dept)) &
        (df['Destino'].isin(selected_dest)) &
        (df['Visitantes'].between(*temp_range))
    ]

    # Tabs para organización
    tab1, tab2, tab3, tab4 = st.tabs(["Distribución", "Comparación", "Tendencias", "Conclusiones"])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            heatmap_fig = px.density_heatmap(
                filtered_df,
                x='Departamento',
                y='Destino',
                z='Visitantes',
                histfunc="avg",
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(heatmap_fig, use_container_width=True)

        with col2:
            violin_fig = px.violin(
                filtered_df,
                y='Visitantes',
                x='Temporada',
                color='Temporada',
                box=True,
                points="all"
            )
            st.plotly_chart(violin_fig, use_container_width=True)

        # Conclusión dinámica
        st.markdown("""
        ### 📌 Conclusiones 
        """)
        if not filtered_df.empty:
            top_cross = filtered_df.groupby(['Departamento', 'Destino'])['Visitantes'].mean().idxmax()
            st.markdown(f"- El cruce con mayor promedio de visitantes es **{top_cross[1]}** en **{top_cross[0]}**.")
            top_temp = filtered_df.groupby('Temporada')['Visitantes'].median().idxmax()
            st.markdown(f"- La temporada con mediana de visitantes más alta es **{top_temp}**.")

            # Resumen general adicional
            st.markdown("""
            ### 📊 Resumen General del Dataset Filtrado
            """)
            st.markdown(f"- Total de registros filtrados: **{len(filtered_df)}**")
            st.markdown(f"- Departamentos seleccionados: **{filtered_df['Departamento'].nunique()}**")
            st.markdown(f"- Tipos de destino seleccionados: **{filtered_df['Destino'].nunique()}**")
            st.markdown(f"- Promedio general de visitantes: **{filtered_df['Visitantes'].mean():,.0f}**")
            st.markdown(f"- Temporadas distintas: **{filtered_df['Temporada'].nunique()}**")
        else:
            st.warning("No hay datos disponibles con los filtros seleccionados.")

    with tab2:
        radar_data = filtered_df.groupby(['Departamento', 'Temporada'])['Visitantes'].mean().reset_index()

        radar_fig = go.Figure()

        for dept in radar_data['Departamento'].unique():
            dept_data = radar_data[radar_data['Departamento'] == dept]
            radar_fig.add_trace(go.Scatterpolar(
                r=dept_data['Visitantes'],
                theta=dept_data['Temporada'],
                fill='toself',
                name=dept
            ))

        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True
        )
        st.plotly_chart(radar_fig, use_container_width=True)

        # Conclusión dinámica
        st.markdown("""
        ### 📌 Conclusiones 
        """)
        if not radar_data.empty:
            top_radar = radar_data.groupby('Departamento')['Visitantes'].mean().idxmax()
            st.markdown(f"- El departamento con mayor promedio general en todas las temporadas es **{top_radar}**.")
        else:
            st.warning("No hay datos suficientes para mostrar comparaciones.")

    with tab3:
        time_series = filtered_df.groupby('Temporada')['Visitantes'].sum().reset_index()

        trend_fig = px.area(
            time_series,
            x='Temporada',
            y='Visitantes',
            markers=True,
            title="Evolución por Temporada Turística"
        )
        st.plotly_chart(trend_fig, use_container_width=True)

    with tab4:
        st.subheader("📌 Conclusiones Dinámicas")
        st.markdown("### Resumen según filtros aplicados")
        total_v = filtered_df['Visitantes'].sum()
        top_dept = filtered_df.groupby('Departamento')['Visitantes'].sum().idxmax()
        top_dest = filtered_df.groupby('Destino')['Visitantes'].sum().idxmax()
        top_season = filtered_df.groupby('Temporada')['Visitantes'].sum().idxmax()

        st.markdown(f"- Se registraron **{total_v:,}** visitantes bajo los filtros actuales.")
        st.markdown(f"- El departamento con mayor flujo turístico es **{top_dept}**.")
        st.markdown(f"- El destino más concurrido es **{top_dest}**.")
        st.markdown(f"- La temporada con más visitas es **{top_season}**.")

        if total_v < 5000:
            st.info("Los filtros actuales muestran un volumen de visitas relativamente bajo. Considera ampliarlos para obtener análisis más robustos.")
        elif total_v > 50000:
            st.success("¡Excelente! Tienes una buena cantidad de datos para explorar patrones significativos.")
