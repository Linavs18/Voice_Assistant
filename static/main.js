
document.addEventListener('DOMContentLoaded', function() {
    const escucharBtn = document.getElementById('escuchar');
    const resultadoDiv = document.getElementById('resultado');
    
    // Función para limpiar el historial de conversación
    function limpiarHistorial() {
        resultadoDiv.innerHTML = '';
    }
    
    // Función para agregar mensajes al historial
    function agregarMensaje(emisor, mensaje, esError = false) {
        const mensajeElement = document.createElement('p');
        if (esError) {
            mensajeElement.className = 'error';
        }
        mensajeElement.innerHTML = `<strong>${emisor}:</strong> ${mensaje}`;
        resultadoDiv.appendChild(mensajeElement);
        resultadoDiv.scrollTop = resultadoDiv.scrollHeight; // Auto-scroll al último mensaje
    }
    
    // Función para hacer hablar al asistente (llamada al backend)
    async function hablarAsistente(texto) {
        try {
            await fetch('/hablar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto: texto })
            });
        } catch (error) {
            console.error('Error al reproducir voz:', error);
        }
    }
    
    // Evento principal del botón de escuchar
    escucharBtn.addEventListener('click', async () => {
        try {
            // Mostrar estado de escucha
            agregarMensaje('Sistema', '🎤 Escuchando...');
            
            // Enviar audio al servidor
            const response = await fetch('/escuchar', { method: 'POST', signal: AbortSignal.timeout(10000) });
            const data = await response.json();
            
            // Procesar respuesta
            if (data.status === 'success') {
                agregarMensaje('Tú', data.comando);
                agregarMensaje('Asistente', data.respuesta);
                
                // Reproducir la respuesta en voz (el backend ya lo hace, pero por si acaso)
                await hablarAsistente(data.respuesta);
            } else {
                agregarMensaje('Error', data.error, true);
                agregarMensaje('Asistente', data.respuesta);
                await hablarAsistente(data.respuesta);
            }
            
        } catch (error) {
            // Manejo de errores de conexión
            const mensajeError = 'Hubo un error de conexión. Intenta de nuevo.';
            agregarMensaje('Error', mensajeError, true);
            await hablarAsistente(mensajeError);
            console.error('Error:', error);
        }
    });
    
    // Botón para limpiar el historial (opcional)
    const limpiarBtn = document.createElement('button');
    limpiarBtn.textContent = 'Limpiar historial';
    limpiarBtn.addEventListener('click', limpiarHistorial);
    document.body.appendChild(limpiarBtn);
});