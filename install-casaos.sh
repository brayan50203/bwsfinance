#!/bin/bash
# Script de instalação automática do BWS Finance no CasaOS
# Uso: curl -fsSL https://raw.githubusercontent.com/seu-repo/bws-finance/main/install-casaos.sh | bash

set -e

echo "🚀 BWS Finance - Instalação Automática para CasaOS"
echo "=================================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ Não execute este script como root!${NC}"
   echo "Execute como usuário normal do CasaOS"
   exit 1
fi

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado!${NC}"
    echo "CasaOS já inclui Docker. Verifique sua instalação."
    exit 1
fi

echo -e "${GREEN}✅ Docker encontrado${NC}"

# Verificar se Docker Compose está instalado
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não encontrado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose encontrado${NC}"

# Definir diretório de instalação
INSTALL_DIR="/DATA/AppData/bws-finance"
echo ""
echo "📂 Diretório de instalação: $INSTALL_DIR"

# Perguntar se deseja continuar
read -p "Deseja continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "Instalação cancelada."
    exit 0
fi

# Criar diretórios
echo ""
echo "📁 Criando estrutura de diretórios..."
mkdir -p "$INSTALL_DIR"/{data,logs,whatsapp,templates/emails,temp,tokens}

# Baixar arquivos do repositório
echo ""
echo "⬇️  Baixando arquivos..."

cd "$INSTALL_DIR"

# Opção 1: Clone via git (se disponível)
if command -v git &> /dev/null; then
    echo "Clonando repositório..."
    git clone https://github.com/seu-usuario/bws-finance.git tmp-clone
    mv tmp-clone/* .
    rm -rf tmp-clone
else
    # Opção 2: Download via curl
    echo "Baixando arquivos via curl..."
    curl -L https://github.com/seu-usuario/bws-finance/archive/main.tar.gz | tar xz --strip-components=1
fi

# Copiar .env.example para .env
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Configurando arquivo .env..."
    cp .env.example .env
    
    # Gerar SECRET_KEY aleatório
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/change-this-to-a-random-secret-key-min-32-chars/$SECRET_KEY/" .env
    
    # Gerar WHATSAPP_AUTH_TOKEN aleatório
    WA_TOKEN=$(openssl rand -hex 16)
    sed -i "s/your-secret-token-here/$WA_TOKEN/" .env
    
    echo -e "${GREEN}✅ Arquivo .env criado com chaves aleatórias${NC}"
fi

# Perguntar configurações de email
echo ""
echo "📧 Configuração de Email (SMTP)"
echo "--------------------------------"
read -p "Host SMTP (default: smtp.gmail.com): " SMTP_HOST
SMTP_HOST=${SMTP_HOST:-smtp.gmail.com}

read -p "Porta SMTP (default: 587): " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-587}

read -p "Usuário SMTP (seu-email@gmail.com): " SMTP_USER

read -sp "Senha SMTP ou App Password: " SMTP_PASSWORD
echo ""

read -p "Email remetente (default: noreply@bwsfinance.com): " SMTP_FROM
SMTP_FROM=${SMTP_FROM:-noreply@bwsfinance.com}

# Atualizar .env com configurações de email
sed -i "s/SMTP_HOST=.*/SMTP_HOST=$SMTP_HOST/" .env
sed -i "s/SMTP_PORT=.*/SMTP_PORT=$SMTP_PORT/" .env
sed -i "s/SMTP_USER=.*/SMTP_USER=$SMTP_USER/" .env
sed -i "s/SMTP_PASSWORD=.*/SMTP_PASSWORD=$SMTP_PASSWORD/" .env
sed -i "s/SMTP_FROM=.*/SMTP_FROM=$SMTP_FROM/" .env

echo -e "${GREEN}✅ Configurações de email salvas${NC}"

# Perguntar sobre notificações
echo ""
echo "🔔 Configuração de Notificações"
echo "--------------------------------"
read -p "Habilitar notificações automáticas? (S/n): " ENABLE_NOTIF
ENABLE_NOTIF=${ENABLE_NOTIF:-S}

if [[ $ENABLE_NOTIF =~ ^[SsYy]$ ]]; then
    sed -i "s/AUTO_NOTIFICATIONS_ENABLED=.*/AUTO_NOTIFICATIONS_ENABLED=true/" .env
    echo -e "${GREEN}✅ Notificações automáticas habilitadas${NC}"
else
    sed -i "s/AUTO_NOTIFICATIONS_ENABLED=.*/AUTO_NOTIFICATIONS_ENABLED=false/" .env
    echo -e "${YELLOW}⚠️  Notificações automáticas desabilitadas${NC}"
fi

# Build das imagens Docker
echo ""
echo "🐳 Construindo imagens Docker..."
docker compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao construir imagens Docker${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Imagens construídas com sucesso${NC}"

# Iniciar containers
echo ""
echo "🚀 Iniciando serviços..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao iniciar containers${NC}"
    exit 1
fi

# Aguardar serviços ficarem prontos
echo ""
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Verificar se backend está rodando
if curl -sf http://localhost:5000/api/notifications/health > /dev/null; then
    echo -e "${GREEN}✅ Backend iniciado com sucesso${NC}"
else
    echo -e "${YELLOW}⚠️  Backend ainda não está respondendo. Aguarde mais alguns segundos.${NC}"
fi

# Verificar se WhatsApp está rodando
if curl -sf http://localhost:3000/health > /dev/null; then
    echo -e "${GREEN}✅ WhatsApp server iniciado com sucesso${NC}"
else
    echo -e "${YELLOW}⚠️  WhatsApp server ainda não está respondendo. Aguarde mais alguns segundos.${NC}"
fi

# Obter IP do servidor
SERVER_IP=$(hostname -I | awk '{print $1}')

# Mensagem final
echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Instalação concluída com sucesso!${NC}"
echo "=================================================="
echo ""
echo "📊 Acesse o painel em:"
echo "   http://$SERVER_IP:5000"
echo "   http://localhost:5000 (local)"
echo ""
echo "📱 Configure o WhatsApp em:"
echo "   http://$SERVER_IP:3000"
echo "   http://localhost:3000 (local)"
echo ""
echo "🔍 Verificar status dos serviços:"
echo "   docker compose ps"
echo ""
echo "📋 Ver logs:"
echo "   docker compose logs -f"
echo ""
echo "🛑 Parar serviços:"
echo "   docker compose down"
echo ""
echo "🔄 Reiniciar serviços:"
echo "   docker compose restart"
echo ""
echo "⚙️  Configurações em: $INSTALL_DIR/.env"
echo ""
echo "=================================================="
echo ""
echo "📝 Próximos passos:"
echo "1. Acesse http://$SERVER_IP:5000 e crie sua conta"
echo "2. Configure preferências de notificação"
echo "3. Escaneie QR code do WhatsApp em http://$SERVER_IP:3000"
echo "4. Pronto! Notificações automáticas estão ativas"
echo ""
echo "📚 Documentação completa: $INSTALL_DIR/DEPLOY_CASAOS.md"
echo ""

# Perguntar se deseja ver logs
read -p "Deseja ver os logs agora? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    docker compose logs -f
fi
