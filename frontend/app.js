
// Dirección de nuestra API
const API_URL = "http://98.93.147.240:8000";

// Elementos de la página
const form = document.getElementById("shorten-form");
const input = document.getElementById("original-url");
const message = document.getElementById("message");
const result = document.getElementById("result");
const shortLink = document.getElementById("short-link");
const copyButton = document.getElementById("copy-button");

// Crear enlace corto
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const originalUrl = input.value;

    message.textContent = "Creando enlace...";
    result.hidden = true;

    try {
        const response = await fetch(`${API_URL}/shorten`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                original_url: originalUrl
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "No se pudo crear el enlace");
        }

        shortLink.href = data.short_url;
        shortLink.textContent = data.short_url;

        result.hidden = false;
        message.textContent = "¡Enlace creado correctamente!";

    } catch (error) {
        message.textContent = error.message;
    }
});

// Copiar enlace corto
copyButton.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(shortLink.href);
        message.textContent = "¡Enlace copiado!";
    } catch (error) {
        message.textContent = "No se pudo copiar el enlace.";
    }
});
