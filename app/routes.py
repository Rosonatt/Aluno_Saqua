# Conteúdo temporário para app/routes.py

from flask import Blueprint

# Criamos APENAS o blueprint principal para o teste
main_bp = Blueprint('main', __name__)

# Criamos APENAS a rota principal, sem nenhuma outra dependência
@main_bp.route('/')
def index():
    return "<h1>A VERSÃO MÍNIMA FUNCIONOU!</h1>"

# As outras rotas e blueprints foram removidas apenas para este teste