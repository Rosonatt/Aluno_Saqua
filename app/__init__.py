from flask import Flask
from .models import NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS

def create_app():
    # Cria a instância principal da aplicação
    app = Flask(__name__)
    
    # Configura a chave secreta
    app.secret_key = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar'

    # Adiciona as configurações globais ao app config para que fiquem disponíveis
    app.config.update(
        NOTA_MINIMA_APROVACAO_MATERIA=NOTA_MINIMA_APROVACAO_MATERIA,
        MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS
    )

    # Bloco para importar e registrar os Blueprints
    with app.app_context():
        # Importa os blueprints que você criou em routes.py
        from .routes import main_bp, aluno_bp, pais_bp, professor_bp, psicopedagogo_bp
        
        # Registra cada blueprint na aplicação
        app.register_blueprint(main_bp)
        app.register_blueprint(aluno_bp)
        app.register_blueprint(pais_bp)
        app.register_blueprint(professor_bp)
        app.register_blueprint(psicopedagogo_bp)

    return app