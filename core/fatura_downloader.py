#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Download de Faturas SAC Desktop
Adaptado do sistema antigo para usar Playwright
Realiza download automático de faturas do https://sac.desktop.com.br/Cliente_Documento.jsp
"""

import os
import time
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from playwright.async_api import Page, Browser
import tempfile
from .captcha_solver import CaptchaSolver
from .logger import logger, performance_metric, security_event
from .storage_manager import storage_manager

class FaturaDownloader:
    """Sistema de download automático de faturas do SAC Desktop"""
    
    def __init__(self, page: Page):
        """Inicializar downloader com página Playwright
        
        Args:
            page: Instância da página Playwright
        """
        self.page = page
        self.captcha_solver = CaptchaSolver(page)
        self.faturas_dir = "faturas"
        self.sac_url = "https://sac.desktop.com.br/Cliente_Documento.jsp"
        
        # Criar diretório de faturas
        self._create_faturas_directory()
        
        # Configurar download path para a página
        self._setup_download_path()
        
        logger.info("FaturaDownloader inicializado para SAC Desktop")
    
    def _create_faturas_directory(self):
        """Criar diretório para armazenar faturas"""
        if not os.path.exists(self.faturas_dir):
            os.makedirs(self.faturas_dir)
            logger.info(f"📁 Diretório de faturas criado: {self.faturas_dir}")
    
    async def _setup_download_path(self):
        """Configurar caminho de download para a página"""
        try:
            # Configurar downloads para ir para pasta faturas
            await self.page.context.set_default_download_path(os.path.abspath(self.faturas_dir))
            logger.info(f"📥 Caminho de download configurado: {os.path.abspath(self.faturas_dir)}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar caminho de download: {e}")
    
    async def baixar_fatura(self, documento: str, protocolo: Optional[str] = None, max_tentativas: int = 3) -> Optional[str]:
        """Baixar fatura para um documento específico
        
        Args:
            documento: CPF/CNPJ do cliente (pode ter máscara)
            protocolo: Protocolo do cliente para identificação
            max_tentativas: Número máximo de tentativas
            
        Returns:
            str: Caminho do arquivo baixado ou None se falhou
        """
        start_time = time.time()
        
        # Limpar documento (remover caracteres especiais)
        documento_limpo = self._limpar_documento(documento)
        
        logger.info(f"🚀 Iniciando download de fatura - Documento: {documento_limpo}, Protocolo: {protocolo}")
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                logger.info(f"🔄 Tentativa {tentativa}/{max_tentativas}")
                
                # Acessar página do SAC Desktop
                await self.page.goto(self.sac_url)
                logger.info(f"🌐 Acessando: {self.sac_url}")
                
                # Aguardar página carregar completamente
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # Resolver reCAPTCHA se presente
                if await self._has_recaptcha():
                    logger.info("🔐 reCAPTCHA detectado, resolvendo...")
                    
                    captcha_solved = await self.captcha_solver.solve_captcha()
                    
                    if not captcha_solved:
                        logger.error(f"❌ Falha ao resolver reCAPTCHA na tentativa {tentativa}")
                        if tentativa < max_tentativas:
                            await asyncio.sleep(5)
                            continue
                        else:
                            performance_metric("fatura_download_failed", time.time() - start_time, error="captcha_failed")
                            return None
                    
                    logger.info("✅ reCAPTCHA resolvido com sucesso!")
                    await asyncio.sleep(2)
                
                # Preencher campo documento
                if await self._preencher_documento(documento_limpo):
                    logger.info(f"📝 Documento preenchido: {documento_limpo}")
                    
                    # Submeter formulário
                    if await self._submeter_formulario():
                        logger.info("✅ Formulário submetido")
                        
                        # Aguardar resultado e tentar baixar
                        arquivo_baixado = await self._processar_resultado(documento_limpo, protocolo)
                        
                        if arquivo_baixado:
                            duration = time.time() - start_time
                            performance_metric("fatura_download_success", duration, documento=documento_limpo)
                            logger.info(f"🎉 Fatura baixada com sucesso: {arquivo_baixado}")
                            return arquivo_baixado
                        else:
                            logger.warning(f"⚠️ Fatura não encontrada para documento: {documento_limpo}")
                    else:
                        logger.error("❌ Erro ao submeter formulário")
                else:
                    logger.error("❌ Erro ao preencher campo documento")
                
                # Se chegou aqui, a tentativa falhou
                if tentativa < max_tentativas:
                    logger.info(f"🔄 Tentativa {tentativa} falhou, aguardando antes da próxima...")
                    await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Erro na tentativa {tentativa}: {e}")
                if tentativa < max_tentativas:
                    await asyncio.sleep(5)
                continue
        
        # Todas as tentativas falharam
        duration = time.time() - start_time
        performance_metric("fatura_download_failed", duration, documento=documento_limpo, tentativas=max_tentativas)
        logger.error(f"❌ Falha após {max_tentativas} tentativas para documento: {documento_limpo}")
        return None
    
    def _limpar_documento(self, documento: str) -> str:
        """Limpar documento removendo caracteres especiais
        
        Args:
            documento: Documento com possíveis máscaras
            
        Returns:
            str: Documento limpo apenas com números
        """
        if not documento:
            return ""
        
        # Remover pontos, traços, barras e espaços
        documento_limpo = ''.join(filter(str.isdigit, documento))
        return documento_limpo
    
    async def _has_recaptcha(self) -> bool:
        """Verificar se há reCAPTCHA na página
        
        Returns:
            bool: True se reCAPTCHA está presente
        """
        try:
            # Procurar por iframe do reCAPTCHA
            await self.page.wait_for_selector("iframe[title='reCAPTCHA']", timeout=3000)
            return True
        except:
            return False
    
    async def _preencher_documento(self, documento: str) -> bool:
        """Preencher campo de documento na página
        
        Args:
            documento: Documento limpo para preencher
            
        Returns:
            bool: True se preenchido com sucesso
        """
        try:
            # Estratégias múltiplas para encontrar o campo documento
            selectors = [
                "input[name='documento']",
                "input[id='documento']", 
                "input[type='text']",
                "input[placeholder*='CPF']",
                "input[placeholder*='CNPJ']",
                "input[placeholder*='documento']"
            ]
            
            campo_encontrado = None
            
            for selector in selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=2000)
                    campo_encontrado = selector
                    break
                except:
                    continue
            
            if not campo_encontrado:
                # Buscar genericamente o primeiro campo de texto
                campos_texto = await self.page.query_selector_all("input[type='text']")
                if campos_texto:
                    campo_encontrado = "input[type='text']"
                else:
                    logger.error("❌ Campo documento não encontrado")
                    return False
            
            # Preencher campo
            await self.page.fill(campo_encontrado, documento)
            
            # Verificar se foi preenchido corretamente
            valor_preenchido = await self.page.input_value(campo_encontrado)
            
            if valor_preenchido == documento:
                logger.info(f"✅ Campo preenchido corretamente: {documento}")
                return True
            else:
                logger.error(f"❌ Erro no preenchimento. Esperado: {documento}, Obtido: {valor_preenchido}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao preencher documento: {e}")
            return False
    
    async def _submeter_formulario(self) -> bool:
        """Submeter formulário com múltiplas estratégias
        
        Returns:
            bool: True se submetido com sucesso
        """
        try:
            # Estratégias múltiplas para submeter o formulário
            strategies = [
                # Estratégia 1: Botão "Avançar" específico (input type='image')
                ("input[type='image'][alt*='Avançar']", "Botão Avançar (image)"),
                ("input[type='Image'][alt*='Avançar']", "Botão Avançar (Image maiúsculo)"),
                
                # Estratégia 2: Por src da imagem
                ("input[src*='admavanc.gif']", "Botão por src admavanc.gif"),
                ("input[src*='avanc']", "Botão por src avanc"),
                
                # Estratégia 3: Botões submit padrão
                ("input[type='submit']", "Input submit"),
                ("button[type='submit']", "Button submit"),
                
                # Estratégia 4: Por texto/value
                ("input[value*='Consultar']", "Botão Consultar"),
                ("input[value*='Buscar']", "Botão Buscar"),
                ("input[value*='Avançar']", "Botão Avançar por value"),
                ("button:has-text('Consultar')", "Button com texto Consultar"),
                ("button:has-text('Buscar')", "Button com texto Buscar"),
                ("button:has-text('Avançar')", "Button com texto Avançar"),
                
                # Estratégia 5: Qualquer input type='image'
                ("input[type='image']", "Qualquer input image"),
                ("input[type='Image']", "Qualquer input Image"),
                
                # Estratégia 6: Primeiro botão encontrado
                ("button", "Primeiro botão genérico")
            ]
            
            for selector, descricao in strategies:
                try:
                    await self.page.wait_for_selector(selector, timeout=2000)
                    await self.page.click(selector)
                    logger.info(f"✅ Formulário submetido usando: {descricao}")
                    return True
                except:
                    continue
            
            # Se nenhuma estratégia funcionou, tentar Enter no campo documento
            try:
                await self.page.press("input[type='text']", "Enter")
                logger.info("✅ Formulário submetido com Enter")
                return True
            except:
                pass
            
            logger.error("❌ Nenhuma estratégia de submissão funcionou")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao submeter formulário: {e}")
            return False
    
    async def _processar_resultado(self, documento: str, protocolo: Optional[str] = None) -> Optional[str]:
        """Processar página de resultado e baixar fatura
        
        Args:
            documento: Documento do cliente
            protocolo: Protocolo para nomenclatura
            
        Returns:
            str: Caminho do arquivo baixado ou None
        """
        try:
            # Aguardar página de resultado carregar
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # Verificar se há mensagens de erro
            page_content = await self.page.content()
            page_text = page_content.lower()
            
            # Mensagens de erro comuns
            error_messages = [
                "não encontrado", "não localizado", "não existe",
                "documento inválido", "cpf inválido", "cnpj inválido", 
                "sem faturas", "nenhuma fatura", "não há faturas",
                "erro", "falha", "problema"
            ]
            
            for error_msg in error_messages:
                if error_msg in page_text:
                    logger.warning(f"⚠️ Mensagem de erro detectada: '{error_msg}'")
                    return None
            
            # Procurar links/botões de download
            download_selectors = [
                # Links com texto específico
                "a:has-text('boleto')",
                "a:has-text('fatura')", 
                "a:has-text('2ª via')",
                "a:has-text('segunda via')",
                "a:has-text('download')",
                "a:has-text('baixar')",
                "a:has-text('pdf')",
                
                # Links por atributos href
                "a[href*='pdf']",
                "a[href*='boleto']", 
                "a[href*='fatura']",
                "a[href*='download']",
                
                # Botões
                "button:has-text('Download')",
                "button:has-text('Baixar')",
                "button:has-text('PDF')",
                
                # Inputs type image/submit
                "input[type='image'][alt*='Download']",
                "input[type='image'][alt*='PDF']", 
                "input[type='image'][alt*='Boleto']",
                
                # Imagens clicáveis
                "img[alt*='Download']",
                "img[alt*='PDF']",
                "img[alt*='Boleto']"
            ]
            
            download_element = None
            
            for selector in download_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        download_element = elements[0]  # Pegar primeiro encontrado
                        logger.info(f"📄 Link de download encontrado: {selector}")
                        break
                except:
                    continue
            
            if download_element:
                # Aguardar download começar
                async with self.page.expect_download() as download_info:
                    await download_element.click()
                    
                download = await download_info.value
                
                # Gerar nome único para o arquivo
                if protocolo and protocolo != 'N/A':
                    filename = f"fatura_protocolo_{protocolo}_{int(time.time())}.pdf"
                else:
                    filename = f"fatura_{documento}_{int(time.time())}.pdf"
                
                # 💾 Salvar arquivo usando StorageManager
                temp_path = os.path.join(tempfile.gettempdir(), filename)
                await download.save_as(temp_path)
                
                # Verificar se arquivo foi baixado
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    # Ler arquivo e usar StorageManager
                    with open(temp_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Salvar usando StorageManager (com auto-limpeza)
                    save_result = await storage_manager.save_invoice(documento, filename, file_data)
                    
                    # Remover arquivo temporário
                    os.unlink(temp_path)
                    
                    if save_result['success']:
                        logger.info(f"✅ Fatura salva via StorageManager: {filename} ({save_result['file_size_mb']:.2f}MB)")
                        logger.info(f"📊 Armazenamento total: {save_result['total_storage_mb']:.2f}MB")
                        security_event("fatura_downloaded", "low", documento=documento, arquivo=filename)
                        return save_result['file_path']
                    else:
                        logger.error(f"❌ Erro ao salvar via StorageManager: {save_result.get('error')}")
                        return None
                else:
                    logger.error("❌ Arquivo baixado está vazio ou não existe")
                    return None
            else:
                logger.warning("❌ Nenhum link de download encontrado")
                
                # Debug: tirar screenshot da página
                try:
                    screenshot_path = os.path.join(self.faturas_dir, f"debug_no_download_{documento}_{int(time.time())}.png")
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"📸 Screenshot salvo para debug: {screenshot_path}")
                except:
                    pass
                    
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado: {e}")
            return None
    
    async def baixar_multiplas_faturas(self, documentos_protocolos: List[tuple], intervalo: float = 5.0) -> Dict[str, Any]:
        """Baixar múltiplas faturas sequencialmente
        
        Args:
            documentos_protocolos: Lista de tuplas (documento, protocolo)
            intervalo: Intervalo entre downloads em segundos
            
        Returns:
            dict: Resultados dos downloads
        """
        start_time = time.time()
        resultados = {}
        sucessos = 0
        erros = 0
        
        logger.info(f"📋 Iniciando download de {len(documentos_protocolos)} faturas...")
        
        for i, (documento, protocolo) in enumerate(documentos_protocolos, 1):
            logger.info(f"\n📄 Processando {i}/{len(documentos_protocolos)}: {documento} (Protocolo: {protocolo})")
            
            arquivo_baixado = await self.baixar_fatura(documento, protocolo)
            
            if arquivo_baixado:
                resultados[documento] = {
                    'status': 'sucesso',
                    'arquivo': arquivo_baixado,
                    'protocolo': protocolo,
                    'timestamp': datetime.now().isoformat()
                }
                sucessos += 1
                logger.info(f"✅ Sucesso {i}/{len(documentos_protocolos)}: {documento}")
            else:
                resultados[documento] = {
                    'status': 'erro',
                    'arquivo': None,
                    'protocolo': protocolo,
                    'timestamp': datetime.now().isoformat()
                }
                erros += 1
                logger.error(f"❌ Erro {i}/{len(documentos_protocolos)}: {documento}")
            
            # Aguardar intervalo entre downloads (exceto no último)
            if i < len(documentos_protocolos):
                logger.info(f"⏳ Aguardando {intervalo}s antes do próximo download...")
                await asyncio.sleep(intervalo)
        
        # Resumo final
        duration = time.time() - start_time
        logger.info(f"\n📊 Resumo final do download em lote:")
        logger.info(f"   ✅ Sucessos: {sucessos}")
        logger.info(f"   ❌ Erros: {erros}")
        logger.info(f"   ⏱️ Tempo total: {duration:.1f}s")
        logger.info(f"   📁 Arquivos salvos em: {os.path.abspath(self.faturas_dir)}")
        
        performance_metric("fatura_download_batch", duration, total=len(documentos_protocolos), sucessos=sucessos, erros=erros)
        
        return {
            'resultados': resultados,
            'resumo': {
                'total': len(documentos_protocolos),
                'sucessos': sucessos,
                'erros': erros,
                'taxa_sucesso': (sucessos / len(documentos_protocolos)) * 100 if documentos_protocolos else 0,
                'tempo_total': duration
            }
        }
    
    def listar_faturas_baixadas(self) -> List[Dict[str, Any]]:
        """Listar todas as faturas baixadas
        
        Returns:
            list: Lista de dicionários com informações dos arquivos
        """
        if not os.path.exists(self.faturas_dir):
            return []
        
        arquivos = []
        for arquivo in os.listdir(self.faturas_dir):
            if arquivo.endswith('.pdf'):
                caminho_completo = os.path.join(self.faturas_dir, arquivo)
                stat = os.stat(caminho_completo)
                arquivos.append({
                    'nome': arquivo,
                    'caminho': caminho_completo,
                    'tamanho_bytes': stat.st_size,
                    'tamanho_mb': round(stat.st_size / 1024 / 1024, 2),
                    'data_modificacao': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'data_criacao': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        # Ordenar por data de modificação (mais recente primeiro)
        return sorted(arquivos, key=lambda x: x['data_modificacao'], reverse=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status atual do downloader
        
        Returns:
            dict: Status e estatísticas
        """
        faturas = self.listar_faturas_baixadas()
        
        return {
            'sac_url': self.sac_url,
            'faturas_dir': os.path.abspath(self.faturas_dir),
            'captcha_solver_disponivel': True,
            'total_faturas_baixadas': len(faturas),
            'tamanho_total_mb': sum(f['tamanho_mb'] for f in faturas),
            'ultima_fatura': faturas[0] if faturas else None
        }

# Função de conveniência
async def baixar_fatura_rapido(page: Page, documento: str, protocolo: Optional[str] = None) -> Optional[str]:
    """Função de conveniência para baixar uma fatura rapidamente
    
    Args:
        page: Página Playwright
        documento: CPF/CNPJ do cliente
        protocolo: Protocolo do cliente
        
    Returns:
        str: Caminho do arquivo baixado ou None
    """
    downloader = FaturaDownloader(page)
    return await downloader.baixar_fatura(documento, protocolo)
# -*- coding: utf-8 -*-
"""
Sistema de Download de Faturas SAC Desktop
Adaptado do sistema antigo para usar Playwright
Realiza download automático de faturas do https://sac.desktop.com.br/Cliente_Documento.jsp
"""

import os
import time
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from playwright.async_api import Page, Browser
import tempfile
from .captcha_solver import CaptchaSolver
from .logger import logger, performance_metric, security_event
from .storage_manager import storage_manager

class FaturaDownloader:
    """Sistema de download automático de faturas do SAC Desktop"""
    
    def __init__(self, page: Page):
        """Inicializar downloader com página Playwright
        
        Args:
            page: Instância da página Playwright
        """
        self.page = page
        self.captcha_solver = CaptchaSolver(page)
        self.faturas_dir = "faturas"
        self.sac_url = "https://sac.desktop.com.br/Cliente_Documento.jsp"
        
        # Criar diretório de faturas
        self._create_faturas_directory()
        
        # Configurar download path para a página
        self._setup_download_path()
        
        logger.info("FaturaDownloader inicializado para SAC Desktop")
    
    def _create_faturas_directory(self):
        """Criar diretório para armazenar faturas"""
        if not os.path.exists(self.faturas_dir):
            os.makedirs(self.faturas_dir)
            logger.info(f"📁 Diretório de faturas criado: {self.faturas_dir}")
    
    async def _setup_download_path(self):
        """Configurar caminho de download para a página"""
        try:
            # Configurar downloads para ir para pasta faturas
            await self.page.context.set_default_download_path(os.path.abspath(self.faturas_dir))
            logger.info(f"📥 Caminho de download configurado: {os.path.abspath(self.faturas_dir)}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar caminho de download: {e}")
    
    async def baixar_fatura(self, documento: str, protocolo: Optional[str] = None, max_tentativas: int = 3) -> Optional[str]:
        """Baixar fatura para um documento específico
        
        Args:
            documento: CPF/CNPJ do cliente (pode ter máscara)
            protocolo: Protocolo do cliente para identificação
            max_tentativas: Número máximo de tentativas
            
        Returns:
            str: Caminho do arquivo baixado ou None se falhou
        """
        start_time = time.time()
        
        # Limpar documento (remover caracteres especiais)
        documento_limpo = self._limpar_documento(documento)
        
        logger.info(f"🚀 Iniciando download de fatura - Documento: {documento_limpo}, Protocolo: {protocolo}")
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                logger.info(f"🔄 Tentativa {tentativa}/{max_tentativas}")
                
                # Acessar página do SAC Desktop
                await self.page.goto(self.sac_url)
                logger.info(f"🌐 Acessando: {self.sac_url}")
                
                # Aguardar página carregar completamente
                await self.page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # Resolver reCAPTCHA se presente
                if await self._has_recaptcha():
                    logger.info("🔐 reCAPTCHA detectado, resolvendo...")
                    
                    captcha_solved = await self.captcha_solver.solve_captcha()
                    
                    if not captcha_solved:
                        logger.error(f"❌ Falha ao resolver reCAPTCHA na tentativa {tentativa}")
                        if tentativa < max_tentativas:
                            await asyncio.sleep(5)
                            continue
                        else:
                            performance_metric("fatura_download_failed", time.time() - start_time, error="captcha_failed")
                            return None
                    
                    logger.info("✅ reCAPTCHA resolvido com sucesso!")
                    await asyncio.sleep(2)
                
                # Preencher campo documento
                if await self._preencher_documento(documento_limpo):
                    logger.info(f"📝 Documento preenchido: {documento_limpo}")
                    
                    # Submeter formulário
                    if await self._submeter_formulario():
                        logger.info("✅ Formulário submetido")
                        
                        # Aguardar resultado e tentar baixar
                        arquivo_baixado = await self._processar_resultado(documento_limpo, protocolo)
                        
                        if arquivo_baixado:
                            duration = time.time() - start_time
                            performance_metric("fatura_download_success", duration, documento=documento_limpo)
                            logger.info(f"🎉 Fatura baixada com sucesso: {arquivo_baixado}")
                            return arquivo_baixado
                        else:
                            logger.warning(f"⚠️ Fatura não encontrada para documento: {documento_limpo}")
                    else:
                        logger.error("❌ Erro ao submeter formulário")
                else:
                    logger.error("❌ Erro ao preencher campo documento")
                
                # Se chegou aqui, a tentativa falhou
                if tentativa < max_tentativas:
                    logger.info(f"🔄 Tentativa {tentativa} falhou, aguardando antes da próxima...")
                    await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Erro na tentativa {tentativa}: {e}")
                if tentativa < max_tentativas:
                    await asyncio.sleep(5)
                continue
        
        # Todas as tentativas falharam
        duration = time.time() - start_time
        performance_metric("fatura_download_failed", duration, documento=documento_limpo, tentativas=max_tentativas)
        logger.error(f"❌ Falha após {max_tentativas} tentativas para documento: {documento_limpo}")
        return None
    
    def _limpar_documento(self, documento: str) -> str:
        """Limpar documento removendo caracteres especiais
        
        Args:
            documento: Documento com possíveis máscaras
            
        Returns:
            str: Documento limpo apenas com números
        """
        if not documento:
            return ""
        
        # Remover pontos, traços, barras e espaços
        documento_limpo = ''.join(filter(str.isdigit, documento))
        return documento_limpo
    
    async def _has_recaptcha(self) -> bool:
        """Verificar se há reCAPTCHA na página
        
        Returns:
            bool: True se reCAPTCHA está presente
        """
        try:
            # Procurar por iframe do reCAPTCHA
            await self.page.wait_for_selector("iframe[title='reCAPTCHA']", timeout=3000)
            return True
        except:
            return False
    
    async def _preencher_documento(self, documento: str) -> bool:
        """Preencher campo de documento na página
        
        Args:
            documento: Documento limpo para preencher
            
        Returns:
            bool: True se preenchido com sucesso
        """
        try:
            # Estratégias múltiplas para encontrar o campo documento
            selectors = [
                "input[name='documento']",
                "input[id='documento']", 
                "input[type='text']",
                "input[placeholder*='CPF']",
                "input[placeholder*='CNPJ']",
                "input[placeholder*='documento']"
            ]
            
            campo_encontrado = None
            
            for selector in selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=2000)
                    campo_encontrado = selector
                    break
                except:
                    continue
            
            if not campo_encontrado:
                # Buscar genericamente o primeiro campo de texto
                campos_texto = await self.page.query_selector_all("input[type='text']")
                if campos_texto:
                    campo_encontrado = "input[type='text']"
                else:
                    logger.error("❌ Campo documento não encontrado")
                    return False
            
            # Preencher campo
            await self.page.fill(campo_encontrado, documento)
            
            # Verificar se foi preenchido corretamente
            valor_preenchido = await self.page.input_value(campo_encontrado)
            
            if valor_preenchido == documento:
                logger.info(f"✅ Campo preenchido corretamente: {documento}")
                return True
            else:
                logger.error(f"❌ Erro no preenchimento. Esperado: {documento}, Obtido: {valor_preenchido}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao preencher documento: {e}")
            return False
    
    async def _submeter_formulario(self) -> bool:
        """Submeter formulário com múltiplas estratégias
        
        Returns:
            bool: True se submetido com sucesso
        """
        try:
            # Estratégias múltiplas para submeter o formulário
            strategies = [
                # Estratégia 1: Botão "Avançar" específico (input type='image')
                ("input[type='image'][alt*='Avançar']", "Botão Avançar (image)"),
                ("input[type='Image'][alt*='Avançar']", "Botão Avançar (Image maiúsculo)"),
                
                # Estratégia 2: Por src da imagem
                ("input[src*='admavanc.gif']", "Botão por src admavanc.gif"),
                ("input[src*='avanc']", "Botão por src avanc"),
                
                # Estratégia 3: Botões submit padrão
                ("input[type='submit']", "Input submit"),
                ("button[type='submit']", "Button submit"),
                
                # Estratégia 4: Por texto/value
                ("input[value*='Consultar']", "Botão Consultar"),
                ("input[value*='Buscar']", "Botão Buscar"),
                ("input[value*='Avançar']", "Botão Avançar por value"),
                ("button:has-text('Consultar')", "Button com texto Consultar"),
                ("button:has-text('Buscar')", "Button com texto Buscar"),
                ("button:has-text('Avançar')", "Button com texto Avançar"),
                
                # Estratégia 5: Qualquer input type='image'
                ("input[type='image']", "Qualquer input image"),
                ("input[type='Image']", "Qualquer input Image"),
                
                # Estratégia 6: Primeiro botão encontrado
                ("button", "Primeiro botão genérico")
            ]
            
            for selector, descricao in strategies:
                try:
                    await self.page.wait_for_selector(selector, timeout=2000)
                    await self.page.click(selector)
                    logger.info(f"✅ Formulário submetido usando: {descricao}")
                    return True
                except:
                    continue
            
            # Se nenhuma estratégia funcionou, tentar Enter no campo documento
            try:
                await self.page.press("input[type='text']", "Enter")
                logger.info("✅ Formulário submetido com Enter")
                return True
            except:
                pass
            
            logger.error("❌ Nenhuma estratégia de submissão funcionou")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao submeter formulário: {e}")
            return False
    
    async def _processar_resultado(self, documento: str, protocolo: Optional[str] = None) -> Optional[str]:
        """Processar página de resultado e baixar fatura
        
        Args:
            documento: Documento do cliente
            protocolo: Protocolo para nomenclatura
            
        Returns:
            str: Caminho do arquivo baixado ou None
        """
        try:
            # Aguardar página de resultado carregar
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # Verificar se há mensagens de erro
            page_content = await self.page.content()
            page_text = page_content.lower()
            
            # Mensagens de erro comuns
            error_messages = [
                "não encontrado", "não localizado", "não existe",
                "documento inválido", "cpf inválido", "cnpj inválido", 
                "sem faturas", "nenhuma fatura", "não há faturas",
                "erro", "falha", "problema"
            ]
            
            for error_msg in error_messages:
                if error_msg in page_text:
                    logger.warning(f"⚠️ Mensagem de erro detectada: '{error_msg}'")
                    return None
            
            # Procurar links/botões de download
            download_selectors = [
                # Links com texto específico
                "a:has-text('boleto')",
                "a:has-text('fatura')", 
                "a:has-text('2ª via')",
                "a:has-text('segunda via')",
                "a:has-text('download')",
                "a:has-text('baixar')",
                "a:has-text('pdf')",
                
                # Links por atributos href
                "a[href*='pdf']",
                "a[href*='boleto']", 
                "a[href*='fatura']",
                "a[href*='download']",
                
                # Botões
                "button:has-text('Download')",
                "button:has-text('Baixar')",
                "button:has-text('PDF')",
                
                # Inputs type image/submit
                "input[type='image'][alt*='Download']",
                "input[type='image'][alt*='PDF']", 
                "input[type='image'][alt*='Boleto']",
                
                # Imagens clicáveis
                "img[alt*='Download']",
                "img[alt*='PDF']",
                "img[alt*='Boleto']"
            ]
            
            download_element = None
            
            for selector in download_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        download_element = elements[0]  # Pegar primeiro encontrado
                        logger.info(f"📄 Link de download encontrado: {selector}")
                        break
                except:
                    continue
            
            if download_element:
                # Aguardar download começar
                async with self.page.expect_download() as download_info:
                    await download_element.click()
                    
                download = await download_info.value
                
                # Gerar nome único para o arquivo
                if protocolo and protocolo != 'N/A':
                    filename = f"fatura_protocolo_{protocolo}_{int(time.time())}.pdf"
                else:
                    filename = f"fatura_{documento}_{int(time.time())}.pdf"
                
                # 💾 Salvar arquivo usando StorageManager
                temp_path = os.path.join(tempfile.gettempdir(), filename)
                await download.save_as(temp_path)
                
                # Verificar se arquivo foi baixado
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    # Ler arquivo e usar StorageManager
                    with open(temp_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Salvar usando StorageManager (com auto-limpeza)
                    save_result = await storage_manager.save_invoice(documento, filename, file_data)
                    
                    # Remover arquivo temporário
                    os.unlink(temp_path)
                    
                    if save_result['success']:
                        logger.info(f"✅ Fatura salva via StorageManager: {filename} ({save_result['file_size_mb']:.2f}MB)")
                        logger.info(f"📊 Armazenamento total: {save_result['total_storage_mb']:.2f}MB")
                        security_event("fatura_downloaded", "low", documento=documento, arquivo=filename)
                        return save_result['file_path']
                    else:
                        logger.error(f"❌ Erro ao salvar via StorageManager: {save_result.get('error')}")
                        return None
                else:
                    logger.error("❌ Arquivo baixado está vazio ou não existe")
                    return None
            else:
                logger.warning("❌ Nenhum link de download encontrado")
                
                # Debug: tirar screenshot da página
                try:
                    screenshot_path = os.path.join(self.faturas_dir, f"debug_no_download_{documento}_{int(time.time())}.png")
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"📸 Screenshot salvo para debug: {screenshot_path}")
                except:
                    pass
                    
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado: {e}")
            return None
    
    async def baixar_multiplas_faturas(self, documentos_protocolos: List[tuple], intervalo: float = 5.0) -> Dict[str, Any]:
        """Baixar múltiplas faturas sequencialmente
        
        Args:
            documentos_protocolos: Lista de tuplas (documento, protocolo)
            intervalo: Intervalo entre downloads em segundos
            
        Returns:
            dict: Resultados dos downloads
        """
        start_time = time.time()
        resultados = {}
        sucessos = 0
        erros = 0
        
        logger.info(f"📋 Iniciando download de {len(documentos_protocolos)} faturas...")
        
        for i, (documento, protocolo) in enumerate(documentos_protocolos, 1):
            logger.info(f"\n📄 Processando {i}/{len(documentos_protocolos)}: {documento} (Protocolo: {protocolo})")
            
            arquivo_baixado = await self.baixar_fatura(documento, protocolo)
            
            if arquivo_baixado:
                resultados[documento] = {
                    'status': 'sucesso',
                    'arquivo': arquivo_baixado,
                    'protocolo': protocolo,
                    'timestamp': datetime.now().isoformat()
                }
                sucessos += 1
                logger.info(f"✅ Sucesso {i}/{len(documentos_protocolos)}: {documento}")
            else:
                resultados[documento] = {
                    'status': 'erro',
                    'arquivo': None,
                    'protocolo': protocolo,
                    'timestamp': datetime.now().isoformat()
                }
                erros += 1
                logger.error(f"❌ Erro {i}/{len(documentos_protocolos)}: {documento}")
            
            # Aguardar intervalo entre downloads (exceto no último)
            if i < len(documentos_protocolos):
                logger.info(f"⏳ Aguardando {intervalo}s antes do próximo download...")
                await asyncio.sleep(intervalo)
        
        # Resumo final
        duration = time.time() - start_time
        logger.info(f"\n📊 Resumo final do download em lote:")
        logger.info(f"   ✅ Sucessos: {sucessos}")
        logger.info(f"   ❌ Erros: {erros}")
        logger.info(f"   ⏱️ Tempo total: {duration:.1f}s")
        logger.info(f"   📁 Arquivos salvos em: {os.path.abspath(self.faturas_dir)}")
        
        performance_metric("fatura_download_batch", duration, total=len(documentos_protocolos), sucessos=sucessos, erros=erros)
        
        return {
            'resultados': resultados,
            'resumo': {
                'total': len(documentos_protocolos),
                'sucessos': sucessos,
                'erros': erros,
                'taxa_sucesso': (sucessos / len(documentos_protocolos)) * 100 if documentos_protocolos else 0,
                'tempo_total': duration
            }
        }
    
    def listar_faturas_baixadas(self) -> List[Dict[str, Any]]:
        """Listar todas as faturas baixadas
        
        Returns:
            list: Lista de dicionários com informações dos arquivos
        """
        if not os.path.exists(self.faturas_dir):
            return []
        
        arquivos = []
        for arquivo in os.listdir(self.faturas_dir):
            if arquivo.endswith('.pdf'):
                caminho_completo = os.path.join(self.faturas_dir, arquivo)
                stat = os.stat(caminho_completo)
                arquivos.append({
                    'nome': arquivo,
                    'caminho': caminho_completo,
                    'tamanho_bytes': stat.st_size,
                    'tamanho_mb': round(stat.st_size / 1024 / 1024, 2),
                    'data_modificacao': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'data_criacao': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        # Ordenar por data de modificação (mais recente primeiro)
        return sorted(arquivos, key=lambda x: x['data_modificacao'], reverse=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status atual do downloader
        
        Returns:
            dict: Status e estatísticas
        """
        faturas = self.listar_faturas_baixadas()
        
        return {
            'sac_url': self.sac_url,
            'faturas_dir': os.path.abspath(self.faturas_dir),
            'captcha_solver_disponivel': True,
            'total_faturas_baixadas': len(faturas),
            'tamanho_total_mb': sum(f['tamanho_mb'] for f in faturas),
            'ultima_fatura': faturas[0] if faturas else None
        }

# Função de conveniência
async def baixar_fatura_rapido(page: Page, documento: str, protocolo: Optional[str] = None) -> Optional[str]:
    """Função de conveniência para baixar uma fatura rapidamente
    
    Args:
        page: Página Playwright
        documento: CPF/CNPJ do cliente
        protocolo: Protocolo do cliente
        
    Returns:
        str: Caminho do arquivo baixado ou None
    """
    downloader = FaturaDownloader(page)
    return await downloader.baixar_fatura(documento, protocolo)