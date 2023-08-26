import time
import threading
import subprocess
import psutil
import signal

# Lista de nombres de procesos a verificar
program_names = ['mixitupfinal.py', 'tkme.js', 'twitchTransFN.exe']

def handle_interrupt(signal, frame):
    stop_programs()

signal.signal(signal.SIGINT, handle_interrupt)

# Función para verificar si los programas ya están en ejecución
def check_programs_running():
    for name in program_names:
        for proc in psutil.process_iter(['name']):
            if name in proc.info['name']:
                return True
    return False

# Función para iniciar los dos programas si no están en ejecución
def start_programs():
    if not check_programs_running():
        subprocess.Popen(['python', 'C:/Users/melser/Downloads/MineCraftTikTokLive-main/tikme/mixitupfinal.py'])
        subprocess.Popen(['node', 'C:/Users/melser/Downloads/MineCraftTikTokLive-main/tikme/tkme.js'])
        subprocess.Popen(['python', 'C:/Users/melser/Downloads/MineCraftTikTokLive-main/tikme/tiktokmensajes.py'])
        subprocess.Popen(['Downloads//twitchTransFN//twitchTransFN.exe'])

# Función para detener los dos programas
def stop_programs():
    # Obtener todos los procesos Python y twitchTransFN en ejecución
    processes = [proc for proc in psutil.process_iter() if proc.name() in ["python.exe", "twitchTransFN.exe"]]

    # Terminar los procesos
    for process in processes:
        process.terminate()
        process.wait()

# Función para reiniciar los dos programas
def restart_programs():
    stop_programs()
    time.sleep(0.5)  # Esperar un segundo para asegurarse de que los programas se hayan detenido
    start_programs()

# Función para crear el temporizador y reiniciar los programas cada cierto tiempo
def reiniciar_cada_x_tiempo(tiempo):
    while True:
        # Verificar si los procesos están activos
        mixitup_running = False
        tiktokmensajes_running = False
        twitchtransfn_running = False
        for process in psutil.process_iter():
            try:
                if process.name() == "python.exe":
                    cmdline = process.cmdline()
                    if len(cmdline) > 1 and cmdline[1] == "mixitupfinal.py":
                        mixitup_running = True
                    elif len(cmdline) > 1 and cmdline[1] == "tikme.js":
                        tiktokmensajes_running = True
                elif process.name() == "twitchTransFN.exe":
                    twitchtransfn_running = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Reiniciar los procesos si es necesario
        if not mixitup_running or not tiktokmensajes_running or not twitchtransfn_running:
            restart_programs()

        time.sleep(2)

# Iniciar los programas al inicio del script
start_programs()

# Ejecutar el bucle principal de la consola
while True:
    entrada = input("Introduce una letra (r para reiniciar): ")
    if entrada.lower() == "r":
        restart_programs()