# bot/handlers.py

import base64
import re
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
import mercadopago
from database.database import SessionLocal
from database.models import User, Product, Order
from payments.mercadopago import create_pix_payment

def escape_markdown_v2(text: str) -> str:
    """Função auxiliar para escapar caracteres especiais do MarkdownV2."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /start."""
    if not update.message or not update.message.from_user:
        return

    user_info = update.message.from_user
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_info.id).first()
        if not user:
            new_user = User(id=user_info.id, full_name=user_info.full_name)
            db.add(new_user)
            db.commit()
            print(f"Novo usuário registrado: {user_info.full_name} ({user_info.id})")
        else:
            print(f"Usuário já conhecido: {user_info.full_name} ({user.id})")
    finally:
        db.close()

    keyboard = [["🛍️ Ver Produtos"], ["📞 Suporte", "💬 Sobre Nós"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    welcome_message = (
        f"Olá, {user_info.first_name}! 👋\n\n"
        "Bem-vindo(a) à nossa loja de conteúdo digital.\n\n"
        "Use o menu abaixo para navegar."
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o botão 'Ver Produtos'."""
    db: Session = SessionLocal()
    try:
        products = db.query(Product).all()
        if not products:
            await update.message.reply_text("😕 Desculpe, não há produtos disponíveis no momento.")
            return

        await update.message.reply_text("Aqui estão nossos produtos disponíveis:")
        for product in products:
            keyboard = [[
                InlineKeyboardButton(f"Comprar por R$ {product.price}", callback_data=f"buy_{product.id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            safe_name = escape_markdown_v2(product.name)
            safe_description = escape_markdown_v2(product.description)
            
            product_message = (
                f"*{safe_name}*\n\n"
                f"{safe_description}"
            )
            await update.message.reply_text(
                text=product_message,
                reply_markup=reply_markup,
                parse_mode='MarkdownV2'
            )
    finally:
        db.close()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para todos os botões de callback."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data and data.startswith("buy_"):
        product_id = int(data.split("_")[1])
        user_id = query.from_user.id
        
        db: Session = SessionLocal()
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                await query.edit_message_text(text="Produto não encontrado.")
                return

            new_order = Order(user_id=user_id, product_id=product_id)
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            
            # --- AQUI ESTÁ A CORREÇÃO ---
            # Removemos a formatação Markdown desta mensagem para evitar erros.
            await query.edit_message_text(text=f"Gerando pagamento para {product.name}...")

            payment_info = create_pix_payment(new_order, product)

            if payment_info:
                qr_code_base64 = payment_info['point_of_interaction']['transaction_data']['qr_code_base64']
                pix_code = payment_info['point_of_interaction']['transaction_data']['qr_code']
                gateway_payment_id = str(payment_info['id'])

                new_order.gateway_payment_id = gateway_payment_id
                db.commit()

                qr_code_bytes = base64.b64decode(qr_code_base64)
                
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=qr_code_bytes,
                    caption="✅ Pagamento PIX gerado! Escaneie o QR Code ou use o código abaixo."
                )
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"`{pix_code}`",
                    parse_mode='MarkdownV2'
                )
            else:
                await query.edit_message_text(text="😕 Desculpe, ocorreu um erro ao gerar o pagamento. Tente novamente mais tarde.")
        finally:
            db.close()