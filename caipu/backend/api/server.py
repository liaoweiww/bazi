from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from api.recipe_routes import recipe_bp
from api.material_routes import material_bp
from api.price_routes import price_bp

app.register_blueprint(recipe_bp)
app.register_blueprint(material_bp)
app.register_blueprint(price_bp)


@app.route('/api/health')
def health():
    return {'status': 'ok'}
