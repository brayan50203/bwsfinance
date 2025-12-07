/**
 * BWS Finance WhatsApp Bot - Venom ULTRA SIMPLES
 */

const venom = require('venom-bot');

console.log('='.repeat(60));
console.log('BWS Finance WhatsApp Bot - VENOM');
console.log('='.repeat(60));
console.log('');
console.log('Aguarde... Iniciando Venom Bot...');
console.log('');

venom
    .create({
        session: 'bws-venom-v2',
        multidevice: true,  // ATIVADO multidevice
        headless: false,  // MOSTRAR NAVEGADOR
        useChrome: true,
        debug: true,  // ATIVADO debug
        logQR: true,
        disableWelcome: true,
        updatesLog: true,  // ATIVADO updates
        browserArgs: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ],
        catchQR: (base64Qrimg, asciiQR, attempts, urlCode) => {
            console.log('');
            console.log('='.repeat(60));
            console.log(`QR CODE - Tentativa ${attempts}`);
            console.log('='.repeat(60));
            console.log(asciiQR);
            console.log('='.repeat(60));
            console.log('Escaneie com seu WhatsApp!');
            console.log('='.repeat(60));
            console.log('');
        },
        statusFind: (statusSession, session) => {
            console.log(`STATUS: ${statusSession}`);
        }
    })
    .then((client) => {
        console.log('');
        console.log('='.repeat(60));
        console.log('WHATSAPP CONECTADO COM SUCESSO!');
        console.log('='.repeat(60));
        console.log('');
        
        // TESTE 1: onMessage
        client.onMessage((message) => {
            console.log('');
            console.log('*** onMessage DISPAROU! ***');
            console.log(`Tipo: ${message.type}`);
            console.log(`De: ${message.from}`);
            console.log(`Grupo?: ${message.isGroupMsg}`);
            console.log(`Minha?: ${message.fromMe}`);
            console.log(`Mensagem: ${message.body}`);
            console.log('');
            
            if (message.isGroupMsg || message.fromMe) {
                console.log('Ignorada (grupo ou minha mensagem)');
                return;
            }
            
            console.log('PROCESSANDO MENSAGEM!');
            client.sendText(message.from, `Recebi sua mensagem: "${message.body}"`);
        });
        
        // TESTE 2: onAnyMessage (captura TUDO)
        client.onAnyMessage((message) => {
            console.log('');
            console.log('*** onAnyMessage DISPAROU! ***');
            console.log(JSON.stringify(message, null, 2));
            console.log('');
        });
        
        console.log('Aguardando mensagens...');
        
    })
    .catch((error) => {
        console.error('');
        console.error('ERRO AO INICIAR VENOM:');
        console.error(error);
        console.error('');
    });
