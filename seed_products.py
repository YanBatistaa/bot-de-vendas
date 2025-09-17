# seed_products.py

from database.database import SessionLocal, create_db_and_tables
from database.models import Product
from decimal import Decimal

def seed_data():
    """
    Função para inserir o produto de teste no banco de dados.
    """
    db = SessionLocal()

    try:
        # Verifica se já existem produtos para não inserir duplicatas
        if db.query(Product).count() == 0:
            print("Inserindo produto de teste (R$ 1,00)...")

            # Produto de Teste
            produto_teste = Product(
                name="TESTE 1",
                description="Produto de teste para validação do fluxo de pagamento.",
                price=Decimal("0.01"),
                content="https://exemplo.com/conteudo/liberado/sucesso"
            )

            db.add(produto_teste)
            db.commit()
            print("Produto de teste inserido com sucesso!")
        else:
            print("O banco de dados já contém produtos. Nenhuma ação foi tomada.")

    finally:
        db.close()

if __name__ == "__main__":
    # Garante que as tabelas existam antes de tentar inserir dados
    create_db_and_tables()
    seed_data()