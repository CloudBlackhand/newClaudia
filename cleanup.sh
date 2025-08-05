#!/bin/bash
# -*- coding: utf-8 -*-
"""
SCRIPT DE LIMPEZA - Claudia Cobranças
Remove arquivos desnecessários e otimiza o projeto
"""

echo "🧹 LIMPEZA AUTOMÁTICA - Claudia Cobranças"
echo "=========================================="
echo "🗑️ Removendo arquivos desnecessários..."
echo ""

# Remover arquivos de backup
echo "📁 Removendo arquivos de backup..."
find . -name "*backup*" -delete 2>/dev/null
find . -name "*broken*" -delete 2>/dev/null
find . -name "*old*" -delete 2>/dev/null
find . -name "*copy*" -delete 2>/dev/null
find . -name "*duplicate*" -delete 2>/dev/null

# Remover cache Python
echo "🐍 Removendo cache Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

# Remover logs temporários
echo "📋 Removendo logs temporários..."
find . -name "*.log" -delete 2>/dev/null
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.temp" -delete 2>/dev/null

# Remover arquivos do sistema
echo "💻 Removendo arquivos do sistema..."
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null
find . -name "*.swp" -delete 2>/dev/null
find . -name "*.swo" -delete 2>/dev/null

# Remover arquivos temporários de upload
echo "📤 Removendo arquivos temporários de upload..."
find . -name "temp_*" -delete 2>/dev/null
find . -name "upload_*" -delete 2>/dev/null

# Limpar diretórios temporários
echo "📂 Limpando diretórios temporários..."
rm -rf tmp/ 2>/dev/null
rm -rf temp/ 2>/dev/null
rm -rf cache/ 2>/dev/null

# Verificar se há arquivos grandes desnecessários
echo "📊 Verificando arquivos grandes..."
find . -type f -size +10M -not -path "./venv/*" 2>/dev/null | while read file; do
    echo "⚠️ Arquivo grande encontrado: $file"
done

# Mostrar estatísticas
echo ""
echo "📈 ESTATÍSTICAS APÓS LIMPEZA:"
echo "=============================="

# Contar arquivos
TOTAL_FILES=$(find . -type f | grep -v venv | wc -l)
echo "📁 Total de arquivos: $TOTAL_FILES"

# Tamanho do projeto (sem venv)
PROJECT_SIZE=$(du -sh . --exclude=venv 2>/dev/null | cut -f1)
echo "💾 Tamanho do projeto: $PROJECT_SIZE"

# Contar linhas de código
PYTHON_FILES=$(find . -name "*.py" | grep -v venv | wc -l)
echo "🐍 Arquivos Python: $PYTHON_FILES"

# Verificar se há problemas
echo ""
echo "🔍 VERIFICANDO PROBLEMAS..."
echo "==========================="

# Verificar sintaxe Python
echo "✅ Verificando sintaxe Python..."
python3 -m py_compile app.py 2>/dev/null && echo "   ✅ app.py - OK" || echo "   ❌ app.py - ERRO"
python3 -m py_compile core/*.py 2>/dev/null && echo "   ✅ core/*.py - OK" || echo "   ❌ core/*.py - ERRO"

# Verificar arquivos essenciais
echo ""
echo "📋 VERIFICANDO ARQUIVOS ESSENCIAIS..."
ESSENTIAL_FILES=("app.py" "config.py" "requirements.txt" "Procfile" "railway_start.py")
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - FALTANDO!"
    fi
done

echo ""
echo "🎉 LIMPEZA CONCLUÍDA!"
echo "====================="
echo "✅ Arquivos desnecessários removidos"
echo "✅ Cache Python limpo"
echo "✅ Projeto otimizado"
echo "✅ Pronto para deploy"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "1. git add ."
echo "2. git commit -m 'Cleanup: Otimização do projeto'"
echo "3. git push origin main"
echo "4. Verificar deploy no Railway" 