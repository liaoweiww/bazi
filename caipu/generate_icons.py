"""为'我的菜谱'小程序生成全套图标"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), 'miniapp', 'images')

# 配色体系
BLUE = '#007AFF'
RED = '#FF3B30'
GREEN = '#34C759'
ORANGE = '#FF9500'
GRAY = '#8E8E93'
LIGHT_BG = '#F2F2F7'
WHITE = '#FFFFFF'
DARK = '#1C1C1E'

CATEGORY_COLORS = {
    '家常菜': '#FF9500',
    '快手菜': '#34C759',
    '汤品': '#007AFF',
    '荤菜': '#FF3B30',
    '素菜': '#34C759',
}

RECIPE_EMOJI = {
    '红烧肉': '🥩', '番茄炒蛋': '🍅', '酸辣土豆丝': '🥔',
    '糖醋排骨': '🍖', '鱼香肉丝': '🥕', '麻婆豆腐': '🫘',
    '清炒时蔬': '🥬', '宫保鸡丁': '🥜', '西红柿蛋花汤': '🍳',
    '回锅肉': '🥓', '清蒸鲈鱼': '🐟', '蛋炒饭': '🍚',
    '可乐鸡翅': '🍗', '蒜蓉西兰花': '🥦', '紫菜蛋花汤': '🍲',
    '醋溜白菜': '🥬', '红烧茄子': '🍆', '凉拌黄瓜': '🥒',
    '番茄牛腩汤': '🍲', '干煸四季豆': '🫛', '蒜蓉粉丝蒸扇贝': '🦪',
    '土豆炖牛肉': '🥩', '白菜豆腐汤': '🫘',
}

RECIPE_SYMBOLS = {
    '红烧肉': '肉', '番茄炒蛋': '蛋', '酸辣土豆丝': '薯',
    '糖醋排骨': '骨', '鱼香肉丝': '丝', '麻婆豆腐': '豆',
    '清炒时蔬': '蔬', '宫保鸡丁': '鸡', '西红柿蛋花汤': '汤',
    '回锅肉': '肉', '清蒸鲈鱼': '鱼', '蛋炒饭': '饭',
    '可乐鸡翅': '翅', '蒜蓉西兰花': '花', '紫菜蛋花汤': '汤',
    '醋溜白菜': '菜', '红烧茄子': '茄', '凉拌黄瓜': '瓜',
    '番茄牛腩汤': '汤', '干煸四季豆': '豆', '蒜蓉粉丝蒸扇贝': '贝',
    '土豆炖牛肉': '牛', '白菜豆腐汤': '汤',
}


def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def create_rounded_rect_mask(size, radius):
    """创建圆角矩形蒙版"""
    w, h = size
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    return mask


def draw_centered_text(draw, text, bounds, fill, font=None):
    """在bounds中居中绘制文字"""
    x1, y1, x2, y2 = bounds
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = x1 + (x2 - x1 - tw) // 2
    y = y1 + (y2 - y1 - th) // 2
    draw.text((x, y), text, fill=fill, font=font)
    return x, y


def create_tab_icons():
    """生成TabBar图标 81x81"""
    size = 81
    # 做菜图标 - 锅/铲形状
    for name, color in [('tab-recipe', GRAY), ('tab-recipe-active', BLUE)]:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        c = hex_to_rgb(color)

        # 画一个圆形锅体
        draw.ellipse([14, 22, 66, 70], fill=c, outline=None)
        # 锅把手
        draw.rounded_rectangle([55, 28, 72, 38], radius=4, fill=c)

        img.save(os.path.join(OUT_DIR, f'{name}.png'))

    # 菜市图标 - 菜篮形状
    for name, color in [('tab-market', GRAY), ('tab-market-active', BLUE)]:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        c = hex_to_rgb(color)

        # 篮子底部
        draw.arc([10, 30, 70, 50], 180, 360, fill=c, width=5)
        # 篮子体
        draw.rectangle([14, 30, 66, 55], fill=c)
        # 把手
        draw.arc([25, 10, 55, 35], 0, 180, fill=c, width=5)
        # 叶子装饰
        draw.ellipse([18, 22, 30, 34], fill=(255, 255, 255, 200))
        draw.ellipse([40, 16, 52, 28], fill=(255, 255, 255, 200))

        img.save(os.path.join(OUT_DIR, f'{name}.png'))
    print('✓ 4 tab icons')


def create_category_icons():
    """菜谱分类图标 128x128"""
    size = 128
    emotes = {
        '家常菜': '🏠', '快手菜': '⚡', '汤品': '🍲',
        '荤菜': '🍖', '素菜': '🥬'
    }
    # 尝试加载emoji字体
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 56)
    except:
        font = ImageFont.load_default()

    for cat, color in CATEGORY_COLORS.items():
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        c = hex_to_rgb(color)

        # 圆角背景
        mask = create_rounded_rect_mask((size, size), 28)
        bg = Image.new('RGBA', (size, size), c + (255,))
        img.paste(bg, (0, 0), mask)

        # 圆形内部
        inner = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        inner_draw = ImageDraw.Draw(inner)
        inner_draw.ellipse([28, 20, 100, 92], fill=(255, 255, 255, 230))
        inner_mask = create_rounded_rect_mask((size, size), 28)
        img.paste(inner, (0, 0), inner_mask)

        # Emoji
        if cat in emotes:
            bbox = draw.textbbox((0, 0), emotes[cat], font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(((size - tw) // 2, (size - th) // 2 - 2), emotes[cat],
                     font=font, embedded_color=True)

        fname = f'cat-{cat}.png'
        img.save(os.path.join(OUT_DIR, fname))
        print(f'  ✓ {fname}')


def create_recipe_icons():
    """每道菜的迷你图标 128x128"""
    size = 128
    try:
        emoji_font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 50)
    except:
        emoji_font = ImageFont.load_default()

    for name, cat in [
        ('红烧肉', '荤菜'), ('番茄炒蛋', '快手菜'), ('酸辣土豆丝', '快手菜'),
        ('糖醋排骨', '荤菜'), ('鱼香肉丝', '家常菜'), ('麻婆豆腐', '家常菜'),
        ('清炒时蔬', '素菜'), ('宫保鸡丁', '家常菜'), ('西红柿蛋花汤', '汤品'),
        ('回锅肉', '家常菜'), ('清蒸鲈鱼', '荤菜'), ('蛋炒饭', '快手菜'),
        ('可乐鸡翅', '家常菜'), ('蒜蓉西兰花', '素菜'), ('紫菜蛋花汤', '汤品'),
        ('醋溜白菜', '快手菜'), ('红烧茄子', '家常菜'), ('凉拌黄瓜', '快手菜'),
        ('番茄牛腩汤', '汤品'), ('干煸四季豆', '家常菜'), ('蒜蓉粉丝蒸扇贝', '荤菜'),
        ('土豆炖牛肉', '荤菜'), ('白菜豆腐汤', '汤品'),
    ]:
        color = CATEGORY_COLORS.get(cat, BLUE)
        c = hex_to_rgb(color)

        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 圆角背景
        mask = create_rounded_rect_mask((size, size), 28)
        bg = Image.new('RGBA', (size, size), c + (255,))
        img.paste(bg, (0, 0), mask)

        # 内圆白色背景
        inner = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        inner_draw = ImageDraw.Draw(inner)
        inner_draw.ellipse([22, 16, 106, 100], fill=(255, 255, 255, 240))
        inner_mask = create_rounded_rect_mask((size, size), 28)
        img.paste(inner, (0, 0), inner_mask)

        # Emoji
        emoji = RECIPE_EMOJI.get(name, '🍽')
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - tw) // 2, (size - th) // 2 - 4), emoji,
                 font=emoji_font, embedded_color=True)

        fname = f'icon-{name}.png'
        img.save(os.path.join(OUT_DIR, fname))
        print(f'  ✓ {fname}')


def create_recipe_covers():
    """菜谱封面图 640x360 带有菜名"""
    size = (640, 360)
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 48)
    except:
        try:
            title_font = ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc', 48)
        except:
            title_font = ImageFont.load_default()

    for name, cat in [
        ('红烧肉', '荤菜'), ('番茄炒蛋', '快手菜'), ('酸辣土豆丝', '快手菜'),
        ('糖醋排骨', '荤菜'), ('鱼香肉丝', '家常菜'), ('麻婆豆腐', '家常菜'),
        ('清炒时蔬', '素菜'), ('宫保鸡丁', '家常菜'), ('西红柿蛋花汤', '汤品'),
        ('回锅肉', '家常菜'), ('清蒸鲈鱼', '荤菜'), ('蛋炒饭', '快手菜'),
        ('可乐鸡翅', '家常菜'), ('蒜蓉西兰花', '素菜'), ('紫菜蛋花汤', '汤品'),
        ('醋溜白菜', '快手菜'), ('红烧茄子', '家常菜'), ('凉拌黄瓜', '快手菜'),
        ('番茄牛腩汤', '汤品'), ('干煸四季豆', '家常菜'), ('蒜蓉粉丝蒸扇贝', '荤菜'),
        ('土豆炖牛肉', '荤菜'), ('白菜豆腐汤', '汤品'),
    ]:
        color = CATEGORY_COLORS.get(cat, BLUE)
        c = hex_to_rgb(color)
        lighter = tuple(min(255, x + 60) for x in c)

        img = Image.new('RGBA', size, (0, 0, 0, 0))

        # 渐变背景
        for y in range(size[1]):
            ratio = y / size[1]
            r = int(c[0] + (lighter[0] - c[0]) * ratio)
            g = int(c[1] + (lighter[1] - c[1]) * ratio)
            b = int(c[2] + (lighter[2] - c[2]) * ratio)
            for x in range(size[0]):
                img.putpixel((x, y), (r, g, b, 255))

        # 圆角蒙版
        mask = create_rounded_rect_mask(size, 32)
        img.putalpha(mask.getchannel(0) if hasattr(mask, 'getchannel') else mask)

        draw = ImageDraw.Draw(img)

        # 底部装饰圆
        draw.ellipse([420, -60, 740, 260], fill=(255, 255, 255, 30))
        draw.ellipse([-80, 200, 200, 480], fill=(255, 255, 255, 20))

        # Emoji大图
        emoji = RECIPE_EMOJI.get(name, '🍽')
        try:
            emoji_font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 100)
            bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((480, (360 - th) // 2), emoji, font=emoji_font, embedded_color=True)
        except:
            pass

        # 菜名
        bbox = draw.textbbox((0, 0), name, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text((40, 120), name, fill=WHITE, font=title_font)

        # 副标题标签
        try:
            small_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 24)
        except:
            small_font = ImageFont.load_default()
        tag = f'· {cat} ·'
        draw.text((46, 185), tag, fill=(255, 255, 255, 180), font=small_font)

        # 分隔线
        draw.rectangle([40, 225, 120, 229], fill=(255, 255, 255, 100))

        fname = f'cover-{name}.png'
        img.save(os.path.join(OUT_DIR, fname))
        print(f'  ✓ {fname}')


def create_market_category_icons():
    """菜市分类图标 128x128"""
    size = 128
    cats = [
        ('蔬菜', '#34C759', '🥬'),
        ('肉类', '#FF3B30', '🥩'),
        ('水产', '#007AFF', '🐟'),
        ('蛋豆制品', '#FF9500', '🥚'),
        ('香料调料', '#FF3B30', '🌶'),
        ('粮油', '#FF9500', '🌾'),
        ('其他', GRAY, '📦'),
    ]
    try:
        emoji_font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 56)
    except:
        emoji_font = ImageFont.load_default()

    for name, color, emoji in cats:
        c = hex_to_rgb(color)
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        mask = create_rounded_rect_mask((size, size), 28)
        bg = Image.new('RGBA', (size, size), c + (255,))
        img.paste(bg, (0, 0), mask)

        inner = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        inner_draw = ImageDraw.Draw(inner)
        inner_draw.ellipse([28, 20, 100, 92], fill=(255, 255, 255, 230))
        inner_mask = create_rounded_rect_mask((size, size), 28)
        img.paste(inner, (0, 0), inner_mask)

        bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - tw) // 2, (size - th) // 2 - 2), emoji,
                 font=emoji_font, embedded_color=True)

        fname = f'mcat-{name}.png'
        img.save(os.path.join(OUT_DIR, fname))
        print(f'  ✓ {fname}')


def create_placeholder_icons():
    """其他占位图标"""
    size = 128
    icons = [
        ('icon-add', BLUE, '+', 80),
        ('icon-search', GRAY, '🔍', 50),
        ('icon-star', ORANGE, '★', 60),
        ('icon-lock', GRAY, '🔒', 50),
    ]
    try:
        emoji_font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 60)
    except:
        emoji_font = ImageFont.load_default()

    for fname, color, text, font_size in icons:
        c = hex_to_rgb(color)
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if text == '+':
            # 圆形＋按钮
            draw.ellipse([14, 14, 114, 114], fill=c)
            draw.rectangle([50, 38, 78, 90], fill=WHITE)
            draw.rectangle([38, 50, 90, 78], fill=WHITE)
        else:
            bbox = draw.textbbox((0, 0), text, font=emoji_font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((size - tw) // 2, (size - th) // 2), text,
                     font=emoji_font, embedded_color=True)

        img.save(os.path.join(OUT_DIR, fname + '.png'))
        print(f'  ✓ {fname}.png')


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    print('Generating icons...\n')

    create_tab_icons()
    create_category_icons()
    create_recipe_icons()
    create_recipe_covers()
    create_market_category_icons()
    create_placeholder_icons()

    count = len(os.listdir(OUT_DIR))
    print(f'\n✅ Done! {count} icons generated in {OUT_DIR}')
