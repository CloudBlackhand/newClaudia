#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Modelo Qwen2.5-1.5B no Railway
"""

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Variáveis globais para o modelo
model = None
tokenizer = None

def load_model():
    """Carregar o modelo Qwen2.5-1.5B quantizado"""
    global model, tokenizer
    
    try:
        logger.info("🔄 Iniciando carregamento do modelo Qwen2.5-1.5B...")
        
        # Carregar tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            "unsloth/Qwen2.5-1.5B-unsloth-bnb-4bit",
            trust_remote_code=True
        )
        
        # Carregar modelo quantizado
        model = AutoModelForCausalLM.from_pretrained(
            "unsloth/Qwen2.5-1.5B-unsloth-bnb-4bit",
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        logger.info("✅ Modelo carregado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar modelo: {e}")
        return False

@app.route('/')
def index():
    """Página inicial"""
    return jsonify({
        'status': 'online',
        'model': 'Qwen2.5-1.5B-unsloth-bnb-4bit',
        'message': 'Modelo de IA funcionando no Railway!'
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'memory_usage': f"{torch.cuda.memory_allocated() / 1024**3:.2f}GB" if torch.cuda.is_available() else "CPU only"
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Gerar resposta usando o modelo"""
    try:
        if model is None or tokenizer is None:
            return jsonify({'error': 'Modelo não carregado'}), 500
        
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt é obrigatório'}), 400
        
        # Tokenizar entrada
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Gerar resposta
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decodificar resposta
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remover o prompt da resposta
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'response': response,
            'model': 'Qwen2.5-1.5B-unsloth-bnb-4bit'
        })
        
    except Exception as e:
        logger.error(f"Erro na geração: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test():
    """Teste simples do modelo"""
    try:
        if model is None or tokenizer is None:
            return jsonify({'error': 'Modelo não carregado'}), 500
        
        # Teste simples
        test_prompt = "Olá, como você está?"
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return jsonify({
            'success': True,
            'test_prompt': test_prompt,
            'response': response,
            'model_working': True
        })
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Carregar modelo na inicialização
    if load_model():
        logger.info("🚀 Iniciando servidor Flask...")
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
    else:
        logger.error("❌ Falha ao carregar modelo. Encerrando...")
        sys.exit(1)
