"""
Dashboard en tiempo real para KaliNova
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

class RealTimeDashboard:
    def __init__(self):
        st.set_page_config(page_title="KaliNova Dashboard", layout="wide")
        
    def display_scan_results(self, results: Dict):
        """Mostrar resultados de escaneo en dashboard"""
        st.title("🔍 KaliNova Live Dashboard")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        col1.metric("Vulnerabilidades", len(results.get('vulnerabilities', [])))
        col2.metric("Targets Activos", results.get('active_targets', 0))
        col3.metric("Tiempo Escaneo", f"{results.get('scan_time', 0)}s")
        
        # Gráfico de vulnerabilidades por tipo
        if 'vulnerabilities' in results:
            vuln_df = pd.DataFrame(results['vulnerabilities'])
            fig = px.bar(vuln_df, x='type', title='Vulnerabilidades por Tipo')
            st.plotly_chart(fig)
        
        # Mapa de red en tiempo real
        if 'network_map' in results:
            st.subheader("🌐 Mapa de Red")
            st.graphviz_chart(results['network_map'])