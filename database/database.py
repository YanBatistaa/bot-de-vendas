# database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import DATABASE_URL
from .models import Base  # Importa a Base dos seus modelos

# Cria a engine de conexão com o banco de dados
# O argumento 'connect_args' é específico para o SQLite para permitir o uso em múltiplos threads.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria uma classe de Sessão que será usada para interagir com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    """
    Função para criar as tabelas no banco de dados com base nos modelos definidos.
    Isso só precisa ser executado uma vez.
    """
    print("Verificando e criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas prontas.")

# Este bloco permite que você execute este arquivo diretamente para criar as tabelas
if __name__ == "__main__":
    create_db_and_tables()