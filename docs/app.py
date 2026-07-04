import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go

# ==============================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================
st.set_page_config(
    page_title="Ernesto Investing AI",
    page_icon="📈",
    layout="wide"
)

TICKERS = ["FSM", "VOLCABC1.LM", "ABX.TO", "BVN", "BHP"]
MODELOS_RNN = ["LSTM", "BiLSTM", "GRU", "SimpleRNN"]

# ==============================================
# CONEXIÓN A MONGODB (usando Streamlit Secrets)
# ==============================================
@st.cache_resource
def conectar_mongo():
    uri = st.secrets["MONGO_URI"]
    client = MongoClient(uri)
    return client["ernesto_investing_ai"]

db = conectar_mongo()
coleccion_precios = db["precios_ohlcv"]
coleccion_predicciones = db["predicciones"]
coleccion_metricas = db["metricas_modelos"]

# ==============================================
# SIDEBAR - NAVEGACIÓN
# ==============================================
st.sidebar.title("📈 Ernesto Investing AI")
pagina = st.sidebar.radio(
    "Módulo",
    ["Mercado", "Clasificador SVC", "Comparador RNN", "Pronóstico LSTM"]
)

ticker = st.sidebar.selectbox("Ticker", TICKERS)

st.sidebar.markdown("---")
st.sidebar.caption("Proyecto académico — iDeSo 2026-II — FISI — UNMSM")

# ==============================================
# MÓDULO: MERCADO
# ==============================================
if pagina == "Mercado":
    st.title(f"📊 Datos de Mercado — {ticker}")

    doc = coleccion_precios.find_one({"ticker": ticker})

    if doc is None:
        st.error(f"No hay datos de mercado para {ticker}")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Último Precio", f"${doc['close'][-1]:.2f}")
        col2.metric("SMA 20", f"${doc['sma20'][-1]:.2f}" if doc['sma20'][-1] else "N/A")
        col3.metric("RSI (14)", f"{doc['rsi'][-1]:.1f}" if doc['rsi'][-1] else "N/A")

        fig_precio = go.Figure()
        fig_precio.add_trace(go.Scatter(x=doc["fechas"], y=doc["close"], name="Precio de Cierre", line=dict(color="#1F3864")))
        fig_precio.add_trace(go.Scatter(x=doc["fechas"], y=doc["sma20"], name="SMA 20", line=dict(color="#C5961A", dash="dot")))
        fig_precio.add_trace(go.Scatter(x=doc["fechas"], y=doc["sma50"], name="SMA 50", line=dict(color="#800000", dash="dot")))
        fig_precio.update_layout(template="plotly_white", title="Precio de Cierre", hovermode="x unified")
        st.plotly_chart(fig_precio, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=doc["fechas"], y=doc["rsi"], name="RSI", line=dict(color="#26A69A")))
            fig_rsi.update_layout(template="plotly_white", title="RSI (14)")
            st.plotly_chart(fig_rsi, use_container_width=True)

        with col_b:
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=doc["fechas"], y=doc["macd"], name="MACD", line=dict(color="#EF5350")))
            fig_macd.update_layout(template="plotly_white", title="MACD")
            st.plotly_chart(fig_macd, use_container_width=True)

# ==============================================
# MÓDULO: CLASIFICADOR SVC
# ==============================================
elif pagina == "Clasificador SVC":
    st.title(f"🎯 Clasificador SVC — {ticker}")

    prediccion = coleccion_predicciones.find_one({"ticker": ticker, "modelo": "SVC"})
    metricas = coleccion_metricas.find_one({"ticker": ticker, "modelo": "SVC"})

    if prediccion is None or metricas is None:
        st.error(f"No hay resultados SVC para {ticker}")
    else:
        senal = prediccion["senal_actual"]
        confianza = prediccion["confianza"] * 100

        if senal == "BUY":
            st.success(f"### 🟢 Señal: {senal} — Confianza: {confianza:.1f}%")
        else:
            st.error(f"### 🔴 Señal: {senal} — Confianza: {confianza:.1f}%")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Accuracy", f"{metricas['accuracy']*100:.1f}%")
        col2.metric("Precision", f"{metricas['precision']*100:.1f}%")
        col3.metric("Recall", f"{metricas['recall']*100:.1f}%")
        col4.metric("F1-Score", f"{metricas['f1']*100:.1f}%")

        st.caption(f"Kernel: {metricas['hiperparametros']['kernel']} | "
                   f"C: {metricas['hiperparametros']['C']} | "
                   f"Gamma: {metricas['hiperparametros']['gamma']}")

        st.subheader("Matriz de Confusión")
        matriz = metricas["matriz_confusion"]
        fig_matriz = go.Figure(data=go.Heatmap(
            z=matriz,
            x=["Predicho: SELL", "Predicho: BUY"],
            y=["Real: SELL", "Real: BUY"],
            colorscale=[[0, "#ffffff"], [1, "#1F3864"]],
            text=matriz,
            texttemplate="%{text}",
            showscale=False
        ))
        st.plotly_chart(fig_matriz, use_container_width=True)

# ==============================================
# MÓDULO: COMPARADOR RNN
# ==============================================
elif pagina == "Comparador RNN":
    st.title(f"🧠 Comparador de Clasificadores RNN — {ticker}")

    cols = st.columns(4)
    metricas_todas = {}

    for i, modelo in enumerate(MODELOS_RNN):
        prediccion = coleccion_predicciones.find_one({"ticker": ticker, "modelo": modelo})
        metricas = coleccion_metricas.find_one({"ticker": ticker, "modelo": modelo})

        if prediccion is None or metricas is None:
            cols[i].warning(f"{modelo}: sin datos")
            continue

        metricas_todas[modelo] = metricas
        senal = prediccion["senal_actual"]
        confianza = prediccion["confianza"] * 100

        with cols[i]:
            st.markdown(f"**{modelo}**")
            if senal == "BUY":
                st.success(f"{senal} ({confianza:.1f}%)")
            else:
                st.error(f"{senal} ({confianza:.1f}%)")

    if metricas_todas:
        st.subheader("Comparación de Métricas")
        df_comparativo = pd.DataFrame([
            {
                "Modelo": modelo,
                "Accuracy": f"{m['accuracy']*100:.1f}%",
                "Precision": f"{m['precision']*100:.1f}%",
                "Recall": f"{m['recall']*100:.1f}%",
                "F1-Score": f"{m['f1']*100:.1f}%"
            }
            for modelo, m in metricas_todas.items()
        ])
        st.dataframe(df_comparativo, use_container_width=True, hide_index=True)

        st.subheader("Gráfico Radar")
        fig_radar = go.Figure()
        colores = {"LSTM": "#1F3864", "BiLSTM": "#C5961A", "GRU": "#26A69A", "SimpleRNN": "#800000"}

        for modelo, m in metricas_todas.items():
            fig_radar.add_trace(go.Scatterpolar(
                r=[m["accuracy"], m["precision"], m["recall"], m["f1"], m["accuracy"]],
                theta=["Accuracy", "Precision", "Recall", "F1-Score", "Accuracy"],
                fill="toself",
                name=modelo,
                line=dict(color=colores.get(modelo))
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            template="plotly_white"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# ==============================================
# MÓDULO: PRONÓSTICO LSTM
# ==============================================
elif pagina == "Pronóstico LSTM":
    st.title(f"📈 Pronóstico de Precios — {ticker}")

    horizonte = st.sidebar.selectbox("Horizonte (días)", [7, 14, 30, 60], index=2)

    prediccion = coleccion_predicciones.find_one({"ticker": ticker, "modelo": "LSTM_Regressor"})
    metricas = coleccion_metricas.find_one({"ticker": ticker, "modelo": "LSTM_Regressor"})

    if prediccion is None or metricas is None:
        st.error(f"No hay resultados de LSTM Regressor para {ticker}")
    else:
        pred_horizonte = prediccion["prediccion_futura"][str(horizonte)]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("RMSE (USD)", f"${metricas['rmse_usd']}")
        col2.metric("RMSE (%)", f"{metricas['rmse_pct']}%")
        col3.metric("R²", f"{metricas['r2']}")
        col4.metric(f"Predicción {horizonte}d", f"${pred_horizonte['precio']}")

        serie_futura = prediccion["serie_futura_completa"][:horizonte]
        dias_futuros = [f"+{i+1}d" for i in range(len(serie_futura))]
        banda_sup = [pred_horizonte["banda_superior"]] * len(serie_futura)
        banda_inf = [pred_horizonte["banda_inferior"]] * len(serie_futura)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prediccion["fechas_test"], y=prediccion["precios_reales_test"],
                                   name="Precio Real (Test)", line=dict(color="#1F3864")))
        fig.add_trace(go.Scatter(x=prediccion["fechas_test"], y=prediccion["precios_predichos_test"],
                                   name="Predicción (Test)", line=dict(color="#C5961A", dash="dash")))
        fig.add_trace(go.Scatter(x=dias_futuros, y=serie_futura,
                                   name=f"Proyección ({horizonte}d)", line=dict(color="#26A69A")))
        fig.add_trace(go.Scatter(x=dias_futuros, y=banda_sup, name="Banda Superior",
                                   line=dict(color="#26A69A", dash="dot", width=1), opacity=0.5))
        fig.add_trace(go.Scatter(x=dias_futuros, y=banda_inf, name="Banda Inferior",
                                   line=dict(color="#26A69A", dash="dot", width=1),
                                   fill="tonexty", fillcolor="rgba(38,166,154,0.1)", opacity=0.5))

        fig.update_layout(template="plotly_white", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)