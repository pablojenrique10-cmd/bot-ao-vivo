const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');

async function connectToWhatsApp() {
    // Salva a sessão para não precisar escanear o QR Code toda vez
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');

    const sock = makeWASocket({
        auth: state,
        logger: pino({ level: 'silent' })
    });

    sock.ev.on('creds.update', saveCreds);

    // Gerencia a conexão e gera o QR Code nos logs
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n--- ESCANEIE O QR CODE ABAIXO NO SEU WHATSAPP ---\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut);
            console.log('Conexão fechada. Reconectando:', shouldReconnect);
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('✅ Bot conectado ao WhatsApp com sucesso!');
        }
    });

    // Ouve as mensagens recebidas
    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg.message || msg.key.fromMe) return;

        const from = msg.key.remoteJid;
        const body = msg.message.conversation || msg.message.extendedTextMessage?.text || '';
        const texto = body.toLowerCase().trim();

        console.log(`Mensagem recebida de ${from}: ${texto}`);

        // Exemplo de resposta ao Menu
        if (['oi', 'ola', 'olá', 'menu'].includes(texto)) {
            const menu = `📺 *MENU PHZIN TV*\n\nOlá! Seja bem-vindo(a). 😊\nEscolha uma das opções:\n\n1️⃣ Ver planos\n2️⃣ Solicitar teste grátis\n3️⃣ Comprar assinatura\n6️⃣ Falar com atendente`;
            
            await sock.sendMessage(from, { text: menu });
        }
    });
}

connectToWhatsApp();
