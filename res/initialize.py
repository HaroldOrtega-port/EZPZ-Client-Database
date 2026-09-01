from .views.clients import bp as clients_bp
from .views.home import bp as home_bp


def routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(clients_bp)
