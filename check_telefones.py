#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def check_telefones():
    print("🔍 Verificando telefones no JSON...")
    
    with open('resultado_cruzamento_20250903_114254.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_vendas = 0
    telefones_validos = 0
    telefones_error = 0
    telefones_vazios = 0
    
    for obj in data:
        for venda in obj.get('dados_vendas', []):
            total_vendas += 1
            telefone1 = venda.get('TELEFONE1', '')
            
            if telefone1 == '#ERROR!':
                telefones_error += 1
            elif not telefone1 or telefone1.strip() == '':
                telefones_vazios += 1
            else:
                telefones_validos += 1
    
    print(f"📊 ANÁLISE DE TELEFONES:")
    print(f"   - Total de vendas: {total_vendas}")
    print(f"   - Telefones válidos: {telefones_validos}")
    print(f"   - Telefones #ERROR!: {telefones_error}")
    print(f"   - Telefones vazios: {telefones_vazios}")
    print(f"   - Taxa de rejeição: {((telefones_error + telefones_vazios) / total_vendas * 100):.1f}%")

if __name__ == "__main__":
    check_telefones()
