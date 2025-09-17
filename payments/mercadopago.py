# payments/mercadopago.py

import mercadopago
from core.config import MERCADO_PAGO_ACCESS_TOKEN
from database.models import Order, Product

# Inicializa o SDK do Mercado Pago com seu Access Token.
sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)

def create_pix_payment(order: Order, product: Product) -> dict | None:
    """
    Cria uma cobrança PIX no Mercado Pago para um determinado pedido.
    Retorna o dicionário de resposta da API do Mercado Pago ou None em caso de erro.
    """
    # Esta URL DEVE ser HTTPS e acessível publicamente.
    # Usaremos o ngrok para desenvolvimento para expor nosso servidor local.
    # Em produção, você substituirá pela URL do seu servidor.
    notification_url = "https://12f0f86180ba.ngrok-free.app/webhook/mercadopago"

    payment_data = {
        "transaction_amount": float(product.price),
        "description": product.name,
        "payment_method_id": "pix",
        "payer": {
            "email": f"user_{order.user_id}@meubot.com",
            "first_name": "UsuarioTelegram",
            "last_name": str(order.user_id),
        },
        "notification_url": notification_url,
        "external_reference": str(order.id)
    }

    try:
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response.get("response")

        if payment and payment.get("status") == "pending":
            return payment
        else:
            print("Erro ao criar pagamento:", payment_response)
            return None
            
    except Exception as e:
        print(f"Erro na API do Mercado Pago: {e}")
        return None