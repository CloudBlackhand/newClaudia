#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar arquivo JSON e preparar para upload no banco
"""

import json
import math

def clean_json_value(value):
    """Limpa valores inválidos do JSON"""
    if isinstance(value, float) and math.isnan(value):
        return None
    elif value == "NaT":
        return None
    elif value == "":
        return None
    return value

def clean_json_object(obj):
    """Limpa objeto JSON recursivamente"""
    if isinstance(obj, dict):
        return {k: clean_json_object(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_object(item) for item in obj]
    else:
        return clean_json_value(obj)

def clean_json_file(input_file, output_file):
    """Limpa arquivo JSON completo"""
    print(f"🧹 LIMPANDO ARQUIVO JSON: {input_file}")
    
    try:
        # Ler arquivo original
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Arquivo lido: {len(data)} registros")
        
        # Limpar dados
        cleaned_data = clean_json_object(data)
        
        # Salvar arquivo limpo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Arquivo limpo salvo: {output_file}")
        
        # Estatísticas
        total_clients = len(cleaned_data)
        clients_with_debt = sum(1 for item in cleaned_data 
                              if item.get('dados_fpd', {}).get('cobrado_fpd', 0) > 0)
        
        print(f"📊 ESTATÍSTICAS:")
        print(f"   - Total de clientes: {total_clients}")
        print(f"   - Clientes com dívida: {clients_with_debt}")
        
        return cleaned_data
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        return None

if __name__ == "__main__":
    input_file = "resultado_cruzamento_20250901_081851.json"
    output_file = "resultado_cruzamento_limpo.json"
    
    cleaned_data = clean_json_file(input_file, output_file)
    
    if cleaned_data:
        print("\n🎉 ARQUIVO LIMPO CRIADO COM SUCESSO!")
        print(f"📁 Arquivo limpo: {output_file}")
        print("🚀 Agora pode ser usado para upload no banco!")

