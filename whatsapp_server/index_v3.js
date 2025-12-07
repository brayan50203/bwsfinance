/**
 * BWS Finance WhatsApp Server v3.0
 * Versão ultra-simplificada para máxima compatibilidade
 */

const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');
const axios = require('axios');
require('dotenv').config({ path: '../.env' });

const app = express();
app.use(express.json());

const PORT = 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://localhost:80';
const AUTH_TOKEN = process.env.WHATSAPP_AUTH_TOKEN || 'bws_finance_token_55653';

let client = null;
let isReady = false;

console.log('🚀 BWS Finance WhatsApp Server v3.0 - ULTRA SIMPLIFICADO');
console.log('📱 Porta:', PORT);
console.log('🔗 Flask:', FLASK_URL);
console.log('⚠️  FILTROS DESABILITADOS - Aceitando de QUALQUER número!\n');

// =========================================
// Funções auxiliares
// =========================================

async function sendToFlask(from, text) {
    const payload = {
        from: from,
        type: 'text',
        text: text,
        timestamp: Date.now()
    };

    console.log(`\n📤 ENVIANDO PARA FLASK:`);
    console.log(`   URL: ${FLASK_URL}/api/whatsapp/webhook`);
    console.log(`   Payload:`, JSON.stringify(payload, null, 2));

    try {
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

        console.log(`✅ FLASK RESPONDEU:`, JSON.stringify(response.data, null, 2));
        
        // REMOVIDO: Flask já envia a resposta diretamente ao usuário via /send
        // Não precisa enviar novamente aqui (evita mensagens duplicadas)
        console.log(`✅ Flask irá enviar a resposta diretamente`);

        return response.data;
    } catch (error) {
        console.error(`❌ ERRO AO CHAMAR FLASK:`, error.message);
        if (error.response) {
            console.error(`   Status:`, error.response.status);
            console.error(`   Data:`, error.response.data);
        }
        
        try {
            await client.sendText(from, '❌ Erro ao processar sua mensagem. Tente novamente.');
        } catch (e) {
            console.error('❌ Erro ao enviar mensagem de erro:', e.message);
        }
    }
}

// =========================================
// Inicialização do WhatsApp
// =========================================

async function startWhatsApp() {
    try {
        console.log('\n🔄 Iniciando WPPConnect...\n');
        
        client = await wppconnect.create({
            session: 'bwsfinance-v3',
            autoClose: 0,
            catchQR: (base64Qr, asciiQR, attempt) => {
                console.log(`\n${'='.repeat(65)}`);
                console.log(`📱 QR CODE (Tentativa ${attempt})`);
                console.log(`${'='.repeat(65)}\n`);
                console.log(asciiQR);
                console.log(`\n${'='.repeat(65)}`);
                console.log('⏳ Escaneie com WhatsApp em até 60 segundos...');
                console.log(`${'='.repeat(65)}\n`);
            },
            statusFind: (statusSession) => {
                console.log(`\n📊 STATUS MUDOU: ${statusSession}`);
                if (statusSession === 'inChat') {
                    console.log('✅ WhatsApp CONECTADO E PRONTO!\n');
                    isReady = true;
                }
            },
            headless: true,
            useChrome: true,
            debug: false,
            logQR: true
        });

        console.log('\n✅ Cliente WPPConnect criado!');
        console.log('🔧 Registrando listeners de mensagem...\n');

        // LISTENER PRINCIPAL - onMessage
        client.onMessage(async (message) => {
            console.log(`\n${'━'.repeat(65)}`);
            console.log(`🔔 onMessage() DISPARADO!`);
            console.log(`${'━'.repeat(65)}`);
            console.log(`   ID: ${message.id}`);
            console.log(`   De: ${message.from}`);
            console.log(`   Para: ${message.to}`);
            console.log(`   Tipo: ${message.type}`);
            console.log(`   Corpo: ${message.body}`);
            console.log(`   É Grupo?: ${message.isGroupMsg}`);
            console.log(`   É Minha?: ${message.fromMe}`);
            console.log(`${'━'.repeat(65)}\n`);

            try {
                // Filtros mínimos
                if (message.isGroupMsg) {
                    console.log('⛔ Ignorado: Mensagem de grupo\n');
                    return;
                }

                if (message.fromMe) {
                    console.log('⛔ Ignorado: Mensagem própria\n');
                    return;
                }

                // Processar diferentes tipos de mensagem
                if (message.type === 'ptt' || message.type === 'audio') {
                    // Áudio - baixar e enviar para Flask
                    console.log('🎤 ÁUDIO DETECTADO! Baixando...\n');
                    
                    try {
                        const buffer = await client.decryptFile(message);
                        const base64 = buffer.toString('base64');
                        
                        console.log('✅ Áudio baixado! Tamanho:', buffer.length, 'bytes');
                        console.log('📤 Enviando para Flask...\n');
                        
                        const response = await axios.post(`${FLASK_URL}/api/whatsapp/webhook`, {
                            from: message.from,
                            type: 'audio',
                            audio_base64: base64,
                            timestamp: message.timestamp
                        }, {
                            headers: {
                                'Authorization': `Bearer ${AUTH_TOKEN}`,
                                'Content-Type': 'application/json'
                            },
                            timeout: 60000 // 60 segundos para Whisper processar
                        });
                        
                        console.log('✅ Flask respondeu:', response.data);
                        console.log('✅ Áudio processado com sucesso!\n');
                    } catch (error) {
                        console.error('❌ Erro ao processar áudio:', error.message);
                        if (error.response) {
                            console.error('   Flask retornou:', error.response.status, error.response.data);
                        }
                        try {
                            await client.sendText(message.from, '❌ Erro ao processar áudio. Tente enviar como texto: "Paguei 50 reais no mercado"');
                        } catch (e) {
                            console.error('❌ Erro ao enviar mensagem de erro:', e.message);
                        }
                    }
                    return;
                }
                
                if (message.type === 'image') {
                    // Imagem - baixar e enviar para Flask
                    console.log('📸 IMAGEM DETECTADA! Baixando...\n');
                    
                    try {
                        const buffer = await client.decryptFile(message);
                        const base64 = buffer.toString('base64');
                        
                        console.log('✅ Imagem baixada! Enviando para Flask...\n');
                        
                        await axios.post(`${FLASK_URL}/api/whatsapp/webhook`, {
                            from: message.from,
                            type: 'image',
                            image_base64: base64,
                            caption: message.caption || '',
                            timestamp: message.timestamp
                        }, {
                            headers: {
                                'Authorization': `Bearer ${AUTH_TOKEN}`,
                                'Content-Type': 'application/json'
                            }
                        });
                        
                        console.log('✅ Imagem enviada para Flask!\n');
                    } catch (error) {
                        console.error('❌ Erro ao processar imagem:', error);
                        await client.sendText(message.from, '❌ Erro ao processar imagem. Tente novamente.');
                    }
                    return;
                }

                // Mensagem de texto
                if (!message.body || message.body.trim() === '') {
                    console.log('⛔ Ignorado: Mensagem sem texto\n');
                    return;
                }

                console.log('✅ MENSAGEM DE TEXTO VÁLIDA! Processando...\n');
                await sendToFlask(message.from, message.body);

            } catch (error) {
                console.error(`❌ ERRO ao processar:`, error);
                console.error(error.stack);
            }
        });

        // LISTENER BACKUP - onAnyMessage (captura TUDO)
        client.onAnyMessage((message) => {
            console.log(`\n🔍 [onAnyMessage] Mensagem detectada:`);
            console.log(`   ID: ${message.id}`);
            console.log(`   De: ${message.from}`);
            console.log(`   Tipo: ${message.type}`);
            console.log(`   Corpo: ${message.body || '(vazio)'}`);
        });

        console.log('✅ Listeners registrados com sucesso!');
        console.log('⏳ Aguardando mensagens...\n');

    } catch (error) {
        console.error('\n❌ ERRO CRÍTICO ao iniciar WhatsApp:', error);
        console.error(error.stack);
        process.exit(1);
    }
}

// =========================================
// API HTTP
// =========================================

app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_connected: isReady,
        client_exists: client !== null,
        version: '3.0',
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
        name: 'BWS Finance WhatsApp Server',
        version: '3.0 - Ultra Simplificado',
        status: isReady ? 'connected' : 'disconnected',
        message: 'Filtros de número DESABILITADOS para debug'
    });
});

// =========================================
// Inicialização
// =========================================

app.listen(PORT, () => {
    console.log(`\n🌐 Servidor HTTP rodando em http://localhost:${PORT}`);
    console.log(`📍 Health: http://localhost:${PORT}/health`);
    console.log(`📍 Send: POST http://localhost:${PORT}/send\n`);
});

startWhatsApp().catch(error => {
    console.error('❌ Falha ao iniciar:', error);
    process.exit(1);
});

process.on('SIGINT', async () => {
    console.log('\n\n🛑 Encerrando servidor...');
    if (client) {
        await client.close();
    }
    process.exit(0);
});
