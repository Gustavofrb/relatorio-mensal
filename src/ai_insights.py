# src/ai_insights.py

"""
Módulo de IA para análise inteligente de feedbacks e geração de insights.

Funcionalidades:
1. Classificação automática de reclamações
2. Análise de sentimento
3. Geração de resumos executivos
4. Alertas preditivos de problemas recorrentes
5. Chatbot para consultas conversacionais

Nota: Este módulo pode usar OpenAI, Anthropic, ou modelos locais via Ollama.
"""

import logging
import os
from typing import List, Dict, Optional
import pandas as pd

class AIInsightsGenerator:
    """
    Gerador de insights inteligentes usando LLM.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gpt-4")
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logging.warning(
                "IA não habilitada (OPENAI_API_KEY não configurada). "
                "Funcionalidades de IA estarão desabilitadas."
            )
    
    def classify_complaints(self, feedback_df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica automaticamente feedbacks em categorias.
        
        Categorias: limpeza, manutenção, check-in, localização, 
                   comunicação, equipamentos, barulho, etc.
        """
        if not self.enabled:
            logging.info("IA desabilitada - usando classificação por palavras-chave")
            return self._classify_by_keywords(feedback_df)
        
        logging.info("Classificando feedbacks com IA...")
        
        try:
            import openai
            openai.api_key = self.api_key
            
            classified = feedback_df.copy()
            
            for idx, row in classified.iterrows():
                feedback_text = row.get('feedback_text', '')
                
                if pd.isna(feedback_text) or len(feedback_text.strip()) < 10:
                    continue
                
                prompt = f"""
Classifique o seguinte feedback de hóspede em UMA das categorias:
- limpeza
- manutenção
- check-in
- localização
- comunicação
- equipamentos
- barulho
- wifi
- água quente
- estacionamento
- outro

Feedback: "{feedback_text}"

Responda apenas com o nome da categoria, nada mais.
"""
                
                try:
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=10,
                        temperature=0
                    )
                    
                    category = response.choices[0].message.content.strip().lower()
                    classified.at[idx, 'ai_category'] = category
                    
                except Exception as e:
                    logging.warning(f"Erro ao classificar feedback {idx}: {e}")
                    continue
            
            return classified
            
        except ImportError:
            logging.warning("Biblioteca openai não instalada. Usando classificação simples.")
            return self._classify_by_keywords(feedback_df)
        except Exception as e:
            logging.error(f"Erro na classificação com IA: {e}")
            return self._classify_by_keywords(feedback_df)
    
    def _classify_by_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classificação simples por palavras-chave.
        """
        categories_keywords = {
            'limpeza': ['sujo', 'limpo', 'limpeza', 'sujeira', 'higiene'],
            'manutenção': ['quebrado', 'estragado', 'manutenção', 'defeito', 'conserto'],
            'check-in': ['check-in', 'checkin', 'entrada', 'chave', 'recepção'],
            'localização': ['localização', 'local', 'distante', 'longe', 'acesso'],
            'comunicação': ['comunicação', 'resposta', 'contato', 'atendimento'],
            'equipamentos': ['equipamento', 'aparelho', 'eletrodoméstico', 'tv', 'geladeira'],
            'barulho': ['barulho', 'ruído', 'barulhento', 'silencioso'],
            'wifi': ['wifi', 'wi-fi', 'internet', 'conexão'],
            'água quente': ['água', 'chuveiro', 'banho', 'quente'],
            'estacionamento': ['estacionamento', 'garagem', 'vaga', 'carro'],
        }
        
        classified = df.copy()
        classified['ai_category'] = 'outro'
        
        for category, keywords in categories_keywords.items():
            for idx, row in classified.iterrows():
                text = str(row.get('feedback_text', '')).lower()
                if any(keyword in text for keyword in keywords):
                    classified.at[idx, 'ai_category'] = category
                    break
        
        return classified
    
    def generate_executive_summary(self, unified_df: pd.DataFrame, month: str) -> str:
        """
        Gera um resumo executivo em linguagem natural do fechamento mensal.
        """
        if not self.enabled:
            return self._generate_simple_summary(unified_df, month)
        
        logging.info("Gerando resumo executivo com IA...")
        
        try:
            import openai
            openai.api_key = self.api_key
            
            # Prepara dados agregados para contexto
            stats = {
                "total_properties": len(unified_df),
                "total_revenue": unified_df["gross_revenue"].sum(),
                "avg_occupancy": unified_df["occupancy_rate"].mean() * 100,
                "avg_rating": unified_df["avg_rating"].mean(),
                "best_property": unified_df.nlargest(1, 'net_revenue')['property_id'].values[0],
                "worst_rating": unified_df.nsmallest(1, 'avg_rating')['property_id'].values[0],
            }
            
            prompt = f"""
Você é um analista de dados experiente. Gere um resumo executivo conciso (máximo 200 palavras) 
do fechamento mensal de {month} para uma empresa de gestão de imóveis de temporada.

Dados do mês:
- Total de imóveis ativos: {stats['total_properties']}
- Faturamento bruto total: R$ {stats['total_revenue']:,.2f}
- Taxa média de ocupação: {stats['avg_occupancy']:.1f}%
- Nota média dos hóspedes: {stats['avg_rating']:.2f}/5.0
- Melhor desempenho financeiro: {stats['best_property']}
- Pior avaliação: {stats['worst_rating']}

Inclua: principais destaques, alertas importantes e recomendações de ação.
Use tom profissional mas acessível.
"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logging.error(f"Erro ao gerar resumo com IA: {e}")
            return self._generate_simple_summary(unified_df, month)
    
    def _generate_simple_summary(self, df: pd.DataFrame, month: str) -> str:
        total_properties = len(df)
        total_revenue = df["gross_revenue"].sum()
        avg_occupancy = df["occupancy_rate"].mean() * 100
        avg_rating = df["avg_rating"].mean()
        
        summary = f"""
RESUMO EXECUTIVO - {month}

Processamos {total_properties} imóveis ativos neste mês.

FINANCEIRO:
- Faturamento bruto total: R$ {total_revenue:,.2f}
- Receita líquida total: R$ {df['net_revenue'].sum():,.2f}

OPERACIONAL:
- Taxa média de ocupação: {avg_occupancy:.1f}%
- Total de reservas: {df['reservations_count'].sum():.0f}

QUALIDADE:
- Nota média dos hóspedes: {avg_rating:.2f}/5.0
- Imóveis com nota abaixo de 4.0: {len(df[df['avg_rating'] < 4.0])}

DESTAQUES:
- Top 3 em faturamento: {', '.join(df.nlargest(3, 'net_revenue')['property_id'].tolist())}
- Alertas de qualidade: {len(df[(df['avg_rating'] < 4.0) & (df['occupancy_rate'] > 0.7)])} imóveis com alta ocupação mas nota baixa
"""
        return summary
    
    def detect_recurring_issues(self, feedback_df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Detecta problemas recorrentes por imóvel para gerar alertas proativos.
        """
        issues_by_property = {}
        
        property_col = None
        if 'property_id' in feedback_df.columns:
            property_col = 'property_id'
        elif 'id_imovel' in feedback_df.columns:
            property_col = 'id_imovel'
        else:
            logging.warning("Coluna de identificação do imóvel não encontrada nos feedbacks")
            return issues_by_property
        
        # Agrupa feedbacks por imóvel
        grouped = feedback_df.groupby(property_col)
        
        for property_id, group in grouped:
            if 'ai_category' in group.columns:
                categories = group['ai_category'].value_counts()
                
                # Alerta se mesma categoria aparece 3+ vezes
                recurring = categories[categories >= 3].index.tolist()
                
                if recurring:
                    issues_by_property[property_id] = recurring
        
        return issues_by_property
    
    def generate_property_insight(self, property_data: pd.Series) -> str:
        """
        Gera insight específico para um imóvel.
        """
        if not self.enabled:
            return self._generate_simple_property_insight(property_data)
        
        try:
            import openai
            openai.api_key = self.api_key
            
            prompt = f"""
Analise rapidamente este imóvel e dê uma recomendação de 1 frase:

Imóvel: {property_data['property_id']}
Cidade: {property_data['city']}
Ocupação: {property_data['occupancy_rate'] * 100:.0f}%
Nota: {property_data['avg_rating']:.1f}/5.0
Margem: {property_data['margin_percent']:.1f}%
Reclamações: {property_data.get('complaints_list', 'nenhuma')}

Seja direto e orientado a ação.
"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Erro ao gerar insight: {e}")
            return self._generate_simple_property_insight(property_data)
    
    def _generate_simple_property_insight(self, data: pd.Series) -> str:
        """
        Insight simples sem IA.
        """
        occupancy = data['occupancy_rate'] * 100
        rating = data['avg_rating']
        margin = data['margin_percent']
        
        if occupancy > 80 and rating < 4.0:
            return "AVISO Alta ocupação com nota baixa - risco de cancelamentos futuros"
        elif margin < 10:
            return "💰 Margem muito baixa - revisar precificação e custos"
        elif occupancy < 30:
            return "📉 Baixa ocupação - considerar ajustes de preço ou marketing"
        elif rating > 4.5 and occupancy > 70:
            return "OK Desempenho excelente - benchmark para outros imóveis"
        else:
            return "ℹ️ Desempenho dentro da normalidade"


class PropertyChatbot:
    """
    Chatbot conversacional para consultas sobre os dados de fechamento.
    
    Exemplos de perguntas:
    - "Quais imóveis tiveram margem negativa em outubro?"
    - "Me mostre os 5 imóveis com melhor ocupação em São Paulo"
    - "Quantos imóveis têm nota abaixo de 4.0?"
    """
    
    def __init__(self, db_path: str):
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.enabled = bool(self.api_key)
    
    def query(self, user_question: str) -> str:
        """
        Responde perguntas em linguagem natural sobre os dados.
        """
        if not self.enabled:
            return "Chatbot IA não disponível (configure OPENAI_API_KEY)"
        
        try:
            import openai
            openai.api_key = self.api_key
            
            # Primeiro, gera SQL com IA
            sql_prompt = f"""
Converta a pergunta do usuário em uma query SQL para o banco SQLite.

Tabelas disponíveis:
- monthly_summary (property_id, month, reservations_count, gross_revenue, net_revenue, 
                   occupancy_rate, avg_rating, city, state, region, margin_percent, complaints_list)

Pergunta: "{user_question}"

Retorne APENAS a query SQL, sem explicações.
"""
            
            sql_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": sql_prompt}],
                max_tokens=200,
                temperature=0
            )
            
            sql_query = sql_response.choices[0].message.content.strip()
            
            # Remove formatação markdown se houver
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logging.info(f"SQL gerado: {sql_query}")
            
            # Executa query
            df = pd.read_sql_query(sql_query, self.conn)
            
            # Gera resposta em linguagem natural
            answer_prompt = f"""
Pergunta do usuário: "{user_question}"

Resultados da consulta:
{df.to_string()}

Responda a pergunta do usuário de forma clara e concisa, usando os dados acima.
Se houver muitos resultados, resuma os principais.
"""
            
            answer_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": answer_prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return answer_response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Erro no chatbot: {e}")
            return f"Erro ao processar pergunta: {str(e)}"
    
    def close(self):
        self.conn.close()
