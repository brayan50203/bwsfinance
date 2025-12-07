/**
 * BWSFinance WhatsApp Server
 * 100% Local & Free Integration using WPPConnect
 * 
 * Features:
 * - Connects to WhatsApp Web
 * - Receives messages (text, audio, image, PDF)
 * - Forwards to Flask API for processing
 * - Sends confirmations back to user
 */

const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: '../.env' });

const app = express();
app.use(express.json());

const PORT = process.env.WHATSAPP_SERVER_PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://localhost:5000';
const AUTH_TOKEN = process.env.WHATSAPP_AUTH_TOKEN || 'change_me';

let client = null;

// =========================================
// WhatsApp Client Initialization
// =========================================

async function initWhatsApp() {
    console.log('🚀 Iniciando WhatsApp Client...');
    
    client = await wppconnect.create({
        session: 'bwsfinance-session',
        catchQR: (base64Qr, asciiQR) => {
            console.log('\n📱 QR Code gerado! Escaneie com WhatsApp:\n');
            console.log(asciiQR);
            console.log('\n✅ Aguardando conexão...\n');
        },
        statusFind: (statusSession, session) => {
            console.log(`📊 Status: ${statusSession}`);
            
            if (statusSession === 'inChat' || statusSession === 'qrReadSuccess') {
                console.log('✅ WhatsApp conectado com sucesso!');
            }
        },
        headless: true,
        devtools: false,
        useChrome: true,
        debug: false,
        logQR: true,
        browserArgs: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    // =========================================
    // Message Handlers
    // =========================================
    
    console.log('🔧 Registrando handler de mensagens...');

    // Usar onAnyMessage que captura TODAS as mensagens
    client.onAnyMessage(async (message) => {
        try {
            console.log(`\n🔔 MENSAGEM DETECTADA!`);
            console.log(`   De: ${message.from}`);
            console.log(`   Tipo: ${message.type}`);
            console.log(`   IsGroup: ${message.isGroupMsg}`);
            console.log(`   FromMe: ${message.fromMe}`);
            console.log(`   Body: ${message.body || '(sem texto)'}`);
            
            // 🚨 PROTEÇÃO: Ignorar mensagens de grupos
            if (message.isGroupMsg) {
                console.log(`⛔ Mensagem de grupo ignorada: ${message.from}`);
                return;
            }
            
            // 🚨 PROTEÇÃO: Apenas processar mensagens RECEBIDAS (não enviadas)
            if (message.fromMe) {
                console.log(`⛔ Mensagem própria ignorada`);
                return;
            }
            
            console.log(`📨 Processando mensagem de ${message.from}:`);
            console.log(`   Tipo: ${message.type}`);
            
            // Verificar remetentes permitidos (se configurado)
            if (!isAllowedSender(message.from)) {
                console.log(`⛔ Remetente não autorizado: ${message.from}`);
                console.log(`   Número limpo: ${message.from.replace('@c.us', '')}`);
                console.log(`   Lista permitida: ${process.env.ALLOWED_SENDERS}`);
                return;
            }

            const payload = await buildPayload(message);
            
            // Enviar para Flask
            await forwardToFlask(payload, message.from);
            
        } catch (error) {
            console.error('❌ Erro ao processar mensagem:', error);
            try {
                await sendMessage(message.from, '❌ Erro ao processar sua mensagem. Tente novamente.');
            } catch (e) {
                console.error('❌ Erro ao enviar mensagem de erro:', e);
            }
        }
    });

    console.log('✅ WhatsApp Client iniciado e aguardando mensagens...\n');
}

// =========================================
// Payload Builder
// =========================================

async function buildPayload(message) {
    const payload = {
        from: message.from,
        timestamp: message.timestamp,
        type: message.type === 'chat' ? 'text' : message.type, // Converter 'chat' para 'text'
        text: message.body || '',
        media_url: null,
        filename: null
    };

    // Processar diferentes tipos de mídia
    if (message.type === 'ptt' || message.type === 'audio') {
        // Áudio / Voz
        payload.type = 'audio';
        const buffer = await client.decryptFile(message);
        const filename = `audio_${Date.now()}.ogg`;
        const filepath = path.join(__dirname, '../temp', filename);
        
        fs.writeFileSync(filepath, buffer);
        payload.media_url = filepath;
        payload.filename = filename;
        
        console.log(`   🎤 Áudio salvo: ${filename}`);
        
    } else if (message.type === 'image') {
        // Imagem
        const buffer = await client.decryptFile(message);
        const filename = `image_${Date.now()}.jpg`;
        const filepath = path.join(__dirname, '../temp', filename);
        
        fs.writeFileSync(filepath, buffer);
        payload.media_url = filepath;
        payload.filename = filename;
        
        console.log(`   🖼️ Imagem salva: ${filename}`);
        
    } else if (message.type === 'document') {
        // PDF ou documento
        const buffer = await client.decryptFile(message);
        const filename = message.filename || `document_${Date.now()}.pdf`;
        const filepath = path.join(__dirname, '../temp', filename);
        
        fs.writeFileSync(filepath, buffer);
        payload.media_url = filepath;
        payload.filename = filename;
        
        console.log(`   📄 Documento salvo: ${filename}`);
    }

    return payload;
}

// =========================================
// Forward to Flask
// =========================================

async function forwardToFlask(payload, sender) {
    try {
        console.log('📤 Enviando para Flask...');
        
        const response = await axios.post(
            `${FLASK_URL}/api/whatsapp/webhook`,
            payload,
            {
                headers: {
                    'Authorization': `Bearer ${AUTH_TOKEN}`,
                    'Content-Type': 'application/json'
                },
                timeout: 30000 // 30 segundos
            }
        );

        console.log('✅ Flask respondeu:', response.data);
        
        // Enviar confirmação ao usuário
        if (response.data.message) {
            await sendMessage(sender, response.data.message);
        }
        
    } catch (error) {
        console.error('❌ Erro ao chamar Flask:', error.message);
        console.error('❌ Detalhes do erro:', error.response?.data || error);
        console.error('❌ Status:', error.response?.status);
        await sendMessage(sender, '❌ Erro ao processar. Tente novamente em instantes.');
    }
}

// =========================================
// Send Message (API Endpoint)
// =========================================

app.post('/send', async (req, res) => {
    try {
        const { to, message, token } = req.body;
        
        // Validar token
        if (token !== AUTH_TOKEN) {
            return res.status(401).json({ error: 'Token inválido' });
        }
        
        if (!client) {
            return res.status(500).json({ error: 'WhatsApp não conectado' });
        }
        
        await sendMessage(to, message);
        
        res.json({ success: true, message: 'Mensagem enviada' });
        
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        res.status(500).json({ error: error.message });
    }
});

async function sendMessage(to, text) {
    if (!client) {
        console.log('⚠️ Cliente WhatsApp não está conectado');
        return;
    }
    
    try {
        await client.sendText(to, text);
        console.log(`✅ Mensagem enviada para ${to}`);
    } catch (error) {
        console.error(`❌ Erro ao enviar mensagem para ${to}:`, error);
    }
}

// =========================================
// Helper Functions
// =========================================

function isAllowedSender(from) {
    const allowed = process.env.ALLOWED_SENDERS;
    
    if (!allowed || allowed.trim() === '') {
        return true; // Permite todos
    }
    
    // Remove @c.us do número recebido para comparação
    const cleanFrom = from.replace('@c.us', '');
    
    const allowedList = allowed.split(',').map(s => s.trim());
    return allowedList.includes(cleanFrom);
}

// =========================================
// Health Check
// =========================================

app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_connected: client !== null,
        timestamp: new Date().toISOString()
    });
});

// =========================================
// Start Server
// =========================================

app.listen(PORT, () => {
    console.log(`✅ Servidor Node rodando na porta ${PORT}`);
    console.log(`📱 WhatsApp API: http://localhost:${PORT}`);
    console.log(`🔗 Flask endpoint: ${FLASK_URL}/api/whatsapp/webhook\n`);
    
    initWhatsApp();
});

// =========================================
// Graceful Shutdown
// =========================================

process.on('SIGINT', async () => {
    console.log('\n🛑 Encerrando servidor...');
    
    if (client) {
        await client.close();
    }
    
    process.exit(0);
});
