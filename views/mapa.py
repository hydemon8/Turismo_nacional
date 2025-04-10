import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, FeatureGroupSubGroup
from utils.data_loader import load_turismo_data


# Paleta de colores por temporada
COLOR_TEMPORADA = {
    "Alta": "#FF5733",
    "Media": "#33C1FF",
    "Baja": "#75FF33"
}

def show():
    st.title("🌍 Mapa Interactivo de Turismo en Colombia")

    # Cargar datos
    df = load_turismo_data()

    # Filtros laterales
    with st.sidebar:
        st.header("🔍 Filtros del Mapa")

        selected_dept = st.multiselect(
            "Departamentos:",
            options=df['Departamento'].unique(),
            default=df['Departamento'].unique()
        )

        selected_dest = st.multiselect(
            "Tipos de Destino:",
            options=df['Destino'].unique(),
            default=df['Destino'].unique()
        )

        selected_temp = st.multiselect(
            "Temporadas:",
            options=df['Temporada'].unique(),
            default=df['Temporada'].unique()
        )

    # Filtrar datos
    filtered_df = df[
        (df['Departamento'].isin(selected_dept)) &
        (df['Destino'].isin(selected_dest)) &
        (df['Temporada'].isin(selected_temp))
    ]

    if filtered_df.empty:
        st.warning("⚠️ No hay datos disponibles con los filtros actuales.")
        return

    # Crear mapa base centrado en Colombia
    center_lat = filtered_df['Latitud'].mean()
    center_lon = filtered_df['Longitud'].mean()
    map_col = folium.Map(location=[center_lat, center_lon], zoom_start=5.5, tiles="CartoDB positron")

    # Agrupador de marcadores principal
    marker_cluster = MarkerCluster().add_to(map_col)

    # Crear capas por temporada
    capas = {}
    for temporada in sorted(filtered_df['Temporada'].unique()):
        capa = folium.FeatureGroup(name=f"Temporada {temporada}", show=True)
        capas[temporada] = capa
        map_col.add_child(capa)

    # Guardar ubicaciones para interacción múltiple
    ubicaciones_info = []

    # Añadir marcadores con agrupamiento y capas
    max_visitantes = filtered_df['Visitantes'].max()
    for _, row in filtered_df.iterrows():
        popup_text = f"""
        <b>Departamento:</b> {row['Departamento']}<br>
        <b>Destino:</b> {row['Destino']}<br>
        <b>Temporada:</b> {row['Temporada']}<br>
        <b>Visitantes:</b> {int(row['Visitantes']):,}
        """
        radio = 4 + (row['Visitantes'] / max_visitantes) * 10
        color = COLOR_TEMPORADA.get(row['Temporada'], "#2A5C7D")

        marker = folium.CircleMarker(
            location=[row['Latitud'], row['Longitud']],
            radius=radio,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=row['Destino']
        )
        capas[row['Temporada']].add_child(marker)

        ubicaciones_info.append({
            "lat": row['Latitud'],
            "lon": row['Longitud'],
            "departamento": row['Departamento']
        })

    # Añadir control de capas
    folium.LayerControl(collapsed=False).add_to(map_col)

    # Mostrar el mapa interactivo con clics
    st.subheader("Mapa de destinos turísticos")
    map_data = st_folium(map_col, width=1150, height=600, returned_objects=["last_object_clicked"])

    # Leyenda visual
    st.markdown("""
    <style>
    .legend {
        display: flex;
        gap: 20px;
        margin-top: 10px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .legend-color {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        display: inline-block;
    }
    </style>
    <div class="legend">
        <div class="legend-item"><span class="legend-color" style="background:#FF5733;"></span>Alta</div>
        <div class="legend-item"><span class="legend-color" style="background:#33C1FF;"></span>Media</div>
        <div class="legend-item"><span class="legend-color" style="background:#75FF33;"></span>Baja</div>
    </div>
    """, unsafe_allow_html=True)

    # Selección múltiple con control: mantener puntos al hacer Ctrl + clic
    if "multi_selection" not in st.session_state:
        st.session_state.multi_selection = []
        st.session_state.ctrl_mode = False

    if map_data and map_data.get("last_object_clicked"):
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        # Determinar departamento del punto clickeado
        for info in ubicaciones_info:
            if abs(info["lat"] - clicked_lat) < 0.01 and abs(info["lon"] - clicked_lon) < 0.01:
                depto = info["departamento"]
                if st.session_state.ctrl_mode:
                    if depto not in st.session_state.multi_selection:
                        st.session_state.multi_selection.append(depto)
                else:
                    st.session_state.multi_selection = [depto]
                break

    col1, col2 = st.columns([1, 4])
    with col1:
        st.session_state.ctrl_mode = st.checkbox("✅ Modo multiselección (Ctrl)", value=st.session_state.ctrl_mode)
        if st.button("🔄 Limpiar selección"):
            st.session_state.multi_selection = []

    if st.session_state.multi_selection:
        st.markdown(f"### 📍 Departamentos seleccionados: {', '.join(st.session_state.multi_selection)}")
        df_deptos = filtered_df[filtered_df['Departamento'].isin(st.session_state.multi_selection)]
        st.dataframe(df_deptos, use_container_width=True)
    else:
        st.markdown("### 📍 Datos de todos los destinos filtrados:")
        st.dataframe(filtered_df, use_container_width=True)

    # Resumen informativo
    st.markdown("""
    ### 📌 Resumen del Mapa
    """)
    st.markdown(f"- Total de registros mostrados: **{len(filtered_df)}**")
    st.markdown(f"- Departamentos: **{filtered_df['Departamento'].nunique()}**")
    st.markdown(f"- Destinos: **{filtered_df['Destino'].nunique()}**")
    st.markdown(f"- Temporadas en visualización: **{filtered_df['Temporada'].nunique()}**")
    st.markdown(f"- Destino con más visitantes: **{filtered_df.loc[filtered_df['Visitantes'].idxmax(), 'Destino']}**")

if __name__ == "__main__":
    show()

