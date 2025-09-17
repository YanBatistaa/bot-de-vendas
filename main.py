# main.py (VERSÃO FINAL com THREADING)

import threading
import uvicorn
import logging
from bot.bot import setup_bot
from web.server import api as fastapi_app

# Configura os logs para termos uma visão clara do que está acontecendo
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_server():
    """
    Função alvo para a thread do servidor. Inicia o Uvicorn.
    """
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    logger.info("Iniciando a aplicação...")

    # 1. Configura a aplicação do bot
    ptb_app = setup_bot()

    # 2. Disponibiliza a instância do bot para o FastAPI ANTES de iniciar o servidor
    fastapi_app.state.ptb_app = ptb_app
    
    # 3. Cria uma nova thread que executará a função `run_server`
    server_thread = threading.Thread(target=run_server)
    
    # 4. Inicia a thread do servidor em segundo plano.
    # O `daemon=True` garante que a thread do servidor será encerrada
    # quando o processo principal (o bot) for encerrado.
    server_thread.daemon = True
    server_thread.start()
    logger.info("Servidor web iniciado em uma thread separada na porta 8000.")

    # 5. Inicia o bot na thread principal.
    # Esta chamada `run_polling` é bloqueante e manterá a aplicação viva.
    logger.info("Bot iniciando em modo polling na thread principal...")
    ptb_app.run_polling()