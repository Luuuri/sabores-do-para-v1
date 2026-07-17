"""
connection.py - Conexão com o Banco de Dados
===========================================
Módulo responsável por gerenciar a conexão com o MySQL.
Carrega as credenciais do arquivo .env e fornece uma função
para obter conexões reutilizáveis.
"""

import mysql.connector
import os
import dotenv

# Carrega as variáveis de ambiente do arquivo .env
dotenv.load_dotenv()


def get_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados MySQL.
    
    As credenciais são lidas do arquivo .env:
        - DB_HOST: Host do servidor MySQL (geralmente 'localhost')
        - DB_USER: Usuário do MySQL (geralmente 'root')
        - DB_PASSWORD: Senha do usuário MySQL
        - DB_NAME: Nome do banco de dados
    
    Returns:
        mysql.connector.connection.MySQLConnection: Conexão ativa com o banco
        
    Raises:
        mysql.connector.Error: Se falhar a conexão com o banco de dados
    """
    return mysql.connector.connect(
        # Host do servidor MySQL
        host=os.getenv("DB_HOST"),
        # Usuário do MySQL
        user=os.getenv("DB_USER"),
        # Senha do usuário MySQL
        password=os.getenv("DB_PASSWORD"),
        # Nome do banco de dados
        database=os.getenv("DB_NAME")
    )
