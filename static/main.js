document.getElementById('escuchar').addEventListener('click', async () => {
    const resultadoDiv = document.getElementById('resultado');
    
    try {
        resultadoDiv.innerHTML += '<p>🎤 Escuchando...</p>';
        
        // 1. Enviar audio al servidor
        const response = await fetch('/escuchar', { method: 'POST' });
        const data = await response.json();
        
        // 2. Mostrar en pantalla (tanto si hay éxito como si hay error)
        if (data.status === 'success') {
            resultadoDiv.innerHTML += `<p><strong>Tú:</strong> ${data.comando}</p>`;
            resultadoDiv.innerHTML += `<p><strong>Asistente:</strong> ${data.respuesta}</p>`;
        } else {
            resultadoDiv.innerHTML += `<p class="error"><strong>Error:</strong> ${data.error}</p>`;
            resultadoDiv.innerHTML += `<p><strong>Asistente:</strong> ${data.respuesta}</p>`;
        }
        
        // Nota: Ya no necesitamos hacer hablar aquí porque el servidor ya lo hace automáticamente
        // cuando procesa el comando en ejecutar_comando() o en los manejadores de error
        
    } catch (error) {
        resultadoDiv.innerHTML += `<p class="error">Error: ${error.message}</p>`;
        
        // En caso de error de conexión con el servidor, hacemos hablar al asistente
        await fetch('/hablar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: "Hubo un error de conexión. Intenta de nuevo." })
        });
    }
});