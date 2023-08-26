const fs = require('fs');
const { WebcastPushConnection } = require('tiktok-live-connector');
const sqlite3 = require('sqlite3').verbose();

// Leer el nombre de usuario desde el archivo config.json
let config;
try {
    const configFile = fs.readFileSync('melser.json', 'utf8');
    config = JSON.parse(configFile);
    console.log(config);
} catch (err) {
    console.error('Error al leer el archivo config.json:', err);
    process.exit(2);
}

let tiktokUsername = config.usuario;

// Crea un nuevo objeto envoltorio y pasa el nombre de usuario
let tiktokLiveConnection = new WebcastPushConnection(tiktokUsername);

// Conéctate al chat (también se puede usar await)
tiktokLiveConnection.connect().then(state => {
    console.info(`Conectado a la sala ${state.roomId}`);
}).catch(err => {
    console.error('Fallo al conectar', err);
});

// Crea una conexión a la base de datos SQLite
let db = new sqlite3.Database('message.db', (err) => {
    if (err) {
        console.error('Error al abrir la base de datos:', err);
    } else {
        console.log('Base de datos abierta correctamente');
        // Crea la tabla message si no existe
        db.run(`CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uniqueId TEXT,
            message TEXT
        )`, (err) => {
            if (err) {
                console.error('Error al crear la tabla message:', err);
            } else {
                console.log('Tabla message creada correctamente');
            }
        });
    }
});

let chatMessages = [];
let otherMessages = [];

// Crea un conjunto para almacenar los mensajes únicos
let uniqueMessages = new Set();
let messageCooldowns = new Map();

// Función para verificar el tiempo de espera entre mensajes
function spamFilter(message) {
    const cooldownTime = 100; // Tiempo de espera en milisegundos (en este caso, 1 segundo)

    if (messageCooldowns.has(message)) {
        const lastSentTime = messageCooldowns.get(message);
        const currentTime = Date.now();
        const elapsedTime = currentTime - lastSentTime;

        if (elapsedTime < cooldownTime) {
            // El mensaje se envió demasiado pronto, no pasa el filtro
            return false;
        }
    }

    // Actualiza el tiempo de envío del mensaje
    messageCooldowns.set(message, Date.now());
    return true;
}
// Función para guardar los mensajes en la base de datos
function guardarMensajes() {
    if (chatMessages.length > 0) {
        // Inserta los mensajes del chat en la base de datos
        let chatValues = chatMessages.map(({ uniqueId, message }) => `('chat', '${uniqueId}', '${message.replace(/'/g, "''")}')`).join(',');
        db.run(`INSERT INTO message (uniqueId, message) VALUES ${chatValues}`, function(err) {
            if (err) {
                console.error('Error al guardar mensajes de chat en la base de datos:', err);
            }
        });

        // Limpia el array de mensajes del chat
        chatMessages = [];
    }

    if (otherMessages.length > 0) {
        // Inserta los otros mensajes en la base de datos
        let otherValues = otherMessages.map(({ uniqueId, message }) => `('${uniqueId}', '${message.replace(/'/g, "''")}')`).join(',');
        db.run(`INSERT INTO message (uniqueId, message) VALUES ${otherValues}`, function(err) {
            if (err) {
                console.error('Error al guardar otros mensajes en la base de datos:', err);
            }
        });

        // Limpia el array de otros mensajes
        otherMessages = [];
    }
}

// Establece un intervalo para guardar los mensajes cada 3 segundos
setInterval(guardarMensajes, 300);

// Establece un intervalo para borrar el diccionario cada 15 segundos
setInterval(() => {
    uniqueMessages.clear();
    messageCooldowns.clear();
    console.log("Diccionario borrado");
}, 500);

// En el evento 'chat'
tiktokLiveConnection.on('chat', data => {
    console.log(`${data.uniqueId} : ${data.comment}`);
    let comment = data.comment;
    let filteredComment = comment.replace(/[-*_+=;:,?()[\]{}<>\\/|#@\"'`^&%$]/g, ''); // Eliminar símbolos del mensaje
    let messageText = filteredComment.length <= 15 ? filteredComment : data.uniqueId; // Establecer el mensaje como el comentario si es corto, de lo contrario, usar data.uniqueId

    // Filtro de spam y mensajes repetidos
    if (spamFilter(messageText) && !uniqueMessages.has(messageText)) {
        chatMessages.push({ uniqueId: data.uniqueId, message: messageText });
        uniqueMessages.add(messageText);
    } else {
        // Elimina el mensaje que no pasa el filtro
        console.log(`Mensaje eliminado: ${data.uniqueId} : ${data.comment}`);
    }
});

// En los otros eventos (gift, envelope, subscribe, follow)
tiktokLiveConnection.on('gift', data => {
    // ...
    otherMessages.push({ uniqueId: data.uniqueId, message: `${data.giftName} de ${data.uniqueId}` });
});

tiktokLiveConnection.on(data => {
    // ...
    otherMessages.push({uniqueId: '', message: `${data.uniqueId} envio ${data} `});
});

tiktokLiveConnection.on( data => {
    // ...
    otherMessages.push({  uniqueId: '', message: `${data.uniqueId} se suscribió!` });
});

tiktokLiveConnection.on(data => {
    // ...
    otherMessages.push({ uniqueId: '', message: `${data.uniqueId} te sigue!` });
});