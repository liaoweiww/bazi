"""
扩展解读模块 - 年运/时运/破解法/把控指南/参考书籍
"""
from typing import Dict, List

# =============================================================================
# 参考书籍数据
# =============================================================================

REFERENCE_BOOKS = [
    {
        "id": "yijing",
        "title": "易经",
        "author": "伏羲、周文王、孔子等",
        "dynasty": "上古/周代",
        "category": "群经之首",
        "cover": "易",
        "intro": "《易经》又称《周易》，是中国最古老的经典之一，被誉为「群经之首，大道之源」。全书以六十四卦为核心，通过卦象、卦辞、爻辞揭示天地万物变化的规律。",
        "content": "《易经》的核心思想是「阴阳变化」，认为宇宙万物皆由阴阳两种力量相互作用而生。每一卦由六爻组成，通过爻的变动来模拟事物发展的阶段性变化。易有三义：简易、变易、不易。八字命理学中许多核心概念如阴阳五行、天干地支的生克制化，其思想根源都可追溯到《易经》。",
        "chapters": [
            {"name": "上经", "desc": "三十卦，始于乾卦，终于离卦，讲述天地万物创生之道"},
            {"name": "下经", "desc": "三十四卦，始于咸卦，终于未济卦，讲述人事变化之理"},
            {"name": "系辞传", "desc": "阐发易理的重要篇章，揭示八卦、六十四卦的哲学含义"},
            {"name": "说卦传", "desc": "详解八卦取象，万物类象的总纲"},
            {"name": "序卦传", "desc": "说明六十四卦排列顺序的内在逻辑"},
        ],
        "quotes": [
            "天行健，君子以自强不息。",
            "地势坤，君子以厚德载物。",
            "一阴一阳之谓道。",
            "易，穷则变，变则通，通则久。",
        ],
        "bazi_relevance": "八字命理学的阴阳五行、生克制化、旺相休囚等核心理论的哲学基础均来源于易经。理解易经有助于深入把握命理学的思维方式。",
        "reading_guide": "初学者建议从《系辞传》入手，再读六十四卦。重点体会'阴阳消长'和'物极必反'的思想，这对理解八字中的五行走势和流年变化非常关键。"
    },
    {
        "id": "qimendunjia",
        "title": "奇门遁甲",
        "author": "黄帝、风后、姜子牙、张良等",
        "dynasty": "上古/周汉",
        "category": "三式之首",
        "cover": "奇",
        "intro": "奇门遁甲是中国古代最高层次的预测学之一，与太乙神数、大六壬并称'三式'。它将天时、地利、人和三者结合，通过九宫八卦、八门九星来推测事物发展的吉凶趋势。",
        "content": "奇门遁甲以洛书九宫为框架，结合天盘（九星）、人盘（八门）、地盘（八卦）、神盘（八神）四层体系。'奇'指乙、丙、丁三奇，'门'指休、生、伤、杜、景、死、惊、开八门，'遁甲'指甲木隐遁于六仪之下。排盘需考虑时间、空间双重因素。",
        "chapters": [
            {"name": "烟波钓叟歌", "desc": "奇门遁甲的纲领性文献，以歌诀形式讲述核心法则"},
            {"name": "奇门法窍", "desc": "详细讲解排盘方法和各类格局判断"},
            {"name": "遁甲演义", "desc": "系统梳理奇门理论和应用技巧"},
            {"name": "奇门旨归", "desc": "汇集历代奇门精要，理论结合实例"},
        ],
        "quotes": [
            "八卦定吉凶，吉凶生大业。",
            "天时不如地利，地利不如人和。",
            "顺天时而动，应地利而行，得人和而成。",
        ],
        "bazi_relevance": "奇门遁甲与八字命理同源而异流，奇门更侧重时空选择。八字看命局好坏，奇门看时机吉凶，两者结合可在了解命局的基础上，帮助选择最佳的行动时机和方位。",
        "reading_guide": "入门先学九宫八卦基础，再掌握八门九星的含义。重点理解'主客'关系和'时令'变化。奇门的学习曲线较陡，建议在掌握八字基础后再深入。"
    },
    {
        "id": "qianliminggao",
        "title": "千里命稿",
        "author": "韦千里",
        "dynasty": "民国",
        "category": "命理经典",
        "cover": "命",
        "intro": "《千里命稿》是民国著名命理学家韦千里的代表作，以白话文写成，案例丰富详实，被誉为现代八字命理学的入门必读之作。韦千里（1911-1988），字千里，精通子平术。",
        "content": "本书最大特色是以现代语言阐述命理，打破古籍晦涩难懂的局限。书中收录了大量韦千里亲自批断的真实命例，每一例都详细分析了命局格局、喜用神、大运流年，并验证了实际人生。全书注重实战，强调'理、象、数'三者结合。",
        "chapters": [
            {"name": "基础篇", "desc": "天干地支、五行生克、十神定位等基础知识"},
            {"name": "格局篇", "desc": "普通格局和特殊格局的判定与应用"},
            {"name": "用神篇", "desc": "取用神的方法和技巧，强调中和为贵"},
            {"name": "岁运篇", "desc": "大运和流年的综合判断方法"},
            {"name": "实例篇", "desc": "大量真实命例，涵盖各阶层各行业"},
        ],
        "quotes": [
            "命理之要，在于中和。太过则折，不及则废。",
            "用神一字值千金，取用之道奥妙无穷。",
            "大运如潮水，流年似浪花，命局似舟船。",
        ],
        "bazi_relevance": "《千里命稿》是连接古籍理论与现代应用的桥梁。韦千里以通俗易懂的文字讲解八字精髓，特别适合有一定基础后想要提升实战水平的学者。书中对用神的论述尤为精到。",
        "reading_guide": "适合已有基础知识的学习者。重点阅读'用神篇'和'实例篇'，体会韦千里如何在实际判断中灵活运用理论。配合排盘软件对照学习效果更佳。"
    },
]

# =============================================================================
# 破解法（化解方法）
# =============================================================================

REMEDY_DATA = {
    "五行缺失": {
        "缺金": {
            "description": "八字中金元素不足，可能表现为决断力不足、缺乏原则性、呼吸系统偏弱。",
            "remedies": [
                {"method": "色彩补益", "detail": "多穿白色、银色、金色的衣物饰品", "level": "日用"},
                {"method": "方位趋吉", "detail": "居住或工作在西方，床头朝西", "level": "环境"},
                {"method": "佩戴饰品", "detail": "佩戴金银饰品、白水晶、月光石", "level": "随身"},
                {"method": "职业选择", "detail": "从事金融、珠宝、机械、法律等属金行业", "level": "事业"},
                {"method": "饮食调理", "detail": "多食白色食物，如白萝卜、百合、银耳、梨", "level": "饮食"},
                {"method": "姓名补充", "detail": "名字中加入带金、白、西等偏旁的字", "level": "长期"},
            ]
        },
        "缺木": {
            "description": "八字中木元素不足，可能表现为魄力不足、缺乏仁爱之心、肝胆功能偏弱。",
            "remedies": [
                {"method": "色彩补益", "detail": "多穿绿色、青色的衣物", "level": "日用"},
                {"method": "方位趋吉", "detail": "居住或工作在东方，床头朝东", "level": "环境"},
                {"method": "植物养护", "detail": "在家中多养绿色植物，特别是兔脚蕨、文竹等木属性植物", "level": "环境"},
                {"method": "佩戴饰品", "detail": "佩戴绿松石、翡翠、祖母绿等绿色宝石", "level": "随身"},
                {"method": "职业选择", "detail": "从事教育、文化、林业、园艺、医药等属木行业", "level": "事业"},
                {"method": "姓名补充", "detail": "名字中加入带木、东、青等偏旁的字", "level": "长期"},
            ]
        },
        "缺水": {
            "description": "八字中水元素不足，可能表现为智慧不足、沟通不畅、肾气偏弱。",
            "remedies": [
                {"method": "色彩补益", "detail": "多穿黑色、深蓝色的衣物", "level": "日用"},
                {"method": "方位趋吉", "detail": "居住或工作在北方，床头朝北", "level": "环境"},
                {"method": "水景布置", "detail": "家中放置鱼缸或水景摆件，但需注意摆放位置", "level": "环境"},
                {"method": "佩戴饰品", "detail": "佩戴黑曜石、海蓝宝、黑玛瑙", "level": "随身"},
                {"method": "职业选择", "detail": "从事物流、贸易、旅游、传媒、渔业等属水行业", "level": "事业"},
                {"method": "姓名补充", "detail": "名字中加入带水、北、黑等偏旁的字", "level": "长期"},
            ]
        },
        "缺火": {
            "description": "八字中火元素不足，可能表现为热情不足、行动力弱、心血管功能偏弱。",
            "remedies": [
                {"method": "色彩补益", "detail": "多穿红色、紫色、橙色的衣物", "level": "日用"},
                {"method": "方位趋吉", "detail": "居住或工作在南方，床头朝南", "level": "环境"},
                {"method": "光线调理", "detail": "保持居室明亮，多晒太阳，避免阴冷潮湿", "level": "环境"},
                {"method": "佩戴饰品", "detail": "佩戴红玛瑙、石榴石、紫水晶", "level": "随身"},
                {"method": "职业选择", "detail": "从事餐饮、能源、演艺、互联网、美容等属火行业", "level": "事业"},
                {"method": "姓名补充", "detail": "名字中加入带火、南、红等偏旁的字", "level": "长期"},
            ]
        },
        "缺土": {
            "description": "八字中土元素不足，可能表现为诚信不足、缺乏稳定性、脾胃功能偏弱。",
            "remedies": [
                {"method": "色彩补益", "detail": "多穿黄色、棕色、咖啡色的衣物", "level": "日用"},
                {"method": "方位趋吉", "detail": "居住或工作在中部或本地发展", "level": "环境"},
                {"method": "陶瓷点缀", "detail": "家中摆放陶瓷器皿、紫砂壶、奇石摆件", "level": "环境"},
                {"method": "佩戴饰品", "detail": "佩戴黄水晶、蜜蜡、黄玉", "level": "随身"},
                {"method": "职业选择", "detail": "从事地产、建筑、农业、仓储、陶瓷等属土行业", "level": "事业"},
                {"method": "姓名补充", "detail": "名字中加入带土、田、山等偏旁的字", "level": "长期"},
            ]
        },
    },
    "五行过旺": {
        "金过旺": {"description": "金过旺性格刚硬，易冲动决断，需以水泄金气、以火克金。", "remedies": ["多接触水元素（游泳、养鱼）", "保持心态柔软，多听他人意见", "避免过度饮酒伤肝"]},
        "木过旺": {"description": "木过旺固执己见，肝功能需注意，需以火泄木气、以金克木。", "remedies": ["多运动出汗泄木气", "学会变通，不要太固执", "适当食用辛辣食物"]},
        "水过旺": {"description": "水过旺情绪起伏大，肾气需注意，需以木泄水气、以土克水。", "remedies": ["培养兴趣爱好", "坚持运动，避免久坐", "多接地气，赤脚行走"]},
        "火过旺": {"description": "火过旺急躁冲动，心脏需注意，需以土泄火气、以水克火。", "remedies": ["多做静态活动（书法、围棋）", "避免过度刺激", "多吃清淡食物"]},
        "土过旺": {"description": "土过旺保守固执，脾胃需注意，需以金泄土气、以木克土。", "remedies": ["多尝试新事物", "增加社交活动", "适当节食，避免暴饮暴食"]},
    },
    "日常通用化解": [
        {"title": "积德行善", "content": "多做善事积累福报，如捐款助学、义务劳动、尊老爱幼。善行能改善气场，化解厄运。"},
        {"title": "读书明理", "content": "通过读书提升认知，了解事物规律。知命而不认命，明理而后改运。"},
        {"title": "择友而交", "content": "结交贵人，远离小人。与正能量的朋友相处，互相成就。"},
        {"title": "修身养性", "content": "培养高尚品德，待人宽厚，处世谦和。德行是最根本的改运之道。"},
        {"title": "风水调理", "content": "保持家居整洁明亮，通风透气。好的环境磁场能助旺运势。"},
        {"title": "择时而动", "content": "重要决策避开忌神年月，选择喜用神当旺之时。时机好，事半功倍。"},
    ]
}

# =============================================================================
# 如何把控（人生把控指南）
# =============================================================================

CONTROL_GUIDE = {
    "overview": "命理学的根本目的不是宿命论，而是知命用命。了解自己的命局特点后，就能更好地把控人生方向，顺势而为。",
    "sections": [
        {
            "title": "认识自我",
            "icon": "知",
            "content": "八字命盘就像人生的说明书。了解自己的日主五行、身强身弱、格局特点、喜用神忌神，是把控人生的第一步。知道自己适合什么，不适合什么，才能在关键选择上不迷失方向。",
            "tips": ["了解自己日主的特点，发挥先天优势", "明确喜用神对应的行业和方向", "正视忌神带来的挑战，提前防范"]
        },
        {
            "title": "顺势而为",
            "icon": "顺",
            "content": "大运每十年一变，流年每年一转。好的大运要积极进取，把握良机；不利的大运要韬光养晦，积蓄力量。与天地同频，方能事半功倍。",
            "tips": ["走喜用神大运时大胆发展事业", "走忌神大运时守成为主，多学习充电", "流年遇上冲合日柱之年的，重大决策需谨慎"]
        },
        {
            "title": "补益之道",
            "icon": "补",
            "content": "命局中不足的五行，可以通过色彩、方位、职业、饮食等多方面进行补充。缺金补金，缺木植木，但需注意适度，不可过度补益破坏原有的平衡。",
            "tips": ["通过衣食住行全方位补充缺失五行", "选择喜用神对应的行业", "与八字互补的人合作共事"]
        },
        {
            "title": "修身养性",
            "icon": "修",
            "content": "命好不如运好，运好不如心好。再好的八字，如果心术不正、行为不端，也难以善终。反之，八字虽差但积善成德之人，也能逢凶化吉，转危为安。",
            "tips": ["保持良好的心态，知足常乐", "积德行善，改善气场", "持续学习提升，改变认知层次"]
        },
        {
            "title": "婚姻经营",
            "icon": "婚",
            "content": "八字中日柱代表本人和配偶，日支为婚姻宫。日支逢冲、逢害的年份需注意感情波动。了解双方八字的生克关系，可以更好地理解和包容对方。",
            "tips": ["多关注对方的优点，少挑剔缺点", "日支逢冲之年多沟通少争执", "选择与命局互补的对象婚姻更稳定"]
        },
        {
            "title": "事业发展",
            "icon": "业",
            "content": "正官、七杀看事业官运，正财偏财看财富财运。正官旺者适合体制内发展，七杀旺者适合创业打拼，食伤旺者可走技术或艺术路线。",
            "tips": ["选择与喜用神五行相符的行业", "印旺适合文职，比劫旺适合创业", "财星旺者宜经商，官星旺者宜从政"]
        },
        {
            "title": "健康管理",
            "icon": "康",
            "content": "五行对应五脏：木主肝、火主心、土主脾、金主肺、水主肾。命局中偏弱的五行对应的脏腑需要特别关注。大运流年克耗相应五行时，更要注意保养。",
            "tips": ["缺金者注意呼吸系统保健", "缺木者注意肝胆养护", "缺水者注意肾脏和泌尿系统", "缺火者注意心血管保健", "缺土者注意脾胃调理"]
        },
    ]
}

# =============================================================================
# 年运解读
# =============================================================================

def generate_year_fortune(paipan_result: Dict, target_year: int = None) -> Dict:
    """
    生成年运分析。

    参数:
        paipan_result: 排盘结果
        target_year: 目标年份（默认当前年）
    """
    from datetime import datetime, date
    if target_year is None:
        target_year = datetime.now().year

    day_master = paipan_result.get('day_master', '')
    dm_wx = paipan_result.get('day_master_wuxing', '')
    four_pillars = paipan_result.get('four_pillars', {})
    strength = paipan_result.get('strength', {})
    yongji = paipan_result.get('yongji', {})
    dayun = paipan_result.get('dayun', {})
    birth_info = paipan_result.get('birth_info', {})

    # 流年干支计算
    GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
    ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
    GAN_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

    year_gan = GAN[(target_year - 4) % 10]
    year_zhi = ZHI[(target_year - 4) % 12]
    year_ganzhi = year_gan + year_zhi
    year_wx = GAN_WX[year_gan]

    # 十神计算
    def get_shishen(ri_gan, other_gan):
        ri_wx = GAN_WX[ri_gan]; ot_wx = GAN_WX[other_gan]
        yinyang = ['阳','阴','阳','阴','阳','阴','阳','阴','阳','阴']
        same_yy = yinyang[GAN.index(ri_gan)] == yinyang[GAN.index(other_gan)]
        wx_sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
        wx_ke = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
        if ri_wx == ot_wx: return '比肩' if same_yy else '劫财'
        if wx_sheng.get(ri_wx) == ot_wx: return '食神' if same_yy else '伤官'
        if wx_ke.get(ri_wx) == ot_wx: return '偏财' if same_yy else '正财'
        if wx_sheng.get(ot_wx) == ri_wx: return '偏印' if same_yy else '正印'
        if wx_ke.get(ot_wx) == ri_wx: return '七杀' if same_yy else '正官'
        return '未知'

    shishen = get_shishen(day_master, year_gan)

    # 流年与各柱关系
    ZHI_LIUCHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}
    ZHI_LIUHE = {('子','丑'):'土',('丑','子'):'土',('寅','亥'):'木',('亥','寅'):'木',
                 ('卯','戌'):'火',('戌','卯'):'火',('辰','酉'):'金',('酉','辰'):'金',
                 ('巳','申'):'水',('申','巳'):'水',('午','未'):'土',('未','午'):'土'}
    ZHI_LIUHAI = {'子':'未','未':'子','丑':'午','午':'丑','寅':'巳','巳':'寅',
                  '卯':'辰','辰':'卯','申':'亥','亥':'申','酉':'戌','戌':'酉'}

    relations = []
    good_signals = []
    bad_signals = []

    for pk, pname in [('year','年柱'),('month','月柱'),('day','日柱'),('hour','时柱')]:
        pzhi = four_pillars[pk]['zhi']
        if year_zhi == pzhi:
            relations.append(f'流年地支{pzhi}与{pname}地支相同（伏吟），该柱相关事务变动较大')
            bad_signals.append(f'{pname}伏吟')
        elif ZHI_LIUCHONG.get(year_zhi) == pzhi:
            relations.append(f'流年地支{pzhi}冲{pname}地支{pzhi}（六冲），变动剧烈')
            bad_signals.append(f'{pname}逢冲')
        elif ZHI_LIUHE.get((year_zhi, pzhi)):
            hua = ZHI_LIUHE[(year_zhi, pzhi)]
            relations.append(f'流年地支{pzhi}合{pname}地支{pzhi}，化{hua}（六合），有合作机缘')
            good_signals.append(f'{pname}逢合')
        elif ZHI_LIUHAI.get(year_zhi) == pzhi:
            relations.append(f'流年地支{pzhi}害{pname}地支{pzhi}（六害），需防小人和口舌')
            bad_signals.append(f'{pname}逢害')

    # 判断是喜用还是忌
    yong_wx = [y['wuxing'] for y in yongji.get('yong_shen', [])]
    ji_wx = [j['wuxing'] for j in yongji.get('ji_shen', [])]

    is_yong = year_wx in yong_wx
    is_ji = year_wx in ji_wx

    # 大运背景
    current_dayun = dayun.get('current_dayun', {})
    dy_ganzhi = current_dayun.get('ganzhi', '') if current_dayun else ''

    # 总体评价
    if is_yong and good_signals:
        overall = f'{target_year}年({year_ganzhi}年)对您总体有利。流年五行{year_wx}为喜用，且{";".join(good_signals)}。这是积极进取的一年，适合开拓新事业、结交贵人、学习提升。'
        rating = '大吉'
    elif is_ji and bad_signals:
        overall = f'{target_year}年({year_ganzhi}年)需谨慎对待。流年五行{year_wx}为忌神，且{";".join(bad_signals)}。建议以守成为主，避免重大变动和冒险投资。'
        rating = '欠佳'
    elif is_yong:
        overall = f'{target_year}年({year_ganzhi}年)运势向好。流年五行{year_wx}为喜用，整体趋势向上，适合稳步发展。'
        rating = '小吉'
    elif is_ji:
        overall = f'{target_year}年({year_ganzhi}年)注意调节。流年五行{year_wx}为忌神，需多加留意，以稳为主。'
        rating = '平平'
    else:
        overall = f'{target_year}年({year_ganzhi}年)中平之年。流年五行{year_wx}中性，既无明显助力也无大的冲克。宜按部就班，踏实前进。'
        rating = '中平'

    # 逐月建议
    monthly = _generate_monthly_tips(year_zhi, year_wx, is_yong)

    # 当前大运背景
    dy_text = ''
    if dy_ganzhi:
        dy_text = f'您目前正处于{dy_ganzhi}大运（{current_dayun.get("age_range","")}岁），'
        if current_dayun.get('gan_wuxing') in yong_wx:
            dy_text += '此大运对您有利，是人生较好的十年阶段。在此期间，每年的流年变化都建立在有利的大运背景之上。'
        elif current_dayun.get('gan_wuxing') in ji_wx:
            dy_text += '此大运对您有所考验，但这十年也是磨练心性、积蓄力量的重要阶段。以稳为主，待时而动。'
        else:
            dy_text += '此大运中平，需结合每年流年具体分析。'

    return {
        "year": target_year,
        "ganzhi": year_ganzhi,
        "gan": year_gan,
        "zhi": year_zhi,
        "wuxing": year_wx,
        "shishen": shishen,
        "rating": rating,
        "overall": overall,
        "relations": relations,
        "is_yong": is_yong,
        "is_ji": is_ji,
        "dayun_background": dy_text,
        "monthly_tips": monthly,
        "advice": _generate_year_advice(is_yong, is_ji, shishen, year_wx, yong_wx)
    }


def _generate_monthly_tips(year_zhi: str, year_wx: str, is_yong: bool) -> List[Dict]:
    """生成逐月建议"""
    ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
    ZHI_WX = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
              '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
    WX_SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    WX_KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
    MONTH_NAMES = ['正月(寅)','二月(卯)','三月(辰)','四月(巳)','五月(午)','六月(未)',
                   '七月(申)','八月(酉)','九月(戌)','十月(亥)','冬月(子)','腊月(丑)']

    tips = []
    for i, zhi in enumerate(ZHI):
        m_wx = ZHI_WX[zhi]
        good = False
        if m_wx == year_wx or WX_SHENG.get(m_wx) == year_wx:
            good = True
        if WX_KE.get(m_wx) == year_wx:
            good = False

        if is_yong:
            if good:
                tip = f'此月{year_wx}气旺盛，运势较好，适合积极开展活动。'
            else:
                tip = f'此月能量转换，速度放慢，适合总结复盘。'
        else:
            if good:
                tip = f'此月{year_wx}气稍弱，压力减轻，可趁机调整。'
            else:
                tip = f'此月{year_wx}气较重，需多加注意，避免冲动决策。'

        tips.append({"month": MONTH_NAMES[i], "zhi": zhi, "wuxing": m_wx, "tip": tip})

    return tips


def _generate_year_advice(is_yong: bool, is_ji: bool, shishen: str, year_wx: str, yong_wx: List[str]) -> str:
    """生成年运建议"""
    advice_parts = []

    if is_yong:
        advice_parts.append(f'今年流年{year_wx}为您的喜用神，能量正旺。')
        advice_parts.append('建议把握时机，在事业、学习、人际关系上积极进取。')
        if shishen in ('正财','偏财'):
            advice_parts.append('今年财运较旺，投资理财可适当积极，但仍需理性决策。')
        elif shishen in ('正官','七杀'):
            advice_parts.append('今年事业运旺，适合争取晋升、项目推进，但需注意工作与休息平衡。')
        elif shishen in ('正印','偏印'):
            advice_parts.append('今年学习运旺，适合深造进修、考取证书、开拓知识领域。')
    else:
        advice_parts.append(f'今年流年{year_wx}非您喜用，需以稳为主。')
        advice_parts.append('建议多做积累少做冒险，注意身体健康和情绪管理。')
        if yong_wx:
            advice_parts.append(f'可多接触{"、".join(yong_wx)}属性的事物来平衡运势。')

    return ''.join(advice_parts)


# =============================================================================
# 时运解读 (基于当前大运+流年)
# =============================================================================

def generate_current_fortune(paipan_result: Dict) -> Dict:
    """生成当前时运分析（当前所处的运势阶段）"""
    from datetime import datetime, date as date_cls

    day_master = paipan_result.get('day_master', '')
    strength = paipan_result.get('strength', {})
    yongji = paipan_result.get('yongji', {})
    dayun = paipan_result.get('dayun', {})
    birth_info = paipan_result.get('birth_info', {})
    four_pillars = paipan_result.get('four_pillars', {})

    current_dayun = dayun.get('current_dayun', {})
    liunian = dayun.get('liunian_current', {})
    start_age = dayun.get('start_age', 0)

    # 计算当前年龄
    solar_str = birth_info.get('solar_date', '')
    today_val = date_cls.today()
    try:
        birth_date = datetime.strptime(solar_str, '%Y-%m-%d').date()
        current_age = today_val.year - birth_date.year - ((today_val.month, today_val.day) < (birth_date.month, birth_date.day))
    except:
        current_age = 30

    # 当前所在大运
    dy_ganzhi = current_dayun.get('ganzhi', '')
    dy_wx = current_dayun.get('gan_wuxing', '')

    yong_wx = [y['wuxing'] for y in yongji.get('yong_shen', [])]
    ji_wx = [j['wuxing'] for j in yongji.get('ji_shen', [])]

    # 大运评价
    if dy_wx in yong_wx:
        dy_eval = f'当前{dy_ganzhi}大运为喜用神大运，这十年整体运势向好，是人生发展的好时期。'
        dy_tag = '好运'
    elif dy_wx in ji_wx:
        dy_eval = f'当前{dy_ganzhi}大运为忌神大运，这十年需以稳为主，重在积累和沉淀。'
        dy_tag = '考验期'
    else:
        dy_eval = f'当前{dy_ganzhi}大运中平，需结合具体流年分析，有起有伏。'
        dy_tag = '平稳期'

    # 流年评价
    ln_ganzhi = liunian.get('ganzhi', '')
    ln_analysis = liunian.get('analysis', '')

    # 综合判断
    today_str = today_val.strftime('%Y-%m-%d')
    this_year = today_val.year

    # 当前阶段建议
    stage_results = _analyze_current_stage(four_pillars, current_dayun, liunian, strength, yongji)

    return {
        "current_date": today_str,
        "current_age": current_age,
        "dayun": {
            "ganzhi": dy_ganzhi,
            "evaluation": dy_eval,
            "tag": dy_tag,
            "age_range": current_dayun.get('age_range', ''),
            "remaining_years": max(0, int(current_dayun.get('start_age', 0) + 10 - current_age)) if current_dayun else 0
        },
        "liunian": {
            "ganzhi": ln_ganzhi,
            "year": this_year,
            "analysis": ln_analysis
        },
        "stage_analysis": stage_results,
        "overall_advice": _generate_current_advice(dy_tag, day_master, yong_wx, ji_wx)
    }


def _analyze_current_stage(pillars: Dict, dayun: Dict, liunian: Dict, strength: Dict, yongji: Dict) -> str:
    """分析当前运势阶段"""
    stage = ""
    sl = strength.get('level', '中和')

    if dayun.get('ganzhi'):
        stage += f'您目前正处于{dayun["ganzhi"]}大运阶段，'
        if '强' in sl:
            stage += '身强能担大任，'
        elif '弱' in sl:
            stage += '身弱需借外力，'
        else:
            stage += '身中和能进能退，'

    if liunian.get('analysis'):
        if '平稳' in liunian.get('analysis', ''):
            stage += '当前流年平稳，适合按部就班、稳扎稳打。'
        elif '冲' in liunian.get('analysis', '') or '刑' in liunian.get('analysis', ''):
            stage += '当前流年变动较大，宜多观察、少做重大决策，保持灵活性。'
        elif '合' in liunian.get('analysis', ''):
            stage += '当前流年有合作机缘，宜积极社交、拓展人脉。'
        else:
            stage += '需结合大运和流年综合判断，顺势而为。'
    else:
        stage += '流年较为平稳，适合脚踏实地做好当下的事情。'

    return stage


def _generate_current_advice(dy_tag: str, day_master: str, yong_wx: List[str], ji_wx: List[str]) -> str:
    """生成当前建议"""
    if dy_tag == '好运':
        advice = '当前是运势较好的阶段，建议抓住时机积极发展。在事业上可以大胆争取，在人际关系上多结交贵人。'
        advice += '但切记好运也有期限，要趁势而上，为将来做好准备。'
    elif dy_tag == '考验期':
        advice = '当前处于运势的考验期，这是磨练心性、提升能力的关键阶段。以守为主，韬光养晦。'
        advice += '多学习、多积累，为下一个人生高峰做准备。遇到困难时保持定力，静待时机。'
    else:
        advice = '当前运势中平，稳定是主基调。做好本职工作，踏踏实实积累。'
        advice += '可在小事上尝试新的方向，为将来做铺垫。'

    if yong_wx:
        advice += f'建议多接触{"、".join(yong_wx)}相关的事物来增强运势。'

    return advice


# =============================================================================
# 破解法生成
# =============================================================================

def generate_remedy(paipan_result: Dict) -> Dict:
    """根据命盘生成个性化的破解方法"""
    wuxing_count = paipan_result.get('wuxing_count', {})
    strength = paipan_result.get('strength', {})
    yongji = paipan_result.get('yongji', {})

    missing = []
    excessive = []

    for wx, info in wuxing_count.items():
        if isinstance(info, dict):
            score = info.get('score', 0)
            if score == 0:
                missing.append(wx)
            elif score >= 3.5:
                excessive.append(wx)

    remedies = []

    # 根据缺失五行推荐
    wx_to_key = {'金':'缺金','木':'缺木','水':'缺水','火':'缺火','土':'缺土'}
    for wx in missing:
        key = wx_to_key.get(wx)
        if key and key in REMEDY_DATA['五行缺失']:
            remedies.append({
                "type": "五行补益",
                "target": f"补{wx}",
                "description": REMEDY_DATA['五行缺失'][key]['description'],
                "methods": REMEDY_DATA['五行缺失'][key]['remedies']
            })

    # 根据五行过旺推荐
    wx_over = {'金':'金过旺','木':'木过旺','水':'水过旺','火':'火过旺','土':'土过旺'}
    for wx in excessive:
        key = wx_over.get(wx)
        if key and key in REMEDY_DATA['五行过旺']:
            remedies.append({
                "type": "五行制化",
                "target": f"泄{wx}",
                "description": REMEDY_DATA['五行过旺'][key]['description'],
                "methods": [{"method": r, "detail": "", "level": "建议"} for r in REMEDY_DATA['五行过旺'][key]['remedies']]
            })

    # 通用化解建议
    general = REMEDY_DATA['日常通用化解']

    # 喜用神针对性建议
    yong_shen = yongji.get('yong_shen', [])
    personalized = []
    if yong_shen:
        personalized.append(f'您的喜用神为{"、".join(f"{y["wuxing"]}({y.get("shishen","")})" for y in yong_shen)}')
        personalized.append('补益方法应以增强喜用神五行为主，化解忌神五行的不利影响。')
        personalized.append('选择与喜用神五行相符的职业、方位、颜色，能有效提升运势。')

    return {
        "missing_elements": missing,
        "excessive_elements": excessive,
        "remedies": remedies,
        "general_remedies": general,
        "personalized": personalized,
        "summary": "以上化解方法均为传统文化中的辅助手段，核心还是在于自身修德、明理、进取。命好不如心好，运好不如德好。"
    }
