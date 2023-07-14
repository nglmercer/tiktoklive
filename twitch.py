from twitchio.ext import commands
import asyncio
import sqlite3
import random
import os

db = sqlite3.connect("messages.db")
cursor = db.cursor()
comments_list = []

class Bot(commands.Bot):
    def __init__(self, token, prefix, initial_channels):
        # Configurar bot con el token, prefijo y canal de Twitch
        super().__init__(token=token, prefix=prefix, initial_channels=initial_channels)
        self.messages = []
        self.timer = None
        self.comments_list = [] 
        
    async def send_twitch_message(self, channel, message):
        # Enviar el mensaje al chat de Twitch
        await self.get_channel(channel).send(message)
        # Eliminar el mensaje de la base de datos
        c = db.cursor()
        c.execute('DELETE FROM messages WHERE message = ?', (message,))
        db.commit()

    async def event_ready(self):
        # Imprimir un mensaje cuando el bot se conecta al chat de Twitch
        print(f"Ya llegué al chat como {self.nick}!")
        # Iniciar el temporizador para enviar mensajes cada 5 minutos
        self.timer = asyncio.create_task(self.send_messages())

    async def event_message(self, message):
        # Imprimir el mensaje en la consola
        print(f"{message.author}: {message.content}")

    async def send_messages(self):
        # Enviar mensajes predeterminados en intervalos regulares
        channel = "nglmercer"
        while True:
            if self.comments_list:
                # Tomar un mensaje aleatorio de la lista de comentarios
                message = random.choice(self.comments_list)
                await self.send_twitch_message(channel, message)
                self.comments_list.remove(message)  # Eliminar el mensaje de la lista
            await asyncio.sleep(3)  # Esperar 5 segundos

async def send_db_message():
    # Enviar los últimos tres mensajes de la base de datos al chat de Twitch
    channel = "nglmercer"
    messages = []  # Agregar una lista para almacenar los últimos tres mensajes
    while True:
        c = db.cursor()
        c.execute('SELECT message FROM messages ORDER BY id DESC LIMIT 3')
        new_messages = c.fetchall()
        for message in reversed(new_messages):
            if message not in messages and message[0] not in bot.comments_list:  # Comparar el nuevo mensaje con la lista de mensajes y la lista de comentarios
                messages.append(message)  # Agregar el mensaje a la lista
                print(f"Mensaje guardado: {message[0]}")  # Imprimir el mensaje guardado en la consola
        if messages:
            print(messages)  # Imprimir la lista de mensajes en la consola
            message = messages.pop(0)  # Tomar el primer mensaje de la lista de mensajes
            bot.comments_list.append(message[0])  # Agregar el mensaje a la lista de comentarios
        await asyncio.sleep(2)  # Esperar 1 segundo

if __name__ == '__main__':
    # Configurar y ejecutar el bot
    token = 'oauth:d2admt44sfsdttz4g888n2i9pectbi'
    prefix = ''
    initial_channels = ['nglmercer']
    bot = Bot(token, prefix, initial_channels)
    loop = asyncio.get_event_loop()
    loop.create_task(send_db_message())  # Agregar tarea para enviar mensajes de la base de datos
    loop.create_task(bot.send_messages())  # Agregar tarea para enviar mensajes personalizados
    loop.run_until_complete(bot.start())
    loop.run_forever()