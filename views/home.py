import streamlit as st
import base64

def show():
    st.title("📊 Dashboard de Turismo Nacional")
    st.markdown("---")

    # Mostrar imagen introductoria
    with open("static/images/intro.jpg", "rb") as f:
        img_data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/jpeg;base64,{img_data}" width="85%" style="border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);" />
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Introducción contextual
    st.markdown("""
    Bienvenido al **Dashboard de Turismo Nacional en Colombia** 🇨🇴.  
    Esta aplicación tiene como objetivo visualizar, explorar y analizar los patrones de turismo dentro del territorio colombiano, a partir de datos recopilados en diferentes departamentos del país.

    A través de esta plataforma interactiva podrás:
    - Consultar estadísticas clave sobre el turismo nacional 📈
    - Analizar la distribución geográfica de los visitantes 🗺️
    - Visualizar destinos más visitados 🏖️
    - Explorar reportes generados dinámicamente según tus filtros 🧾
    """)

    st.markdown("---")

    # Métricas clave
    st.subheader("📌 Métricas Generales")
    cols = st.columns(3)
    metrics = [
        ("🚀 Visitantes Totales", "1,007,603"),
        ("📍 Destinos Únicos", "10"),
        ("⏳ Temporada Alta", "Diciembre"),
    ]

    for col, (title, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card">📍<h4>{title}</h4>'
                f'<p style="font-size:24px; color: #2A5C7D;"><strong>{value}</strong></p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")
    
    # Gráfico de tendencia ficticia
    st.subheader("📈 Tendencia de visitantes (Ejemplo)")
    st.line_chart({"Visitantes": [1, 3, 2, 4, 3, 5]}, height=300)

