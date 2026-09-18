import streamlit as st
import yfinance as yf
import plotly.express as px
from google import genai as gemini

# 1. Configuración de la interfaz web
st.set_page_config(page_title="Dashboard IA Financiera", layout="wide")

# Barra lateral para el control del usuario
st.sidebar.header("⚙️ Configuración del Dashboard")

# Selector de empresas dinámico
lista_tickers = st.sidebar.multiselect(
    "Selecciona las Empresas a analizar:",
    options=["AAPL", "MSFT", "NVDA", "TSLA", "MELI", "GOOGL", "AMZN", "META"],
    default=["AAPL", "MSFT", "NVDA"]
)

# Selector de periodo de tiempo
periodo = st.sidebar.selectbox(
    "Periodo de tiempo de los datos:",
    options=["3m", "6m", "1y", "2y", "5y"],
    index=2  # Por defecto selecciona '1y' (1 año)
)

st.title("📊 Dashboard Financiero con Inteligencia Artificial")
st.markdown("Analiza la cotización de tus activos favoritos en tiempo real y genera reportes automáticos con IA.")

# Control de error: si no hay empresas seleccionadas
if not lista_tickers:
    st.warning("⚠️ Por favor, selecciona al menos una empresa en la barra lateral para ver los gráficos.")
else:
    try:
        # 2. Descarga de datos limpia y forzada a DataFrame
        datos = yf.download(lista_tickers, period=periodo, group_by='ticker')
        
        # Estructuramos los precios de cierre de forma limpia para evitar errores de Pandas
        precios = yf.download(lista_tickers, period=periodo)["Close"]
        
        # Si es un solo ticker, yfinance devuelve una Serie. La convertimos a DataFrame.
        if len(lista_tickers) == 1:
            precios = precios.to_frame(name=lista_tickers)

        # Eliminamos cualquier fila vacía para que Plotly no falle
        precios = precios.dropna()

        # 3. Diseño en dos columnas estéticas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Últimos Precios de Cierre")
            st.dataframe(precios.tail(10), use_container_width=True)
            
        with col2:
            st.subheader("📉 Evolución de Inversión de $1000 USD")
            inversion = precios / precios.iloc[0] * 1000

            # Creación del gráfico con el modo oscuro real forzado
            fig = px.line(
                inversion, 
                title=f"Rendimiento simulado de $1000 USD (Periodo: {periodo})",
                labels={"value": "Valor de la inversión ($)", "Date": "Fecha", "variable": "Empresa"},
                template="plotly_dark"
            )
            
            fig.update_layout(
                paper_bgcolor="#111111",
                plot_bgcolor="#111111",
                font_color="#F2F5FA"
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Hubo un problema al cargar los gráficos financieros: {e}")

    # Estructura visual para separar el módulo de IA
    st.markdown("---")

    # 4. BOTÓN Y PROMPT DE REPORTE CON IA CON ACCESO SEGURO A SECRETS
    st.subheader("🤖 Análisis de Portafolio con IA Experta")
    
    try:
        # CONEXIÓN SEGURA: Leemos la clave desde la configuración de la nube de Streamlit
        api_key_segura = st.secrets.get("GEMINI_API_KEY")
        cliente = gemini.Client(api_key=api_key_segura) 
        
        prompt = f"""
        Actúa como un analista financiero experto certificado. Haz un análisis profundo del rendimiento de las acciones del portafolio actual: {', '.join(lista_tickers)} durante el periodo seleccionado de {periodo}. 
        Considera los eventos macroeconómicos, lanzamientos tecnológicos y noticias del mercado que justifiquen las alzas y bajas de cada una.
        Utiliza formato Markdown limpio con títulos legibles, negritas y viñetas para que sea estético.
        
        Datos de precios de los últimos días para tu análisis:
        {precios.tail(5).to_string() if 'precios' in locals() else 'Datos no disponibles'}
        """
        
        if st.button("🚀 Generar Reporte Financiero de este Portafolio"):
            with st.spinner("Gemini está analizando las cotizaciones en tiempo real y redactando el informe..."):
                respuesta = cliente.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
                st.markdown(respuesta.text)

    except Exception as e:
        st.error(f"Ocurrió un inconveniente con el motor de Inteligencia Artificial: {e}")
