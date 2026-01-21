"""
Sistema de Logging Centralizado

ANTI-PADRÃO CORRIGIDO: Print Debugging
Anteriormente usava print() em todo o código. Agora usa logging module
com níveis configuráveis (DEBUG, INFO, WARNING, ERROR).

Autores: Henrique Crachat (2501450)
"""
import logging
import sys
from pathlib import Path


def setup_logging(level=logging.INFO, log_file=None):
    """
    Configura o sistema de logging da aplicação.

    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ficheiro opcional para gravar logs
    """
    # Formato do log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        # Criar diretório se não existir
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))

    # Configurar logging básico
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )


def get_logger(name):
    """
    Obtém um logger configurado para o módulo especificado.

    Args:
        name: Nome do módulo (__name__)

    Returns:
        Logger configurado

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Operação completada")
        >>> logger.error("Erro ao processar dados")
    """
    return logging.getLogger(name)


# Configuração padrão ao importar
setup_logging(level=logging.INFO)
