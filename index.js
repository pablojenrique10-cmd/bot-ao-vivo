const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');
const pino = require('pino');
const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;

let qrCodeData = '';

// Rota para exibir o QR Code em formato de imagem na Web
app.get('/qr', async (req, res) => {
    if (!qrCodeData) {
        return res.send(`
            <html>
                <body style="display:flex;justify-content:center;align-items:center;height:100vh;background:#111;color:#fff;font-family:sans-serif;flex-direction:column;">
                    <h2>QR Code ainda não gerado ou o WhatsApp já está conectado!</h2>
                    <p>Atualize a página em alguns segundos se acabou de reiniciar.</p>
                </body>
            </html>
        `);
    }
    try {
        const url = await QRCode.toDataURL(qrCodeData);
        res.send(`
            <html>
                <body style="display:flex;justify-content:center;align-items:center;height:100vh;background:#111;color:#fff;font-family:sans-serif;flex-direction:column;">
                    <h2>Escaneie o QR Code abaixo no seu WhatsApp:</h2>
                    <img src="${url}" style="width:300px;height:300px;border:10px solid white;border-radius:10px;margin-top:20px;"/>
                </body>
            </html>
        `);
    } catch (err) {
        res.status(500).send('Erro ao gerar imagem do QR Code');
    }
});

app.get('/', (req, res) => {
    res.send('Bot de WhatsApp rodando com sucesso! Acesse /qr para ver o QR Code.');
});

app.listen(PORT, () => {
    console.log(`Servidor HTTP rodando na porta ${PORT}`);
});

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
            qrCodeData = qr;
            console.log('\n--- QR CODE GERADO! Acesse a URL do Render com /qr no final para escanear ---\n');
            qrcodeTerminal.generate(qr, { small: true });
        }

        if (connection === 'close') {
            qrCodeData = '';
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

            console.log(`Conexão fechada. Reconectando em 5 segundos...`);
            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 5000);
            }
        } else if (connection === 'open') {
            qrCodeData = '';
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
