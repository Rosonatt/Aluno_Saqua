# Conteúdo temporário para app/__init__.py

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'teste' 

    # Importamos apenas o blueprint de teste do nosso routes.py simplificado
    from .routes import main_bp
    
    # Registramos apenas o blueprint de teste
    app.register_blueprint(main_bp)

    return app