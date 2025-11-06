#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' 

# Banner
echo -e "${BLUE}"
echo -e "${NC}"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}  Arquivo .env não encontrado!${NC}"
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo -e "${GREEN}Arquivo .env criado. Edite-o com suas credenciais.${NC}"
    echo ""
fi

# Função de ajuda
show_help() {
    echo "Uso: ./manage.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start         - Inicia todos os serviços"
    echo "  stop          - Para todos os serviços"
    echo "  restart       - Reinicia todos os serviços"
    echo "  logs          - Mostra logs dos serviços"
    echo "  logs-app      - Mostra logs apenas do app Python"
    echo "  logs-n8n      - Mostra logs apenas do N8N"
    echo "  status        - Status dos containers"
    echo "  exec-app      - Executa fechamento manualmente"
    echo "  shell-app     - Abre shell no container app"
    echo "  shell-n8n     - Abre shell no container n8n"
    echo "  import-workflow - Importa workflow automaticamente no N8N"
    echo "  clean         - Remove containers e volumes (CUIDADO!)"
    echo "  rebuild       - Reconstrói as imagens"
    echo "  help          - Mostra esta ajuda"
    echo ""
}

check_services() {
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "${RED} Serviços não estão rodando.${NC}"
        echo "Execute: ./manage.sh start"
        exit 1
    fi
}

# Processar comando
case "${1:-help}" in
    start)
        echo -e "${BLUE} Iniciando serviços...${NC}"
        docker-compose up -d
        echo ""
        echo -e "${GREEN} Serviços iniciados!${NC}"
        echo ""
        echo -e "${BLUE} Acesse o N8N em: ${NC}http://localhost:5678"
        echo ""
        echo "Para ver os logs: ./manage.sh logs"
        echo "Para importar workflow: ./manage.sh import-workflow"
        ;;
    
    stop)
        echo -e "${YELLOW}⏸  Parando serviços...${NC}"
        docker-compose down
        echo -e "${GREEN} Serviços parados${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW} Reiniciando serviços...${NC}"
        docker-compose restart
        echo -e "${GREEN}Serviços reiniciados${NC}"
        ;;
    
    logs)
        echo -e "${BLUE}Logs dos serviços (Ctrl+C para sair)${NC}"
        docker-compose logs -f
        ;;
    
    logs-app)
        echo -e "${BLUE} Logs do App Python (Ctrl+C para sair)${NC}"
        docker-compose logs -f app
        ;;
    
    logs-n8n)
        echo -e "${BLUE} Logs do N8N (Ctrl+C para sair)${NC}"
        docker-compose logs -f n8n
        ;;
    
    status)
        echo -e "${BLUE}Status dos containers:${NC}"
        docker-compose ps
        ;;
    
    exec-app)
        check_services
        MONTH="${2:-$(date -d 'last month' +%Y-%m)}"
        echo -e "${BLUE} Executando fechamento para o mês: ${MONTH}${NC}"
        docker-compose exec app python -m src.main --month="${MONTH}"
        ;;
    
    shell-app)
        check_services
        echo -e "${BLUE} Abrindo shell no container app...${NC}"
        docker-compose exec app /bin/bash
        ;;
    
    shell-n8n)
        check_services
        echo -e "${BLUE} Abrindo shell no container n8n...${NC}"
        docker-compose exec n8n /bin/sh
        ;;
    
    import-workflow)
        check_services
        echo -e "${BLUE} Importando workflow no N8N...${NC}"
        echo ""
        echo "1. Acesse: http://localhost:5678"
        echo "2. Faça login (admin / seazone2025)"
        echo "3. Clique em '+' → 'Import from File'"
        echo "4. Selecione: workflows/n8n_workflow.json"
        echo "5. Configure credenciais SMTP (opcional)"
        echo "6. Ative o workflow (toggle no topo)"
        echo ""
        echo -e "${GREEN} Siga as instruções acima${NC}"
        ;;
    
    clean)
        echo -e "${RED}  ATENÇÃO: Isso vai remover containers, volumes e dados!${NC}"
        read -p "Tem certeza? (sim/não): " confirm
        if [ "$confirm" = "sim" ]; then
            echo -e "${YELLOW}  Removendo containers e volumes...${NC}"
            docker-compose down -v
            echo -e "${GREEN} Limpeza concluída${NC}"
        else
            echo "Cancelado."
        fi
        ;;
    
    rebuild)
        echo -e "${BLUE}🔨 Reconstruindo imagens...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN} Imagens reconstruídas${NC}"
        echo "Execute: ./manage.sh start"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo -e "${RED} Comando inválido: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
