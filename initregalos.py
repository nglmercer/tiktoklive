import subprocess
import time
import threading

# Función para iniciar los dos programas
def start_programs():
    subprocess.Popen(['python', 'tiktokmensajes.py'])
    subprocess.Popen(['python', 'twregalos.py'])
    subprocess.Popen(['python', 'twmensajes.py'])
# Función para detener los dos programas
def stop_programs():
    subprocess.call(['taskkill', '/F', '/IM', 'python.exe'])

# Función para reiniciar los dos programas
def restart_programs():
    global estado, ultimo_tiempo_actividad
    stop_programs()
    time.sleep(1)  # Esperar un segundo para asegurarse de que los programas se hayan detenido
    start_programs()
    estado = "activo"
    print("Estado: Activo")
    ultimo_tiempo_actividad = time.time()

# Función para crear el temporizador y reiniciar los programas cada cierto tiempo
def reiniciar_cada_x_tiempo(tiempo_reinicio):
    global tiempo_reinicio_actual, estado, ultimo_tiempo_actividad
    tiempo_reinicio_actual = tiempo_reinicio
    print(f"Tiempo de reinicio: {tiempo_reinicio_actual} seg")
    estado = "activo"
    ultimo_tiempo_actividad = time.time()
    timer = threading.Timer(tiempo_reinicio_actual, reiniciar_cada_x_tiempo, args=(tiempo_reinicio_actual,))
    timer.start()
    restart_programs()

# Función para actualizar el tiempo de reinicio
def actualizar_tiempo_reinicio(tiempo_reinicio_nuevo):
    global tiempo_reinicio_actual
    tiempo_reinicio_actual = tiempo_reinicio_nuevo
    print(f"Tiempo de reinicio actualizado: {tiempo_reinicio_actual} seg")

# Función para cerrar la ventana y detener los programas
def on_closing():
    stop_programs()

# Iniciar los programas al inicio del script
start_programs()

# Crear el temporizador y reiniciar los programas cada cierto tiempo
tiempo_reinicio_actual = 300 # 1 minuto
reiniciar_cada_x_tiempo(tiempo_reinicio_actual)

# Mostrar el estado actual
estado = "activo"
print("Estado: Activo")


# Ejecutar el bucle principal de la consola
while True:
    entrada = input("Introduce una letra (r para reiniciar, d para detener, t para actualizar el tiempo de reinicio): ")
    if entrada.lower() == "r":
        restart_programs()
    elif entrada.lower() == "d":
        stop_programs()
        estado = "inactivo"
        print("Estado: Inactivo")
    elif entrada.lower() == "t":
        tiempo_reinicio_nuevo = int(input("Introduce el nuevo tiempo de reinicio en segundos: "))
        actualizar_tiempo_reinicio(tiempo_reinicio_nuevo)
    else:
        print("Entrada inválida. Introduce r para reiniciar, d para detener, t para actualizar el tiempo de reinicio.")
    
    # Actualizar el tiempo de la última actividad en los programas
    ultimo_tiempo_actividad = time.time()