#!/usr/bin/env python
"""
Script demonstrativo das funcionalidades de IA.

Este script mostra como usar:
1. Classificação automática de feedbacks
2. Geração de resumo executivo
3. Chatbot conversacional para consultas

Uso:
    python demo_ai.py
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_insights import AIInsightsGenerator, PropertyChatbot
import pandas as pd
import sqlite3


def demo_classificacao_feedbacks():
    """
    Demonstra a classificação automática de feedbacks.
    """
    print("\n" + "="*60)
    print("DEMO 1: Classificação Automática de Feedbacks")
    print("="*60)
    
    # Feedbacks de exemplo
    feedbacks_exemplo = pd.DataFrame({
        'property_id': ['SP-001', 'RJ-002', 'MG-003', 'SP-004'],
        'feedback_text': [
            'O apartamento estava muito sujo, a limpeza deixou a desejar',
            'WiFi não funcionava e o ar condicionado estava quebrado',
            'Check-in demorado, tive que esperar 1 hora para pegar as chaves',
            'Localização excelente, mas o barulho da rua atrapalhou muito'
        ]
    })
    
    print("\n Feedbacks recebidos:")
    for idx, row in feedbacks_exemplo.iterrows():
        print(f"\n{row['property_id']}: \"{row['feedback_text']}\"")
    
    # Classificar com IA
    ai = AIInsightsGenerator()
    
    if ai.enabled:
        print("\n Classificando com IA (OpenAI)...")
        classificados = ai.classify_complaints(feedbacks_exemplo)
        
        print("\nOK Resultados da classificação:")
        for idx, row in classificados.iterrows():
            categoria = row.get('ai_category', 'não classificado')
            print(f"  {row['property_id']}: [{categoria}]")
    else:
        print("\nAVISO  IA não habilitada. Usando classificação por palavras-chave...")
        classificados = ai._classify_by_keywords(feedbacks_exemplo)
        
        print("\nOK Resultados (fallback):")
        for idx, row in classificados.iterrows():
            categoria = row.get('ai_category', 'outro')
            print(f"  {row['property_id']}: [{categoria}]")


def demo_resumo_executivo():
    """
    Demonstra a geração de resumo executivo.
    """
    print("\n" + "="*60)
    print("DEMO 2: Resumo Executivo com IA")
    print("="*60)
    
    # Carrega dados reais do banco
    db_path = "data/database.sqlite"
    
    if not os.path.exists(db_path):
        print("\nAVISO  Banco de dados não encontrado. Execute 'python main.py' primeiro.")
        return
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT * FROM monthly_summary ORDER BY month DESC LIMIT 50", 
        conn
    )
    conn.close()
    
    if df.empty:
        print("\nAVISO  Nenhum dado encontrado no banco.")
        return
    
    month = df['month'].iloc[0]
    print(f"\n Gerando resumo para o mês: {month}")
    print(f"   Total de imóveis: {len(df)}")
    
    ai = AIInsightsGenerator()
    resumo = ai.generate_executive_summary(df, month)
    
    print("\n📄 RESUMO EXECUTIVO:")
    print("-" * 60)
    print(resumo)
    print("-" * 60)


def demo_chatbot():
    """
    Demonstra o chatbot conversacional.
    """
    print("\n" + "="*60)
    print("DEMO 3: Chatbot Conversacional")
    print("="*60)
    
    db_path = "data/database.sqlite"
    
    if not os.path.exists(db_path):
        print("\nAVISO  Banco de dados não encontrado. Execute 'python main.py' primeiro.")
        return
    
    chatbot = PropertyChatbot(db_path)
    
    if not chatbot.enabled:
        print("\nAVISO  Chatbot IA não disponível.")
        print("   Configure OPENAI_API_KEY para habilitar.")
        chatbot.close()
        return
    
    print("\n Chatbot Seazone - Pronto para responder perguntas!")
    print("   (digite 'sair' para encerrar)")
    
    perguntas_exemplo = [
        "Quantos imóveis foram processados no último mês?",
        "Quais os 3 imóveis com maior faturamento?",
        "Mostre imóveis com nota abaixo de 4.0",
        "Qual a taxa média de ocupação em São Paulo?"
    ]
    
    print("\n💡 Perguntas sugeridas:")
    for i, pergunta in enumerate(perguntas_exemplo, 1):
        print(f"   {i}. {pergunta}")
    
    print("\n" + "-"*60)
    
    while True:
        try:
            pergunta = input("\n❓ Você: ").strip()
            
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando chatbot...")
                break
            
            if not pergunta:
                continue
            
            print("\n Processando...")
            resposta = chatbot.query(pergunta)
            print(f"\n💬 Chatbot: {resposta}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Encerrando chatbot...")
            break
        except Exception as e:
            print(f"\nERRO Erro: {e}")
    
    chatbot.close()


def demo_insights_propriedade():
    """
    Demonstra insights individuais por imóvel.
    """
    print("\n" + "="*60)
    print("DEMO 4: Insights Individuais por Imóvel")
    print("="*60)
    
    db_path = "data/database.sqlite"
    
    if not os.path.exists(db_path):
        print("\nAVISO  Banco de dados não encontrado.")
        return
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        """
        SELECT * FROM monthly_summary 
        ORDER BY month DESC 
        LIMIT 5
        """, 
        conn
    )
    conn.close()
    
    if df.empty:
        print("\nAVISO  Nenhum dado encontrado.")
        return
    
    print(f"\n🏠 Gerando insights para 5 imóveis de exemplo...")
    
    ai = AIInsightsGenerator()
    
    for idx, property_data in df.iterrows():
        property_id = property_data['property_id']
        city = property_data['city']
        
        insight = ai.generate_property_insight(property_data)
        
        print(f"\n {property_id} ({city})")
        print(f"   Ocupação: {property_data['occupancy_rate']*100:.1f}% | "
              f"Nota: {property_data['avg_rating']:.1f}/5.0 | "
              f"Margem: {property_data['margin_percent']:.1f}%")
        print(f"   💡 Insight: {insight}")


def main():
    """
    Menu principal do script de demonstração.
    """
    print("\n" + " "* 20)
    print("DEMONSTRAÇÃO DE FUNCIONALIDADES DE IA")
    print("Sistema de Fechamento Mensal - Seazone Tech")
    print(" " * 20)
    
    # Verificar se OpenAI está configurada
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key:
        print("\nAVISO  AVISO: OPENAI_API_KEY não configurada.")
        print("   As funcionalidades de IA usarão fallback (sem LLM).")
        print("   Para habilitar IA completa, configure a variável de ambiente:")
        print("   export OPENAI_API_KEY='sk-proj-...'")
    else:
        print("\nOK OpenAI API configurada - IA completa habilitada!")
    
    while True:
        print("\n" + "-"*60)
        print("Escolha uma demonstração:")
        print("-"*60)
        print("1. Classificação Automática de Feedbacks")
        print("2. Resumo Executivo com IA")
        print("3. Chatbot Conversacional")
        print("4. Insights Individuais por Imóvel")
        print("5. Executar todas as demos")
        print("0. Sair")
        print("-"*60)
        
        try:
            escolha = input("\nDigite sua escolha (0-5): ").strip()
            
            if escolha == '0':
                print("\n👋 Encerrando...")
                break
            elif escolha == '1':
                demo_classificacao_feedbacks()
            elif escolha == '2':
                demo_resumo_executivo()
            elif escolha == '3':
                demo_chatbot()
            elif escolha == '4':
                demo_insights_propriedade()
            elif escolha == '5':
                demo_classificacao_feedbacks()
                demo_resumo_executivo()
                demo_insights_propriedade()
                demo_chatbot()
            else:
                print("\nERRO Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Encerrando...")
            break
        except Exception as e:
            print(f"\nERRO Erro: {e}")
    
    print("\nOK Demo encerrada com sucesso!")


if __name__ == "__main__":
    main()
