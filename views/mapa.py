import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from utils.data_loader import load_turismo_data

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
            df['Departamento'].unique(), 
            default=df['Departamento'].unique()
        )
        selected_dest = st.multiselect(
            "Tipos de Destino:", 
            df['Destino'].unique(), 
            default=df['Destino'].unique()
        )
        selected_temp = st.multiselect(
            "Temporadas:", 
            df['Temporada'].unique(), 
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

    # Configuración del mapa (coordenadas centradas en Colombia)
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5.5, tiles="CartoDB positron")
    marker_cluster = MarkerCluster().add_to(m)

    # Lista para almacenar ubicaciones
    ubicaciones_info = []
    
    # Añadir marcadores
    max_visitantes = filtered_df['Visitantes'].max()
    for _, row in filtered_df.iterrows():
        popup_text = f"""
        <b>Departamento:</b> {row['Departamento']}<br>
        <b>Destino:</b> {row['Destino']}<br>
        <b>Temporada:</b> {row['Temporada']}<br>
        <b>Visitantes:</b> {int(row['Visitantes']):,}
        """
        radio = 4 + (row['Visitantes'] / max_visitantes) * 10
        color = COLOR_TEMPORADA[row['Temporada']]

        marker = folium.CircleMarker(
            location=[row['Latitud'], row['Longitud']],
            radius=radio,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=row['Destino']
        ).add_to(marker_cluster)

        ubicaciones_info.append({
            "lat": row['Latitud'],
            "lon": row['Longitud'],
            "departamento": row['Departamento']
        })

    # Control de capas
    folium.LayerControl().add_to(m)

    # Mostrar mapa
    st.subheader("Mapa de destinos turísticos")
    map_data = st_folium(m, width=1150, height=600, returned_objects=["last_object_clicked"])

    # Leyenda visual
    st.markdown("""
        <style>
        .legend {
            display: flex;
            gap: 20px;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.9);  /* Fondo blanco semi-transparente */
            border-radius: 5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            border: 1px solid #e6e6e6;  /* Borde sutil */
        }
        .legend-item span {
            color: #333333;  /* Texto oscuro */
            font-size: 0.9em;
            text-shadow: 0 1px 1px rgba(255, 255, 255, 0.7); /* Sombra para mejor lectura */
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 1px solid rgba(0, 0, 0, 0.1);  /* Borde para contraste */
        }
        </style>
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background:#FF5733;"></div>
                <span>Temporada Alta</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:#33C1FF;"></div>
                <span>Temporada Media</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background:#75FF33;"></div>
                <span>Temporada Baja</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Gestión de selección múltiple
    if "multi_selection" not in st.session_state:
        st.session_state.multi_selection = []
        st.session_state.ctrl_mode = False

    if map_data and map_data.get("last_object_clicked"):
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]

        for info in ubicaciones_info:
            if abs(info["lat"] - clicked_lat) < 0.01 and abs(info["lon"] - clicked_lon) < 0.01:
                depto = info["departamento"]
                if st.session_state.ctrl_mode:
                    if depto not in st.session_state.multi_selection:
                        st.session_state.multi_selection.append(depto)
                else:
                    st.session_state.multi_selection = [depto]
                break

    # Controles de selección
    col1, col2 = st.columns([1, 4])
    with col1:
        st.session_state.ctrl_mode = st.checkbox(
            "✅ Modo multiselección",
            help="Mantén presionado Ctrl para seleccionar múltiples departamentos",
            value=st.session_state.ctrl_mode
        )
        if st.button("🔄 Limpiar selección"):
            st.session_state.multi_selection = []

    # Mostrar datos
    if st.session_state.multi_selection:
        st.markdown(f"### 📍 Departamentos seleccionados: {', '.join(st.session_state.multi_selection)}")
        df_seleccion = filtered_df[filtered_df['Departamento'].isin(st.session_state.multi_selection)]
    else:
        st.markdown("### 📍 Todos los destinos filtrados")
        df_seleccion = filtered_df
    
    st.dataframe(
        df_seleccion,
        use_container_width=True,
        column_order=["Departamento", "Destino", "Temporada", "Visitantes"],
        hide_index=True
    )

    # Resumen estadístico
    st.markdown("### 📊 Resumen Estadístico")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registros", len(filtered_df))
    with col2:
        st.metric("Departamentos Únicos", filtered_df['Departamento'].nunique())
    with col3:
        st.metric("Máx. Visitantes", f"{int(filtered_df['Visitantes'].max()):,}")

if __name__ == "__main__":
    show()

