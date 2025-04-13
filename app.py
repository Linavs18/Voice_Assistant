import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import spotipy
from flask import Flask, render_template, request, jsonify
from spotipy.oauth2 import SpotifyOAuth

# Configurar Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="e2ac6738ea2c417994296daccee7dee4",
    client_secret="8bd0a76aff5648d4a1e96037149db1e3",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state,user-modify-playback-state"
))

# Inicializar motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def hablar(texto):
    engine.say(texto)
    engine.runAndWait()

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

def controlar_spotify(comando):
    try:
        if "pausa" in comando:
            sp.pause_playback()
            hablar("Spotify pausado")
        elif "reproduce" in comando:
            sp.start_playback()
            hablar("Reproduciendo Spotify")
        elif "siguiente" in comando:
            sp.next_track()
            hablar("Siguiente canción")
        elif "anterior" in comando:
            sp.previous_track()
            hablar("Canción anterior")
        else:
            hablar("Comando de Spotify no reconocido")
    except:
        hablar("No pude conectar con Spotify")

def ejecutar_comando(comando):
    if "hora" in comando:
        hora = datetime.datetime.now().strftime("%H:%M")
        hablar(f"La hora actual es {hora}")
    elif "abre google" in comando:
        webbrowser.open("https://www.google.com")
        hablar("Abriendo Google")
    elif "cómo estás" in comando:
        hablar("Estoy muy bien, gracias por preguntar")
    elif "reproduce música" in comando:
        path = "C:\\Tu\\Ruta\\a\\Musica"  # Cambia por tu carpeta de música
        canciones = os.listdir(path)
        if canciones:
            os.startfile(os.path.join(path, canciones[0]))
            hablar("Reproduciendo música")
        else:
            hablar("No encontré canciones")
    elif "abre spotify" in comando:
        ruta_spotify = "C:\\Users\\TuUsuario\\AppData\\Roaming\\Spotify\\Spotify.exe"
        os.startfile(ruta_spotify)
        hablar("Abriendo Spotify")
    elif "spotify" in comando:
        controlar_spotify(comando)
    elif "salir" in comando:
        hablar("Hasta luego")
        exit()
    else:
        hablar("No entendí ese comando")

# Loop principal
if __name__ == "__main__":
    hablar("Hola, soy tu asistente. ¿En qué te puedo ayudar?")
    while True:
        comando = escuchar()
        if comando:
            ejecutar_comando(comando)
