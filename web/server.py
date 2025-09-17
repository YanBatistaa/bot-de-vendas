# web/server.py

import json
import re
import uuid # <-- Importe a biblioteca UUID
from fastapi import FastAPI, Request, Response, status, HTTPException
from sqlalchemy.orm import Session
from telegram.ext import Application
import mercadopago

from core.security import validate_mercadopago_signature
from database.database import SessionLocal
from database.models import Order, OrderStatus, Product
from payments.mercadopago import sdk

api = FastAPI()

async def deliver_product(order: Order, product: Product, ptb_app: Application):
    """
    Função assíncrona para enviar o conteúdo digital ao usuário via Telegram.
    """
    success_message = (
        f"Pagamento aprovado!\n\n"
        f"Seu conteúdo '{product.name}' está liberado:\n{product.content}"
    )
    
    try:
        await ptb_app.bot.send_message(
            chat_id=order.user_id,
            text=success_message
        )
        print(f"Produto entregue com sucesso para o pedido {order.id}")
    except Exception as e:
        print(f"Erro ao entregar o produto para o pedido {order.id}: {e}")

@api.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    """
    Endpoint que recebe, valida e processa as notificações de pagamento.
    """
    ptb_app: Application = request.app.state.ptb_app
    
    try:
        body_bytes = await validate_mercadopago_signature(request)
    except HTTPException as e:
        if e.status_code == 403:
            print("Recebida notificação com assinatura inválida. Ignorando.")
            return Response(status_code=status.HTTP_200_OK)
        raise e

    notification_data = json.loads(body_bytes)
    
    if notification_data.get("type") == "payment":
        payment_id = notification_data.get("data", {}).get("id")
        if not payment_id:
            return Response(status_code=status.HTTP_200_OK)

        print(f"Notificação recebida para o pagamento ID: {payment_id}. Verificando status na API...")
        
        try:
            payment_info_response = sdk.payment().get(payment_id)
            payment_info = payment_info_response.get("response", {})
            payment_status = payment_info.get("status")
            print(f"Status retornado pela API para o pagamento {payment_id}: {payment_status}")

            if payment_status == "approved":
                db: Session = SessionLocal()
                try:
                    order_id_str = payment_info.get("external_reference")
                    if not order_id_str:
                         print(f"Webhook para pagamento {payment_id} não possui external_reference.")
                         return Response(status_code=status.HTTP_200_OK)

                    # --- AQUI ESTÁ A CORREÇÃO ---
                    # Convertendo a string de volta para um objeto UUID
                    order_uuid = uuid.UUID(order_id_str)
                    
                    # Usando o objeto UUID na busca
                    order = db.query(Order).filter(Order.id == order_uuid).first()

                    if not order or order.status == OrderStatus.PAID:
                        print(f"Pedido {order_id_str} não encontrado ou já processado.")
                        return Response(status_code=status.HTTP_200_OK)

                    order.status = OrderStatus.PAID
                    db.commit()
                    db.refresh(order)
                    print(f"Pedido {order.id} atualizado para PAGO.")
                    
                    product = db.query(Product).filter(Product.id == order.product_id).first()
                    if product:
                        await deliver_product(order, product, ptb_app)
                    else:
                        print(f"ERRO CRÍTICO: Produto não encontrado para o pedido {order.id}")
                finally:
                    db.close()
            else:
                print(f"Pagamento {payment_id} não está aprovado ({payment_status}). Nenhuma ação será tomada.")
        
        except Exception as e:
            print(f"Erro ao processar o webhook para o pagamento {payment_id}: {e}")

    return Response(status_code=status.HTTP_200_OK)