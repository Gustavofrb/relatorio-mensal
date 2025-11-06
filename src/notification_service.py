# src/notification_service.py

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from datetime import datetime

class NotificationService:
    """
    Serviço centralizado para envio de notificações sobre o fechamento mensal.
    Suporta: Email, Webhook (Slack/Teams), e logs estruturados.
    """
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "automacao@seazone.com")
        
        self.finance_team = os.getenv("FINANCE_EMAILS", "financeiro@seazone.com").split(",")
        self.operations_team = os.getenv("OPERATIONS_EMAILS", "operacoes@seazone.com").split(",")
        self.support_team = os.getenv("SUPPORT_EMAILS", "suporte@seazone.com").split(",")
        self.it_team = os.getenv("IT_EMAILS", "ti@seazone.com").split(",")
        
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        
    def send_success_notification(self, month: str, report_paths: dict) -> None:
        """
        Envia notificação de sucesso após fechamento mensal.
        """
        logging.info("Enviando notificações de sucesso...")
        
        subject = f"OK Fechamento Mensal {month} - Concluído com Sucesso"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .report {{ background-color: #f1f1f1; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>OK Fechamento Mensal Concluído</h1>
            </div>
            <div class="content">
                <p><strong>Mês de Referência:</strong> {month}</p>
                <p><strong>Data/Hora de Processamento:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                
                <h2> Relatórios Gerados</h2>
                <div class="report">
                    <strong>Relatório Financeiro:</strong> {report_paths.get('financial', 'N/A')}
                </div>
                <div class="report">
                    <strong>Relatório de Qualidade:</strong> {report_paths.get('quality', 'N/A')}
                </div>
                <div class="report">
                    <strong>Relatório de Ocupação:</strong> {report_paths.get('occupancy', 'N/A')}
                </div>
                
                <h3> Próximos Passos</h3>
                <ul>
                    <li>Os relatórios estão anexados a este email</li>
                    <li>Dados disponíveis no banco SQLite: <code>data/database.sqlite</code></li>
                    <li>Consulte o dashboard para visualizações interativas</li>
                </ul>
                
                <div class="footer">
                    <p>Automação Seazone Tech | Sistema de Fechamento Mensal v1.0</p>
                    <p>Em caso de dúvidas, entre em contato com a equipe de TI</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        all_recipients = list(set(
            self.finance_team + 
            self.operations_team + 
            self.support_team
        ))
        
        self._send_email(
            to_emails=all_recipients,
            subject=subject,
            html_body=html_body,
            attachments=[
                report_paths.get('financial'),
                report_paths.get('quality'),
                report_paths.get('occupancy')
            ]
        )
        
        self._send_slack_notification(
            message=f"OK Fechamento mensal {month} concluído com sucesso!",
            color="good"
        )
        
    def send_error_notification(self, month: str, error: Exception) -> None:
        """
        Envia notificação de erro para equipe de TI.
        """
        logging.error("Enviando notificações de erro...")
        
        subject = f"ERRO ERRO no Fechamento Mensal {month}"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .error {{ background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0; }}
                code {{ background-color: #f5f5f5; padding: 2px 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ERRO Erro no Fechamento Mensal</h1>
            </div>
            <div class="content">
                <p><strong>Mês de Referência:</strong> {month}</p>
                <p><strong>Data/Hora:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                
                <div class="error">
                    <h3>Detalhes do Erro:</h3>
                    <p><strong>Tipo:</strong> {type(error).__name__}</p>
                    <p><strong>Mensagem:</strong> {str(error)}</p>
                </div>
                
                <h3> Ações Necessárias</h3>
                <ul>
                    <li>Verificar os logs em <code>output/run.log</code></li>
                    <li>Validar conectividade com a API externa</li>
                    <li>Verificar integridade do banco de dados</li>
                    <li>Executar manualmente: <code>python main.py --month {month}</code></li>
                </ul>
                
                <p><strong>AVISO IMPORTANTE:</strong> O fechamento mensal não foi concluído. 
                Os relatórios do mês {month} não foram gerados.</p>
            </div>
        </body>
        </html>
        """
        
        self._send_email(
            to_emails=self.it_team,
            subject=subject,
            html_body=html_body
        )
        
        # Alerta crítico no Slack
        self._send_slack_notification(
            message=f" ERRO no fechamento mensal {month}: {str(error)}",
            color="danger"
        )
        
    def send_daily_summary(self, month: str, stats: dict) -> None:
        """
        Envia resumo executivo do fechamento para liderança.
        """
        subject = f" Resumo Executivo - Fechamento {month}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2> Resumo Executivo - {month}</h2>
            
            <h3>Métricas Consolidadas</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #4CAF50; color: white;">
                    <th style="padding: 10px; text-align: left;">Métrica</th>
                    <th style="padding: 10px; text-align: right;">Valor</th>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">Total de Imóveis Ativos</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats.get('total_properties', 0)}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">Faturamento Bruto Total</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">R$ {stats.get('total_revenue', 0):,.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">Receita Líquida Total</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">R$ {stats.get('net_revenue', 0):,.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">Taxa de Ocupação Média</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats.get('avg_occupancy', 0):.1f}%</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;">Nota Média dos Hóspedes</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats.get('avg_rating', 0):.2f} ⭐</td>
                </tr>
            </table>
            
            <p style="margin-top: 30px; color: #666; font-size: 12px;">
                Relatórios detalhados disponíveis no sistema | 
                <a href="#">Acessar Dashboard</a>
            </p>
        </body>
        </html>
        """
        
        # Envia apenas para liderança
        leadership_emails = os.getenv("LEADERSHIP_EMAILS", "diretoria@seazone.com").split(",")
        self._send_email(
            to_emails=leadership_emails,
            subject=subject,
            html_body=html_body
        )
    
    def _send_email(
        self, 
        to_emails: List[str], 
        subject: str, 
        html_body: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Envia email via SMTP.
        """
        if not self.smtp_user or not self.smtp_password:
            logging.warning("Credenciais SMTP não configuradas. Email não enviado.")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Anexar arquivos
            if attachments:
                for file_path in attachments:
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Conecta e envia
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logging.info(f"Email enviado com sucesso para: {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar email: {e}")
            return False
    
    def _send_slack_notification(self, message: str, color: str = "good") -> bool:
        """
        Envia notificação para Slack via webhook.
        """
        if not self.slack_webhook:
            logging.warning("Webhook do Slack não configurado.")
            return False
            
        try:
            import requests
            
            payload = {
                "attachments": [{
                    "color": color,
                    "text": message,
                    "footer": "Automação Seazone",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(self.slack_webhook, json=payload)
            response.raise_for_status()
            
            logging.info("Notificação Slack enviada com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar notificação Slack: {e}")
            return False
