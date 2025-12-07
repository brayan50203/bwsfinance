/**
 * BWS Finance WhatsApp Bot v4.0 - Venom Bot
 * Baseado em: https://github.com/gustavosett/pixzinho-whatsapp-bot
 */

const venom = require('venom-bot');
const express = require('express');
const axios = require('axios');
require('dotenv').config({ path: '../.env' });

const app = express();
app.use(express.json());

const PORT = process.env.WHATSAPP_SERVER_PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://localhost:5000';
const AUTH_TOKEN = process.env.WHATSAPP_AUTH_TOKEN || 'bws_finance_token_55653';

let client = null;
let isReady = false;

console.log('🚀 BWS Finance WhatsApp Bot v4.0 - Venom Bot');
console.log('📱 Porta:', PORT);
console.log('🔗 Flask:', FLASK_URL);
console.log('');

// =========================================
// Funções Auxiliares
// =========================================

function cleanPhoneNumber(phone) {
    return phone.replace('@c.us', '').replace('@g.us', '');
}

function formatPhoneNumber(phone) {
    let clean = phone.replace(/\D/g, '');
    if (!clean.startsWith('+')) {
        clean = '+' + clean;
    }
    return clean;
}

async function sendToFlask(message) {
    try {
        const from = cleanPhoneNumber(message.from);
        const formattedFrom = formatPhoneNumber(from);
        
        console.log(`\n📤 Enviando para Flask:`);
        console.log(`   De: ${formattedFrom}`);
        console.log(`   Mensagem: ${message.body}`);
        
        const payload = {
            from: formattedFrom,
            type: 'text',
            text: message.body || '',
            timestamp: message.timestamp || Date.now()
        };
        
        const response = await axios.post(
            `${FLASK_URL}/api/whatsapp/webhook`,
            payload,
            {
                headers: {
                    'Authorization': `Bearer ${AUTH_TOKEN}`,
                    'Content-Type': 'application/json'
                },
                timeout: 30000
            }
        );
        
        console.log(`✅ Flask respondeu:`, response.data);
        
        // Enviar resposta de volta
        if (response.data.message) {
            await client.sendText(message.from, response.data.message);
            console.log(`✅ Resposta enviada ao usuário`);
        }
        
    } catch (error) {
        console.error(`❌ Erro ao enviar para Flask:`, error.message);
    }
}

// =========================================
// Inicializar Venom
// =========================================

venom
    .create({
        session: 'bwsfinance-venom',
        multidevice: true,
        headless: true,
        useChrome: true,
        debug: false,
        logQR: true,
        browserArgs: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process'
        ],
        disableWelcome: true,
        updatesLog: false
    })
    .then((venomClient) => {
        console.log('\n✅ Venom Bot iniciado com sucesso!');
        client = venomClient;
        isReady = true;
        
        // ========================================
        // Listener de Mensagens
        // ========================================
        client.onMessage(async (message) => {
            try {
                console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`📨 NOVA MENSAGEM RECEBIDA!`);
                console.log(`   De: ${message.from}`);
                console.log(`   Tipo: ${message.type}`);
                console.log(`   Corpo: ${message.body || '(vazio)'}`);
                console.log(`   É grupo: ${message.isGroupMsg}`);
                console.log(`   É própria: ${message.fromMe}`);
                
                // Filtros básicos
                if (message.isGroupMsg) {
                    console.log(`⛔ Ignorado: Mensagem de grupo`);
                    return;
                }
                
                if (message.fromMe) {
                    console.log(`⛔ Ignorado: Mensagem própria`);
                    return;
                }
                
                if (!message.body || message.body.trim() === '') {
                    console.log(`⛔ Ignorado: Mensagem vazia`);
                    return;
                }
                
                console.log(`✅ Mensagem válida! Processando...`);
                await sendToFlask(message);
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
                
            } catch (error) {
                console.error(`❌ Erro ao processar mensagem:`, error);
            }
        });
        
        console.log('⏳ Aguardando mensagens...\n');
        
    })
    .catch((error) => {
        console.error('❌ Erro ao iniciar Venom:', error);
        process.exit(1);
    });

// =========================================
// API HTTP
// =========================================

app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_connected: isReady,
        client_exists: client !== null,
        version: '4.0-venom',
        timestamp: new Date().toISOString()
    });
});

app.post('/send', async (req, res) => {
    try {
        const { to, message } = req.body;
        
        if (!to || !message) {
            return res.status(400).json({
                success: false,
                error: 'Parâmetros "to" e "message" são obrigatórios'
            });
        }
        
        if (!isReady || !client) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp ainda não está conectado'
            });
        }
        
        const phone = to.includes('@') ? to : `${to}@c.us`;
        await client.sendText(phone, message);
        
        res.json({
            success: true,
            message: 'Mensagem enviada com sucesso'
        });
        
    } catch (error) {
        console.error('❌ Erro ao enviar mensagem:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.get('/', (req, res) => {
    res.json({
        name: 'BWS Finance WhatsApp Bot',
        version: '4.0-venom',
        status: isReady ? 'connected' : 'disconnected',
        library: 'venom-bot',
        message: 'Bot rodando com Venom Bot - Baseado em Pixzinho'
    });
});

// Iniciar servidor HTTP
app.listen(PORT, () => {
    console.log(`🌐 Servidor HTTP rodando em http://localhost:${PORT}`);
    console.log(`📍 Health: http://localhost:${PORT}/health`);
    console.log(`📍 Send: POST http://localhost:${PORT}/send\n`);
});
