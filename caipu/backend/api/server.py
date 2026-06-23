"""家庭私厨 API 服务层"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, send_from_directory, request, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 图片上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====== 注册蓝图 ======
from api.recipes      import recipes_bp
from api.ingredients  import ingredients_bp
from api.meal_plans   import meal_plans_bp
from api.purchases    import purchases_bp
from api.feasts       import feasts_bp
from api.users        import users_bp
from api.checkins     import checkins_bp
from api.tenants      import tenants_bp

app.register_blueprint(recipes_bp,     url_prefix='/api/recipes')
app.register_blueprint(ingredients_bp, url_prefix='/api/ingredients')
app.register_blueprint(meal_plans_bp,  url_prefix='/api/meal-plans')
app.register_blueprint(purchases_bp,   url_prefix='/api/purchases')
app.register_blueprint(feasts_bp,      url_prefix='/api/feasts')
app.register_blueprint(users_bp,       url_prefix='/api/users')
app.register_blueprint(checkins_bp,    url_prefix='/api/checkins')
app.register_blueprint(tenants_bp,     url_prefix='/api/tenants')


@app.route('/api/health')
def health_check():
    from data.database import check_db
    db_ok = check_db()
    return jsonify({
        "status": "ok",
        "app": "家庭私厨",
        "db": "connected" if db_ok else "disconnected"
    })


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """上传菜谱图片"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "仅支持 png/jpg/jpeg/gif/webp"}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    return jsonify({"url": f"/uploads/{filename}", "filename": filename}), 201


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route('/')
def index():
    root = os.path.join(os.path.dirname(__file__), '..', '..')
    resp = make_response(send_from_directory(root, 'index.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp
