/**
 * BWS Finance WhatsApp Server v4.0 - IMPROVED
 * Com auto-registro de usuários e melhorias de confiabilidade
 */

const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');
const axios = require('axios');
require('dotenv').config({ path: '../.env' });

const app = express();
app.use(express.json());

const PORT = 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://localhost:5000';
const AUTH_TOKEN = process.env.WHATSAPP_AUTH_TOKEN || 'bws_finance_token_55653';

let client = null;
let isReady = false;
let reconnectAttempts = 0;
const MAX_RECONNECT = 5;

console.log('🚀 BWS Finance WhatsApp Server v4.0 - IMPROVED');
console.log('📱 Porta:', PORT);
console.log('🔗 Flask:', FLASK_URL);
console.log('✨ Features: Auto-registro + Retry lógico + Validação\n');

// =========================================
// Funções de Validação e Formatação
// =========================================

function formatPhoneNumber(number) {
    // Remove tudo exceto números
    let clean = number.replace(/\D/g, '');
    
    // Se começar com 55, mantém
    if (!clean.startsWith('55')) {
        // Se tem DDD (11974764971), adiciona 55
        if (clean.length === 11) {
            clean = '55' + clean;
        }
    }
    
    return '+' + clean;
}

function isValidMessage(message) {
    // Rejeita grupos
    if (message.isGroupMsg) {
        console.log('   ⛔ Rejeitado: Grupo');
        return false;
    }
    
    // Rejeita mensagens próprias
    if (message.fromMe) {
        console.log('   ⛔ Rejeitado: Mensagem própria');
        return false;
    }
    
    // Rejeita se não tem corpo
    if (!message.body || message.body.trim() === '') {
        console.log('   ⛔ Rejeitado: Sem texto');
        return false;
    }
    
    // Rejeita mensagens do WhatsApp (status, etc)
    if (message.from === 'status@broadcast') {
        console.log('   ⛔ Rejeitado: Status broadcast');
        return false;
    }
    
    return true;
}

// =========================================
// Comunicação com Flask
// =========================================

async function sendToFlask(from, text, messageType = 'text') {
    const formattedPhone = formatPhoneNumber(from);
    
    const payload = {
        from: formattedPhone,
        type: messageType,
        text: text,
        timestamp: Date.now()
    };

    console.log(`\n📤 ENVIANDO PARA FLASK:`);
    console.log(`   Número original: ${from}`);
    console.log(`   Número formatado: ${formattedPhone}`);
    console.log(`   Mensagem: ${text}`);

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

        console.log(`✅ FLASK RESPONDEU (${response.status})`);
        
        if (response.data.message) {
            console.log(`📨 Resposta: ${response.data.message.substring(0, 100)}...`);
            await sendMessage(from, response.data.message);
        }

        return response.data;
        
    } catch (error) {
        console.error(`❌ ERRO AO CHAMAR FLASK:`);
        
        if (error.response) {
            console.error(`   Status: ${error.response.status}`);
            console.error(`   Erro: ${error.response.data?.error || 'Desconhecido'}`);
            
            // Se erro é "número não cadastrado", enviar instruções
            if (error.response.status === 400 && 
                error.response.data?.error?.includes('não cadastrado')) {
                
                const mensagemCadastro = `
🔐 *Número não cadastrado*

Para usar o BWS Finance Assistant via WhatsApp, você precisa ter uma conta.

📝 *Como cadastrar:*
1. Acesse: http://192.168.80.122:5000
2. Clique em "Registrar"
3. Use este número de WhatsApp: ${formattedPhone}

Após cadastrar, volte aqui e envie sua mensagem novamente! 😊
`.trim();
                
                await sendMessage(from, mensagemCadastro);
                return { error: 'user_not_registered', handled: true };
            }
        } else {
            console.error(`   Erro de rede: ${error.message}`);
        }
        
        // Mensagem genérica de erro
        await sendMessage(from, '❌ Erro temporário. Tente novamente em alguns segundos.');
        return { error: error.message };
    }
}

async function sendMessage(to, message, retries = 3) {
    const phone = to.includes('@') ? to : `${to}@c.us`;
    
    for (let i = 0; i < retries; i++) {
        try {
            await client.sendText(phone, message);
            console.log(`✅ Mensagem enviada para ${to}`);
            return true;
        } catch (error) {
            console.error(`❌ Tentativa ${i + 1}/${retries} falhou:`, error.message);
            if (i < retries - 1) {
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }
    }
    
    console.error(`❌ Falha ao enviar após ${retries} tentativas`);
    return false;
}

// =========================================
// Gerenciamento de Conexão
// =========================================

async function startWhatsApp() {
    try {
        console.log('\n🔄 Iniciando WPPConnect...\n');
        
        client = await wppconnect.create({
            session: 'bwsfinance-v4',
            autoClose: 60000,
            catchQR: (base64Qr, asciiQR, attempt) => {
                console.log(`\n${'='.repeat(65)}`);
                console.log(`📱 QR CODE (Tentativa ${attempt}/3)`);
                console.log(`${'='.repeat(65)}\n`);
                console.log(asciiQR);
                console.log(`\n${'='.repeat(65)}`);
                console.log('⏳ Escaneie com WhatsApp em até 60 segundos...');
                console.log(`${'='.repeat(65)}\n`);
            },
            statusFind: (statusSession) => {
                console.log(`\n📊 STATUS: ${statusSession}`);
                
                if (statusSession === 'inChat' || statusSession === 'qrReadSuccess') {
                    console.log('✅ WhatsApp CONECTADO!\n');
                    isReady = true;
                    reconnectAttempts = 0;
                } else if (statusSession === 'notLogged') {
                    console.log('⚠️  Sessão expirada - precisa escanear QR novamente\n');
                    isReady = false;
                } else if (statusSession === 'desconnectedMobile') {
                    console.log('⚠️  Celular desconectado\n');
                    isReady = false;
                    attemptReconnect();
                }
            },
            headless: false,  // Mostrar navegador para debug
            useChrome: true,
            debug: false,
            logQR: true,
            disableWelcome: true,
            updatesLog: false
        });

        console.log('✅ Cliente WPPConnect criado!');
        console.log('🔧 Registrando listeners...\n');

        // Listener principal
        client.onMessage(async (message) => {
            const timestamp = new Date().toLocaleString('pt-BR');
            console.log(`\n${'━'.repeat(70)}`);
            console.log(`🔔 MENSAGEM RECEBIDA [${timestamp}]`);
            console.log(`${'━'.repeat(70)}`);
            console.log(`   De: ${message.from}`);
            console.log(`   Tipo: ${message.type}`);
            console.log(`   Texto: ${message.body || '(vazio)'}`);

            if (!isValidMessage(message)) {
                console.log(`${'━'.repeat(70)}\n`);
                return;
            }

            console.log(`   ✅ VÁLIDA - Processando...`);
            console.log(`${'━'.repeat(70)}\n`);

            try {
                await sendToFlask(message.from, message.body, message.type);
            } catch (error) {
                console.error(`❌ ERRO ao processar:`, error.message);
            }
        });

        // Listener adicional para debug
        client.onAnyMessage((message) => {
            console.log(`🔍 [DEBUG] Qualquer mensagem: ${message.id} (${message.type})`);
        });

        // Listener de ACK (confirmação de envio)
        client.onAck((ack) => {
            if (ack.ack === 2) {
                console.log(`📬 Mensagem entregue: ${ack.id._serialized}`);
            } else if (ack.ack === 3) {
                console.log(`👀 Mensagem lida: ${ack.id._serialized}`);
            }
        });

        console.log('✅ Todos os listeners registrados!');
        console.log('⏳ Aguardando mensagens...\n');
        
        // Heartbeat para manter conexão viva
        setInterval(() => {
            if (isReady) {
                console.log(`💓 [${new Date().toLocaleTimeString()}] Conexão ativa`);
            }
        }, 60000); // A cada 60 segundos

    } catch (error) {
        console.error('\n❌ ERRO CRÍTICO ao iniciar WhatsApp:', error.message);
        attemptReconnect();
    }
}

async function attemptReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT) {
        console.error(`❌ Máximo de ${MAX_RECONNECT} tentativas de reconexão atingido`);
        console.error('🔄 Reinicie o servidor manualmente');
        return;
    }
    
    reconnectAttempts++;
    const delay = reconnectAttempts * 10000; // 10s, 20s, 30s, etc
    
    console.log(`\n🔄 Tentando reconectar (${reconnectAttempts}/${MAX_RECONNECT}) em ${delay/1000}s...`);
    
    setTimeout(async () => {
        try {
            if (client) {
                await client.close();
            }
            await startWhatsApp();
        } catch (error) {
            console.error('❌ Falha na reconexão:', error.message);
            attemptReconnect();
        }
    }, delay);
}

// =========================================
// API HTTP
// =========================================

app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_connected: isReady,
        client_exists: client !== null,
        version: '4.0 - Improved',
        reconnect_attempts: reconnectAttempts,
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

        const sent = await sendMessage(to, message);

        res.json({
            success: sent,
            message: sent ? 'Mensagem enviada' : 'Falha ao enviar'
        });

    } catch (error) {
        console.error('❌ Erro ao enviar:', error.message);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.get('/', (req, res) => {
    res.json({
        name: 'BWS Finance WhatsApp Server',
        version: '4.0 - Improved',
        status: isReady ? 'connected' : 'disconnected',
        features: [
            'Auto-registro de usuários',
            'Retry automático',
            'Validação robusta',
            'Heartbeat de conexão',
            'Reconexão automática'
        ]
    });
});

// =========================================
// Inicialização
// =========================================

app.listen(PORT, () => {
    console.log(`\n🌐 Servidor HTTP: http://localhost:${PORT}`);
    console.log(`📍 Health: http://localhost:${PORT}/health`);
    console.log(`📍 Send: POST http://localhost:${PORT}/send\n`);
});

startWhatsApp().catch(error => {
    console.error('❌ Falha fatal:', error);
    process.exit(1);
});

process.on('SIGINT', async () => {
    console.log('\n\n🛑 Encerrando servidor...');
    if (client) {
        await client.close();
    }
    process.exit(0);
});

process.on('uncaughtException', (error) => {
    console.error('❌ Exceção não capturada:', error);
    attemptReconnect();
});

process.on('unhandledRejection', (error) => {
    console.error('❌ Promise rejeitada:', error);
});
