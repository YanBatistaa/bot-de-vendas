# web/server.py (VERSÃO TEMPORÁRIA APENAS PARA VALIDAR A URL)

import json
from fastapi import FastAPI, Request, Response, status
from telegram.ext import Application

# Cria a instância da aplicação FastAPI
api = FastAPI()

@api.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    """
    Endpoint temporário que apenas responde 'OK' para o teste do Mercado Pago.
    """
    print("Recebido webhook de teste do Mercado Pago. Respondendo 'OK' para validação da URL.")
    # Simplesmente retornamos um status 200 (OK) para qualquer requisição.
    return Response(status_code=status.HTTP_200_OK)