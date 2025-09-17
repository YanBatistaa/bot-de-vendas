# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

if not TELEGRAM_TOKEN or not DATABASE_URL or not MERCADO_PAGO_ACCESS_TOKEN:
    raise ValueError(
        "As variáveis TELEGRAM_TOKEN, DATABASE_URL e MERCADO_PAGO_ACCESS_TOKEN são obrigatórias no arquivo .env"
    )

# LINHA DE DEPURAÇÃO TEMPORÁRIA
print(f"--> WEBHOOK_SECRET CARREGADA: {WEBHOOK_SECRET}")