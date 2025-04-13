function hablar() {
    const recognition = new webkitSpeechRecognition() || new SpeechRecognition();
    recognition.lang = "es-ES";
    recognition.start();
  
    recognition.onresult = function (event) {
      const texto = event.results[0][0].transcript;
      document.getElementById("respuesta").innerText = "🎧 Entendido: " + texto;
      enviarComando(texto);
    };
  
    recognition.onerror = function () {
      document.getElementById("respuesta").innerText = "❌ Error al escuchar";
    };
  }
  
  function enviarComando(texto) {
    fetch("/comando", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    })
      .then(res => res.json())
      .then(data => {
        const respuesta = data.respuesta;
        document.getElementById("respuesta").innerText = respuesta;
        decir(respuesta);
      });
  }
  
  function decir(texto) {
    const msg = new SpeechSynthesisUtterance();
    msg.lang = "es-ES";
    msg.text = texto;
    speechSynthesis.speak(msg);
  }
  