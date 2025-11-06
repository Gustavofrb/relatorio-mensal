#!/bin/bash
# Script para importar workflow automaticamente no N8N

set -e

echo "🔄 Aguardando N8N iniciar..."
sleep 10

# Verificar se N8N está respondendo
until curl -s http://n8n:5678/healthz > /dev/null 2>&1; do
    echo "⏳ N8N ainda não está pronto, aguardando..."
    sleep 5
done

echo "✅ N8N está pronto!"

# Credenciais do N8N (Basic Auth)
N8N_USER="${N8N_USER:-admin}"
N8N_PASSWORD="${N8N_PASSWORD:-seazone2025}"

echo "📥 Importando workflow do arquivo..."

# Importar workflow via API
RESPONSE=$(curl -s -u "$N8N_USER:$N8N_PASSWORD" \
    -X POST \
    -H "Content-Type: application/json" \
    -d @/workflows/n8n_workflow.json \
    http://n8n:5678/api/v1/workflows)

# Verificar resposta (sem jq)
if echo "$RESPONSE" | grep -q '"id"'; then
    echo "✅ Workflow importado com sucesso!"
    echo "$RESPONSE"
    echo ""
    echo "🌐 Acesse o N8N em: http://localhost:5678"
    echo "   Usuário: $N8N_USER"
    echo "   Senha: $N8N_PASSWORD"
else
    echo "❌ Erro ao importar workflow"
    echo "$RESPONSE"
    exit 1
fi
