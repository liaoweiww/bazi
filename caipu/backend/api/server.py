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


@app.route('/api/ai/generate-image', methods=['POST'])
def generate_ai_image():
    """AI 生成菜品图片 — MVP 版本
    接收 {prompt}，调用 AI API 生成图片并保存到 uploads/
    若未配置 AI API，返回提示信息
    """
    import json as _json
    body = request.get_json() or {}
    prompt = body.get('prompt', '')
    if not prompt:
        return jsonify({"error": "prompt 必填"}), 400

    # 尝试调用 AI API（如已配置）
    ai_url = os.environ.get('CAIPU_AI_API_URL', '')
    ai_key = os.environ.get('CAIPU_AI_API_KEY', '')
    if ai_url:
        try:
            import requests as _req
            resp = _req.post(ai_url, json={
                "prompt": prompt,
                "n": 1, "size": "512x512",
                "response_format": "b64_json"
            }, headers={"Authorization": f"Bearer {ai_key}"}, timeout=60)
            if resp.status_code == 200:
                import base64
                data = resp.json()
                img_data = base64.b64decode(data['data'][0]['b64_json'])
                filename = f"ai_{uuid.uuid4().hex}.png"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(img_data)
                return jsonify({"url": f"/uploads/{filename}", "filename": filename, "source": "ai"}), 201
        except Exception as e:
            pass  # 降级到简单生成

    # MVP 降级：生成简单的纯色占位图
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (512, 512), '#FDFAF5')
        draw = ImageDraw.Draw(img)
        # 画圆角边框
        draw.rectangle([20, 20, 492, 492], outline='#B5453A', width=3)
        # 写文字
        emoji = body.get('emoji', '🍳')
        draw.text((256, 180), emoji, fill='#2C2416', anchor='mm')
        draw.text((256, 300), prompt[:30], fill='#7A7060', anchor='mm')
        draw.text((256, 350), '🏠 家庭私厨 · AI生成', fill='#C9A96E', anchor='mm')

        filename = f"ai_{uuid.uuid4().hex}.png"
        filepath = os.path.join(UPLOAD_DIR, filename)
        img.save(filepath, 'PNG')
        return jsonify({"url": f"/uploads/{filename}", "filename": filename, "source": "ai_local"}), 201
    except Exception as e:
        return jsonify({"error": f"图片生成失败: {str(e)}"}), 500


@app.route('/')
def index():
    root = os.path.join(os.path.dirname(__file__), '..', '..')
    resp = make_response(send_from_directory(root, 'index.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp
