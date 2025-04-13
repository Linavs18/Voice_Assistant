import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import spotipy
import subprocess
import platform

from pytube import YouTube
from pytube import Search
from flask_cors import CORS
from flask import Flask, render_template, request, jsonify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

CORS(app)
# Configurar el cliente de Spotify 
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="e2ac6738ea2c417994296daccee7dee4",
    client_secret="8bd0a76aff5648d4a1e96037149db1e3",
    redirect_uri="http://localhost:8888/callback",
))

# Inicializar motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def hablar(texto):
    engine.say(texto)
    engine.runAndWait()
    return texto  # Devolvemos el texto para mostrarlo en la web

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
        return "No entendí lo que dijiste."
    except sr.RequestError:
        return "No tengo conexión para procesar tu voz."

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

def buscar_y_reproducir_spotify(comando):
    try:
        # Primero intentar abrir Spotify si no está abierto
        devices = sp.devices()
        if not devices['devices']:
            print("No hay dispositivos activos, intentando abrir Spotify...")
            spotify_abierto = abrir_spotify()
            if spotify_abierto:
                # Esperar un momento para que Spotify arranque
                import time
                time.sleep(3)
                # Volver a verificar dispositivos
                devices = sp.devices()
                if not devices['devices']:
                    return "He abierto Spotify pero no detecta dispositivos activos. Intenta de nuevo en unos segundos."
            else:
                return "No pude abrir Spotify automáticamente. Por favor, ábrelo manualmente."
            
        # Obtener ID del dispositivo activo para usar explícitamente
        device_id = devices['devices'][0]['id']
        
        # Comando: "spotify [canción] de [artista]"
        if "de" in comando:
            # Extrae canción y artista
            partes = comando.split("de")
            cancion = partes[0].replace("spotify", "").strip()
            artista = partes[1].strip()
            print(f"Buscando en Spotify: '{cancion}' de '{artista}'")
            
            # Busca en Spotify
            results = sp.search(q=f"track:{cancion} artist:{artista}", type="track", limit=1)
            
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(device_id=device_id, uris=[track_uri])
                return f"Reproduciendo en Spotify: {cancion} de {artista}"
            else:
                # Intentar búsqueda más general
                results = sp.search(q=f"{cancion} {artista}", type="track", limit=1)
                if results['tracks']['items']:
                    track_uri = results['tracks']['items'][0]['uri']
                    sp.start_playback(device_id=device_id, uris=[track_uri])
                    track_name = results['tracks']['items'][0]['name']
                    artist_name = results['tracks']['items'][0]['artists'][0]['name']
                    return f"Reproduciendo en Spotify: {track_name} de {artist_name}"
                else:
                    return f"No encontré {cancion} de {artista} en Spotify"
        else:
            # Busca por el nombre de la canción solamente
            # Comando: "spotify [canción]"
            query = comando.replace("spotify", "").strip()
            print(f"Buscando en Spotify: '{query}'")
            results = sp.search(q=query, type="track", limit=1)
            
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(device_id=device_id, uris=[track_uri])
                track_name = results['tracks']['items'][0]['name']
                artist_name = results['tracks']['items'][0]['artists'][0]['name']
                return f"Reproduciendo en Spotify: {track_name} de {artist_name}"
            else:
                return f"No encontré {query} en Spotify"
    except Exception as e:
        print(f"Error al reproducir en Spotify: {str(e)}")
        return f"Error al reproducir en Spotify: {str(e)}"

def controlar_spotify(comando):
    try:
        devices = sp.devices()
        if not devices['devices']:
            print("No hay dispositivos activos, intentando abrir Spotify...")
            spotify_abierto = abrir_spotify()
            if spotify_abierto:
                # Esperar un momento para que Spotify arranque
                import time
                time.sleep(3)
                # Volver a verificar dispositivos
                devices = sp.devices()
                if not devices['devices']:
                    return "He abierto Spotify pero no detecta dispositivos activos. Intenta de nuevo en unos segundos."
            else:
                return "No pude abrir Spotify automáticamente. Por favor, ábrelo manualmente."
            
        if "pausa" in comando:
            sp.pause_playback()
            return "Spotify pausado"
        elif "continuar" in comando or "reanudar" in comando:
            sp.start_playback()
            return "Reanudando Spotify"
        elif "siguiente" in comando:
            sp.next_track()
            return "Pasando a la siguiente canción en Spotify"
        elif "anterior" in comando:
            sp.previous_track()
            return "Volviendo a la canción anterior en Spotify"
        else:
            return "Comando de Spotify no reconocido"
    except Exception as e:
        print(f"Error con Spotify: {str(e)}")
        return f"No pude conectar con Spotify: {str(e)}"

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
    if any(palabra in comando for palabra in ["hora", "qué hora es", "dime la hora"]):
        hora = datetime.datetime.now().strftime("%I:%M %p")  # Formato de 12 horas
        respuesta = f"Son las {hora}"
        hablar(respuesta)
        return respuesta
    
    elif "abre spotify" in comando:
        if abrir_spotify():
            respuesta = "Abriendo Spotify"
        else:
            respuesta = "No pude abrir Spotify"
        hablar(respuesta)
        return respuesta
    
    # Comandos específicos de Spotify
    elif "spotify" in comando:
        if any(palabra in comando for palabra in ["pausa", "continuar", "reanudar", "siguiente", "anterior"]):
            respuesta = controlar_spotify(comando)
        else:
            # Para reproducir música: "spotify [canción] de [artista]" o "spotify [canción]"
            respuesta = buscar_y_reproducir_spotify(comando)
        
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
    
    # Comandos adicionales se pueden agregar aquí
    
    else:
        respuesta = "No entendí. Por favor di 'spotify' para música en Spotify, 'youtube' para videos o 'abre spotify' para iniciar la aplicación."
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
            audio = r.listen(source, timeout=5)
        
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
    app.run(debug=True)