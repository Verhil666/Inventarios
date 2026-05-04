import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Ferretería Pro - Inventario", layout="wide", page_icon="🛠️")

# --- DISEÑO ELEGANTE (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Fondo y fuente */
    .main { background-color: #f4f7f6; }
    .stApp { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Encabezados */
    h1 { color: #1e3a8a; font-weight: 800; }
    
    /* Botones y inputs */
    .stButton>button {
        border-radius: 8px;
        background-color: #1e3a8a;
        color: white;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        border-color: #3b82f6;
    }
    
    /* Tarjetas de métricas */
    [data-testid="stMetricValue"] { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS (BASE DE DATOS EN MEMORIA) ---
if 'inventario' not in st.session_state:
    data = {
        'Herramienta': ['Taladro Percutor', 'Juego de Llaves', 'Esmeriladora'],
        'Marca': ['Dewalt', 'Stanley', 'Bosch'],
        'Descripción': ['20V Max XR Sin Escobillas', '20 piezas acero cromo vanadio', '4-1/2 Pulgadas 750W'],
        'Cantidad': [12, 25, 8],
        'Último Inventario': [datetime.now().date()] * 3
    }
    st.session_state.inventario = pd.DataFrame(data)

# --- FUNCIONES DE CONTROL ---
def guardar_datos(df_actualizado):
    st.session_state.inventario = df_actualizado
    st.toast("¡Cambios guardados con éxito!", icon="💾")

# --- INTERFAZ PRINCIPAL ---
st.title("🛠️ Sistema de Inventario Ferretería")
st.markdown("Gestione sus herramientas, marcas y existencias con precisión.")

# Métricas rápidas
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Herramientas", len(st.session_state.inventario))
with col_m2:
    st.metric("Stock Total", int(st.session_state.inventario['Cantidad'].sum()))
with col_m3:
    bajo_stock = st.session_state.inventario[st.session_state.inventario['Cantidad'] < 5].shape[0]
    st.metric("Alertas Stock Bajo", bajo_stock, delta_color="inverse")

# --- PESTAÑAS ---
tab_visor, tab_nuevo, tab_excel = st.tabs(["📋 Visor y Edición", "➕ Agregar Herramienta", "📥 Exportar / Importar"])

# --- PESTAÑA 1: VISOR Y EDICIÓN (CRUD INTEGRADO) ---
with tab_visor:
    st.subheader("Panel de Control de Stock")
    st.info("💡 **Tips:** Puedes editar directamente en la tabla. Para borrar, selecciona la fila y presiona 'Delete' en tu teclado.")
    
    # Editor de datos potente (Edita y Elimina)
    df_editado = st.data_editor(
        st.session_state.inventario,
        num_rows="dynamic", # Esto permite agregar y borrar filas directamente
        use_container_width=True,
        column_config={
            "Herramienta": st.column_config.TextColumn("Nombre Herramienta", required=True),
            "Marca": st.column_config.SelectboxColumn("Marca", options=["Dewalt", "Makita", "Milwaukee", "Stanley", "Bosch", "Truper", "Otros"]),
            "Cantidad": st.column_config.NumberColumn("Stock", min_value=0, step=1),
            "Último Inventario": st.column_config.DateColumn("Fecha Inventario")
        },
        key="editor_tabla"
    )

    if st.button("💾 Guardar todos los cambios"):
        guardar_datos(df_editado)

# --- PESTAÑA 2: AGREGAR NUEVO ---
with tab_nuevo:
    st.subheader("Registrar Nueva Herramienta")
    with st.container(border=True):
        with st.form("form_nuevo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                h_nombre = st.text_input("Nombre de la Herramienta")
                h_marca = st.selectbox("Marca", ["Dewalt", "Makita", "Milwaukee", "Stanley", "Bosch", "Truper", "Otros"])
                h_desc = st.text_area("Descripción detallada")
            with c2:
                h_cant = st.number_input("Cantidad inicial", min_value=0, step=1)
                h_fecha = st.date_input("Fecha de registro", datetime.now())
            
            submit = st.form_submit_button("✅ Registrar Herramienta")
            
            if submit:
                if h_nombre:
                    nueva_fila = pd.DataFrame([{
                        'Herramienta': h_nombre,
                        'Marca': h_marca,
                        'Descripción': h_desc,
                        'Cantidad': h_cant,
                        'Último Inventario': h_fecha
                    }])
                    st.session_state.inventario = pd.concat([st.session_state.inventario, nueva_fila], ignore_index=True)
                    st.success(f"¡{h_nombre} agregado al inventario!")
                    st.rerun()
                else:
                    st.error("El nombre de la herramienta es obligatorio.")

# --- PESTAÑA 3: EXPORTAR/IMPORTAR (EXCEL) ---
with tab_excel:
    st.subheader("Sincronización con Excel")
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.write("### 📤 Exportar a Excel")
        st.write("Descarga el inventario actual para editarlo externamente.")
        
        # Convertir a Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.inventario.to_excel(writer, index=False, sheet_name='Inventario_Ferreteria')
        
        st.download_button(
            label="📥 Descargar Inventario (.xlsx)",
            data=output.getvalue(),
            file_name=f"inventario_ferreteria_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_der:
        st.write("### 📥 Importar desde Excel")
        archivo_subido = st.file_uploader("Cargar archivo Excel", type=["xlsx"])
        
        if archivo_subido:
            try:
                df_nuevo = pd.read_excel(archivo_subido)
                # Validación básica de columnas
                columnas_req = ['Herramienta', 'Marca', 'Descripción', 'Cantidad', 'Último Inventario']
                if all(col in df_nuevo.columns for col in columnas_req):
                    if st.button("🚀 Reemplazar Inventario Actual"):
                        st.session_state.inventario = df_nuevo
                        st.success("Inventario actualizado desde Excel.")
                        st.rerun()
                else:
                    st.error(f"El archivo debe contener las columnas: {columnas_req}")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

# --- PIE DE PÁGINA ---
st.divider()
st.caption(f"© {datetime.now().year} Ferretería Pro Dashboard | Control de Inventario Digital")