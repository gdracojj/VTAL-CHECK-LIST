const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const API_URL = 'http://127.0.0.1:8000/api/messages';

const MONITORED_GROUPS = [
    // Adicione aqui os IDs dos grupos autorizados.
    // Exemplo:
    // 'ID_DO_GRUPO'
];

const client = new Client({
    authStrategy: new LocalAuth({
        clientId: 'controlops'
    }),
    puppeteer: {
        headless: true
    }
});


client.on('qr', (qr) => {
    console.log('\nESCANEIE O QR CODE COM O WHATSAPP:\n');

    qrcode.generate(qr, {
        small: true
    });
});


client.on('authenticated', () => {
    console.log('WhatsApp autenticado.');
});


client.on('ready', () => {
    console.log('\nWhatsApp conectado com sucesso!');
    console.log('ControlOps pronto para monitoramento.\n');
});


client.on('message', async (message) => {

    if (!message.from.endsWith('@g.us')) {
        return;
    }


    if (
        MONITORED_GROUPS.length > 0 &&
        !MONITORED_GROUPS.includes(message.from)
    ) {
        return;
    }


    const receivedAt = new Date(
        message.timestamp * 1000
    ).toISOString();


    console.log('----------------------------------------');

    console.log(
        'GRUPO ID:',
        message.from
    );

    console.log(
        'REMETENTE:',
        message.author || 'individual'
    );

    console.log(
        'MENSAGEM:',
        message.body
    );

    console.log(
        'HORÁRIO:',
        new Date(
            message.timestamp * 1000
        ).toLocaleString('pt-BR')
    );


    try {

        const response = await fetch(
            API_URL,
            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({
                    group: message.from,
                    message: message.body,
                    received_at: receivedAt
                })
            }
        );


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


    console.log(
        '----------------------------------------'
    );
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