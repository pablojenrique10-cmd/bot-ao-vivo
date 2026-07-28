const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const express = require('express');

// Cria servidor Web simples para o Render não cancelar o Deploy
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.send('Bot de WhatsApp está rodando!');
});

app.listen(PORT, () => {
    console.log(`Servidor HTTP rodando na porta ${PORT}`);
});

// Lógica do WhatsApp
async function connectToWhatsApp() {
    const { version } = await fetchLatestBaileysVersion();
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');

    const sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: 'silent' }),
        printQRInTerminal: false,
        browser: ['Ubuntu', 'Chrome', '20.0.04']
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n======================================================');
            console.log('       ESCANEIE O QR CODE ABAIXO NO SEU WHATSAPP       ');
            console.log('======================================================\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

            console.log(`Conexão fechada. Reconectando em 5 segundos...`);

            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 5000);
            }
        } else if (connection === 'open') {
            console.log('✅ Bot conectado ao WhatsApp com sucesso!');
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg.message || msg.key.fromMe) return;

        const from = msg.key.remoteJid;
        const body = msg.message.conversation || msg.message.extendedTextMessage?.text || '';
        const texto = body.toLowerCase().trim();

        if (['oi', 'ola', 'olá', 'menu'].includes(texto)) {
            const menu = `📺 *MENU PHZIN TV*\n\nOlá! Seja bem-vindo(a). 😊\nEscolha uma das opções:\n\n1️⃣ Ver planos\n2️⃣ Solicitar teste grátis\n3️⃣ Comprar assinatura\n6️⃣ Falar com atendente`;
            await sock.sendMessage(from, { text: menu });
        }
    });
}

connectToWhatsApp();
