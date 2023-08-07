from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent, DisconnectEvent
import sqlite3
import asyncio
import time

messages_db = sqlite3.connect("messages.db")
messages_cursor = messages_db.cursor()

# Crear la tabla `messages` si no existe
messages_cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT,
        message TEXT
    )
""")
messages_db.commit()

db = sqlite3.connect("regalos.db")
cursor = db.cursor()

# Crear la tabla `messages` si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT,
        message TEXT
    )
""")
db.commit()

client: TikTokLiveClient = TikTokLiveClient(unique_id="@melserngl")

# Crear una lista de comentarios y regalos recibidos
comments_list = []
gifts_list = []

@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)

#comentarios es a {event.comment}
@client.on("comment")
async def on_tiktok_comment(event: CommentEvent):
    comment = f"{event.comment}"
    with open("regalos.txt", "a") as file:
        file.write(comment)
    if not comment.startswith("/") and not comment.startswith(".") and not any(char in comment for char in "*_-+=;:,?()[]{}<>\\/|#@\"'`^&%$"):  # Verificar si el comentario no comienza con '/', '.' y no contiene caracteres especiales
        if len(comment) <= 10:
            # Comentario corto, enviar como mensaje normal
            messages_cursor.execute("INSERT INTO messages (channel, message) VALUES (?, ?)", ("tiktok",comment))
        else:
            # Comentario largo, enviar con el número de usuario
            username = f" - {event.user.nickname} "
            messages_cursor.execute("INSERT INTO messages (channel, message) VALUES (?, ?)", ("tiktok",comment + username))
        messages_db.commit()
        comments_list.append(comment)  # Agregar el comentario a la lista

@client.on("gift")
async def on_gift(event: GiftEvent):
    message = f"{event.gift.info.name} " 
    print(f"{event.gift.info.name} " )
    cursor.execute("INSERT INTO messages (channel, message) VALUES (?, ?)", ("tiktok", message ))
    db.commit()
    comments_list.append(message)

@client.on("disconnect")
async def on_disconnect(event: DisconnectEvent):
    reconnect() 
    await asyncio.sleep(5) 
def reconnect():
    print("reconectando...")

async def send_db_message():
    while True:
        c = messages_db.cursor()
        c.execute('SELECT message FROM messages ORDER BY id DESC LIMIT 1')
        message = c.fetchone()
        if message is not None:
            message = message[0]
            comments_list.append(message)  # Agregar el comentario a la lista
        if comments_list:
            comments_list.clear()  # Vaciar la lista
        await asyncio.sleep(2)  # 

async def send_db_gift():
    while True:
        c = db.cursor()
        c.execute('SELECT message FROM messages ORDER BY id DESC LIMIT 1')
        message = c.fetchone()
        if message is not None:
            message = message[0]
            comments_list.append(message)  # Agregar el comentario a la lista
        if comments_list:
            comments_list.clear()  # Vaciar la lista
        await asyncio.sleep(2)  # 

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_db_message())
    loop.create_task(send_db_gift())
    client.run()
    