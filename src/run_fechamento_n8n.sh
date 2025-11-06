#!/bin/bash
# Script para executar o fechamento mensal via N8N
# Funciona em qualquer ambiente (local ou Docker)
# Uso: ./run_fechamento_n8n.sh [YYYY-MM]

set -e

# Detectar diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Mês de referência (padrão: mês anterior)
if [ -z "$1" ]; then
    # Calcular mês anterior (compatível com Linux e BSD/Mac)
    MONTH=$(date -d "last month" +%Y-%m 2>/dev/null || date -v-1m +%Y-%m)
else
    MONTH="$1"
fi

# Detectar Python correto
if [ -f "../.venv/bin/python3" ]; then
    PYTHON="../.venv/bin/python3"
    PYTHON_ENV="Virtual Environment"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
    PYTHON_ENV="System Python"
else
    echo "ERRO: Python3 não encontrado!"
    exit 1
fi

# Verificar se pandas está instalado
if ! $PYTHON -c "import pandas" 2>/dev/null; then
    echo "ERRO: Pandas não instalado!"
    echo "Instale as dependências: pip install -r requirements.txt"
    exit 1
fi

echo "=== Iniciando fechamento mensal para $MONTH ==="
echo "Diretório: $SCRIPT_DIR"
echo "Python: $PYTHON ($PYTHON_ENV)"
echo "Versão: $($PYTHON --version)"
echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Executar o script Python
echo "Executando: $PYTHON -m main --month=$MONTH"
echo ""

$PYTHON -m main --month="$MONTH"

EXIT_CODE=$?

echo ""
echo "=== Execução finalizada ==="
echo "Exit Code: $EXIT_CODE"
echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"

exit $EXIT_CODE
