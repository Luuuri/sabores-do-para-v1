# TESTANDO PRA CRIAR FUNCIONÁRIOS NO SQL

from pathlib import Path
from app.backend.repositories.user_repository import create_user

create_user("Luisa", "teste@email.com", "123", "admin")
print("Usuário criado!")