#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"

EOF
echo -e "${NC}"

echo -e "${YELLOW}Iniciando instalação...${NC}"
echo ""

# Verificar Docker
echo -e "${BLUE}[1/5]${NC} Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED} Docker não encontrado!${NC}"
    echo "Instale Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker instalado: $(docker --version)${NC}"

# Verificar Docker Compose
echo -e "${BLUE}[2/5]${NC} Verificando Docker Compose..."
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED} Docker Compose não encontrado!${NC}"
    echo "Instale Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN} Docker Compose instalado${NC}"

echo -e "${BLUE}[3/5]${NC} Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN} Arquivo .env criado${NC}"
    echo -e "${YELLOW}💡 Edite .env para adicionar suas credenciais (opcional)${NC}"
else
    echo -e "${GREEN}Arquivo .env já existe${NC}"
fi


echo -e "${BLUE}[4/5]${NC} Configurando permissões..."
chmod +x manage.sh docker-entrypoint.sh src/run_fechamento_n8n.sh 2>/dev/null || true
echo -e "${GREEN} Permissões configuradas${NC}"

# Iniciar serviços
echo -e "${BLUE}[5/5]${NC} Iniciando serviços Docker..."
echo -e "${YELLOW} Aguarde... (pode levar 1-2 minutos)${NC}"
echo ""

docker compose up -d

echo ""
echo -e "${BLUE} Acesse o N8N:${NC}"
echo -e "   ${GREEN}http://localhost:5678${NC}"
echo ""
echo -e "${BLUE} Credenciais padrão:${NC}"
echo -e "   Usuário: ${GREEN}admin${NC}"
echo -e "   Senha: ${GREEN}admin2025${NC}"
echo ""
echo -e "${BLUE} Próximos passos:${NC}"
echo "   1. Acesse http://localhost:5678"
echo "   2. Faça login"
echo "   3. Importe o workflow: workflows/n8n_workflow.json"
echo "   4. Configure SMTP (opcional)"
echo "   5. Ative o workflow (toggle verde)"
echo ""
echo -e "${BLUE} Documentação:${NC}"
echo "   • QUICKSTART_DOCKER.md  - Início rápido"
echo "   • DOCKER_README.md      - Guia completo"
echo "   • ./manage.sh help      - Comandos disponíveis"
echo ""
echo -e "${BLUE}  Comandos úteis:${NC}"
echo "   ./manage.sh logs        - Ver logs"
echo "   ./manage.sh status      - Status dos containers"
echo "   ./manage.sh exec-app    - Executar fechamento manualmente"
echo "   ./manage.sh stop        - Parar serviços"
echo ""
echo -e "${GREEN} Pronto para uso!${NC}"
