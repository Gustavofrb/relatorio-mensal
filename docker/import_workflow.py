#!/usr/bin/env python3
"""
Script para importar workflow automaticamente no N8N via API.
Aguarda N8N iniciar e então importa o workflow via REST API.
"""

import json
import time
import os
import sys
import requests

# Configurações
N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
WORKFLOW_FILE = "/workflows/n8n_workflow.json"
MAX_RETRIES = 30

def wait_for_n8n():
    """Aguarda N8N iniciar"""
    print(" Aguardando N8N iniciar...")
    
    for i in range(MAX_RETRIES):
        try:
            response = requests.get(f"{N8N_URL}/healthz", timeout=5)
            if response.status_code == 200:
                print(" N8N está pronto!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Tentativa {i+1}/{MAX_RETRIES}... aguardando...")
        time.sleep(5)
    
    print("Timeout aguardando N8N iniciar")
    return False

def workflow_exists():
    """Verifica se já existe algum workflow no N8N e retorna o ID"""
    if not N8N_API_KEY:
        print("N8N_API_KEY não configurada, pulando verificação")
        return None
    
    try:
        response = requests.get(
            f"{N8N_URL}/api/v1/workflows",
            headers={"X-N8N-API-KEY": N8N_API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            workflows = data.get("data", [])
            count = len(workflows)
            if count > 0:
                print(f"ℹ️  {count} workflow(s) já existe(m) no N8N")
                return workflows[0].get("id")
        return None
    except Exception as e:
        print(f" Erro ao verificar workflows existentes: {e}")
        return None

def update_workflow(workflow_id):
    """Atualiza um workflow existente"""
    if not N8N_API_KEY:
        print("❌ N8N_API_KEY não configurada!")
        return False
    
    print(f"🔄 Atualizando workflow existente (ID: {workflow_id})...")
    
    try:
        # Ler arquivo do workflow
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        print(f"   Nome: {workflow_data.get('name', 'N/A')}")
        print(f"   Nodes: {len(workflow_data.get('nodes', []))}")
        
        clean_workflow = {
            "name": workflow_data.get("name"),
            "nodes": workflow_data.get("nodes", []),
            "connections": workflow_data.get("connections", {}),
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData")
        }
        
        clean_workflow = {k: v for k, v in clean_workflow.items() if v is not None}
        
        response = requests.put(
            f"{N8N_URL}/api/v1/workflows/{workflow_id}",
            headers={
                "X-N8N-API-KEY": N8N_API_KEY,
                "Content-Type": "application/json"
            },
            json=clean_workflow,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"Workflow atualizado com sucesso!")
            print(f"   ID: {result.get('id', 'N/A')}")
            print(f"   Nome: {result.get('name', 'N/A')}")
            return True
        else:
            print(f"Erro ao atualizar workflow (HTTP {response.status_code})")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def import_workflow():
    """Importa o workflow do arquivo JSON via API"""
    if not N8N_API_KEY:
        print("N8N_API_KEY não configurada!")
        print("   Configure a variável de ambiente N8N_API_KEY")
        return False
    
    print(" Importando workflow do arquivo...")
    
    try:
        # Ler arquivo do workflow
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        print(f"   Nome: {workflow_data.get('name', 'N/A')}")
        print(f"   Nodes: {len(workflow_data.get('nodes', []))}")
        
        # Limpar campos que a API não aceita (somente campos esperados)
        clean_workflow = {
            "name": workflow_data.get("name"),
            "nodes": workflow_data.get("nodes", []),
            "connections": workflow_data.get("connections", {}),
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData")
        }
        
        # Remover campos None
        clean_workflow = {k: v for k, v in clean_workflow.items() if v is not None}
        
        # Importar via API com API Key
        response = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            headers={
                "X-N8N-API-KEY": N8N_API_KEY,
                "Content-Type": "application/json"
            },
            json=clean_workflow,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Workflow importado com sucesso!")
            print(f"   ID: {result.get('id', 'N/A')}")
            print(f"   Nome: {result.get('name', 'N/A')}")
            print()
            print(f"🌐 Acesse o N8N em: {N8N_URL}")
            print()
            print("⚠️  IMPORTANTE: Ative o workflow manualmente no N8N!")
            print("   1. Abra o N8N no navegador")
            print("   2. Clique no workflow 'Fechamento Mensal Seazone'")
            print("   3. Clique no toggle verde no canto superior direito")
            return True
        else:
            print(f"❌ Erro ao importar workflow (HTTP {response.status_code})")
            print(f"   Resposta: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {WORKFLOW_FILE}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("  N8N Workflow Auto-Import/Update")
    print("=" * 60)
    print()
    
    # Aguardar N8N iniciar
    if not wait_for_n8n():
        sys.exit(1)
    
    # Sempre verificar e atualizar/importar o workflow
    workflow_id = workflow_exists()
    
    if workflow_id:
        print("🔄 Atualizando workflow existente com versão mais recente...")
        if update_workflow(workflow_id):
            print()
            print(f"🌐 Acesse o N8N em: {N8N_URL}")
            print()
            print("✅ Workflow atualizado! Agora usa HTTP Request (funciona em qualquer ambiente)")
            print("   - Endpoint: http://app:8000/run")
            print("   - Não depende mais de caminhos absolutos")
            print()
            print("⚠️  Verifique se o workflow está ativo:")
            print("   1. Abra http://localhost:5678")
            print("   2. Clique no workflow 'Fechamento Mensal Seazone'")
            print("   3. Toggle deve estar verde (ativo)")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("📥 Importando workflow pela primeira vez...")
        if import_workflow():
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
