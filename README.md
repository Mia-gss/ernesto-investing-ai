# Ernesto Investing AI

Sistema operacional de análisis financiero que integra **ingesta de datos reales**, **modelos de Machine Learning / Deep Learning**, una **API REST** y un **frontend interactivo**, usando **MongoDB Atlas** como capa de persistencia entre cada etapa.

Proyecto desarrollado para el curso **Introducción al Desarrollo de Software (iDeSo)** — Facultad de Ingeniería de Sistemas e Informática (FISI), **Universidad Nacional Mayor de San Marcos (UNMSM)**.

> Trabajo grupal Semana 13 — Integración Frontend-Backend-MongoDB.
> Prof. Mg. Ing. Ernesto D. Cancho-Rodríguez, MBA.

---

## Flujo de datos end-to-end

```
[1] yfinance (Yahoo Finance)
        │  descarga OHLCV real
        ▼
[2] MongoDB Atlas — colección precios_ohlcv
        │  se leen y procesan los precios
        ▼
[3] Modelos de IA (SVC, RNNs, LSTM Regressor)
        │  entrenan y predicen
        ▼
[4] MongoDB Atlas — colecciones predicciones y metricas_modelos
        │  se leen resultados ya calculados
        ▼
[5] FastAPI + ngrok — API REST (no recalcula, solo lee de Mongo)
        │  fetch() HTTP
        ▼
[6] Frontend HTML + Plotly.js — dashboards interactivos
```

La API nunca recalcula nada: únicamente lee resultados ya guardados en MongoDB, por lo que responde en milisegundos. El frontend ya no usa datos simulados (`Math.random()`); consume datos reales servidos por la API.

---

## Los 5 activos del proyecto

| Ticker (Yahoo Finance) | Empresa | Bolsa |
|---|---|---|
| `FSM` | Fortuna Silver Mines | NYSE |
| `VOLCABC1.LM` | Volcan Compañía Minera | BVL |
| `ABX.TO` | Barrick Gold | TSX |
| `BVN` | Buenaventura | NYSE |
| `BHP` | BHP Billiton | NYSE |

---

## Módulos del sistema

| Módulo | Descripción |
|---|---|
| **Mercado** | Precio de cierre + SMA-20/SMA-50, y RSI-14 / MACD por ticker. |
| **Clasificador SVC** | Señal BUY/SELL con un Support Vector Classifier (GridSearchCV), métricas (accuracy, precision, recall, F1) y matriz de confusión. |
| **Comparador RNN** | 4 arquitecturas (LSTM, BiLSTM, GRU, SimpleRNN) comparadas con gráfico radar y tabla de métricas. |
| **Pronóstico LSTM Regressor** | Predicción de precios a futuro (7/14/30/60 días) con bandas de confianza al 95%. |

---

## Estructura del repositorio

```
ernesto-investing-ai/
│
├── README.md                              # Este archivo
│
├── docs/                              # Interfaces web (GitHub Pages)
│   ├── index.html                         # Portal de entrada
│   ├── modulo_mercado.html                # Dashboard de mercado
│   ├── modulo_svc.html                    # Clasificador SVC
│   ├── modulo_rnns.html                   # Comparador RNN
│   ├── modulo_lstm_regressor.html         # Pronóstico LSTM
│   └── assets/
│       ├── api-client.js                  # Cliente HTTP centralizado
│       └── style.css                      # Estilos del sistema
│
└── notebooks/                             # Google Colab (backend)
    ├── Notebook1_Ingesta_MongoDB.ipynb          # Ingesta yfinance → MongoDB
    ├── Notebook2_SVC_MongoDB.ipynb               # Clasificador SVC
    ├── Notebook3_RNNs_MongoDB.ipynb              # Comparador RNN (4 arquitecturas)
    ├── Notebook4_LSTM_Regressor_MongoDB.ipynb    # Pronóstico LSTM
    └── Notebook5_API_FastAPI.ipynb               # API REST (FastAPI + ngrok)
```

---

## Backend — Notebooks de Google Colab

### Notebook 1 — Ingesta de Datos
Descarga OHLCV de los 5 tickers con `yfinance`, calcula indicadores técnicos (SMA-20, SMA-50, EMA-12, EMA-26, RSI-14, MACD) con la librería `ta`, y guarda cada ticker (upsert) en la colección **`precios_ohlcv`** de MongoDB.

### Notebook 2 — Clasificador SVC
Lee `precios_ohlcv` de MongoDB, construye un target binario (BUY si el precio sube al día siguiente), entrena un **Support Vector Classifier** con `GridSearchCV` (kernels `linear`/`rbf`, `C`, `gamma`) sobre una partición temporal 80/20 (sin data leakage), y guarda la señal, historial y métricas en las colecciones **`predicciones`** y **`metricas_modelos`**.

### Notebook 3 — Comparador RNN
Prepara secuencias temporales a partir de MongoDB y entrena 4 arquitecturas — **LSTM, BiLSTM, GRU y SimpleRNN** — para clasificación BUY/SELL, guardando predicción y métricas de cada modelo por ticker.

### Notebook 4 — LSTM Regressor
Entrena un **LSTM** para regresión de precio continuo, evalúa con RMSE/MAE/R² sobre el set de test, y proyecta el precio futuro a distintos horizontes (7, 14, 30, 60 días) con bandas de confianza.

### Notebook 5 — API FastAPI
Levanta una API REST con **FastAPI**, expuesta a Internet vía **ngrok**, con CORS habilitado. Lee exclusivamente de MongoDB (no recalcula nada):

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/salud` | Verifica que la API y MongoDB estén operativos |
| `GET` | `/api/mercado/{ticker}` | Precios OHLCV + indicadores técnicos |
| `GET` | `/api/svc/{ticker}` | Señal, historial y métricas del SVC |
| `GET` | `/api/rnns/{ticker}` | Predicción y métricas de las 4 RNN |
| `GET` | `/api/lstm/{ticker}?horizonte=` | Pronóstico LSTM (`horizonte` ∈ {7, 14, 30, 60}) |

**Base de datos:** `ernesto_investing_ai` · **Colecciones:** `precios_ohlcv`, `predicciones`, `metricas_modelos`.

---

## Frontend

Frontend estático en HTML/JS/CSS, desplegado en **GitHub Pages**, sin frameworks ni build step:

- **`index.html`** — portal de entrada donde se pega la URL pública de ngrok (Notebook 5), se guarda en `sessionStorage`, y se verifica la conexión con `/api/salud`.
- **`modulo_mercado.html`**, **`modulo_svc.html`**, **`modulo_rnns.html`**, **`modulo_lstm_regressor.html`** — cada uno hace `fetch()` a su endpoint correspondiente y grafica los resultados con **Plotly.js**.
- **`assets/api-client.js`** — cliente HTTP único (`ApiClient`) usado por todos los módulos; centraliza la URL base, headers (`ngrok-skip-browser-warning`) y manejo de errores.
- **`assets/style.css`** — estilos compartidos (paleta institucional, tarjetas, tablas, indicador de conexión).

> Nota: La URL de ngrok es temporal: cambia cada vez que se reinicia el Notebook 5. Hay que volver a pegarla en el portal (`index.html`) tras cada reinicio.

---

## Cómo ejecutar el sistema

1. **MongoDB Atlas**: crear un clúster M0 gratuito, un usuario de base de datos y habilitar el acceso de red `0.0.0.0/0`. Guardar la cadena de conexión como el Secret `MONGO_URI` en Colab.
2. **Backend (Google Colab)**, en orden:
   1. `Notebook1_Ingesta_MongoDB.ipynb` → puebla `precios_ohlcv`.
   2. `Notebook2_SVC_MongoDB.ipynb` → puebla `predicciones` / `metricas_modelos` (modelo `SVC`).
   3. `Notebook3_RNNs_MongoDB.ipynb` → agrega resultados de `LSTM`, `BiLSTM`, `GRU`, `SimpleRNN`.
   4. `Notebook4_LSTM_Regressor_MongoDB.ipynb` → agrega resultados de `LSTM_Regressor`.
   5. `Notebook5_API_FastAPI.ipynb` → levanta la API y expone la URL pública de ngrok.
3. **Frontend**: abrir `index.html` (local o en GitHub Pages), pegar la URL de ngrok del paso anterior y verificar la conexión. Desde ahí se navega a los 4 módulos.

---

## Stack técnico

**Backend / IA:** Python · Google Colab · yfinance · `ta` · pandas / NumPy · scikit-learn (SVC + GridSearchCV) · TensorFlow/Keras (LSTM, BiLSTM, GRU, SimpleRNN) · FastAPI · Uvicorn · ngrok · PyMongo

**Base de datos:** MongoDB Atlas

**Frontend:** HTML5 · CSS3 · JavaScript (Vanilla) · Plotly.js

**Despliegue:** GitHub Pages (frontend) · Google Colab + ngrok (backend, temporal)

---

## Autoría

Proyecto académico — Universidad Nacional Mayor de San Marcos (UNMSM), Facultad de Ingeniería de Sistemas e Informática (FISI), curso Introducción al Desarrollo de Software (iDeSo), 2026-II.
