#!/bin/bash
# Script wrapper para N8N executar o fechamento mensal
# Funciona dentro do container N8N chamando o container da aplicação

set -e

MONTH="${1:-$(date -d 'last month' +%Y-%m 2>/dev/null || date -v-1m +%Y-%m)}"

echo "=== N8N Trigger - Fechamento Mensal $MONTH ==="
echo "Container N8N → Container App (app-fechamento)"
echo ""

# Executar comando no container da aplicação
# Nota: Requer Docker CLI instalado no N8N ou usar volumes compartilhados
if command -v docker &> /dev/null; then
    # Opção 1: Via docker exec 
    docker exec app-fechamento /app/run_fechamento_n8n.sh "$MONTH"
else
    # Opção 2: Executar script diretamente se volumes estão montados
    if [ -f "/app/src/run_fechamento_n8n.sh" ]; then
        bash /app/src/run_fechamento_n8n.sh "$MONTH"
    else
        echo "ERRO: Não foi possível executar o script"
        echo "Certifique-se que:"
        echo "  1. Docker CLI está instalado no container N8N, OU"
        echo "  2. Volumes compartilhados estão configurados"
        exit 1
    fi
fi
