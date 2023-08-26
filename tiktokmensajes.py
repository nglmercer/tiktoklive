from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent, DisconnectEvent, EnvelopeEvent
import sqlite3
import asyncio
import os
from asyncio import AbstractEventLoop
import json
import time
import threading

# Ruta relativa a la base de datos
db_path = os.path.join(os.path.dirname(__file__), "message.db")

# Ruta relativa al archivo de configuración
config_path = os.path.join(os.path.dirname(__file__), "config.json")

# Conexión a la base de datos
message_db = sqlite3.connect(db_path)
message_cursor = message_db.cursor()

# Conexión a la base de datos (segunda instancia)
db = sqlite3.connect(db_path)
cursor = db.cursor()

# Leer el archivo de configuración
with open(config_path, 'r') as config_file:
    config = json.load(config_file)
    print(config)

# Obtener el nombre de usuario del archivo de configuración
usuario = config.get('usuario', '')

#client: TikTokLiveClient = TikTokLiveClient(usuario)
client: TikTokLiveClient = TikTokLiveClient(usuario)

# Crear una lista de comentarios y regalos recibidos
comments_list = []
gifts_list = []

# Crear un diccionario para almacenar el tiempo en que se envió cada comentario
comment_cooldowns = {}

# Variable para determinar el tiempo de espera entre comentarios (en segundos)
spam_filter_time = 0

# Función para reiniciar el diccionario cada 0 segundos
def reset_comment_cooldowns():
    global comment_cooldowns
    comment_cooldowns = {}
    threading.Timer(spam_filter_time, reset_comment_cooldowns).start()

# Llamar a la función de reinicio para iniciar el temporizador
reset_comment_cooldowns()

@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Conectado a la sala ID:", client.room_id)

@client.on("comment")
async def on_tiktok_comment(event: CommentEvent):
    comment = f"{event.comment}"

    # Inicializar la lista de comentarios únicos si aún no existe
    if "unique_comments_list" not in globals():
        global unique_comments_list
        unique_comments_list = []

    if not comment.startswith("/") and not comment.startswith(".") and not any(char in comment for char in "*_-+=;:,?()[]{}<>\\/|#@\"'`^&%$"):
        # Filtro de tiempo de espera entre comentarios y eliminación de duplicados
        current_time = time.time()
        if spam_filter_time > 0 and comment in comment_cooldowns or comment in unique_comments_list:
            # El comentario es un duplicado o se envió demasiado rápido, no pasa el filtro
            print(f"Mensaje duplicado o spam eliminado: {comment}")
            return

        comment_cooldowns[comment] = current_time
        comments_list.append(comment)
        unique_comments_list.append(comment)

        # Eliminar comentarios duplicados de la lista
        unique_comments_list = list(set(unique_comments_list))
        if len(unique_comments_list) < len(comments_list):
            print(f"Mensaje duplicado eliminado: {comment}")
            comments_list.pop()
            return

        if comment.startswith("!") and len(comment) >= 3:
            message_cursor.execute("INSERT INTO message (channel, message) VALUES (?, ?)", ("tiktok", comment))
            username = ""
        else:
            username = f" de {event.user.nickname} "
            message_cursor.execute("INSERT INTO message (channel, message) VALUES (?, ?)", ("tiktok", comment + username))
        message_db.commit()

@client.on("gift")
async def on_gift(event: GiftEvent):
    message = f"{event.gift.info.name}" 
    print(f"{event.gift.info.name} " )
    giftuser = f" de {event.user.unique_id}" 
    cursor.execute("INSERT INTO message (channel, message) VALUES (?, ?)", ("tiktok", message + giftuser))
    db.commit()
    comments_list.append(message)

@client.on("disconnect")
async def on_disconnect(event: DisconnectEvent):
    print("reconectando...")

async def send_db_message():
    while True:
        c = message_db.cursor()
        c.execute('SELECT message FROM message ORDER BY id DESC LIMIT 1')
        message = c.fetchone()
        if message is not None:
            message = message[0]
            comments_list.append(message)
        if comments_list:
            temp_list = []
            for comment in comments_list:
                if comment not in temp_list:
                    temp_list.append(comment)
            comments_list = temp_list
        await asyncio.sleep(2)

async def send_db_gift():
    while True:
        c = db.cursor()
        c.execute('SELECT message FROM message ORDER BY id DESC LIMIT 1')
        message = c.fetchone()
        if message is not None:
            message = message[0]
            comments_list.append(message)  # Agregar el comentario a la lista
        if comments_list:
            comments_list.clear()  # Vaciar la lista
        await asyncio.sleep(2)  # 

if __name__ == '__main__':
    loop: AbstractEventLoop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    loop.create_task(send_db_message())
    loop.create_task(send_db_gift())
    loop.create_task(client.run())