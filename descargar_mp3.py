#!/usr/bin/env python3
"""
Script para descargar canciones MP3 para memoria USB de carro.
Usa yt-dlp para descargar audio de YouTube y convertirlo a MP3.

Uso:
    python descargar_mp3.py                    # Modo interactivo
    python descargar_mp3.py "nombre cancion"   # Buscar y descargar
    python descargar_mp3.py URL                # Descargar desde URL
"""

import subprocess
import sys
import os
from pathlib import Path

# Configuración
CARPETA_SALIDA = Path(__file__).parent / "canciones"
CALIDAD_MP3 = "192"  # kbps - buena calidad para carro (128, 192, 256, 320)


def verificar_dependencias():
    """Verifica que yt-dlp y ffmpeg estén instalados."""
    dependencias_faltantes = []
    
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        dependencias_faltantes.append("yt-dlp")
    
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        dependencias_faltantes.append("ffmpeg")
    
    if dependencias_faltantes:
        print("\n❌ Faltan dependencias. Instálalas con:")
        if "yt-dlp" in dependencias_faltantes:
            print("   brew install yt-dlp")
            print("   # o: pip install yt-dlp")
        if "ffmpeg" in dependencias_faltantes:
            print("   brew install ffmpeg")
        print()
        return False
    return True


def descargar_mp3(busqueda_o_url: str):
    """Descarga una canción como MP3."""
    
    # Crear carpeta de salida si no existe
    CARPETA_SALIDA.mkdir(exist_ok=True)
    
    # Determinar si es URL o búsqueda
    if busqueda_o_url.startswith(("http://", "https://", "www.")):
        url = busqueda_o_url
        print(f"\n🔗 Descargando desde URL...")
    else:
        url = f"ytsearch1:{busqueda_o_url}"
        print(f"\n🔍 Buscando: {busqueda_o_url}")
    
    # Comando yt-dlp optimizado para MP3 de carro
    comando = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", CALIDAD_MP3 + "K",
        "--embed-thumbnail",           # Agrega carátula (algunos carros la muestran)
        "--add-metadata",              # Agrega metadatos (título, artista)
        "--output", str(CARPETA_SALIDA / "%(title)s.%(ext)s"),
        "--no-playlist",               # Solo descarga un video, no playlists completas
        "--restrict-filenames",        # Usa nombres de archivo seguros
        "--progress",
        url
    ]
    
    try:
        print(f"📥 Descargando y convirtiendo a MP3...")
        resultado = subprocess.run(comando, check=True)
        print(f"✅ ¡Descarga completada!")
        print(f"📁 Guardado en: {CARPETA_SALIDA}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al descargar: {e}")
        return False


def descargar_playlist(url: str):
    """Descarga una playlist completa de YouTube."""
    
    CARPETA_SALIDA.mkdir(exist_ok=True)
    
    print(f"\n📋 Descargando playlist...")
    
    comando = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", CALIDAD_MP3 + "K",
        "--embed-thumbnail",
        "--add-metadata",
        "--output", str(CARPETA_SALIDA / "%(playlist_index)02d - %(title)s.%(ext)s"),
        "--yes-playlist",
        "--progress",
        url
    ]
    
    try:
        subprocess.run(comando, check=True)
        print(f"✅ ¡Playlist descargada!")
        print(f"📁 Guardado en: {CARPETA_SALIDA}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False


def modo_interactivo():
    """Modo interactivo para descargar múltiples canciones."""
    
    print("\n" + "="*50)
    print("🎵 DESCARGADOR DE MP3 PARA USB DE CARRO 🚗")
    print("="*50)
    print(f"\n📁 Las canciones se guardarán en: {CARPETA_SALIDA}")
    print("\nOpciones:")
    print("  • Escribe el nombre de una canción para buscarla")
    print("  • Pega una URL de YouTube para descargarla")
    print("  • Escribe 'playlist URL' para descargar playlist completa")
    print("  • Escribe 'salir' para terminar\n")
    
    while True:
        try:
            entrada = input("🎤 Canción o URL: ").strip()
            
            if not entrada:
                continue
            
            if entrada.lower() in ["salir", "exit", "q", "quit"]:
                print("\n👋 ¡Hasta luego! Disfruta tu música 🎶")
                break
            
            if entrada.lower().startswith("playlist "):
                url = entrada[9:].strip()
                descargar_playlist(url)
            else:
                descargar_mp3(entrada)
            
            print()  # Línea en blanco para separar
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break


def mostrar_contenido_carpeta():
    """Muestra las canciones descargadas."""
    if not CARPETA_SALIDA.exists():
        print("📁 Aún no hay canciones descargadas.")
        return
    
    mp3s = list(CARPETA_SALIDA.glob("*.mp3"))
    if not mp3s:
        print("📁 Aún no hay canciones descargadas.")
        return
    
    print(f"\n📁 Canciones en {CARPETA_SALIDA}:")
    for i, mp3 in enumerate(sorted(mp3s), 1):
        tamaño = mp3.stat().st_size / (1024 * 1024)  # MB
        print(f"   {i}. {mp3.name} ({tamaño:.1f} MB)")
    print(f"\n   Total: {len(mp3s)} canciones")


def main():
    # Verificar dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    # Si hay argumentos, descargar directamente
    if len(sys.argv) > 1:
        entrada = " ".join(sys.argv[1:])
        
        if entrada == "--list":
            mostrar_contenido_carpeta()
        elif entrada.lower().startswith("playlist "):
            descargar_playlist(entrada[9:])
        else:
            descargar_mp3(entrada)
    else:
        # Modo interactivo
        modo_interactivo()


if __name__ == "__main__":
    main()
