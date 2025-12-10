import streamlit as st
import pandas as pd

# ----- Configuración inicial -----
st.set_page_config(page_title="Report Kapp", layout="wide")

st.title("📊 Report Kapp")
st.write("Aplicación de carga, transformación y visualización de datos.")

# ----- Panel lateral -----
st.sidebar.header("⚙️ Configuración de entrada")

# Subir archivo Excel
uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo Excel",
    type=["xlsx", "xls"]
)

# Código alfanumérico
codigo = st.sidebar.text_input("Código alfanumérico")

# Fecha
fecha = st.sidebar.date_input("Fecha")

st.sidebar.write("---")

# ----- Lógica principal -----
if uploaded_file:
    # Leer archivo
    df = pd.read_excel(uploaded_file)

    st.subheader("📥 Archivo original")
    st.dataframe(df, use_container_width=True)

    # ----- Ejemplo de transformación -----
    # (Luego podemos personalizarla con tus reglas reales)
    df_transformada = df.copy()
    df_transformada["codigo_ingresado"] = codigo
    df_transformada["fecha_ingresada"] = fecha

    # Ejemplo: agregar un índice o transformar columnas
    df_transformada["row_id"] = range(1, len(df) + 1)

    st.subheader("🔄 Datos transformados")
    st.dataframe(df_transformada, use_container_width=True)

    # Descargar archivo transformado
    output_excel = df_transformada.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar archivo transformado (CSV)",
        data=output_excel,
        file_name="reporte_transformado.csv",
        mime="text/csv"
    )

else:
    st.info("📁 Sube un archivo Excel desde el panel lateral para comenzar.")
