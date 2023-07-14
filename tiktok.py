from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent
import sqlite3
import asyncio
import time

db = sqlite3.connect("messages.db")
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

client: TikTokLiveClient = TikTokLiveClient(unique_id="@axil_pon")

# Crear una lista de comentarios y regalos recibidos
comments_list = []
gifts_list = []

@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)

@client.on("comment")
async def on_tiktok_comment(event: CommentEvent):
    comment = event.comment
    print(comment)
    cursor.execute("INSERT INTO messages (channel, message) VALUES (?, ?)", ("tiktok", comment))
    db.commit()
    comments_list.append(comment)  # Agregar el comentario a la lista

@client.on("gift")
async def on_gift(event: GiftEvent):
    message = f"{event.gift.info.name} " 
    print(f"{event.gift.info.name} " )
    cursor.execute("INSERT INTO messages (channel, message) VALUES (?, ?)", ("tiktok", message))
    db.commit()
    comments_list.append(message)

async def send_db_message():
    # Enviar el último mensaje de la base de datos al chat de Twitch
    channel = "nglmercer"
    delete_count = 0  # Agregar una variable para contar los segundos
    while True:
        c = db.cursor()
        c.execute('SELECT message FROM messages ORDER BY id DESC LIMIT 1')
        message = c.fetchone()
        if message is not None:
            message = message[0]
            comments_list.append(message)  # Agregar el comentario a la lista
        if comments_list:
            print(comments_list)  # Imprimir la lista de comentarios en la consola
            comments_list.clear()  # Vaciar la lista
        await asyncio.sleep(1)  # 

def reconnect():
    print("Disconnected from TikTok. Attempting to reconnect...")
    client.run()  # Vuelve a ejecutar el cliente TikTokLiveClient

@client.on("disconnect")
async def on_disconnect():
    reconnect()  # Llama a la función de reconexión en caso de desconexión

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_db_message())
    try:
        client.run()
    except Exception as e:
        print("An error occurred:", e)
        print("Waiting 5 seconds before reconnecting...")
        time.sleep(5)  # Espera 5 segundos antes de intentar reconectar
        reconnect()
    loop.run_forever()
