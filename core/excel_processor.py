#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Planilhas Excel - FPD e VENDAS
Baseado no sistema original, otimizado para o SuperBot
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Processador otimizado para planilhas FPD e VENDAS"""
    
    def __init__(self):
        self.df_fpd = None
        self.df_vendas_sheets = {}
        self.matched_data = []
        self.protocolo_column = None
        
    def load_fpd(self, file_path: str) -> Dict[str, Any]:
        """Carregar planilha FPD - versão melhorada com suporte a múltiplas abas"""
        try:
            logger.info(f"📊 Carregando FPD: {file_path}")
            
            # Colunas críticas para converter como string
            colunas_para_string = {
                'protocolo': str,
                'documento': str,
                'num_cliente': str,
                'cpf': str,
                'cnpj': str
            }
            
            # Converter protocolo como string para evitar problemas
            converters = {'protocolo': str}
            
            # Verificar se o arquivo tem múltiplas abas
            excel_file = pd.ExcelFile(file_path)
            if len(excel_file.sheet_names) > 1:
                logger.info(f"📑 FPD com múltiplas abas: {len(excel_file.sheet_names)} abas encontradas")
                
                # Tentar encontrar a aba principal com dados FPD
                main_sheet = None
                for sheet_name in excel_file.sheet_names:
                    # Ignorar abas de controle/dashboard
                    if any(ignore in sheet_name.upper() for ignore in ['PAINEL', 'DASH', 'CONTROLE', 'LAYOUT']):
                        continue
                    
                    # Ler amostra da aba
                    try:
                        sample = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
                        # Verificar se parece uma aba FPD (tem colunas relacionadas a FPD)
                        if any('fpd' in str(col).lower() for col in sample.columns):
                            main_sheet = sheet_name
                            logger.info(f"✅ Aba principal FPD encontrada: {sheet_name}")
                            break
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao verificar aba {sheet_name}: {e}")
                
                # Se encontrou aba principal, usar ela
                if main_sheet:
                    self.df_fpd = pd.read_excel(
                        file_path,
                        sheet_name=main_sheet,
                        engine='openpyxl',
                        dtype=colunas_para_string,
                        converters=converters
                    )
                else:
                    # Se não encontrou, usar a primeira aba
                    logger.warning("⚠️ Nenhuma aba FPD identificada, usando a primeira aba")
                    self.df_fpd = pd.read_excel(
                        file_path,
                        engine='openpyxl',
                        dtype=colunas_para_string,
                        converters=converters
                    )
            else:
                # Arquivo com uma única aba
                self.df_fpd = pd.read_excel(
                    file_path,
                    engine='openpyxl',
                    dtype=colunas_para_string,
                    converters=converters
                )
            
            # Encontrar coluna protocolo
            self.protocolo_column = self._find_protocol_column(self.df_fpd)
            
            if not self.protocolo_column:
                return {
                    "success": False,
                    "error": "Coluna PROTOCOLO não encontrada na planilha FPD"
                }
            
            # Limpar protocolos
            self._clean_protocols()
            
            # Aplicar filtros básicos (FPD = 1, não pagos)
            filtered_fpd = self._apply_basic_filters()
            
            logger.info(f"✅ FPD carregada: {len(self.df_fpd)} total, {len(filtered_fpd)} filtrados")
            
            return {
                "success": True,
                "total_records": len(self.df_fpd),
                "filtered_records": len(filtered_fpd),
                "protocol_column": self.protocolo_column,
                "stats": {
                    "total": len(self.df_fpd),
                    "with_protocol": len(self.df_fpd[self.df_fpd[self.protocolo_column].notna()]),
                    "filtered": len(filtered_fpd)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar FPD: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Removida lógica de múltiplas planilhas, vendas, matching e cruzamento de dados. Agora só processa uma planilha de clientes.
    
    def get_cobranca_data(self) -> List[Dict[str, Any]]:
        """Obter dados preparados para cobrança"""
        return [record for record in self.matched_data if record.get('ready_for_cobranca', False)]
    
    def has_matched_data(self) -> bool:
        """Verificar se tem dados processados"""
        return len(self.matched_data) > 0
    
    def _find_protocol_column(self, df: pd.DataFrame) -> Optional[str]:
        """Encontrar coluna protocolo - detecção melhorada"""
        # Busca exata por nomes comuns de protocolo
        possible_names = ['protocolo', 'protocol', 'PROTOCOLO', 'PROTOCOL', 'Protocolo', 'Protocol']
        
        # Verificar correspondência exata primeiro
        for col in df.columns:
            if str(col) in possible_names:
                logger.info(f"   🔍 Coluna de protocolo encontrada (correspondência exata): {col}")
                return col
        
        # Verificar correspondência parcial
        for col in df.columns:
            if any(name.lower() in str(col).lower() for name in ['protocolo', 'protocol']):
                logger.info(f"   🔍 Coluna de protocolo encontrada (correspondência parcial): {col}")
                return col
        
        # Busca por conteúdo - verificar se alguma coluna contém dados que parecem protocolos
        # (números com mais de 8 dígitos em pelo menos 80% das linhas)
        sample_size = min(100, len(df))
        for col in df.columns:
            if df[col].dtype == 'object':  # Apenas colunas de texto
                sample = df[col].head(sample_size)
                valid_protocols = 0
                
                for val in sample:
                    if pd.notna(val) and str(val).strip():
                        # Verificar se é um número longo (possível protocolo)
                        digits = ''.join(filter(str.isdigit, str(val)))
                        if len(digits) >= 8:
                            valid_protocols += 1
                
                # Se mais de 80% dos valores parecem protocolos
                if valid_protocols / sample_size >= 0.8:
                    logger.info(f"   🔍 Possível coluna de protocolo detectada por conteúdo: {col}")
                    return col
        
        return None
    
    def _clean_protocols(self):
        """Limpar protocolos - remover NaN, vazios, etc."""
        if self.protocolo_column and self.df_fpd is not None:
            # Converter para string e limpar
            self.df_fpd[self.protocolo_column] = self.df_fpd[self.protocolo_column].astype(str)
            self.df_fpd[self.protocolo_column] = self.df_fpd[self.protocolo_column].replace('nan', '')
            self.df_fpd[self.protocolo_column] = self.df_fpd[self.protocolo_column].replace('None', '')
            
            # Remover linhas com protocolo vazio
            self.df_fpd = self.df_fpd[self.df_fpd[self.protocolo_column] != '']
    
    def _apply_basic_filters(self) -> pd.DataFrame:
        """Aplicar filtros EXATOS como sistema original - FPD=1 E não pagou E fatura zerada"""
        if self.df_fpd is None:
            return pd.DataFrame()
        
        logger.info("🎯 APLICANDO FILTROS EXATOS DOS FPDs")
        logger.info("=" * 50)
        
        df_filtered = self.df_fpd.copy()
        inicial_count = len(df_filtered)
        
        # ETAPA 1: Filtro FPD = 1 (EXATAMENTE 1, não apenas > 0)
        fpd_col = self._find_column(df_filtered, ['fpd', 'FPD'])
        if fpd_col:
            logger.info(f"🔢 ETAPA 1: Filtro FPD = 1 (coluna {fpd_col})")
            
            # Garantir conversão robusta para numérico
            if df_filtered[fpd_col].dtype == 'object':
                df_filtered[fpd_col] = df_filtered[fpd_col].replace('', '0')
                df_filtered[fpd_col] = df_filtered[fpd_col].replace('nan', '0')
                df_filtered[fpd_col] = df_filtered[fpd_col].replace('None', '0')
            
            df_filtered[fpd_col] = pd.to_numeric(df_filtered[fpd_col], errors='coerce').fillna(0)
            
            # Filtro EXATAMENTE igual a 1
            antes_fpd = len(df_filtered)
            df_filtered = df_filtered[df_filtered[fpd_col] == 1]
            depois_fpd = len(df_filtered)
            
            logger.info(f"   ✅ FPD = 1: {antes_fpd:,} → {depois_fpd:,} registros")
        else:
            logger.warning("   ❌ Coluna FPD não encontrada!")
        
        # ETAPA 2: Filtro de status NÃO PAGOU (incluindo fatura zerada)
        status_col = self._find_column(df_filtered, ['faixa_pgto_fpd', 'faixa_pagamento', 'status'])
        if status_col:
            logger.info(f"💰 ETAPA 2: Filtro não pagou (coluna {status_col})")
            
            antes_status = len(df_filtered)
            
            # Status EXATOS como no sistema original
            status_nao_pagos = [
                '00) NAO PAGOU', 
                '00) NAO PAGOU (FATURA ZERADA)'
            ]
            
            df_filtered = df_filtered[df_filtered[status_col].isin(status_nao_pagos)]
            depois_status = len(df_filtered)
            
            logger.info(f"   ✅ Não pagou: {antes_status:,} → {depois_status:,} registros")
            
            # Mostrar distribuição por status
            if not df_filtered.empty:
                status_counts = df_filtered[status_col].value_counts()
                logger.info("   📊 Distribuição por status:")
                for status, count in status_counts.items():
                    logger.info(f"      • {status}: {count:,}")
        else:
            logger.warning("   ❌ Coluna de status não encontrada!")
        
        # ETAPA 3: Filtro protocolo válido (não vazio)
        if self.protocolo_column:
            logger.info(f"🔑 ETAPA 3: Filtro protocolo válido (coluna {self.protocolo_column})")
            
            antes_protocolo = len(df_filtered)
            
            # Remover protocolos nulos, vazios ou 'nan'
            df_filtered = df_filtered[df_filtered[self.protocolo_column].notna()]
            df_filtered = df_filtered[df_filtered[self.protocolo_column] != '']
            df_filtered = df_filtered[df_filtered[self.protocolo_column] != 'nan']
            df_filtered = df_filtered[df_filtered[self.protocolo_column] != 'None']
            
            depois_protocolo = len(df_filtered)
            logger.info(f"   ✅ Protocolo válido: {antes_protocolo:,} → {depois_protocolo:,} registros")
        
        # RESUMO FINAL
        final_count = len(df_filtered)
        logger.info("=" * 50)
        logger.info(f"📊 RESUMO DOS FILTROS:")
        logger.info(f"   🔢 Inicial: {inicial_count:,} registros")
        logger.info(f"   ✅ Final: {final_count:,} registros")
        logger.info(f"   📉 Redução: {((inicial_count - final_count) / inicial_count * 100):.1f}%")
        
        return df_filtered
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Encontrar coluna por nomes possíveis - versão melhorada"""
        # Primeiro tentar correspondência exata (case insensitive)
        for col in df.columns:
            if any(name.lower() == str(col).lower() for name in possible_names):
                logger.debug(f"   🔍 Coluna encontrada (correspondência exata): {col}")
                return col
        
        # Depois tentar correspondência parcial
        for col in df.columns:
            if any(name.lower() in str(col).lower() for name in possible_names):
                logger.debug(f"   🔍 Coluna encontrada (correspondência parcial): {col}")
                return col
        
        # Se não encontrar, tentar inferir pelo conteúdo
        # Implementação específica para cada tipo de coluna pode ser adicionada aqui
        
        return None
    
    def _extract_client_name(self, row: pd.Series) -> str:
        """Extrair nome do cliente"""
        name_columns = ['nome', 'first_name', 'cliente', 'nome_cliente']
        for col in name_columns:
            for actual_col in row.index:
                if col.lower() in str(actual_col).lower():
                    value = row[actual_col]
                    if pd.notna(value) and str(value).strip():
                        return str(value).strip()
        return "Cliente"
    
    def _extract_phone(self, row: pd.Series) -> Optional[str]:
        """Extrair telefone"""
        phone_columns = ['telefone', 'celular', 'whatsapp', 'fone', 'phone']
        for col in phone_columns:
            for actual_col in row.index:
                if col.lower() in str(actual_col).lower():
                    value = row[actual_col]
                    if pd.notna(value) and str(value).strip():
                        # Limpar telefone
                        phone = ''.join(filter(str.isdigit, str(value)))
                        if len(phone) >= 10:  # Mínimo para ser um telefone válido
                            return phone
        return None
    
    def _extract_document(self, row: pd.Series) -> Optional[str]:
        """Extrair CPF/CNPJ"""
        doc_columns = ['cpf', 'cnpj', 'documento', 'doc']
        for col in doc_columns:
            for actual_col in row.index:
                if col.lower() in str(actual_col).lower():
                    value = row[actual_col]
                    if pd.notna(value) and str(value).strip():
                        # Limpar documento
                        doc = ''.join(filter(str.isdigit, str(value)))
                        if len(doc) >= 11:  # CPF ou CNPJ
                            return doc
        return None 