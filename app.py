import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --------- Login Section ---------
def check_login(username, password):
    correct_username = "admin"
    correct_password = "password123"
    if username == correct_username and password == correct_password:
        return True
    else:
        return False

def show_login():
    st.title("Login to Report Kapp")
    username = st.text_input("Username", key="login_username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
    
    if st.button("Login", key="login_button"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Login Successful!")
            return True
        else:
            st.error("Invalid credentials. Please try again.")
            return False
    return False

# Check login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if not show_login():
        st.stop()

# --------- Main Application ---------
def transform_data(df, loading_date, origin_warehouse_name, origin_warehouse_code, official_delivery_number, buying_station, product_name):
    df['Cantidad de cacao en BABA en quintales'] = pd.to_numeric(df['Cantidad de cacao en BABA en quintales'], errors='coerce').fillna(0)
    df['Cantidad de cacao SECO entregado en quintales'] = pd.to_numeric(df['Cantidad de cacao SECO entregado en quintales'], errors='coerce').fillna(0)
    
    # Loading Sheet
    df['Total Gross Weight (kg)*'] = (df['Cantidad de cacao en BABA en quintales'] + df['Cantidad de cacao SECO entregado en quintales']) * 45.36
    df['Total Net Weight (kg)*'] = df['Total Gross Weight (kg)*']

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
        'Total Number Of Sacks*': (df['Total Gross Weight (kg)*'].sum() / 69).round(0),
        'Total Gross Weight (kg)*': df['Total Gross Weight (kg)*'].sum(),
        'Total Net Weight (kg)*': df['Total Net Weight (kg)*'].sum(),
        'Product*': product_name
    }

    loading_df = pd.DataFrame([loading_data])
    
    # Buying Sheet
    df['Net Weight (Kg)*'] = (df['Cantidad de cacao en BABA en quintales'] + df['Cantidad de cacao SECO entregado en quintales'] * 45.36)
    
    buying_data = pd.DataFrame({
        'Buying Date*': df['Fechas de entrega (DIA/MES/AÑO)'].apply(lambda x: x.strftime('%Y-%m-%d')),
        'Producer Code*': df['Codigo del Productor'],
        'Producer Name': df['Nombre del Productor'],
        'Buying Station': buying_station,
        'Net Weight (Kg)*': df['Net Weight (Kg)*'].round(0),
        'Number Of Sacks*': '',
        'Receipt Number*': df['Numero de comprobante de pago'],
        'Loading Official Delivery Number*': official_delivery_number
    })
    
    return loading_df, buying_data

# Streamlit page config
st.set_page_config(page_title="Report Kapp", layout="wide", initial_sidebar_state="collapsed")

# Application header
st.markdown("<h1 style='text-align: center;'>📊 Report Kapp</h1>", unsafe_allow_html=True)
st.write("An application for uploading, transforming, and visualizing cacao data.")

# Sidebar styling
st.sidebar.title("⚙️ Input Configuration")
uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
origin_warehouse_name = st.sidebar.text_input("Origin Warehouse Name")
origin_warehouse_code = st.sidebar.text_input("Origin Warehouse Code")
official_delivery_number = st.sidebar.text_input("Official Delivery Number")
buying_station = st.sidebar.text_input("Buying Station")
product_name = st.sidebar.text_input("Product Name")

loading_date = datetime.today().strftime('%Y-%m-%d')

# Get the current time in Ecuador (GMT-5)
ecuador_tz = pytz.timezone('America/Guayaquil')
ecuador_time = datetime.now(ecuador_tz).strftime('%Y-%m-%d_%H-%M-%S')

# Main application logic
if uploaded_file:
    # Read the uploaded Excel file
    df = pd.read_excel(uploaded_file)

    # Validate necessary columns
    required_columns = [
        'Nombre del Productor', 'Codigo del Productor', 
        'Cantidad de cacao en BABA en quintales', 'Cantidad de cacao SECO entregado en quintales', 
        'Fechas de entrega (DIA/MES/AÑO)', 'Numero de comprobante de pago'
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing the following columns: {', '.join(missing_columns)}")
    else:
        # Transform the data
        loading_df, buying_df = transform_data(df, loading_date, origin_warehouse_name, origin_warehouse_code, official_delivery_number, buying_station, product_name)

        # Display results
        st.subheader("🔄 Transformed Data")
        st.write("### 'Loading' Sheet")
        st.dataframe(loading_df, use_container_width=True)

        st.write("### 'Buying' Sheet")
        st.dataframe(buying_df, use_container_width=True)

        # Generate the Excel file with custom name
        file_name = f"MultiLoad_KATCHILE_{origin_warehouse_code}_{ecuador_time}.xlsx"
        
        with pd.ExcelWriter(file_name) as writer:
            loading_df.to_excel(writer, sheet_name="Loading", index=False)
            buying_df.to_excel(writer, sheet_name="Buying", index=False)

        # Download button
        st.download_button(
            label="⬇️ Download Transformed File (Excel)",
            data=open(file_name, "rb").read(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("📁 Upload an Excel file from the sidebar to get started.")
