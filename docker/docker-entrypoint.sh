#!/bin/bash
set -e

echo "Inicializando Seazone - Fechamento Mensal..."

# Verificar e criar diretórios necessários
mkdir -p /app/src/data /app/src/output

# Verific se o banco de dados existe
if [ ! -f "/app/src/data/database.sqlite" ]; then
    echo "Banco de dados não encontrado. Será criado na primeira execução."
fi

# Exibir informações
echo "Ambiente configurado:"
echo "   - Python: $(python --version)"
echo "   - Diretório: $(pwd)"
echo "   - Data: /app/src/data"
echo "   - Output: /app/src/output"

if python -c "import pandas" 2>/dev/null; then
    echo "Dependências instaladas"
else
    echo "Erro: Dependências não instaladas"
    exit 1
fi

echo ""
echo "Para executar o fechamento manualmente:"
echo "   docker-compose exec app python -m src.main --month=2025-10"
echo ""
echo "N8N disponível em: http://localhost:5678"
echo "   Usuário: ${N8N_USER:-admin}"
echo "   Senha: ${N8N_PASSWORD:-seazone2025}"
echo ""

exec "$@"
