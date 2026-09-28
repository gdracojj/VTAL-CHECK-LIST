const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth({
        clientId: 'vtal-ccor'
    }),
    puppeteer: {
        headless: true
    }
});

client.on('qr', (qr) => {
    console.log('\nESCANEIE O QR CODE COM O WHATSAPP:\n');
    qrcode.generate(qr, { small: true });
});

client.on('authenticated', () => {
    console.log('WhatsApp autenticado.');
});

client.on('ready', () => {
    console.log('\nWhatsApp conectado com sucesso!');
    console.log('Monitoramento de mensagens ativo.\n');
});

client.on('message', (message) => {
    if (!message.from.endsWith('@g.us')) {
        return;
    }

    console.log('----------------------------------------');
    console.log('GRUPO ID:', message.from);
    console.log('REMETENTE:', message.author || 'individual');
    console.log('MENSAGEM:', message.body);
    console.log(
        'HORÁRIO:',
        new Date(message.timestamp * 1000).toLocaleString('pt-BR')
    );
    console.log('----------------------------------------');
});

client.on('auth_failure', (msg) => {
    console.error('Falha na autenticação:', msg);
});

client.on('disconnected', (reason) => {
    console.log('WhatsApp desconectado:', reason);
});

client.initialize();