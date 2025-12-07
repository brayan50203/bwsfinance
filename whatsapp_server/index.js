/**
 * BWSFinance WhatsApp Server v2.0
 * Versão simplificada e robusta
 */

const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');
const axios = require('axios');
require('dotenv').config({ path: '../.env' });

const app = express();
app.use(express.json());

const PORT = process.env.WHATSAPP_SERVER_PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://localhost:5000';
const AUTH_TOKEN = process.env.WHATSAPP_AUTH_TOKEN || 'bws_finance_token_55653';
const ALLOWED_NUMBERS = (process.env.ALLOWED_SENDERS || '').split(',').map(n => n.trim()).filter(n => n);

let client = null;
let isReady = false;

console.log('🚀 BWS Finance WhatsApp Server v2.0');
console.log('📱 Porta:', PORT);
console.log('🔗 Flask:', FLASK_URL);
console.log('🔐 Números permitidos:', ALLOWED_NUMBERS.length > 0 ? ALLOWED_NUMBERS.join(', ') : 'TODOS');

// =========================================
// Funções auxiliares
// =========================================

function cleanPhoneNumber(phone) {
    return phone.replace('@c.us', '').replace('@g.us', '');
}

function formatPhoneNumber(phone) {
    // Remove tudo que não for número
    let clean = phone.replace(/\D/g, '');
    
    // Adiciona + no início se não tiver
    if (!clean.startsWith('+')) {
        clean = '+' + clean;
    }
    
    console.log(`[formatPhoneNumber] Input: "${phone}" → Output: "${clean}"`);
    return clean;
}

function isAllowedNumber(phone) {
    if (ALLOWED_NUMBERS.length === 0) return true; // Se não configurou, libera todos
    const clean = cleanPhoneNumber(phone);
    const formatted = formatPhoneNumber(clean);
    
    // Tenta com e sem +
    return ALLOWED_NUMBERS.some(allowed => {
        const allowedFormatted = formatPhoneNumber(allowed);
        return formatted === allowedFormatted || 
               formatted === allowed || 
               clean === allowed ||
               '+' + clean === allowedFormatted;
    });
}

async function sendToFlask(message) {
    const from = cleanPhoneNumber(message.from);
    console.log(`\n[sendToFlask] 1. Original: ${message.from}`);
    console.log(`[sendToFlask] 2. Limpo: ${from}`);
    
    const formattedFrom = formatPhoneNumber(from);
    console.log(`[sendToFlask] 3. Formatado final: ${formattedFrom}`);
    
    const payload = {
        from: formattedFrom,  // Número formatado com +
        type: message.type === 'chat' ? 'text' : message.type,
        text: message.body || '',
        timestamp: message.timestamp || Date.now(),
        media_url: null,
        filename: null
    };

    console.log(`📤 Enviando para Flask...`);
    console.log(`   Número formatado: ${from} → ${formattedFrom}`);
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

        console.log(`✅ Flask respondeu:`, response.data);
        
        // Enviar resposta de volta para o usuário
        if (response.data.message) {
            await client.sendText(message.from, response.data.message);
            console.log(`✅ Resposta enviada ao usuário`);
        }

        return response.data;
    } catch (error) {
        console.error(`❌ Erro ao chamar Flask:`, error.message);
        
        // Enviar mensagem de erro ao usuário
        try {
            await client.sendText(message.from, '❌ Erro ao processar sua mensagem. Tente novamente em alguns instantes.');
        } catch (e) {
            console.error('❌ Erro ao enviar mensagem de erro:', e.message);
        }
        
        throw error;
    }
}

// =========================================
// Inicialização do WhatsApp
// =========================================

async function startWhatsApp() {
    try {
        client = await wppconnect.create({
            session: 'bwsfinance-session',
            autoClose: 0, // Não fechar automaticamente
            catchQR: (base64Qr, asciiQR, attempt) => {
                console.log(`\n📱 QR CODE (Tentativa ${attempt}):\n`);
                console.log(asciiQR);
                console.log('\n⏳ Escaneie com WhatsApp em até 60 segundos...\n');
            },
            statusFind: (statusSession) => {
                console.log(`📊 Status: ${statusSession}`);
                
                if (statusSession === 'inChat') {
                    console.log('✅ WhatsApp conectado e pronto!');
                    isReady = true;
                }
            },
            headless: true,
            useChrome: true,
            debug: false,
            logQR: true,
            browserArgs: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });

        console.log('🔧 Registrando eventos...');

        // IMPORTANTE: Garantir que listeners estejam registrados APÓS cliente estar pronto
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Listener de TODAS as mensagens (para debug) - VERSÃO ATUALIZADA
        client.onAnyMessage((message) => {
            const cleanFrom = cleanPhoneNumber(message.from);
            const formattedFrom = formatPhoneNumber(cleanFrom);
            
            console.log(`\n🔍 [DEBUG] onAnyMessage disparado! 🔍`);
            console.log(`   ID: ${message.id}`);
            console.log(`   De: ${message.from}`);
            console.log(`   De (limpo): ${cleanFrom}`);
            console.log(`   De (formatado): ${formattedFrom}`);
            console.log(`   Para: ${message.to || 'N/A'}`);
            console.log(`   Tipo: ${message.type}`);
            console.log(`   Corpo: ${message.body || '(vazio)'}`);
            console.log(`   IsGroup: ${message.isGroupMsg}`);
            console.log(`   FromMe: ${message.fromMe}`);
            console.log(`   Chat ID: ${message.chatId || 'N/A'}`);
            console.log(`   Timestamp: ${new Date().toLocaleString('pt-BR')}`);
        });

        // Evento de mensagem recebida - VERSÃO ATUALIZADA
        client.onMessage(async (message) => {
            try {
                const cleanFrom = cleanPhoneNumber(message.from);
                const formattedFrom = formatPhoneNumber(cleanFrom);
                
                console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`📨 NOVA MENSAGEM RECEBIDA! 🎉`);
                console.log(`   De: ${message.from}`);
                console.log(`   De (formatado): ${formattedFrom}`);
                console.log(`   Tipo: ${message.type}`);
                console.log(`   Corpo: ${message.body || '(sem texto)'}`);
                console.log(`   Grupo: ${message.isGroupMsg ? 'SIM' : 'NÃO'}`);
                console.log(`   Própria: ${message.fromMe ? 'SIM' : 'NÃO'}`);
                console.log(`   Timestamp: ${new Date().toLocaleString('pt-BR')}`);

                // Filtros básicos
                if (message.isGroupMsg) {
                    console.log(`⛔ Ignorado: Mensagem de grupo`);
                    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
                    return;
                }

                if (message.fromMe) {
                    console.log(`⛔ Ignorado: Mensagem própria`);
                    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
                    return;
                }

                // TEMPORÁRIO: Comentado filtro de números autorizados para debug
                // if (!isAllowedNumber(message.from)) {
                //     console.log(`⛔ Ignorado: Número não autorizado`);
                //     console.log(`   Número: ${cleanFrom}`);
                //     console.log(`   Formatado: ${formattedFrom}`);
                //     console.log(`   Permitidos: ${ALLOWED_NUMBERS.join(', ')}`);
                //     return;
                // }

                // Processar mensagem
                console.log(`✅ Mensagem válida! Processando (FILTRO DESABILITADO)...`);
                await sendToFlask(message);
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);

            } catch (error) {
                console.error(`❌ Erro ao processar mensagem:`, error);
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
            }
        });

        // Evento de ACK (confirmação de envio)
        client.onAck((ack) => {
            console.log(`📬 ACK recebido:`, ack);
        });

        // Listener adicional para GARANTIR captura de mensagens
        client.onStateChange((state) => {
            console.log(`🔄 Estado mudou: ${state}`);
            if (state === 'CONNECTED' || state === 'inChat') {
                isReady = true;
                console.log('✅ Cliente pronto para receber mensagens!');
            }
        });

        console.log('✅ WhatsApp Server iniciado com sucesso!');
        console.log('⏳ Aguardando mensagens...\n');
        
        // Log periódico para confirmar que o servidor está vivo
        setInterval(() => {
            console.log(`💓 [${new Date().toLocaleTimeString('pt-BR')}] Servidor ativo - Aguardando mensagens...`);
        }, 30000); // A cada 30 segundos
        
        // SOLUÇÃO ALTERNATIVA: Polling de mensagens não lidas
        // Como onMessage não está disparando, vamos buscar mensagens ativamente
        console.log('🔄 Iniciando polling de mensagens não lidas...');
        let lastCheckedMessageIds = new Set();
        
        setInterval(async () => {
            try {
                // Buscar todos os chats com mensagens não lidas
                const chats = await client.getAllChatsWithMessages(false);
                
                for (const chat of chats) {
                    // Pular grupos
                    if (chat.isGroup) continue;
                    
                    // Buscar mensagens do chat
                    const messages = await client.getAllMessagesInChat(chat.id._serialized, false, false);
                    
                    // Processar apenas mensagens novas e não próprias
                    for (const msg of messages) {
                        // Pular se já processamos
                        if (lastCheckedMessageIds.has(msg.id._serialized)) continue;
                        
                        // Pular mensagens próprias
                        if (msg.fromMe) {
                            lastCheckedMessageIds.add(msg.id._serialized);
                            continue;
                        }
                        
                        // Marcar como processada
                        lastCheckedMessageIds.add(msg.id._serialized);
                        
                        // Processar mensagem nova!
                        console.log(`\n🔔 [POLLING] Nova mensagem detectada!`);
                        console.log(`   De: ${msg.from}`);
                        console.log(`   Corpo: ${msg.body}`);
                        
                        // Simular objeto de mensagem do onMessage
                        const messageObj = {
                            id: msg.id._serialized,
                            from: msg.from,
                            to: msg.to,
                            body: msg.body,
                            type: msg.type,
                            timestamp: msg.timestamp,
                            isGroupMsg: msg.isGroupMsg,
                            fromMe: msg.fromMe,
                            chatId: chat.id._serialized
                        };
                        
                        // Processar
                        await sendToFlask(messageObj);
                    }
                }
                
                // Limpar IDs antigos (manter apenas últimos 1000)
                if (lastCheckedMessageIds.size > 1000) {
                    const idsArray = Array.from(lastCheckedMessageIds);
                    lastCheckedMessageIds = new Set(idsArray.slice(-1000));
                }
                
            } catch (error) {
                console.error(`❌ Erro no polling: ${error.message}`);
            }
        }, 5000); // Verificar a cada 5 segundos

    } catch (error) {
        console.error('❌ Erro ao iniciar WhatsApp:', error);
        process.exit(1);
    }
}

// =========================================
// API HTTP
// =========================================

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_connected: isReady,
        client_exists: client !== null,
        timestamp: new Date().toISOString()
    });
});

// Enviar mensagem (endpoint de teste)
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

        // Adicionar @c.us se não tiver
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

// Informações do servidor
app.get('/', (req, res) => {
    res.json({
        name: 'BWS Finance WhatsApp Server',
        version: '2.0',
        status: isReady ? 'connected' : 'disconnected',
        endpoints: {
            health: 'GET /health',
            send: 'POST /send',
            webhook: `${FLASK_URL}/api/whatsapp/webhook`
        }
    });
});

// =========================================
// Inicialização
// =========================================

// Iniciar servidor HTTP
app.listen(PORT, () => {
    console.log(`\n🌐 Servidor HTTP rodando na porta ${PORT}`);
    console.log(`📍 http://localhost:${PORT}`);
    console.log(`📍 http://localhost:${PORT}/health\n`);
});

// Iniciar WhatsApp
startWhatsApp().catch(error => {
    console.error('❌ Falha crítica:', error);
    process.exit(1);
});

// Tratamento de erros não capturados
process.on('unhandledRejection', (error) => {
    console.error('❌ Unhandled Rejection:', error);
});

process.on('SIGINT', async () => {
    console.log('\n\n🛑 Encerrando servidor...');
    if (client) {
        await client.close();
    }
    process.exit(0);
});
