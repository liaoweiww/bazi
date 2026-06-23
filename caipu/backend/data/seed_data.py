"""系统食材预设数据 (严格对照需求文档第五章)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import get_db

# 每个元组: (id, name, emoji, category1, category2, category3, unit, storage, shelf_life_days)
INGREDIENTS = [
    # ===== 5.1 畜禽肉类 =====
    # 畜肉-猪
    ("ing_pork_belly", "五花肉", "🥩", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    ("ing_pork_tender", "里脊肉", "🥩", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    ("ing_pork_lean", "瘦肉", "🥩", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    ("ing_pork_rib", "排骨", "🍖", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    ("ing_pork_trotter", "猪蹄", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    ("ing_pork_intestine", "猪大肠", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 2),
    ("ing_pork_ear", "猪耳朵", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    ("ing_pork_tongue", "猪舌头", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    ("ing_pork_heart", "猪心", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 2),
    ("ing_pork_liver", "猪肝", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 2),
    ("ing_pork_tripe", "猪肚", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 2),
    ("ing_pork_skin", "猪皮", "🐷", "畜禽肉类", "畜肉", "猪", "斤", "fridge", 3),
    # 畜肉-牛
    ("ing_beef_brisket", "牛腩", "🐮", "畜禽肉类", "畜肉", "牛", "斤", "fridge", 3),
    ("ing_beef_slice", "牛肉片", "🥩", "畜禽肉类", "畜肉", "牛", "斤", "fridge", 3),
    ("ing_beef_shank", "牛腱子", "🐮", "畜禽肉类", "畜肉", "牛", "斤", "fridge", 3),
    ("ing_beef_rib", "牛肋条", "🐮", "畜禽肉类", "畜肉", "牛", "斤", "fridge", 3),
    ("ing_beef_eye", "牛里脊", "🥩", "畜禽肉类", "畜肉", "牛", "斤", "fridge", 3),
    ("ing_beef_tongue", "牛舌", "🐮", "畜禽肉类", "畜肉", "牛", "斤", "fridge", 2),
    ("ing_beef_omasum", "牛百叶", "🐮", "畜禽肉类", "畜肉", "牛", "斤", "fridge", 2),
    # 畜肉-羊
    ("ing_lamb_slice", "羊肉卷", "🐑", "畜禽肉类", "畜肉", "羊", "斤", "freezer", 90),
    ("ing_lamb_rib", "羊排", "🐑", "畜禽肉类", "畜肉", "羊", "斤", "freezer", 90),
    ("ing_lamb_chunk", "羊肉块", "🐑", "畜禽肉类", "畜肉", "羊", "斤", "freezer", 90),
    ("ing_lamb_leg", "羊腿肉", "🐑", "畜禽肉类", "畜肉", "羊", "斤", "freezer", 90),
    ("ing_lamb_offal", "羊杂", "🐑", "畜禽肉类", "畜肉", "羊", "斤", "freezer", 60),
    # 禽肉-鸡
    ("ing_chicken_breast", "鸡胸肉", "🐔", "畜禽肉类", "禽肉", "鸡", "斤", "fridge", 2),
    ("ing_chicken_leg", "鸡腿", "🍗", "畜禽肉类", "禽肉", "鸡", "斤", "fridge", 2),
    ("ing_chicken_wing", "鸡翅", "🍗", "畜禽肉类", "禽肉", "鸡", "斤", "fridge", 2),
    ("ing_chicken_whole", "整鸡", "🐔", "畜禽肉类", "禽肉", "鸡", "斤", "fridge", 2),
    # 禽肉-鸭
    ("ing_duck", "鸭肉", "🦆", "畜禽肉类", "禽肉", "鸭", "斤", "fridge", 2),
    ("ing_duck_leg", "鸭腿", "🦆", "畜禽肉类", "禽肉", "鸭", "斤", "fridge", 2),
    ("ing_duck_wing", "鸭翅", "🦆", "畜禽肉类", "禽肉", "鸭", "斤", "fridge", 2),
    ("ing_duck_neck", "鸭脖", "🦆", "畜禽肉类", "禽肉", "鸭", "斤", "fridge", 2),
    # 禽肉-鹅
    ("ing_goose", "鹅肉", "🦢", "畜禽肉类", "禽肉", "鹅", "斤", "fridge", 2),
    # 禽肉-鸽
    ("ing_pigeon", "鸽子肉", "🐦", "畜禽肉类", "禽肉", "鸽", "斤", "fridge", 2),
    # 蛋类
    ("ing_egg", "鸡蛋", "🥚", "畜禽肉类", "蛋类", "鸡蛋", "个", "room", None),
    ("ing_duck_egg", "鸭蛋", "🥚", "畜禽肉类", "蛋类", "鸭蛋", "个", "room", None),
    ("ing_quail_egg", "鹌鹑蛋", "🥚", "畜禽肉类", "蛋类", "鹌鹑蛋", "个", "room", None),
    ("ing_salted_egg", "咸鸭蛋", "🥚", "畜禽肉类", "蛋类", "鸭蛋", "个", "room", None),
    ("ing_century_egg", "皮蛋", "🥚", "畜禽肉类", "蛋类", "皮蛋", "个", "room", None),

    # ===== 5.2 鲜蔬类 =====
    # 绿叶菜
    ("ing_spinach", "菠菜", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_lettuce_oil", "油麦菜", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_lettuce", "生菜", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_bokchoy", "上海青", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_water_spinach", "空心菜", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 2),
    ("ing_choi_sum", "菜心", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_kale_ch", "芥蓝", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_crown_daisy", "茼蒿", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 2),
    ("ing_baby_cabbage", "娃娃菜", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_amaranth", "苋菜", "🥬", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 2),
    ("ing_chive", "韭菜", "🌿", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 2),
    ("ing_cilantro", "香菜", "🌿", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_garlic_sprout", "蒜苗", "🌱", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    ("ing_garlic_scape", "蒜苔", "🌱", "鲜蔬类", "绿叶菜", "绿叶蔬菜", "斤", "fridge", 3),
    # 瓜茄
    ("ing_tomato", "西红柿", "🍅", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "room", None),
    ("ing_cucumber", "黄瓜", "🥒", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "fridge", 5),
    ("ing_wax_gourd", "冬瓜", "🎃", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "room", None),
    ("ing_pumpkin", "南瓜", "🎃", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "room", None),
    ("ing_luffa", "丝瓜", "🥒", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "fridge", 5),
    ("ing_bitter_gourd", "苦瓜", "🥒", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "fridge", 5),
    ("ing_eggplant", "茄子", "🍆", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "fridge", 5),
    ("ing_zucchini", "西葫芦", "🥒", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "fridge", 5),
    ("ing_baby_pumpkin", "贝贝南瓜", "🎃", "鲜蔬类", "瓜茄", "瓜茄果蔬", "斤", "room", None),
    # 根茎
    ("ing_potato", "土豆", "🥔", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "room", None),
    ("ing_carrot", "胡萝卜", "🥕", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "fridge", 7),
    ("ing_radish", "白萝卜", "🥕", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "fridge", 7),
    ("ing_yam", "山药", "🥔", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "room", None),
    ("ing_lotus_root", "莲藕", "🪷", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "fridge", 7),
    ("ing_taro", "芋头", "🥔", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "room", None),
    ("ing_celtuce", "莴笋", "🥬", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "fridge", 5),
    ("ing_ginger", "生姜", "🫚", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "room", None),
    ("ing_garlic", "大蒜", "🧄", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "room", None),
    ("ing_water_chestnut", "马蹄", "🥔", "鲜蔬类", "根茎", "根茎蔬菜", "斤", "room", None),
    # 菌菇
    ("ing_enoki", "金针菇", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "fridge", 5),
    ("ing_shiitake", "香菇", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "fridge", 5),
    ("ing_king_oyster", "杏鲍菇", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "fridge", 5),
    ("ing_oyster_mush", "平菇", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "fridge", 3),
    ("ing_wood_ear", "木耳", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "room", None),
    ("ing_beech_mush", "蟹味菇", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "fridge", 5),
    ("ing_white_beech", "白玉菇", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "fridge", 5),
    ("ing_tea_mush", "茶树菇", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "room", None),
    ("ing_bamboo_fungus", "竹荪", "🍄", "鲜蔬类", "菌菇", "菌菇杂蔬", "斤", "room", None),
    # 香辛
    ("ing_green_pepper", "青椒", "🫑", "鲜蔬类", "香辛", "香辛配菜", "斤", "fridge", 5),
    ("ing_red_pepper", "红椒", "🫑", "鲜蔬类", "香辛", "香辛配菜", "斤", "fridge", 5),
    ("ing_onion", "洋葱", "🧅", "鲜蔬类", "香辛", "香辛配菜", "斤", "room", None),
    ("ing_celery", "芹菜", "🥬", "鲜蔬类", "香辛", "香辛配菜", "斤", "fridge", 5),
    ("ing_broccoli", "西兰花", "🥦", "鲜蔬类", "香辛", "香辛配菜", "斤", "fridge", 5),
    ("ing_cauliflower", "花菜", "🥦", "鲜蔬类", "香辛", "香辛配菜", "斤", "fridge", 5),
    ("ing_green_onion", "小葱", "🌱", "鲜蔬类", "香辛", "香辛配菜", "斤", "fridge", 5),
    ("ing_leek_onion", "大葱", "🌱", "鲜蔬类", "香辛", "香辛配菜", "斤", "fridge", 7),

    # ===== 5.3 水产海鲜 =====
    # 淡水鱼
    ("ing_grass_carp", "草鱼", "🐟", "水产海鲜", "淡水鱼", "淡水鱼", "斤", "fridge", 2),
    ("ing_crucian_carp", "鲫鱼", "🐟", "水产海鲜", "淡水鱼", "淡水鱼", "斤", "fridge", 2),
    ("ing_bass", "鲈鱼", "🐟", "水产海鲜", "淡水鱼", "淡水鱼", "斤", "fridge", 2),
    ("ing_snakehead", "黑鱼", "🐟", "水产海鲜", "淡水鱼", "淡水鱼", "斤", "fridge", 2),
    ("ing_catfish", "鲶鱼", "🐟", "水产海鲜", "淡水鱼", "淡水鱼", "斤", "fridge", 2),
    ("ing_wuchang_bream", "武昌鱼", "🐟", "水产海鲜", "淡水鱼", "淡水鱼", "斤", "fridge", 2),
    ("ing_tilapia", "罗非鱼", "🐟", "水产海鲜", "淡水鱼", "淡水鱼", "斤", "fridge", 2),
    # 海鱼
    ("ing_hairtail", "带鱼", "🐟", "水产海鲜", "海鱼", "海鱼", "斤", "freezer", 60),
    ("ing_yellow_croaker", "黄花鱼", "🐟", "水产海鲜", "海鱼", "海鱼", "斤", "fridge", 2),
    ("ing_salmon", "三文鱼", "🍣", "水产海鲜", "海鱼", "海鱼", "斤", "fridge", 2),
    ("ing_basa", "巴沙鱼", "🐟", "水产海鲜", "海鱼", "海鱼", "斤", "freezer", 60),
    ("ing_cod", "鳕鱼", "🐟", "水产海鲜", "海鱼", "海鱼", "斤", "freezer", 60),
    ("ing_saury", "秋刀鱼", "🐟", "水产海鲜", "海鱼", "海鱼", "斤", "freezer", 60),
    # 虾蟹贝
    ("ing_shrimp", "基围虾", "🦐", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    ("ing_crayfish", "小龙虾", "🦞", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    ("ing_crab", "螃蟹", "🦀", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    ("ing_clam", "花甲", "🦪", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    ("ing_scallop", "扇贝", "🦪", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    ("ing_clams", "花蛤", "🦪", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    ("ing_razor_clam", "蛏子", "🦪", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    ("ing_oyster", "生蚝", "🦪", "水产海鲜", "虾蟹贝", "虾蟹贝类", "斤", "fridge", 2),
    # 其他水产
    ("ing_squid", "鱿鱼", "🦑", "水产海鲜", "其他水产", "其他水产", "斤", "freezer", 60),
    ("ing_cuttlefish", "墨鱼", "🦑", "水产海鲜", "其他水产", "其他水产", "斤", "freezer", 60),
    ("ing_sea_cucumber", "海参", "🪸", "水产海鲜", "其他水产", "其他水产", "斤", "freezer", 90),
    ("ing_jellyfish", "海蜇", "🪼", "水产海鲜", "其他水产", "其他水产", "斤", "fridge", 3),
    ("ing_dried_shrimp", "虾米", "🦐", "水产海鲜", "其他水产", "其他水产", "斤", "room", None),
    ("ing_dried_scallop", "干贝", "🦪", "水产海鲜", "其他水产", "其他水产", "斤", "room", None),

    # ===== 5.4 五谷干货 =====
    # 主食
    ("ing_rice", "大米", "🍚", "五谷干货", "主食", "主食谷物", "斤", "room", None),
    ("ing_millet", "小米", "🫘", "五谷干货", "主食", "主食谷物", "斤", "room", None),
    ("ing_glutinous_rice", "糯米", "🍚", "五谷干货", "主食", "主食谷物", "斤", "room", None),
    ("ing_corn", "玉米", "🌽", "五谷干货", "主食", "主食谷物", "斤", "room", None),
    ("ing_black_rice", "黑米", "🍚", "五谷干货", "主食", "主食谷物", "斤", "room", None),
    ("ing_brown_rice", "糙米", "🍚", "五谷干货", "主食", "主食谷物", "斤", "room", None),
    ("ing_oats", "燕麦", "🌾", "五谷干货", "主食", "主食谷物", "斤", "room", None),
    # 面食
    ("ing_noodle", "面条", "🍜", "五谷干货", "面食", "面食干货", "斤", "room", None),
    ("ing_dried_noodle", "挂面", "🍜", "五谷干货", "面食", "面食干货", "斤", "room", None),
    ("ing_vermicelli", "粉丝", "🫘", "五谷干货", "面食", "面食干货", "斤", "room", None),
    ("ing_wide_vermicelli", "粉条", "🫘", "五谷干货", "面食", "面食干货", "斤", "room", None),
    ("ing_instant_noodle", "方便面", "🍜", "五谷干货", "面食", "面食干货", "斤", "room", None),
    ("ing_rice_noodle", "河粉", "🍜", "五谷干货", "面食", "面食干货", "斤", "fridge", 2),
    ("ing_rice_vermicelli", "米粉", "🍜", "五谷干货", "面食", "面食干货", "斤", "room", None),
    # 豆类
    ("ing_soybean", "黄豆", "🫘", "五谷干货", "豆类", "豆类杂粮", "斤", "room", None),
    ("ing_mung_bean", "绿豆", "🫘", "五谷干货", "豆类", "豆类杂粮", "斤", "room", None),
    ("ing_red_bean", "红豆", "🫘", "五谷干货", "豆类", "豆类杂粮", "斤", "room", None),
    ("ing_black_bean", "黑豆", "🫘", "五谷干货", "豆类", "豆类杂粮", "斤", "room", None),
    ("ing_kidney_bean", "芸豆", "🫘", "五谷干货", "豆类", "豆类杂粮", "斤", "room", None),
    ("ing_chickpea", "鹰嘴豆", "🫘", "五谷干货", "豆类", "豆类杂粮", "斤", "room", None),
    # 干果
    ("ing_red_date", "红枣", "🫒", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_goji", "枸杞", "🔴", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_longan", "桂圆", "🫐", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_peanut", "花生", "🥜", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_sesame", "芝麻", "🫘", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_lotus_seed", "莲子", "🪷", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_lily_bulb", "百合", "🌺", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_walnut", "核桃", "🥜", "五谷干货", "干果", "干果干货", "斤", "room", None),
    ("ing_almond", "杏仁", "🥜", "五谷干货", "干果", "干果干货", "斤", "room", None),

    # ===== 5.5 调味佐料 =====
    # 基础调味
    ("ing_salt", "食盐", "🧂", "调味佐料", "基础调味", "基础调味", "斤", "room", None),
    ("ing_sugar", "白砂糖", "🍬", "调味佐料", "基础调味", "基础调味", "斤", "room", None),
    ("ing_msg", "味精", "🧂", "调味佐料", "基础调味", "基础调味", "斤", "room", None),
    ("ing_chicken_essence", "鸡精", "🧂", "调味佐料", "基础调味", "基础调味", "斤", "room", None),
    ("ing_rock_sugar", "冰糖", "🍬", "调味佐料", "基础调味", "基础调味", "斤", "room", None),
    ("ing_brown_sugar", "红糖", "🍬", "调味佐料", "基础调味", "基础调味", "斤", "room", None),
    # 酱汁
    ("ing_light_soy", "生抽", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_dark_soy", "老抽", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_oyster_sauce", "蚝油", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_vinegar", "陈醋", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_fragrant_vinegar", "香醋", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_cooking_wine", "料酒", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_ketchup", "番茄酱", "🥫", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_sweet_bean", "甜面酱", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_bean_paste", "豆瓣酱", "🫗", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    ("ing_chili_sauce", "辣椒酱", "🌶️", "调味佐料", "酱汁", "酱汁调味", "毫升", "room", None),
    # 香料
    ("ing_sichuan_pepper", "花椒", "🌶️", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_star_anise", "八角", "⭐", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_cinnamon", "桂皮", "🪵", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_bay_leaf", "香叶", "🌿", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_dried_chili", "干辣椒", "🌶️", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_cumin", "孜然", "🌿", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_fennel", "小茴香", "🌿", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_white_pepper", "白胡椒粉", "🧂", "调味佐料", "香料", "香料调味", "两", "room", None),
    ("ing_black_pepper", "黑胡椒粉", "🧂", "调味佐料", "香料", "香料调味", "两", "room", None),
    # 油脂
    ("ing_cooking_oil", "食用油", "🫒", "调味佐料", "油脂", "油脂类", "毫升", "room", None),
    ("ing_sesame_oil", "香油", "🫒", "调味佐料", "油脂", "油脂类", "毫升", "room", None),
    ("ing_chili_oil", "辣椒油", "🌶️", "调味佐料", "油脂", "油脂类", "毫升", "room", None),
    ("ing_sichuan_oil", "花椒油", "🌶️", "调味佐料", "油脂", "油脂类", "毫升", "room", None),
    ("ing_scallion_oil", "葱油", "🌿", "调味佐料", "油脂", "油脂类", "毫升", "room", None),
    ("ing_lard", "猪油", "🥩", "调味佐料", "油脂", "油脂类", "斤", "fridge", 30),
    ("ing_beef_tallow", "牛油", "🥩", "调味佐料", "油脂", "油脂类", "斤", "fridge", 30),

    # ===== 5.6 水果类 =====
    ("ing_apple", "苹果", "🍎", "水果类", "常见水果", "常见水果", "斤", "fridge", 14),
    ("ing_banana", "香蕉", "🍌", "水果类", "常见水果", "常见水果", "斤", "room", None),
    ("ing_orange", "橙子", "🍊", "水果类", "常见水果", "常见水果", "斤", "room", None),
    ("ing_tangerine", "橘子", "🍊", "水果类", "常见水果", "常见水果", "斤", "room", None),
    ("ing_grape", "葡萄", "🍇", "水果类", "常见水果", "常见水果", "斤", "fridge", 7),
    ("ing_strawberry", "草莓", "🍓", "水果类", "常见水果", "常见水果", "斤", "fridge", 3),
    ("ing_watermelon", "西瓜", "🍉", "水果类", "常见水果", "常见水果", "斤", "fridge", 7),
    ("ing_mango", "芒果", "🥭", "水果类", "常见水果", "常见水果", "斤", "room", None),
    ("ing_dragon_fruit", "火龙果", "🐉", "水果类", "常见水果", "常见水果", "斤", "room", None),
    ("ing_kiwi", "猕猴桃", "🥝", "水果类", "常见水果", "常见水果", "斤", "fridge", 7),
    ("ing_pear", "梨", "🍐", "水果类", "常见水果", "常见水果", "斤", "fridge", 14),
    ("ing_pineapple", "菠萝", "🍍", "水果类", "常见水果", "常见水果", "斤", "room", None),
    ("ing_cherry", "樱桃", "🍒", "水果类", "常见水果", "常见水果", "斤", "fridge", 5),
    ("ing_lychee", "荔枝", "🫐", "水果类", "常见水果", "常见水果", "斤", "fridge", 3),
    ("ing_longan_fruit", "龙眼", "🫐", "水果类", "常见水果", "常见水果", "斤", "fridge", 3),
]


def seed_ingredients():
    """灌入系统食材（幂等：已存在的跳过）"""
    with get_db() as conn:
        cur = conn.cursor()
        count = 0
        for ing in INGREDIENTS:
            cur.execute("SELECT id FROM ingredients WHERE id = %s", (ing[0],))
            if cur.fetchone():
                continue  # 已存在，跳过
            cur.execute(
                "INSERT INTO ingredients (id, name, emoji, category1, category2, category3, unit, storage, shelf_life_days, is_system) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)",
                ing
            )
            count += 1
        return count
