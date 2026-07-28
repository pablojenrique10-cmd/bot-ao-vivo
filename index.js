const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const QRCode = require('qrcode');
const pino = require('pino');
const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;

let latestQrImage = '';
let isConnected = false;

// Página Web para exibir o QR Code
app.get('/qr', (req, res) => {
    if (isConnected) {
        return res.send(`
            <html style="background:#111;color:#fff;font-family:sans-serif;text-align:center;padding-top:50px;">
                <h2>✅ WhatsApp já está conectado!</h2>
                <p>O bot está ativo e pronto para responder.</p>
            </html>
        `);
    }

    if (!latestQrImage) {
        return res.send(`
            <html style="background:#111;color:#fff;font-family:sans-serif;text-align:center;padding-top:50px;">
                <h2>⏳ Gerando QR Code...</h2>
                <p>Aguarde alguns segundos e <a href="/qr" style="color:#00ff88;">clique aqui para atualizar</a>.</p>
                <script>setTimeout(() => { location.reload(); }, 5000);</script>
            </html>
        `);
    }

    res.send(`
        <html style="background:#111;color:#fff;font-family:sans-serif;text-align:center;padding-top:30px;">
            <h2>Escaneie o QR Code abaixo com seu WhatsApp:</h2>
            <img src="${latestQrImage}" style="width:300px;height:300px;border:8px solid white;border-radius:12px;margin:20px;" />
            <p style="color:#aaa;">Esta página atualiza automaticamente.</p>
            <script>setTimeout(() => { location.reload(); }, 15000);</script>
        </html>
    `);
});

app.get('/', (req, res) => {
    res.send('Bot Online! Acesse <a href="/qr">/qr</a> para conectar ou checar status.');
});

app.listen(PORT, () => {
    console.log(`Servidor Web rodando na porta ${PORT}`);
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

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            isConnected = false;
            latestQrImage = await QRCode.toDataURL(qr);
            console.log('⚡ NOVO QR CODE GERADO! Acesse /qr para escanear.');
        }

        if (connection === 'close') {
            isConnected = false;
            latestQrImage = '';
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

            console.log(`Conexão fechada. Reconectando em 5 segundos...`);
            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 5000);
            }
        } else if (connection === 'open') {
            isConnected = true;
            latestQrImage = '';
            console.log('✅ Bot conectado ao WhatsApp com sucesso!');
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg.message) return;

        const from = msg.key.remoteJid;
        
        // Pega o texto da mensagem independente do tipo (texto simples ou resposta estendida)
        const body = msg.message.conversation || 
                     msg.message.extendedTextMessage?.text || 
                     msg.message.buttonsResponseMessage?.selectedButtonId || '';
        
        const texto = body.toLowerCase().trim();

        // Exibe no console toda mensagem que chega para acompanhamento nos Logs do Render
        console.log(`📩 Mensagem de ${from}: "${body}" (Mensagem própria: ${msg.key.fromMe})`);

        // Ignora se for o próprio bot enviando mensagem
        if (msg.key.fromMe) return;

        // Responde se contiver oi, ola, olá ou menu
        if (['oi', 'ola', 'olá', 'menu'].includes(texto) || texto.includes('oi') || texto.includes('menu')) {
            const menu = `📺 *MENU PHZIN TV*\n\nOlá! Seja bem-vindo(a). 😊\nEscolha uma das opções:\n\n1️⃣ Ver planos\n2️⃣ Solicitar teste grátis\n3️⃣ Comprar assinatura\n6️⃣ Falar com atendente`;
            await sock.sendMessage(from, { text: menu });
            console.log(`✅ Menu enviado para ${from}`);
        }
    });
}

connectToWhatsApp();
