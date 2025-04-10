import streamlit as st
from streamlit_option_menu import option_menu
import base64

from views import home, analisis, mapa, reportes


# Configuración
def setup_config():
    return {
        "page_title": "Analítica Turística Colombia",
        "page_icon": "🌴",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }

CUSTOM_CSS = """
<style>
:root { --primary-color: #2A5C7D; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2A5C7D 0%, #1E3A5A 100%);
    color: white;
}

.stButton>button { transition: all 0.3s ease; }
.metric-card { box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
</style>
"""

def main():
    st.set_page_config(**setup_config())
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    with st.sidebar:
        # Logo
        logo = "static/images/logo_turismo.jpg"
        with open(logo, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div style="text-align:center; margin:20px 0;">'
            f'<img src="data:image/png;base64,{logo_data}" width="75%">'
            f'</div>', 
            unsafe_allow_html=True
        )

        selected = option_menu(
            menu_title=None,
            options=["Inicio", "Análisis", "Mapa", "Reportes"],
            icons=["house", "bar-chart", "geo-alt", "file-text"],
            styles={
                "nav-link": {"font-size": "16px", "margin": "8px 0"},
                "nav-link-selected": {"background-color": "#F35B5B"}
            }
        )

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#888; padding:10px">
            <p>Desarrollado por Sara Guerra</p>
            <p>v1.0 | 2024</p>
        </div>
        """, unsafe_allow_html=True)

    # Contenido principal
    if selected == "Inicio":
        home.show()
    elif selected == "Análisis":
        analisis.show()
    elif selected == "Mapa":
        mapa.show()
    elif selected == "Reportes":
        reportes.show()

if __name__ == "__main__":
    main()
