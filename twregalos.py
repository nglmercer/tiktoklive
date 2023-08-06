from twitchio.ext import commands
import asyncio
import sqlite3

db = sqlite3.connect("regalos.db")
cursor = db.cursor()
comments_list = []

class Bot(commands.Bot):
    def __init__(self, token, prefix, initial_channels):
        # Configurar bot con el token, prefijo y canal de Twitch
        super().__init__(token=token, prefix=prefix, initial_channels=initial_channels)
        self.messages = []
        self.timer = None
        self.comments_list = []
        self.db = sqlite3.connect("regalos.db")
        self.cursor = self.db.cursor()
        self.ws_options = {'timeout': 300}

    async def send_twitch_message(self, channel, message):
    # Verificar si el mensaje no está vacío o es None
        if message and message.strip() != "":
        # Enviar el mensaje al chat de Twitch
            await self.get_channel(channel).send(f"{message}")
            await asyncio.sleep(1)
        # Buscar el mensaje original o modificado en la base de datos
            self.cursor.execute('SELECT message FROM messages WHERE message != ? AND (message = ? OR message = ?)', ("", message, message.replace("/", "!")))
            messages = self.cursor.fetchall()
            if messages:
            # Eliminar ambos mensajes de la base de datos
                for msg in messages:
                    self.cursor.execute('DELETE FROM messages WHERE message = ?', (msg[0],))
                    self.db.commit()
                    await asyncio.sleep(1) 

    async def event_ready(self):
        # Imprimir un mensaje cuando el bot se conecta al chat de Twitch
        print(f"Ya llegué al chat como {self.nick}!")
        # Iniciar el temporizador para enviar mensajes cada 5 minutos
        self.timer = asyncio.create_task(self.send_messages())

    async def event_message(self, message):
        # Imprimir el mensaje en la consola
        print(f"{message.content}")

    async def send_messages(self):
        # Enviar mensajes predeterminados y de la base de datos en intervalos regulares
        channel = "nglmercer"
        while True:
            # Obtener una muestra aleatoria de los mensajes de la base de datos
            self.cursor.execute('SELECT message FROM messages WHERE message IS NOT NULL AND message != "" ORDER BY RANDOM() LIMIT 1')
            new_messages = self.cursor.fetchone()
            if new_messages and new_messages[0] not in self.comments_list:
                # Agregar el mensaje a la lista de comentarios y enviarlo al chat de Twitch
                self.comments_list.append(new_messages[0])
                await self.send_twitch_message(channel, new_messages[0])

if __name__ == '__main__':
    # Configurar y ejecutar el bot
    token = 'oauth:spn0gho8t1x65pxnhpo97xlxtat5ps'
    prefix = ''
    initial_channels = ['nglmercer']
    bot = Bot(token, prefix, initial_channels)
    bot.run()