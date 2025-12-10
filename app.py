import streamlit as st
import pandas as pd
from datetime import datetime

# --------- Login Section ---------
# Simple authentication system (username and password)
def check_login(username, password):
    # Set your username and password
    correct_username = "admin"
    correct_password = "password123"
    
    if username == correct_username and password == correct_password:
        return True
    else:
        return False

# Function to display login form
def show_login():
    st.title("Welcome to Report Kapp")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
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
# Function for calculations and transformations
def transform_data(df, loading_date, origin_warehouse_name, origin_warehouse_code, official_delivery_number, buying_station, product_name):
    # Convert to numeric and replace NaN with 0
    df['Cantidad de cacao en BABA en quintales'] = pd.to_numeric(df['Cantidad de cacao en BABA en quintales'], errors='coerce').fillna(0)
    df['Cantidad de cacao SECO entregado en quintales'] = pd.to_numeric(df['Cantidad de cacao SECO entregado en quintales'], errors='coerce').fillna(0)
    
    # ----- "Loading" Sheet -----
    # Calculations for 'Total Gross Weight (kg)*' and 'Total Net Weight (kg)*'
    df['Total Gross Weight (kg)*'] = (df['Cantidad de cacao en BABA en quintales'] + df['Cantidad de cacao SECO entregado en quintales']) * 45.36
    df['Total Net Weight (kg)*'] = df['Total Gross Weight (kg)*']  # Assume net weight equals gross weight for now

    # Generate Loading sheet data
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
        'Total Number Of Sacks*': (df['Total Gross Weight (kg)*'].sum() / 69).round(0),  # Round it
        'Total Gross Weight (kg)*': df['Total Gross Weight (kg)*'].sum(),  # Sum total
        'Total Net Weight (kg)*': df['Total Net Weight (kg)*'].sum(),  # Sum total
        'Product*': product_name
    }
    
    loading_df = pd.DataFrame([loading_data])
    
    # ----- "Buying" Sheet -----
    # Calculate the 'Net Weight (Kg)*' column for the Buying sheet
    df['Net Weight (Kg)*'] = (df['Cantidad de cacao en BABA en quintales'] + df['Cantidad de cacao SECO entregado en quintales'] * 45.36)
    
    # Create Buying sheet data
    buying_data = pd.DataFrame({
        'Buying Date*': df['Fechas de entrega (DIA/MES/AÑO)'].apply(lambda x: x.strftime('%Y-%m-%d')),
        'Producer Code*': df['Codigo del Productor'],
        'Producer Name': df['Nombre del Productor'],
        'Buying Station': buying_station,
        'Net Weight (Kg)*': df['Net Weight (Kg)*'],  # Keep the value with decimals
        'Number Of Sacks*': '',  # This field is empty
        'Receipt Number*': df['Numero de comprobante de pago'],
        'Loading Official Delivery Number*': official_delivery_number
    })
    
    return loading_df, buying_data

# --------- Configuration and Inputs ---------
st.set_page_config(page_title="Report Kapp", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .reportview-container {
        background: #F7F7F7;
    }
    .sidebar .sidebar-content {
        background: #FFFFFF;
        padding-top: 50px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 25px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput input {
        font-size: 16px;
    }
    .stTextInput label {
        font-size: 14px;
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📊 Report Kapp")
st.write("An application to upload, transform, and visualize cacao data in a professional and clean layout.")

# --------- Sidebar ---------
st.sidebar.header("⚙️ Configuration")

# Inputs
uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx", "xls"], label_visibility="collapsed")
origin_warehouse_name = st.sidebar.text_input("Origin Warehouse Name", label_visibility="collapsed")
origin_warehouse_code = st.sidebar.text_input("Origin Warehouse Code", label_visibility="collapsed")
official_delivery_number = st.sidebar.text_input("Official Delivery Number", label_visibility="collapsed")
buying_station = st.sidebar.text_input("Buying Station", label_visibility="collapsed")
product_name = st.sidebar.text_input("Product Name", label_visibility="collapsed")

# Current date
loading_date = datetime.today().strftime('%Y-%m-%d')

# --------- Main Logic ---------
if uploaded_file:
    # Read the uploaded Excel file
    df = pd.read_excel(uploaded_file)

    # Validate that the necessary columns are present
    required_columns = [
        'Nombre del Productor', 'Codigo del Productor', 
        'Cantidad de cacao en BABA en quintales', 'Cantidad de cacao SECO entregado en quintales', 
        'Fechas de entrega (DIA/MES/AÑO)', 'Numero de comprobante de pago'
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing the following columns: {', '.join(missing_columns)}")
    else:
        # Call the transformation function
        loading_df, buying_df = transform_data(df, loading_date, origin_warehouse_name, origin_warehouse_code, official_delivery_number, buying_station, product_name)

        # Show the transformed data
        st.subheader("🔄 Transformed Data")

        # Show the two sheets
        st.write("### 'Loading' Sheet")
        st.dataframe(loading_df, use_container_width=True)

        st.write("### 'Buying' Sheet")
        # Round the 'Net Weight (Kg)*' column for display (keeping real values intact)
        buying_df['Net Weight (Kg)*'] = buying_df['Net Weight (Kg)*'].round(0)
        st.dataframe(buying_df, use_container_width=True)

        # Generate the Excel file with both sheets
        with pd.ExcelWriter("Transformed_Report.xlsx") as writer:
            loading_df.to_excel(writer, sheet_name="Loading", index=False)
            buying_df.to_excel(writer, sheet_name="Buying", index=False)

        # Download button for the Excel file
        st.download_button(
            label="⬇️ Download Transformed File (Excel)",
            data=open("Transformed_Report.xlsx", "rb").read(),
            file_name="Transformed_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("📁 Upload an Excel file from the sidebar to get started.")
