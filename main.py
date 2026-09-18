import streamlit as st
import yfinance as yf
import plotly.express as px

# Configuración del título de la página web
st.set_page_config(page_title="Dashboard Financiero", layout="wide")
st.title("📊 Análisis de Acciones: AAPL, MSFT, NVDA")

# Descarga de datos (Tu lógica original)
tikers = "AAPL", "NVDA", "MSFT"
datos = yf.download(tikers, period="1y")
precios = datos["Close"]

# Mostrar la tabla de datos de forma interactiva en la web
st.subheader("📈 Últimos Precios de Cierre")
st.dataframe(precios.tail())

# Gráfico interactivo de Plotly (Tu lógica original)
st.subheader("📉 Evolución de una Inversión de $1000 USD")
inversion = precios / precios.values[0] * 1000

fig = px.line(inversion, 
              title="Si invertís $1000, ¿Cuánto tendrías hoy?",
              labels={"value": "Valor de $1000", "Date": "Fecha", "variable": "Empresa"},
              template="plotly_dark")

# Esto renderiza el gráfico directamente en la página web
st.plotly_chart(fig, use_container_width=True)