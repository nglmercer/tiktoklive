import asyncio
import aiohttp
import json
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent, DisconnectEvent
from typing import List
from collections import deque
from datetime import datetime, timedelta

usuario = input("Introduce el nombre de usuario: ")

#client: TikTokLiveClient = TikTokLiveClient(usuario)
client: TikTokLiveClient = TikTokLiveClient(usuario)

# Crear una lista de comentarios y regalos recibidos
comments_list: List[str] = []
unique_comments_list: deque = deque(maxlen=900)  # Lista de comentarios únicos

# Filtro de tiempo entre comentarios (en segundos)
tiempo_entre_comentarios = 2

# URL base de la API de MixItUp
base_url = "http://localhost:8911/api/v2"

# Endpoint para enviar un mensaje al chat
chat_endpoint = "/chat/message"

# Credenciales de autenticación
headers = {
    "Authorization": "Bearer <tu_token_de_autenticación>",
    "Content-Type": "application/json"
}

async def send_message(message):
    async with aiohttp.ClientSession() as session:
        # Creación del objeto de mensaje
        chat_message = {
            "Message": message,
            "Platform": "Twitch",  # Cambiar según la plataforma correspondiente
            "SendAsStreamer": False
        }
        
        async with session.post(base_url + chat_endpoint, headers=headers, data=json.dumps(chat_message)) as response:
            if response.status == 200:
                print(f"enviado : {message}")

@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Conectado a la sala ID:", client.room_id)
@client.on("comment")
async def on_tiktok_comment(event: CommentEvent):
    comment = f"{event.comment}"

    if not comment.startswith("/") and not comment.startswith(".") and not any(char in comment for char in "*_-+=;:,?()[]{}<>\\/|#@\"'`^&%$"):
        # Filtro de tiempo de espera entre comentarios
        current_time = datetime.now()
        if unique_comments_list and (current_time - unique_comments_list[-1][1]).total_seconds() < tiempo_entre_comentarios:
            # El comentario se envió demasiado rápido, no pasa el filtro
            print(f"Comentario enviado demasiado rápido: {comment}")
            return

        # Filtro de comentarios duplicados
        if comment in [c[0] for c in unique_comments_list]:
            # El comentario es un duplicado, no pasa el filtro
            print(f"Comentario duplicado eliminado: {comment}")
            return

        unique_comments_list.append((comment, current_time))
        comments_list.append(comment)

        if comment.startswith("!") and len(comment) >= 2:
            username = ""
        else:
            username = f" de {event.user.nickname} "
        comments_list.append(comment)
        await send_message(comment)

@client.on("gift")
async def on_gift(event: GiftEvent):
    message = f"{event.gift.info.name}"
    print(f"{event.gift.info.name}")
    giftuser = f" de {event.user.unique_id}"
    comments_list.append(message)
    await send_message(message)

@client.on("disconnect")
async def on_disconnect(event: DisconnectEvent):
    print("reconectando...")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [client.run()]
    loop.run_until_complete(asyncio.gather(*tasks))
    
