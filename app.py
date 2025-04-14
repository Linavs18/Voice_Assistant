import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import subprocess
import platform
from pytube import YouTube
from pytube import Search
from flask_cors import CORS
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

CORS(app)
# Configurar el cliente de Spotify 

def hablar(texto):
    engine = pyttsx3.init()  # Reiniciar en cada llamada
    engine.setProperty('rate', 150)
    engine.say(texto)
    engine.runAndWait()
    engine.stop()  # Liberar recursos
    return texto

def escuchar():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Escuchando...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        comando = r.recognize_google(audio, language="es-ES")
        print(f"🗣️ Has dicho: {comando}")
        return comando.lower()
    except sr.UnknownValueError:
        hablar("No entendí lo que dijiste.")
        return ""
    except sr.RequestError:
        hablar("No tengo conexión para procesar tu voz.")
        return ""
    finally:
            source.__exit__() 

def abrir_spotify():
    """Abre la aplicación de Spotify según el sistema operativo"""
    try:
        sistema = platform.system()
        if sistema == "Windows":
            os.startfile("spotify")
            return True
        elif sistema == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "Spotify"])
            return True
        elif sistema == "Linux":
            subprocess.Popen(["spotify"])
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al abrir Spotify: {str(e)}")
        return False

def reproducir_youtube(comando):
    try:
        # Comando específico: "youtube [búsqueda]"
        busqueda = comando.replace("youtube", "").strip()
        print(f"Buscando en YouTube: '{busqueda}'")
        
        # Busca en YouTube
        s = Search(busqueda)
        if not s.results or len(s.results) == 0:
            return "No encontré resultados en YouTube para esa búsqueda"
            
        video_url = f"https://youtube.com/watch?v={s.results[0].video_id}"
        
        # Abre el video en el navegador
        webbrowser.open(video_url)
        return f"Reproduciendo en YouTube: {s.results[0].title}"
    
    except Exception as e:
        print(f"Error con YouTube: {str(e)}")
        return f"No pude encontrar el video en YouTube: {str(e)}"

def ejecutar_comando(comando):
    if not comando:
        respuesta = "No escuché nada. ¿Puedes repetirlo?"
        hablar(respuesta)
        return respuesta
    
    comando = comando.lower().strip()
    
    # Comando para decir la hora
    if "hora" in comando:
        hora = datetime.datetime.now().strftime("%H:%M")
        respuesta = "La hora actual es " + hora
        hablar(respuesta)
        return respuesta
    
    elif "abre spotify" in comando:
        if abrir_spotify():
            respuesta = "Abriendo Spotify"
        else:
            respuesta = "No pude abrir Spotify"
        hablar(respuesta)
        return respuesta

    # Comandos específicos de YouTube
    elif "youtube" in comando:
        respuesta = reproducir_youtube(comando)
        hablar(respuesta)
        return respuesta
    
    elif "abre google" in comando:
        webbrowser.open("https://www.google.com")
        respuesta = "Abriendo Google en tu navegador"
        hablar(respuesta)
        return respuesta
    
    elif "cómo estás" in comando:
        respuesta = "Estoy muy bien, gracias por preguntar"
        hablar(respuesta)
        return respuesta
    
    elif "salir" in comando:
        respuesta = "Hasta luego"
        hablar(respuesta)
        return respuesta
        exit()
    
    # Comandos adicionales se pueden agregar aquí
    
    else:
        respuesta = "No entendí. Por favor di 'youtube' para videos o 'abre spotify' para iniciar la aplicación."
        hablar(respuesta)
        return respuesta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/escuchar', methods=['POST'])
def escuchar_comando():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Escuchando...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        
        try:
            comando = r.recognize_google(audio, language="es-ES")
            respuesta = ejecutar_comando(comando)
            return jsonify({
                'status': 'success',
                'comando': comando,
                'respuesta': respuesta
            })
        except sr.UnknownValueError:
            # Si no se detectó ningún comando
            respuesta = "No entendí lo que dijiste. ¿Puedes repetirlo?"
            hablar(respuesta)  # Reproducir mensaje de error por voz
            return jsonify({
                'status': 'error',
                'error': 'No se detectó ningún comando',
                'comando': '',
                'respuesta': respuesta
            })
        
    except sr.WaitTimeoutError:
        respuesta = "Tiempo de espera agotado. Intenta de nuevo."
        hablar(respuesta)  # Reproducir mensaje de error por voz
        return jsonify({
            'status': 'error',
            'error': 'Tiempo de espera agotado',
            'comando': '',
            'respuesta': respuesta
        })
    except Exception as e:
        respuesta = f"Ocurrió un error: {str(e)}"
        hablar(respuesta)  # Reproducir mensaje de error por voz
        return jsonify({
            'status': 'error',
            'error': str(e),
            'comando': '',
            'respuesta': respuesta
        })


@app.route('/hablar', methods=['POST'])
def hablar_texto():
    data = request.json
    texto = data.get('texto', '')
    respuesta = hablar(texto)
    return jsonify({'respuesta': respuesta})
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
