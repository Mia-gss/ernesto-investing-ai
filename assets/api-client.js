// ==============================================
// CLIENTE API CENTRALIZADO - Ernesto Investing AI
// ==============================================

const ApiClient = (function () {

    // La URL se guarda en sessionStorage para que persista entre módulos
    // pero se reconfigura fácilmente si ngrok cambia de URL
    function obtenerBaseUrl() {
        return sessionStorage.getItem("api_base_url") || "";
    }

    function establecerBaseUrl(url) {
        // Quita la barra final si la tiene, para evitar // duplicados
        const limpia = url.trim().replace(/\/$/, "");
        sessionStorage.setItem("api_base_url", limpia);
    }

    async function llamarEndpoint(ruta) {
        const base = obtenerBaseUrl();

        if (!base) {
            throw new Error("No se ha configurado la URL de la API. Vuelve al portal principal.");
        }

        const url = base + ruta;

        const respuesta = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "true"
            },
            mode: "cors"
        });

        if (!respuesta.ok) {
            let detalle = respuesta.statusText;
            try {
                const cuerpoError = await respuesta.json();
                detalle = cuerpoError.detail || detalle;
            } catch (_) {}
            throw new Error(`Error ${respuesta.status}: ${detalle}`);
        }

        return respuesta.json();
    }

    async function verificarSalud() {
        return llamarEndpoint("/api/salud");
    }

    async function obtenerMercado(ticker) {
        return llamarEndpoint(`/api/mercado/${ticker}`);
    }

    async function obtenerSVC(ticker) {
        return llamarEndpoint(`/api/svc/${ticker}`);
    }

    async function obtenerRNNs(ticker) {
        return llamarEndpoint(`/api/rnns/${ticker}`);
    }

    async function obtenerLSTMRegressor(ticker, horizonte = 30) {
        return llamarEndpoint(`/api/lstm/${ticker}?horizonte=${horizonte}`);
    }

    return {
        obtenerBaseUrl,
        establecerBaseUrl,
        verificarSalud,
        obtenerMercado,
        obtenerSVC,
        obtenerRNNs,
        obtenerLSTMRegressor
    };

})();