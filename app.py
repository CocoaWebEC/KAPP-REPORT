import streamlit as st
import pandas as pd
from datetime import datetime

# Función para realizar los cálculos y transformaciones
def transform_data(df, loading_date, origin_warehouse_name, origin_warehouse_code, official_delivery_number, buying_station, product_name):
    # Convertir a numérico y reemplazar NaN con 0
    df['Cantidad de cacao en BABA en quintales'] = pd.to_numeric(df['Cantidad de cacao en BABA en quintales'], errors='coerce').fillna(0)
    df['Cantidad de cacao SECO entregado en quintales'] = pd.to_numeric(df['Cantidad de cacao SECO entregado en quintales'], errors='coerce').fillna(0)
    
    # ----- Hoja "Loading" -----
    # Cálculos para 'Total Gross Weight (kg)*' y 'Total Net Weight (kg)*'
    df['Total Gross Weight (kg)*'] = (df['Cantidad de cacao en BABA en quintales'] + df['Cantidad de cacao SECO entregado en quintales']) * 45.36
    df['Total Net Weight (kg)*'] = df['Total Gross Weight (kg)*']  # Se asume que el peso neto es igual por ahora

    # Generar datos de la hoja Loading
    loading_data = {
        'Loading Date*': loading_date,
        'Origin Warehouse Name': origin_warehouse_name,
        'Origin Warehouse Code': origin_warehouse_code,
        'Destination Warehouse Name': 'ECUADOR DIRECT',
        'Destination Warehouse Code*': 'DIR',
        'Truck License Plate*': "XX",
        'Driver': "XX",
        'Official Delivery Number*': official_delivery_number,
        'Project': '',
        'Total Number Of Sacks*': (df['Total Gross Weight (kg)*'].sum() / 69).round(0),  # redondeo
        'Total Gross Weight (kg)*': df['Total Gross Weight (kg)*'].sum().round(0),  # redondeo
        'Total Net Weight (kg)*': df['Total Net Weight (kg)*'].sum().round(0),  # redondeo
        'Product*': product_name
    }
    
    loading_df = pd.DataFrame([loading_data])
    
    # ----- Hoja "Buying" -----
    # Cálculo de la columna 'Net Weight (Kg)*' en la hoja Buying
    df['Net Weight (Kg)*'] = (df['Cantidad de cacao en BABA en quintales'] + df['Cantidad de cacao SECO entregado en quintales'] * 45.36)
    
    # Aquí solo redondeamos para la visualización (sin alterar el valor real para cálculos posteriores)
    buying_data = pd.DataFrame({
        'Buying Date*': df['Fechas de entrega (DIA/MES/AÑO)'].apply(lambda x: x.strftime('%Y-%m-%d')),
        'Producer Code*': df['Codigo del Productor'],
        'Producer Name': df['Nombre del Productor'],
        'Buying Station': buying_station,
        'Net Weight (Kg)*': df['Net Weight (Kg)*'].round(0),  # Redondeo para la visualización
        'Number Of Sacks*': '',  # Este campo queda vacío
        'Receipt Number*': df['Numero de comprobante de pago'],
        'Loading Official Delivery Number*': official_delivery_number
    })
    
    return loading_df, buying_data

# ----- Configuración inicial -----
st.set_page_config(page_title="Report Kapp", layout="wide")
st.title("📊 Report Kapp")
st.write("Aplicación para cargar, transformar y visualizar datos de cacao.")

# ----- Panel lateral -----
st.sidebar.header("⚙️ Configuración de entrada")

# Inputs
uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])
origin_warehouse_name = st.sidebar.text_input("Nombre del Almacén de Origen")
origin_warehouse_code = st.sidebar.text_input("Código del Almacén de Origen")
official_delivery_number = st.sidebar.text_input("Número Oficial de Entrega")
buying_station = st.sidebar.text_input("Estación de Compra")
product_name = st.sidebar.text_input("Nombre del Producto")

# Fecha actual
loading_date = datetime.today().strftime('%Y-%m-%d')

st.sidebar.write("---")

# ----- Lógica principal -----
if uploaded_file:
    # Leer archivo Excel
    df = pd.read_excel(uploaded_file)

    # Validar que las columnas necesarias estén presentes
    required_columns = [
        'Nombre del Productor', 'Codigo del Productor', 
        'Cantidad de cacao en BABA en quintales', 'Cantidad de cacao SECO entregado en quintales', 
        'Fechas de entrega (DIA/MES/AÑO)', 'Numero de comprobante de pago'
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Faltan las siguientes columnas: {', '.join(missing_columns)}")
    else:
        # Llamar la función de transformación
        loading_df, buying_df = transform_data(df, loading_date, origin_warehouse_name, origin_warehouse_code, official_delivery_number, buying_station, product_name)

        # Mostrar las tablas generadas
        st.subheader("🔄 Datos transformados")

        # Mostrar las dos hojas
        st.write("### Hoja 'Loading'")
        st.dataframe(loading_df, use_container_width=True)

        st.write("### Hoja 'Buying'")
        st.dataframe(buying_df, use_container_width=True)

        # Generar archivo Excel con ambas hojas
        with pd.ExcelWriter("Reporte_Transformado.xlsx") as writer:
            loading_df.to_excel(writer, sheet_name="Loading", index=False)
            buying_df.to_excel(writer, sheet_name="Buying", index=False)

        # Descargar archivo Excel
        st.download_button(
            label="⬇️ Descargar archivo transformado (Excel)",
            data=open("Reporte_Transformado.xlsx", "rb").read(),
            file_name="Reporte_Transformado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("📁 Sube un archivo Excel desde el panel lateral para comenzar.")
