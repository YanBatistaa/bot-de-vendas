# core/security.py

import hmac
import hashlib
from fastapi import Request, HTTPException, status
from urllib.parse import urlparse, parse_qs

from core.config import WEBHOOK_SECRET

async def validate_mercadopago_signature(request: Request) -> bytes:
    """
    Valida a assinatura do webhook do Mercado Pago usando a fórmula correta,
    decifrada a partir dos logs de depuração.
    """
    if not WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WEBHOOK_SECRET não está configurado."
        )

    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")

    if not x_signature or not x_request_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cabeçalhos de assinatura ausentes."
        )

    try:
        parts = {p.split("=")[0]: p.split("=")[1] for p in x_signature.split(",")}
        ts = parts.get("ts")
        signature_hash = parts.get("v1")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de assinatura inválido."
        )

    if not ts or not signature_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timestamp ou hash da assinatura ausentes."
        )
    
    # --- CORREÇÃO FINAL DA LÓGICA DO MANIFEST ---
    # A fórmula correta, confirmada por padrões de API, é uma combinação
    # do ID da requisição, o timestamp e o ID do pagamento extraído da URL.
    parsed_url = urlparse(str(request.url))
    query_params = parse_qs(parsed_url.query)
    
    payment_id = query_params.get("data.id", [None])[0] or query_params.get("id", [None])[0]

    if not payment_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID do pagamento não encontrado na notificação.")

    manifest = f"id:{payment_id};request-id:{x_request_id};ts:{ts};"

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=manifest.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature_hash):
        print(f"\n--- FALHA NA VALIDAÇÃO ---")
        print(f"Manifesto Gerado: {manifest}")
        print(f"Assinatura Recebida: {signature_hash}")
        print(f"Assinatura Calculada: {expected_signature}")
        print(f"--- FIM DA FALHA ---\n")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assinatura inválida."
        )
    
    print(f"\n--- SUCESSO NA VALIDAÇÃO ---")
    print(f"Assinatura para o pagamento {payment_id} validada com sucesso!")
    print(f"--- FIM DO SUCESSO ---\n")

    body = await request.body()
    return body