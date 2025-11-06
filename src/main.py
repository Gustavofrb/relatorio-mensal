# src/main.py

import argparse
import logging
import os
import sys

# Garante que imports funcionem tanto rodando de src/ quanto da raiz
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_MONTH, OUTPUT_DIR
from data_collector import DataCollector
from data_transformer import DataTransformer
from data_loader import DataLoader
from report_generator import ReportGenerator
from notification_service import NotificationService
from ai_insights import AIInsightsGenerator
from utils import get_previous_month_str, ensure_dir

def configure_logging():
    ensure_dir(OUTPUT_DIR)
    log_path = os.path.join(OUTPUT_DIR, "run.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ],
    )

def parse_args():
    parser = argparse.ArgumentParser(
        description="Automação de fechamento mensal e geração de relatórios."
    )
    parser.add_argument(
        "--month",
        help="Mês de referência no formato YYYY-MM. Se omitido, usa o mês anterior.",
        default=DEFAULT_MONTH or None
    )
    return parser.parse_args()

def calculate_stats(df) -> dict:
    """Calcula estatísticas consolidadas para o resumo executivo."""
    return {
        "total_properties": len(df),
        "total_revenue": df["gross_revenue"].sum(),
        "net_revenue": df["net_revenue"].sum(),
        "avg_occupancy": df["occupancy_rate"].mean() * 100,
        "avg_rating": df["avg_rating"].mean(),
        "total_reservations": df["reservations_count"].sum(),
    }

def main():
    configure_logging()
    args = parse_args()
    notifier = NotificationService()

    month = args.month or get_previous_month_str()
    logging.info(f"Iniciando processo de fechamento para o mês {month}")

    try:
        # 1. Coleta de dados
        collector = DataCollector()
        raw_data = collector.collect_all(month)

        # 2. Transformação e cálculo de KPIs
        transformer = DataTransformer()
        unified_df = transformer.process(raw_data)

        # 3. Persistência no banco de dados
        loader = DataLoader()
        loader.save_all(unified_df)

        # 4. Análises com IA
        logging.info("Iniciando análises com IA...")
        ai = AIInsightsGenerator()
        
        # 4.1. Classificar feedbacks automaticamente
        if 'feedback' in raw_data and not raw_data['feedback'].empty:
            feedback_classified = ai.classify_complaints(raw_data['feedback'])
            logging.info(f"Feedbacks classificados: {len(feedback_classified)} registros")
            
            feedback_path = os.path.join(OUTPUT_DIR, "feedbacks_classificados.csv")
            feedback_classified.to_csv(feedback_path, index=False)
            logging.info(f"Feedbacks classificados salvos em {feedback_path}")
        
        # 4.2. Detectar problemas recorrentes
        if 'feedback' in raw_data and not raw_data['feedback'].empty:
            recurring_issues = ai.detect_recurring_issues(feedback_classified)
            if recurring_issues:
                logging.warning(f"AVISO: Problemas recorrentes detectados em {len(recurring_issues)} imóveis:")
                for prop, issues in recurring_issues.items():
                    logging.warning(f"   - {property_id}: {', '.join(issues)}")
        
        # 4.3. Gerar resumo executivo
        executive_summary = ai.generate_executive_summary(unified_df, month)
        summary_path = os.path.join(OUTPUT_DIR, "resumo_executivo.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(executive_summary)
        logging.info(f"Resumo executivo salvo em {summary_path}")
        
        # 4.4. Gerar insights por imóvel 
        logging.info("Gerando insights individuais por imóvel...")
        insights = []
        
        # Top 5 melhores
        top5 = unified_df.nlargest(5, 'net_revenue')
        for idx, row in top5.iterrows():
            insight = ai.generate_property_insight(row)
            insights.append({
                'property_id': row['property_id'],
                'city': row['city'],
                'tipo': 'Top Performance',
                'insight': insight
            })
        
        # 5 piores
        bottom5 = unified_df.nsmallest(5, 'net_revenue')
        for idx, row in bottom5.iterrows():
            insight = ai.generate_property_insight(row)
            insights.append({
                'property_id': row['property_id'],
                'city': row['city'],
                'tipo': 'Atenção Necessária',
                'insight': insight
            })
        
        # Salvar insights
        import pandas as pd
        insights_df = pd.DataFrame(insights)
        insights_path = os.path.join(OUTPUT_DIR, "insights_ia.csv")
        insights_df.to_csv(insights_path, index=False)
        logging.info(f"Insights de IA salvos em {insights_path}")
        
        # 5. Geração de relatórios
        reports = ReportGenerator()
        paths = reports.generate(unified_df)

        # 6. Cálculo de estatísticas consolidadas
        stats = calculate_stats(unified_df)

        logging.info("Processo concluído com sucesso.")
        logging.info(f"Relatórios gerados: {paths}")
        logging.info(f"Estatísticas: {stats}")

        # Notificação de sucesso
        notifier.send_success_notification(month, paths)
        notifier.send_daily_summary(month, stats)

    except Exception as e:
        logging.exception(f"Erro durante o processo: {e}")
        
        # Notificação de erro
        try:
            notifier.send_error_notification(month, e)
        except:
            logging.error("Falha ao enviar notificação de erro")
        
        raise

if __name__ == "__main__":
    main()
