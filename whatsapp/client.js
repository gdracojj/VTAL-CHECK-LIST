const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const API_URL = 'http://127.0.0.1:8000/api/messages';

// Grupo utilizado para teste da coleta histórica
const TEST_GROUP_ID = '120363406687331271@g.us';

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

client.on('ready', async () => {
    console.log('\nWhatsApp conectado com sucesso!');
    console.log('Monitoramento de mensagens ativo.\n');

    const TEST_GROUP_ID = '120363406687331271@g.us';

    try {
        console.log('Testando getChatModel...');

        const resultado = await client.pupPage.evaluate(
            async (groupId) => {
                const chat = await window.WWebJS.getChatModel(groupId);

                if (!chat) {
                    return {
                        encontrado: false
                    };
                }

                return {
                    encontrado: true,
                    id: chat.id?._serialized || null,
                    nome: chat.name || chat.formattedTitle || null,
                    tipo: chat.id?.server || null
                };
            },
            TEST_GROUP_ID
        );

        console.log('\nRESULTADO getChatModel:');
        console.log(resultado);

    } catch (error) {
        console.error(
            '\nERRO NO getChatModel:',
            error.message
        );
    }
});

client.on('message', async (message) => {
    // Ignora mensagens individuais
    if (!message.from.endsWith('@g.us')) {
        return;
    }

    const receivedAt = new Date(
        message.timestamp * 1000
    ).toISOString();

    console.log('----------------------------------------');
    console.log('GRUPO ID:', message.from);
    console.log(
        'REMETENTE:',
        message.author || 'individual'
    );
    console.log('MENSAGEM:', message.body);
    console.log(
        'HORÁRIO:',
        new Date(
            message.timestamp * 1000
        ).toLocaleString('pt-BR')
    );

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                group: message.from,
                message: message.body,
                received_at: receivedAt
            })
        });

        const result = await response.json();

        console.log(
            'ENVIADO PARA API:',
            response.status
        );

        console.log(
            'RESULTADO:',
            result
        );

    } catch (error) {
        console.error(
            'ERRO AO ENVIAR PARA API:',
            error.message
        );
    }

    console.log('----------------------------------------');
});

client.on('auth_failure', (msg) => {
    console.error(
        'Falha na autenticação:',
        msg
    );
});

client.on('disconnected', (reason) => {
    console.log(
        'WhatsApp desconectado:',
        reason
    );
});

client.initialize();