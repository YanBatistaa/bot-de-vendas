# database/models.py

import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    Numeric,
    ForeignKey,
    BigInteger
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

# Base declarativa do SQLAlchemy. Nossas classes de modelo herdarão dela.
Base = declarative_base()

# Usamos um Enum para os status do pedido. Isso evita erros de digitação
# e torna o código mais claro e seguro.
class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"

class User(Base):
    """
    Modelo para armazenar os usuários do Telegram.
    """
    __tablename__ = "users"

    # Usamos BigInteger pois o ID de usuário do Telegram pode ser um número grande.
    id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento: Um usuário pode ter vários pedidos.
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.full_name}')>"

class Product(Base):
    """
    Modelo para armazenar os produtos digitais que você vende.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    # Usamos Numeric para preços para evitar problemas de arredondamento com float.
    price = Column(Numeric(10, 2), nullable=False)
    # Armazena o link do conteúdo digital ou o file_id do Telegram.
    content = Column(String, nullable=False)

    # Relacionamento: Um produto pode estar em vários pedidos.
    orders = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"

class Order(Base):
    """
    Modelo para rastrear cada transação de compra.
    Este é o modelo mais importante para a lógica de pagamento.
    """
    __tablename__ = "orders"

    # Usamos UUID como chave primária para os pedidos. É um ID único e não sequencial,
    # o que é mais seguro para expor externamente, se necessário.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # A máquina de estados da nossa transação.
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # ID do pagamento gerado pelo gateway (ex: Mercado Pago). Essencial para reconciliação.
    gateway_payment_id = Column(String, unique=True, index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status='{self.status.value}')>"