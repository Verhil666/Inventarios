import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Sistema de Inventario", layout="wide", page_icon="📦")

# --- ESTILO ---
st.markdown("""
<style>
.main { background-color: #f4f7f6; }
h1 { color: #1e3a8a; font-weight: 800; }
.stButton>button {
    border-radius: 8px;
    background-color: #1e3a8a;
    color: white;
}
.stButton>button:hover {
    background-color: #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# --- ARCHIVO LOCAL ---
ARCHIVO = "inventario.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
        df["Último Inventario"] = pd.to_datetime(df["Último Inventario"]).dt.date
        return df
    else:
        return pd.DataFrame(columns=[
            'Herramienta', 'Marca', 'Descripción', 'Cantidad', 'Último Inventario'
        ])

def guardar_datos(df):
    df.to_csv(ARCHIVO, index=False)
    st.session_state.inventario = df
    st.toast("Cambios guardados", icon="💾")

# --- INIT ---
if 'inventario' not in st.session_state:
    st.session_state.inventario = cargar_datos()

# --- HEADER ---
st.title("📦 Sistema de Inventario")
st.markdown("Controla tu stock de manera simple y rápida.")

# --- MÉTRICAS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Productos", len(st.session_state.inventario))

with col2:
    st.metric("Stock Total", int(st.session_state.inventario['Cantidad'].sum()) if not st.session_state.inventario.empty else 0)

with col3:
    bajo = st.session_state.inventario[st.session_state.inventario['Cantidad'] < 5].shape[0]
    st.metric("Stock Bajo", bajo)

# --- BUSCADOR ---
busqueda = st.text_input("🔍 Buscar herramienta")

df = st.session_state.inventario.copy()

if busqueda:
    df = df[df['Herramienta'].str.contains(busqueda, case=False, na=False)]

# --- TABLAS ---
st.subheader("Inventario")

df_editado = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Cantidad": st.column_config.NumberColumn(min_value=0, step=1),
        "Último Inventario": st.column_config.DateColumn()
    }
)

# --- GUARDAR ---
if st.button("💾 Guardar cambios"):
    guardar_datos(df_editado)

# --- AGREGAR NUEVO ---
st.subheader("➕ Agregar producto")

with st.form("nuevo"):
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre")
        marca = st.text_input("Marca")
        descripcion = st.text_area("Descripción")

    with col2:
        cantidad = st.number_input("Cantidad", min_value=0, step=1)
        fecha = st.date_input("Fecha", datetime.now())

    submit = st.form_submit_button("Agregar")

    if submit:
        if nombre.strip() == "":
            st.error("El nombre es obligatorio")
        else:
            nueva = pd.DataFrame([{
                "Herramienta": nombre,
                "Marca": marca,
                "Descripción": descripcion,
                "Cantidad": cantidad,
                "Último Inventario": fecha
            }])

            df_total = pd.concat([st.session_state.inventario, nueva], ignore_index=True)
            guardar_datos(df_total)
            st.success("Producto agregado")
            st.rerun()

# --- FOOTER ---
st.divider()
st.caption("Sistema de Inventario | Desarrollado en Streamlit")
