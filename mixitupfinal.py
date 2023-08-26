import json
import asyncio
import aiosqlite
import aiohttp
import os

# URL base de la API de MixItUp
base_url = "http://localhost:8911/api/v2"

# Endpoint para enviar un mensaje al chat
chat_endpoint = "/chat/message"

# Credenciales de autenticación
headers = {
    "Authorization": "Bearer <tu_token_de_autenticación>",
    "Content-Type": "application/json"
}

# Lista para almacenar los mensajes recibidos
message_list = []

async def send_message():
    db_path = os.path.join(os.path.dirname(__file__), "message.db")  # Ruta relativa a la base de datos

    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("SELECT * FROM message") as cursor:
            messages = await cursor.fetchall()

            async with aiohttp.ClientSession() as session:
                for message in messages:
                    # Creación del objeto de mensaje
                    chat_message = {
                        "Message": message[3],  # El mensaje se encuentra en la tercera columna de la tabla
                        "Platform": "Twitch",  # Cambiar según la plataforma correspondiente
                        "SendAsStreamer": False
                    }

                    # Envío del mensaje al chat
                    async with session.post(base_url + chat_endpoint, headers=headers, data=json.dumps(chat_message)) as response:
                        # Verificación de la respuesta
                        if response.status == 200:
                            # Eliminación del mensaje de la base de datos
                            await conn.execute("DELETE FROM message WHERE id = ?", (message[0],))  # El ID del mensaje se encuentra en la primera columna de la tabla
                            await conn.commit()
                            print("Mensaje enviado", message)
                        else:
                            print("Error al enviar:", response.text)

async def main():
    global message_list  # Declarar la variable como global

    while True:
        await send_message()
        await asyncio.sleep(2)

asyncio.run(main())