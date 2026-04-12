import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. Configuración de página
st.set_page_config(page_title="Análisis de Impacto", layout="wide")

# 2. Definir rutas y conectar (ESTO FALTABA)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'data', 'sentimientos.db')

conn = sqlite3.connect(db_path)

# 3. Leer Datos
try:
    df = pd.read_sql_query("SELECT * FROM tweets", conn)
    conn.close()
except Exception as e:
    st.error(f"Error al leer la base de datos: {e}")
    st.stop()

# 4. Separar Original de Respuestas
# Usamos el prefijo que definimos en el main_unitario
original = df[df['tema'].str.contains('Original')]
replies = df[df['tema'].str.contains('Reply')]

st.title("🎯 Impacto de Publicación Específica")

if not original.empty:
    # Bloque del Post Principal (estilo chat)
    with st.container(border=True):
        st.subheader("Post Original Analizado")
        st.info(original.iloc[-1]['texto'])
        st.caption(f"📅 Fecha: {original.iloc[-1]['date']}")
    
    st.divider()
    
    # Métricas de la Audiencia
    if not replies.empty:
        total_r = len(replies)
        # Calculamos sentimientos de las respuestas
        conteo = replies['sentimiento'].value_counts()
        pos_n = conteo.get('Positivo', 0)
        neg_n = conteo.get('Negativo', 0)
        neu_n = conteo.get('Neutral', 0)
        
        pos_p = (pos_n / total_r) * 100
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Comentarios", total_r)
        m2.metric("Positivos", pos_n, delta=f"{pos_p:.1f}%")
        m3.metric("Neutrales", neu_n)
        m4.metric("Negativos", neg_n, delta=f"-{((neg_n/total_r)*100):.1f}%", delta_color="inverse")

        st.write("### visualización de Clima Social")
        c1, c2 = st.columns([2, 1])
        
        with c1:
            color_map = {'Positivo': '#00CC96', 'Neutral': '#636EFA', 'Negativo': '#EF553B'}
            fig = px.pie(replies, names='sentimiento', 
                         title="Distribución de Opinión Pública",
                         color='sentimiento', 
                         color_discrete_map=color_map,
                         hole=0.4) # Lo hace tipo anillo, queda más moderno
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("Muestra de Comentarios")
            st.dataframe(replies[['sentimiento', 'texto']].tail(15), hide_index=True)
    else:
        st.warning("Se encontró el post original pero no hay respuestas registradas aún.")
else:
    st.warning("No hay datos. Corré primero 'python src/main_unitario.py'")