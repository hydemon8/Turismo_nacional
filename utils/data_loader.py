import pandas as pd
import streamlit as st

@st.cache_data  # Decorador de caché de Streamlit
def load_turismo_data():
    """Carga el dataset de turismo desde un CSV"""
    try:
        df = pd.read_csv("turismo_nacional.csv")
        return df
    except FileNotFoundError:
        st.error("Error: Archivo no encontrado 🚨")
        return pd.DataFrame()