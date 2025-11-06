# 🏠 Sistema de Fechamento Mensal Automatizado - Seazone Tech

> Solução completa para automação do fechamento mensal de imóveis de temporada, eliminando processos manuais e criando uma fonte única da verdade para dados operacionais.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Problema Resolvido](#-problema-resolvido)
- [Arquitetura da Solução](#-arquitetura-da-solução)
- [Como Funciona](#-como-funciona)
- [Instalação e Configuração](#-instalação-e-configuração)
- [Execução](#-execução)
- [Orquestração e Agendamento](#-orquestração-e-agendamento)
- [Relatórios Gerados](#-relatórios-gerados)
- [Monitoramento e Alertas](#-monitoramento-e-alertas)
- [Funcionalidades com IA](#-funcionalidades-com-ia-bônus)
- [Escalabilidade](#-escalabilidade)
- [Governança de Dados](#-governança-de-dados)
- [FAQ](#-faq)

---

## 🎯 Visão Geral

Este sistema substitui o processo manual caótico de fechamento mensal, onde três equipes diferentes editavam uma única planilha gigante, gerando:

- ❌ Retrabalho constante
- ❌ Dados inconsistentes
- ❌ Zero rastreabilidade
- ❌ Falta de governança

Por uma solução automatizada que:

- ✅ **Coleta automática** de dados via API
- ✅ **Transformação e cálculo** padronizado de KPIs
- ✅ **Persistência** em banco de dados (fonte única da verdade)
- ✅ **Geração automática** de 3 relatórios principais
- ✅ **Distribuição inteligente** por email/Slack
- ✅ **Monitoramento** com logs e alertas
- ✅ **Insights com IA** (análise de feedbacks, chatbot)

---

## 🔥 Problema Resolvido

### Antes (Processo Manual)

```
Equipe Hosting → Copia dados da plataforma → Cola na planilha
       ↓
Equipe Suporte → Copia feedbacks CSV → Cola na planilha
       ↓
Equipe Financeiro → Adiciona custos → Cola na planilha
       ↓
    ❌ PLANILHA QUEBRA ❌
       ↓
Cada time gera seu próprio relatório "do jeito que dá"
```

### Depois (Automação)

```
API Mock (3 fontes) → Data Collector → Transformer → SQLite DB
                                                         ↓
                                                    Fonte Única
                                                         ↓
                                  ┌──────────────────────┴──────────────────────┐
                                  ↓                      ↓                      ↓
                          Relatório Financeiro   Relatório Qualidade   Relatório Ocupação
                                  ↓                      ↓                      ↓
                            Email/Slack            Email/Slack            Email/Slack
```

---

## 🏗️ Arquitetura da Solução

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE ORQUESTRAÇÃO                       │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │     n8n      │ ou│ GitHub Actions│ ou│  Cron Job    │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   CAMADA DE INGESTÃO                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  data_collector.py                                        │  │
│  │  - /bookings-operational   (reservas por imóvel)          │  │
│  │  - /property-details        (dados cadastrais)            │  │
│  │  - /platform-fees           (taxas por cidade)            │  │
│  │  - /guest-feedback          (avaliações CSV)              │  │
│  │  - /extra-costs             (custos extras CSV)           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                 CAMADA DE TRANSFORMAÇÃO                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  data_transformer.py                                      │  │
│  │  - Agregação de métricas                                  │  │
│  │  - Cálculo de KPIs padronizados                           │  │
│  │  - Join de múltiplas fontes                               │  │
│  │  - Validação de qualidade                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA DE PERSISTÊNCIA                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite / PostgreSQL (Supabase)                           │  │
│  │  - properties (dimensão)                                  │  │
│  │  - monthly_summary (fato)                                 │  │
│  │  - execution_logs (auditoria)                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA DE APRESENTAÇÃO                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  report_generator.py + notification_service.py            │  │
│  │  - CSV: Financeiro, Qualidade, Ocupação                   │  │
│  │  - PDF: Resumo Executivo (opcional)                       │  │
│  │  - Email: Distribuição por equipe                         │  │
│  │  - Slack: Alertas em tempo real                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Como Funciona

### Fluxo Completo (Executado Todo Dia 1º do Mês)

1. **Trigger Automático** (00:00 dia 1º do mês)
   - n8n ou GitHub Actions dispara o workflow
   - Calcula automaticamente o mês anterior

2. **Coleta de Dados** (`data_collector.py`)
   ```python
   # Coleta das 5 fontes de dados em paralelo
   - Bookings Operational (API JSON)
   - Property Details (API JSON)
   - Platform Fees (API JSON)
   - Guest Feedback (CSV)
   - Extra Costs (CSV)
   ```

3. **Transformação** (`data_transformer.py`)
   ```python
   # Calcula KPIs padronizados:
   - Taxa de Ocupação = (dias_ocupados / dias_no_mês) × 100
   - Receita Líquida = faturamento_bruto - taxas - custos_extras
   - Margem % = (receita_líquida / faturamento_bruto) × 100
   - Nota Média = AVG(ratings)
   ```

4. **Persistência** (`data_loader.py`)
   ```python
   # Salva no SQLite (fonte única da verdade)
   - Tabela: properties (dimensão)
   - Tabela: monthly_summary (fato principal)
   ```

5. **Geração de Relatórios** (`report_generator.py`)
   ```python
   # 3 relatórios principais em CSV
   - relatorio_financeiro.csv
   - relatorio_qualidade.csv
   - relatorio_ocupacao.csv
   ```

6. **Distribuição** (`notification_service.py`)
   ```python
   # Envia relatórios segmentados:
   - Financeiro → financeiro@seazone.com
   - Qualidade → suporte@seazone.com + operacoes@seazone.com
   - Ocupação → operacoes@seazone.com
   - Resumo Executivo → diretoria@seazone.com
   
   # Alertas no Slack
   - Canal #operations: notificação de sucesso/erro
   ```

7. **IA & Insights** (`ai_insights.py`) - Opcional
   ```python
   # Análises inteligentes:
   - Classificação automática de feedbacks
   - Resumo executivo em linguagem natural
   - Alertas preditivos (problemas recorrentes)
   - Chatbot para consultas SQL em linguagem natural
   ```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- pip
- Git

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd desafioTecnico
```

### 2. Crie Ambiente Virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Instale Dependências

```bash
cd src
pip install -r requirements.txt
```

### 4. Configure Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
# SMTP para envio de emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=automacao@seazone.com
SMTP_PASSWORD=sua_senha_app

# Destinatários por equipe
FROM_EMAIL=automacao@seazone.com
FINANCE_EMAILS=financeiro@seazone.com
OPERATIONS_EMAILS=operacoes@seazone.com
SUPPORT_EMAILS=suporte@seazone.com
IT_EMAILS=ti@seazone.com
LEADERSHIP_EMAILS=diretoria@seazone.com

# Webhook Slack (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# OpenAI para IA (opcional)
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4
```

---

## 🎮 Execução

### Execução Manual

```bash
cd src

# Processa o mês anterior automaticamente
python main.py

# Ou especifica um mês específico
python main.py --month 2025-10
```

### Saída Esperada

```
2025-11-05 13:17:11 [INFO] Iniciando processo de fechamento para o mês 2025-10
2025-11-05 13:17:11 [INFO] Iniciando coleta de dados para o mês 2025-10
2025-11-05 13:17:12 [INFO] bookings-operational: 50 linhas
2025-11-05 13:17:12 [INFO] property-details: 50 linhas
2025-11-05 13:17:12 [INFO] platform-fees: 50 linhas
2025-11-05 13:17:12 [INFO] guest-feedback: 648 linhas
2025-11-05 13:17:12 [INFO] extra-costs: 304 linhas
2025-11-05 13:17:12 [INFO] Iniciando transformação dos dados...
2025-11-05 13:17:12 [INFO] Transformação concluída: 50 linhas no dataset final.
2025-11-05 13:17:12 [INFO] Salvando tabela 'properties'...
2025-11-05 13:17:12 [INFO] Salvando tabela 'monthly_summary'...
2025-11-05 13:17:13 [INFO] Gerando relatórios...
2025-11-05 13:17:13 [INFO] Relatório salvo em output\relatorio_financeiro.csv
2025-11-05 13:17:13 [INFO] Relatório salvo em output\relatorio_qualidade.csv
2025-11-05 13:17:13 [INFO] Relatório salvo em output\relatorio_ocupacao.csv
2025-11-05 13:17:13 [INFO] Processo concluído com sucesso.
```

### Arquivos Gerados

```
src/
├── data/
│   └── database.sqlite          ← Fonte única da verdade
├── output/
│   ├── relatorio_financeiro.csv ← Para financeiro & proprietários
│   ├── relatorio_qualidade.csv  ← Para suporte & operações
│   ├── relatorio_ocupacao.csv   ← Para operações
│   └── run.log                  ← Logs detalhados
```

---

## 🤖 Orquestração e Agendamento

### Opção 1: n8n (Recomendado)

**Arquivo:** `workflows/n8n_workflow.json`

1. **Importar workflow** no n8n
2. **Configurar credenciais:**
   - API Token Seazone
   - Credenciais SMTP
   - Webhook Slack
   - Conexão PostgreSQL/Supabase (para logs)

3. **Ativar workflow**

**Funcionalidades do workflow n8n:**
- ✅ Schedule trigger (dia 1º do mês às 00:00)
- ✅ Coleta paralela de todas as fontes
- ✅ Execução do script Python
- ✅ Verificação de sucesso/erro
- ✅ Envio de emails com anexos
- ✅ Alertas no Slack
- ✅ Registro de execução no banco

### Opção 2: GitHub Actions (Alternativa)

**Arquivo:** `.github/workflows/monthly-closing.yml`

- ✅ Execução automática via cron
- ✅ Execução manual pelo GitHub UI
- ✅ Upload de relatórios como artifacts
- ✅ Notificações no Slack
- ✅ Criação automática de issues em caso de erro

**Para ativar:**
1. Configure secrets no GitHub:
   - `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`
   - `FINANCE_EMAILS`, `OPERATIONS_EMAILS`, etc.
   - `SLACK_WEBHOOK_URL`
   - `OPENAI_API_KEY` (opcional)

2. Push para o repositório
3. Workflow roda automaticamente todo dia 1º

### Opção 3: Cron Job (Servidor Linux)

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa dia 1º às 00:00)
0 0 1 * * cd /path/to/desafioTecnico/src && /path/to/.venv/bin/python main.py >> /var/log/fechamento-mensal.log 2>&1
```

---

## 📊 Relatórios Gerados

### 1. Relatório Financeiro (`relatorio_financeiro.csv`)

**Destinatários:** Equipe Financeira + Proprietários

**Colunas:**
- `property_id` - ID do imóvel
- `owner_name` - Nome do proprietário/condomínio
- `city`, `state`, `region` - Localização
- `month` - Mês de referência
- `reservations_count` - Quantidade de reservas
- `gross_revenue` - Faturamento bruto (R$)
- `platform_fee_amount` - Taxa da plataforma (R$)
- `extra_cost_total` - Custos extras (R$)
- `net_revenue` - Receita líquida (R$)
- `margin_value` - Margem (R$)
- `margin_percent` - Margem (%)

**Exemplo:**
```csv
property_id,owner_name,city,gross_revenue,net_revenue,margin_percent
SP-SAO-PAULO-001,Vila Jardim,São Paulo,24000.00,20400.00,85.0
RJ-RIO-JANEIRO-001,Condomínio Mar,Rio de Janeiro,18500.00,15200.00,82.2
```

### 2. Relatório de Qualidade (`relatorio_qualidade.csv`)

**Destinatários:** Equipe de Suporte + Operações

**Colunas:**
- `property_id` - ID do imóvel
- `owner_name` - Nome do proprietário
- `city`, `state`, `region` - Localização
- `month` - Mês de referência
- `avg_rating` - Nota média dos hóspedes (0-5)
- `complaints_list` - Reclamações categorizadas

**Uso:**
- Identificar imóveis com notas baixas
- Priorizar ações de melhoria
- Prevenir cancelamentos futuros

### 3. Relatório de Ocupação (`relatorio_ocupacao.csv`)

**Destinatários:** Equipe de Operações (Hosting)

**Colunas:**
- `property_id` - ID do imóvel
- `owner_name` - Nome do proprietário
- `city`, `state`, `region` - Localização
- `month` - Mês de referência
- `reservations_count` - Quantidade de reservas
- `occupied_days` - Dias ocupados
- `occupancy_rate` - Taxa de ocupação (0-1)

**Uso:**
- Benchmarking por região
- Ajustes de precificação
- Ações de marketing para imóveis com baixa ocupação

---

## 🔔 Monitoramento e Alertas

### Logs Estruturados

**Arquivo:** `output/run.log`

- Timestamp de cada etapa
- Quantidade de registros processados
- Erros detalhados com stack trace
- Estatísticas consolidadas

### Notificações por Email

**Cenário de Sucesso:**
- Assunto: ✅ Fechamento Mensal YYYY-MM - Concluído
- Corpo: Resumo executivo + estatísticas
- Anexos: 3 relatórios CSV

**Cenário de Erro:**
- Assunto: ❌ ERRO no Fechamento Mensal
- Corpo: Detalhes do erro + ações necessárias
- Destinatários: Equipe de TI

### Alertas no Slack

**Canal #operations:**
- Notificação de sucesso (verde)
- Alerta de erro (vermelho)
- Link direto para logs

### Rastreabilidade

**Banco de Dados - Tabela `execution_logs`:**
```sql
CREATE TABLE execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_date TIMESTAMP,
    month_ref TEXT,
    status TEXT,  -- 'success' ou 'error'
    error_message TEXT,
    duration_seconds INTEGER
);
```

**Consulta de Histórico:**
```sql
SELECT * FROM execution_logs 
ORDER BY execution_date DESC 
LIMIT 10;
```

---

## 🤖 Funcionalidades com IA (Bônus)

### 1. Classificação Automática de Feedbacks

**Módulo:** `ai_insights.py` → `AIInsightsGenerator.classify_complaints()`

- **Entrada:** Texto livre do feedback do hóspede
- **Saída:** Categoria padronizada (limpeza, manutenção, check-in, wifi, etc.)
- **Tecnologia:** OpenAI GPT-4 ou fallback para keywords

**Exemplo:**
```python
feedback_text = "O chuveiro estava frio e o WiFi não funcionava"
categoria = ai.classify_complaints(feedback_df)
# Resultado: ["água quente", "wifi"]
```

### 2. Resumo Executivo em Linguagem Natural

**Módulo:** `ai_insights.py` → `AIInsightsGenerator.generate_executive_summary()`

- **Entrada:** DataFrame consolidado do mês
- **Saída:** Texto narrativo de 150-200 palavras
- **Uso:** Email para liderança/diretoria

**Exemplo de Saída:**
```
"Em outubro de 2025, processamos 50 imóveis ativos com faturamento 
bruto de R$ 642.300,00. A taxa média de ocupação foi de 73,2%, 
ligeiramente abaixo do trimestre anterior. Destaque positivo para 
SP-SAO-PAULO-005 (Jardim Europa), líder em faturamento com R$ 45.200,00.

ALERTA: 8 imóveis apresentam alta ocupação (>70%) mas nota baixa (<4.0),
indicando risco de cancelamentos futuros. Recomendamos ação imediata 
nas propriedades RJ-RIO-JANEIRO-002 e MG-BELO-HORIZONTE-007.

Reclamações recorrentes sobre 'limpeza' foram identificadas em 12 imóveis,
sugerindo necessidade de revisão dos processos de higienização."
```

### 3. Detecção de Problemas Recorrentes

**Módulo:** `ai_insights.py` → `AIInsightsGenerator.detect_recurring_issues()`

- **Lógica:** Se mesma categoria de reclamação aparece 3+ vezes no mesmo imóvel
- **Saída:** Alerta proativo para equipe de operações

**Exemplo:**
```python
{
    "SP-SAO-PAULO-007": ["limpeza", "wifi"],
    "RJ-RIO-JANEIRO-003": ["check-in", "comunicação"]
}
```

### 4. Chatbot Conversacional (PropertyChatbot)

**Módulo:** `ai_insights.py` → `PropertyChatbot`

**Perguntas Suportadas:**
- "Quais imóveis tiveram margem negativa em outubro?"
- "Me mostre os 5 imóveis com melhor ocupação em São Paulo"
- "Quantos imóveis têm nota abaixo de 4.0?"
- "Lista imóveis com alta ocupação mas nota baixa"

**Tecnologia:**
1. LLM converte pergunta em SQL
2. Executa query no SQLite
3. LLM formata resposta em linguagem natural

**Exemplo de Uso:**
```python
chatbot = PropertyChatbot("data/database.sqlite")
resposta = chatbot.query("Quais imóveis de São Paulo têm margem abaixo de 10%?")
print(resposta)
# "Foram encontrados 3 imóveis em São Paulo com margem abaixo de 10%:
#  - SP-SAO-PAULO-004: 8.2%
#  - SP-SAO-PAULO-009: 7.5%
#  - SP-SAO-PAULO-012: 5.1%"
```

### Configuração de IA

**Variável de Ambiente:**
```env
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=gpt-4  # ou gpt-3.5-turbo para economia
```

**Fallback sem IA:**
- Se `OPENAI_API_KEY` não configurada, usa classificação por keywords
- Resumos simples com estatísticas diretas
- Chatbot desabilitado (retorna mensagem explicativa)

---

## 📈 Escalabilidade

### Cenário Atual: 50 Imóveis
- ✅ SQLite funciona perfeitamente
- ✅ Processamento em segundos
- ✅ Relatórios leves (~50KB)

### Cenário Futuro: 5.000 Imóveis

#### 1. Banco de Dados

**Migração: SQLite → PostgreSQL (Supabase)**

```sql
-- Criar no Supabase
CREATE TABLE properties (...);
CREATE TABLE monthly_summary (...);

-- Índices para performance
CREATE INDEX idx_monthly_summary_month ON monthly_summary(month);
CREATE INDEX idx_monthly_summary_city ON monthly_summary(city);
CREATE INDEX idx_monthly_summary_region ON monthly_summary(region);

-- Particionamento por ano
CREATE TABLE monthly_summary_2025 PARTITION OF monthly_summary
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

**Vantagens:**
- Suporta milhões de registros
- Queries paralelas
- Backup automático
- API REST nativa

#### 2. Processamento

**Otimizações:**

```python
# Processamento em chunks
for chunk in pd.read_csv('large_file.csv', chunksize=1000):
    process(chunk)

# Paralelização com multiprocessing
from multiprocessing import Pool
with Pool(4) as p:
    results = p.map(process_property, properties)

# Caching de dados estáticos
@lru_cache(maxsize=1000)
def get_property_details(property_id):
    return db.query(...)
```

#### 3. Armazenamento de Relatórios

**Migração: CSV Local → Cloud Storage**

```python
# AWS S3 / Google Cloud Storage
s3_client.upload_file(
    'relatorio_financeiro.csv',
    'seazone-reports',
    f'reports/{year}/{month}/financeiro.csv'
)

# Gerar URLs assinadas para acesso temporário
url = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'seazone-reports', 'Key': 'reports/2025/10/financeiro.csv'},
    ExpiresIn=3600
)
```

#### 4. Dashboard Interativo

**Opções:**

- **Streamlit** (Python, fácil)
- **Metabase** (Open-source BI)
- **Superset** (Apache, poderoso)
- **PowerBI / Looker** (Enterprise)

**Exemplo com Streamlit:**
```python
import streamlit as st
import pandas as pd

st.title("Dashboard Fechamento Mensal")

month = st.selectbox("Selecione o mês", ["2025-10", "2025-09", ...])
df = load_data(month)

col1, col2, col3 = st.columns(3)
col1.metric("Faturamento Total", f"R$ {df['gross_revenue'].sum():,.2f}")
col2.metric("Taxa Média Ocupação", f"{df['occupancy_rate'].mean()*100:.1f}%")
col3.metric("Nota Média", f"{df['avg_rating'].mean():.2f} ⭐")

st.map(df[['lat', 'lon']])  # Mapa de imóveis
st.bar_chart(df.groupby('city')['gross_revenue'].sum())
```

#### 5. Data Warehouse (Longo Prazo)

**Arquitetura Star Schema:**

```
        ┌────────────────┐
        │   dim_date     │
        │  - month       │
        │  - quarter     │
        │  - year        │
        └────────┬───────┘
                 │
        ┌────────┴───────┐
        │ fact_metrics   │◄──────┐
        │ - property_id  │       │
        │ - date_id      │       │
        │ - revenue      │       │
        │ - occupancy    │       │
        └────────────────┘       │
                                 │
        ┌────────────────┐       │
        │ dim_property   │───────┘
        │ - property_id  │
        │ - city         │
        │ - region       │
        └────────────────┘
```

**Ferramentas:**
- **BigQuery** (Google)
- **Redshift** (AWS)
- **Snowflake**

---

## 🔐 Governança de Dados

### Fonte Única da Verdade

**Localização:** `data/database.sqlite` (ou Supabase em produção)

**Regras:**
1. ✅ Apenas o script automatizado escreve no banco
2. ✅ Times consultam via relatórios ou SQL read-only
3. ✅ Histórico nunca é deletado (apenas soft-delete com flag)
4. ✅ Auditoria via `execution_logs`

### Padronização de KPIs

**Glossário Único:**

| KPI | Definição | Fórmula |
|-----|-----------|---------|
| **Faturamento Bruto** | Soma de todas as reservas do imóvel | `SUM(booking_value)` |
| **Receita Líquida** | Faturamento após taxas e custos | `bruto - taxas - custos` |
| **Margem %** | Percentual de lucro sobre faturamento | `(líquido / bruto) × 100` |
| **Taxa de Ocupação** | Percentual de dias ocupados | `(dias_ocupados / dias_mês) × 100` |
| **Nota Média** | Média aritmética das avaliações | `AVG(rating)` |

**Documentação:** `docs/SCHEMA.md`

### Controle de Acesso

**Níveis:**
- **Leitura:** Qualquer funcionário (via relatórios)
- **Consulta SQL:** Apenas analistas/TI (read-only connection)
- **Escrita:** Apenas script automatizado
- **Administração:** Apenas DBA/TI

**Implementação futura com Supabase:**
```sql
-- Role apenas leitura
CREATE ROLE analista_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analista_ro;

-- Role escrita (apenas para aplicação)
CREATE ROLE app_writer;
GRANT INSERT, UPDATE ON monthly_summary TO app_writer;
```

---

## 📚 FAQ

### Como consumir os dados?

**Opção 1: Relatórios CSV**
- Abrir no Excel / Google Sheets
- Recebidos por email automaticamente

**Opção 2: Consultas SQL**
```sql
sqlite3 data/database.sqlite

-- Exemplo: Top 10 imóveis por receita
SELECT property_id, city, net_revenue 
FROM monthly_summary 
WHERE month = '2025-10'
ORDER BY net_revenue DESC 
LIMIT 10;
```

**Opção 3: Dashboard (futuro)**
- Streamlit app com visualizações interativas
- Acesso via navegador

**Opção 4: Chatbot IA**
```python
from ai_insights import PropertyChatbot

bot = PropertyChatbot("data/database.sqlite")
resposta = bot.query("Quais imóveis têm margem negativa?")
```

### E se a API externa cair?

**Mecanismos de Resiliência:**

1. **Retry automático** (3 tentativas com backoff exponencial)
```python
@retry(tries=3, delay=2, backoff=2)
def fetch_api():
    ...
```

2. **Notificação imediata** por email/Slack para equipe de TI

3. **Execução manual** após correção:
```bash
python main.py --month 2025-10
```

4. **Cache de dados anteriores** (fallback para último mês válido)

### Como adicionar novos KPIs?

1. **Adicionar cálculo** em `data_transformer.py`:
```python
merged["novo_kpi"] = merged["campo1"] / merged["campo2"]
```

2. **Atualizar schema** em `data_loader.py`:
```python
CREATE TABLE monthly_summary (
    ...
    novo_kpi REAL,
    ...
);
```

3. **Incluir em relatório** em `report_generator.py`:
```python
financial_cols = [
    ...,
    "novo_kpi"
]
```

4. **Documentar** em `docs/SCHEMA.md`

### Posso rodar localmente para testes?

Sim!

```bash
# 1. Clone o repo
git clone <url>

# 2. Instale dependências
pip install -r src/requirements.txt

# 3. Execute
cd src
python main.py --month 2025-10

# 4. Verifique saídas
ls output/
sqlite3 data/database.sqlite "SELECT COUNT(*) FROM monthly_summary;"
```

### Como migrar para produção?

**Checklist:**

- [ ] Configurar servidor (EC2, Digital Ocean, etc.)
- [ ] Migrar SQLite → PostgreSQL (Supabase)
- [ ] Configurar variáveis de ambiente (.env)
- [ ] Ativar workflow n8n ou GitHub Actions
- [ ] Configurar SMTP para emails
- [ ] Integrar webhook Slack
- [ ] Testar execução manual
- [ ] Validar agendamento automático
- [ ] Treinar equipes para consumir relatórios
- [ ] Documentar processo de troubleshooting

---

## 🤝 Contribuindo

Este é um projeto técnico de avaliação, mas sugestões são bem-vindas:

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto foi desenvolvido como parte de um desafio técnico para Seazone Tech.

---

## 👤 Autor

**Desenvolvido como solução para o Desafio Técnico Seazone**

🚀 **Stack:** Python, SQLite, n8n, GitHub Actions, OpenAI API  
📅 **Data:** Novembro 2025  
🎯 **Objetivo:** Eliminar processos manuais e criar governança de dados escalável

---

## 🔗 Links Úteis

- [Documentação da API Mock](https://desafio-tecnico-seazone-tech.vercel.app/docs)
- [Schema do Banco de Dados](docs/SCHEMA.md)
- [Workflow n8n](workflows/n8n_workflow.json)
- [GitHub Actions Workflow](.github/workflows/monthly-closing.yml)

---

**🎉 Sistema 100% funcional e pronto para escala!**
