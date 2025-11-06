"""
Servidor HTTP simples para triggerar o fechamento mensal via N8N.
Expõe endpoint /run que executa o fechamento e retorna os logs.
"""

from flask import Flask, request, jsonify
import subprocess
import os
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({"status": "healthy", "service": "fechamento-mensal"}), 200

@app.route('/run', methods=['POST'])
def run_fechamento():
    """
    Executa o fechamento mensal para o mês especificado.
    
    Body JSON (opcional):
    {
        "month": "2025-10"  # YYYY-MM format
    }
    
    Se month não for fornecido, usa o mês anterior.
    """
    try:
        # Obter mês do request ou calcular mês anterior
        data = request.get_json() or {}
        month = data.get('month')
        
        if not month:
            # Calcular mês anterior
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            month = last_month.strftime('%Y-%m')
        
        # Validar formato do mês
        try:
            datetime.strptime(month, '%Y-%m')
        except ValueError:
            return jsonify({
                "error": "Invalid month format. Use YYYY-MM",
                "example": "2025-10"
            }), 400
        
        # Garantir que os diretórios existem
        os.makedirs('/app/data', exist_ok=True)
        os.makedirs('/app/output', exist_ok=True)
        
        # Executar Python com o diretório correto
        cmd = [
            'python3', '-m', 'main',
            f'--month={month}'
        ]
        
        # Executar e capturar output
        process = subprocess.run(
            cmd,
            cwd='/app', 
            capture_output=True,
            text=True,
            timeout=600  
        )
        
        response = {
            "month": month,
            "exitCode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "success": process.returncode == 0,
            "timestamp": datetime.now().isoformat()
        }
        
        status_code = 200 if process.returncode == 0 else 500
        return jsonify(response), status_code
        
    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "Execution timeout (> 10 minutes)",
            "month": month
        }), 500
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
