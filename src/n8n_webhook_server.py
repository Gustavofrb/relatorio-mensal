#!/usr/bin/env python3
"""
Servidor HTTP simples para executar o script de fechamento via n8n
Uso: python3 n8n_webhook_server.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import logging
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 8765

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Endpoint POST /run"""
        if self.path.startswith('/run'):
            self._handle_run()
        else:
            self._send_error(404, "Endpoint não encontrado")
    
    def do_GET(self):
        """Endpoint GET /health"""
        if self.path == '/health':
            self._send_json({"status": "ok", "service": "n8n-webhook"})
        else:
            self._send_error(404, "Use POST /run?month=YYYY-MM")
    
    def _handle_run(self):
        """Executa o script de fechamento"""
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            month = params.get('month', [''])[0]
            
            logger.info(f"Executando fechamento para o mês: {month or 'automático'}")
            
            script = "/home/gustavo/projects/desafioTecnico/src/run_fechamento_n8n.sh"
            cmd = [script] if not month else [script, month]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  
            )
            
            response = {
                "exitCode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "month": month or "automático",
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                logger.info(f"OK Fechamento concluído com sucesso")
                self._send_json(response, status=200)
            else:
                logger.error(f"ERRO Erro no fechamento: {result.stderr}")
                self._send_json(response, status=500)
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na execução do script")
            self._send_json({
                "exitCode": -1,
                "error": "Timeout (5 minutos)",
                "success": False
            }, status=500)
        except Exception as e:
            logger.error(f"Erro: {e}")
            self._send_json({
                "exitCode": -1,
                "error": str(e),
                "success": False
            }, status=500)
    
    def _send_json(self, data, status=200):
        """Envia resposta JSON"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _send_error(self, code, message):
        """Envia erro"""
        self._send_json({"error": message}, status=code)
    
    def log_message(self, format, *args):
        """Override para usar logging"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server():
    """Inicia o servidor"""
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    logger.info(f" Servidor iniciado na porta {PORT}")
    logger.info(f" Health check: http://localhost:{PORT}/health")
    logger.info(f" Executar: POST http://localhost:{PORT}/run?month=2025-10")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info(" Servidor encerrado")
        server.shutdown()

if __name__ == "__main__":
    run_server()
