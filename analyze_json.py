#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def analyze_json():
    print("🔍 Analisando JSON...")
    
    with open('resultado_cruzamento_20250903_114254.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Total de objetos no JSON: {len(data)}")
    
    total_vendas = 0
    objetos_com_vendas = 0
    objetos_sem_vendas = 0
    
    for i, obj in enumerate(data):
        vendas_count = len(obj.get('dados_vendas', []))
        total_vendas += vendas_count
        
        if vendas_count > 0:
            objetos_com_vendas += 1
        else:
            objetos_sem_vendas += 1
            
        if i < 10:  # Mostrar primeiros 10
            print(f"📊 Objeto {i+1}: {vendas_count} vendas")
    
    print(f"\n🎯 RESUMO:")
    print(f"   - Total de objetos: {len(data)}")
    print(f"   - Objetos com vendas: {objetos_com_vendas}")
    print(f"   - Objetos sem vendas: {objetos_sem_vendas}")
    print(f"   - TOTAL DE VENDAS: {total_vendas}")
    
    # Verificar se há objetos com múltiplas vendas
    print(f"\n🔍 Verificando objetos com múltiplas vendas...")
    for i, obj in enumerate(data):
        vendas_count = len(obj.get('dados_vendas', []))
        if vendas_count > 1:
            print(f"   - Objeto {i+1}: {vendas_count} vendas")
            if i < 3:  # Mostrar detalhes dos primeiros 3
                for j, venda in enumerate(obj['dados_vendas']):
                    print(f"     Venda {j+1}: {venda.get('NOME', 'N/A')}")

if __name__ == "__main__":
    analyze_json()
