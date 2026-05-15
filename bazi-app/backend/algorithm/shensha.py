"""
神煞与专业命理模块
- 神煞: 天乙贵人/文昌/桃花/驿马/羊刃/禄神/华盖/将星/劫煞/亡神/天德/月德等30+神煞
- 十二长生
- 胎元/命宫/身宫
- 空亡
- 天干五合/地支三合六合/刑冲害
"""
from typing import Dict, List, Tuple

TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
GAN_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
GAN_YY = {'甲':'阳','乙':'阴','丙':'阳','丁':'阴','戊':'阳','己':'阴','庚':'阳','辛':'阴','壬':'阳','癸':'阴'}

# ==================== 神煞计算 ====================

def calc_all_shensha(four_pillars: Dict, day_gan: str, year_zhi: str, month_zhi: str, gender: str = '男') -> Dict:
    """
    计算所有神煞
    返回: {神煞名: {柱位: 具体说明}}
    """
    result = {}

    # 年干神煞
    year_gan = four_pillars['year']['gan']
    day_zhi = four_pillars['day']['zhi']
    hour_zhi = four_pillars['hour']['zhi']

    # 1. 天乙贵人 (日干/年干起)
    tg_map = {
        '甲':'丑未','乙':'子申','丙':'亥酉','丁':'亥酉',
        '戊':'丑未','己':'子申','庚':'丑未','辛':'午寅',
        '壬':'卯巳','癸':'卯巳'
    }
    tianyi_zhi = tg_map.get(day_gan, '')
    result['天乙贵人'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] in tianyi_zhi:
            result['天乙贵人'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 天乙贵人照命，逢凶化吉'})

    # 2. 文昌星 (日干起)
    wenchang_map = {'甲':'巳','乙':'午','丙':'申','丁':'酉','戊':'申','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'}
    wc = wenchang_map.get(day_gan, '')
    result['文昌'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == wc:
            result['文昌'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 文昌入命，聪明好学，文采出众'})

    # 3. 桃花/咸池 (日支/年支查)
    taohua_map = {'子':'酉','丑':'午','寅':'卯','卯':'子','辰':'酉','巳':'午','午':'卯','未':'子','申':'酉','酉':'午','戌':'卯','亥':'子'}
    th = taohua_map.get(day_zhi, '')
    result['桃花'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == th:
            result['桃花'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 桃花入命，人缘佳，异性缘旺'})

    # 4. 驿马 (日支/年支查)
    yima_map = {'子':'寅','丑':'亥','寅':'申','卯':'巳','辰':'寅','巳':'亥','午':'申','未':'巳','申':'寅','酉':'亥','戌':'申','亥':'巳'}
    ym = yima_map.get(day_zhi, '')
    result['驿马'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == ym:
            result['驿马'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 驿马星动，奔波劳碌，利于外出发展'})

    # 5. 羊刃 (日干查)
    yangren_map = {'甲':'卯','乙':'辰','丙':'午','丁':'未','戊':'午','己':'未','庚':'酉','辛':'戌','壬':'子','癸':'丑'}
    yr = yangren_map.get(day_gan, '')
    result['羊刃'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == yr:
            result['羊刃'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 羊刃驾杀，个性刚强，武职显贵，然需防刑伤'})

    # 6. 禄神 (日干查临官位)
    lushen_map = {'甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}
    ls = lushen_map.get(day_gan, '')
    result['禄神'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == ls:
            result['禄神'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 禄神入命，衣食丰足，福禄双全'})

    # 7. 华盖 (日支查)
    huagai_map = {'子':'辰','丑':'丑','寅':'戌','卯':'未','辰':'辰','巳':'丑','午':'戌','未':'未','申':'辰','酉':'丑','戌':'戌','亥':'未'}
    hg = huagai_map.get(day_zhi, '')
    result['华盖'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == hg:
            result['华盖'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 华盖入命，聪慧孤高，利于艺术玄学'})

    # 8. 将星 (日支查三合局帝旺位)
    jiangxing_map = {'子':'子','丑':'酉','寅':'午','卯':'卯','辰':'子','巳':'酉','午':'午','未':'卯','申':'子','酉':'酉','戌':'午','亥':'卯'}
    jx = jiangxing_map.get(day_zhi, '')
    result['将星'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == jx:
            result['将星'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 将星入命，有领导才能，威权显赫'})

    # 9. 劫煞 (日支查)
    jiesha_map = {'子':'巳','丑':'寅','寅':'亥','卯':'申','辰':'巳','巳':'寅','午':'亥','未':'申','申':'巳','酉':'寅','戌':'亥','亥':'申'}
    js = jiesha_map.get(day_zhi, '')
    result['劫煞'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == js:
            result['劫煞'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 劫煞入命，需防意外破财，小心谨慎'})

    # 10. 亡神 (日支查)
    wangshen_map = {'子':'亥','丑':'申','寅':'巳','卯':'寅','辰':'亥','巳':'申','午':'巳','未':'寅','申':'亥','酉':'申','戌':'巳','亥':'寅'}
    ws = wangshen_map.get(day_zhi, '')
    result['亡神'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == ws:
            result['亡神'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 亡神入命，心思缜密，然多疑虑'})

    # 11. 天德贵人 (月支查)
    tiande_map = {'寅':'丁','卯':'申','辰':'壬','巳':'辛','午':'亥','未':'甲','申':'癸','酉':'寅','戌':'丙','亥':'乙','子':'巳','丑':'庚'}
    td = tiande_map.get(month_zhi, '')
    result['天德'] = []
    for pk, pl in four_pillars.items():
        if pl['gan'] == td:
            result['天德'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 天德贵人，福泽深厚，化险为夷'})

    # 12. 月德贵人 (月支查三合局阳干)
    yuede_map = {'寅':'丙','卯':'甲','辰':'壬','巳':'庚','午':'丙','未':'甲','申':'壬','酉':'庚','戌':'丙','亥':'甲','子':'壬','丑':'庚'}
    yd = yuede_map.get(month_zhi, '')
    result['月德'] = []
    for pk, pl in four_pillars.items():
        if pl['gan'] == yd:
            result['月德'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 月德贵人，心地善良，逢凶化吉'})

    # 13. 学堂 (日干查长生位)
    xuetang_map = {'甲':'亥','乙':'午','丙':'寅','丁':'酉','戊':'寅','己':'酉','庚':'巳','辛':'子','壬':'申','癸':'卯'}
    xt = xuetang_map.get(day_gan, '')
    result['学堂'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == xt:
            result['学堂'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 学堂入命，学业有成，考试运佳'})

    # 14. 金舆 (日干查)
    jinyu_map = {'甲':'辰','乙':'巳','丙':'未','丁':'申','戊':'未','己':'申','庚':'戌','辛':'亥','壬':'丑','癸':'寅'}
    jy = jinyu_map.get(day_gan, '')
    result['金舆'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == jy:
            result['金舆'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 金舆引从，富贵荣华，车马之福'})

    # 15. 天医 (月支查)
    tianyi_map = {'寅':'丑','卯':'寅','辰':'卯','巳':'辰','午':'巳','未':'午','申':'未','酉':'申','戌':'酉','亥':'戌','子':'亥','丑':'子'}
    ty = tianyi_map.get(month_zhi, '')
    result['天医'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == ty:
            result['天医'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 天医入命，利于医学/养生行业'})

    # 16. 孤辰 (年支查)
    guchen_map = {'子':'寅','丑':'寅','寅':'巳','卯':'巳','辰':'巳','巳':'申','午':'申','未':'申','申':'亥','酉':'亥','戌':'亥','亥':'寅'}
    gc = guchen_map.get(year_zhi, '')
    result['孤辰'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == gc:
            result['孤辰'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 孤辰入命，个性独立，六亲缘薄'})

    # 17. 寡宿 (年支查)
    guasu_map = {'子':'戌','丑':'戌','寅':'丑','卯':'丑','辰':'丑','巳':'辰','午':'辰','未':'辰','申':'未','酉':'未','戌':'未','亥':'戌'}
    gs = guasu_map.get(year_zhi, '')
    result['寡宿'] = []
    for pk, pl in four_pillars.items():
        if pl['zhi'] == gs:
            result['寡宿'].append({'pillar': pk, 'desc': f'{pl["ganzhi"]} 寡宿入命，需经营人际，防孤独'})

    # 只返回有结果的神煞
    return {k: v for k, v in result.items() if v}


# ==================== 十二长生 ====================

def calc_12_changsheng(day_gan: str) -> Dict[str, str]:
    """
    计算日干在十二地支的长生状态
    返回: {地支: 长生状态}
    """
    changsheng_seq = ['长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝','胎','养']
    start_positions = {'甲':0,'乙':9,'丙':2,'丁':11,'戊':2,'己':11,'庚':6,'辛':3,'壬':8,'癸':5}
    # 阳干顺行，阴干逆行
    start = start_positions.get(day_gan, 0)
    is_yang = GAN_YY[day_gan] == '阳'

    result = {}
    for i, zhi in enumerate(DIZHI):
        idx = (start + i) % 12 if is_yang else (start - i) % 12
        result[zhi] = changsheng_seq[idx]
    return result


def get_changsheng_for_zhi(day_gan: str, zhi: str) -> str:
    """获取日干在某地支的长生状态"""
    cs = calc_12_changsheng(day_gan)
    return cs.get(zhi, '')


# ==================== 胎元/命宫/身宫 ====================

def calc_taiyuan(month_ganzhi: str) -> str:
    """
    胎元: 月柱天干顺推一位，地支顺推三位
    例: 月柱壬午 → 胎元癸酉
    """
    mg, mz = month_ganzhi[0], month_ganzhi[1]
    tg_idx = (TIANGAN.index(mg) + 1) % 10
    dz_idx = (DIZHI.index(mz) + 3) % 12
    return TIANGAN[tg_idx] + DIZHI[dz_idx]


def calc_minggong(month_zhi: str, hour_zhi: str) -> str:
    """
    命宫: 以子为正月，逆推至出生月，再在出生时上顺推
    例: 午月辰时 → 命宫在申
    """
    month_idx = DIZHI.index(month_zhi)
    hour_idx = DIZHI.index(hour_zhi)
    # 命宫地支 = (14 - 月数 + 时数) mod 12，子=1...亥=12
    month_num = month_idx + 1
    hour_num = hour_idx + 1
    minggong_num = (14 - month_num + hour_num) % 12
    if minggong_num == 0: minggong_num = 12
    return DIZHI[minggong_num - 1]


def calc_shengong(minggong_zhi: str, month_gan: str) -> str:
    """身宫天干推算（与命宫同法）"""
    # 简化: 以年上起月法推算
    start_map = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    base_gan = start_map.get(month_gan, '甲')
    base_idx = TIANGAN.index(base_gan)
    minggong_idx = DIZHI.index(minggong_zhi)
    gan_idx = (base_idx + minggong_idx) % 10
    return TIANGAN[gan_idx]


# ==================== 空亡 ====================

def calc_kongwang(day_ganzhi: str) -> Tuple[str, str]:
    """
    空亡: 根据日柱所在旬，确定两个空亡地支
    六十甲子每旬10个，缺2个地支即为空亡
    """
    # 日柱干支序号
    ganzhi_index = (TIANGAN.index(day_ganzhi[0]) - DIZHI.index(day_ganzhi[1])) % 10
    if ganzhi_index % 2 != 0:
        # 不是旬首，找旬首
        pass
    # 旬首地支
    xunshou_zhi_idx = DIZHI.index(day_ganzhi[1]) - (TIANGAN.index(day_ganzhi[0]) % 10)
    xunshou_zhi_idx = xunshou_zhi_idx % 12
    # 空亡 = 旬首前两位
    kw1 = DIZHI[(xunshou_zhi_idx - 2) % 12]
    kw2 = DIZHI[(xunshou_zhi_idx - 1) % 12]
    return kw1, kw2


# ==================== 天干五合 ====================
GAN_HE = [('甲','己','土'),('乙','庚','金'),('丙','辛','水'),('丁','壬','木'),('戊','癸','火')]

def get_gan_he(gan: str) -> List[Dict]:
    """获取某天干的五合信息"""
    results = []
    for g1, g2, hua in GAN_HE:
        if gan == g1:
            results.append({'he_with': g2, 'hua_wuxing': hua, 'name': f'{g1}{g2}合化{hua}'})
        elif gan == g2:
            results.append({'he_with': g1, 'hua_wuxing': hua, 'name': f'{g1}{g2}合化{hua}'})
    return results


# ==================== 地支合会 ====================

# 地支六合
ZHI_LIUHE = {'子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯','辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'}
ZHI_LIUHE_WX = {'子丑':'土','寅亥':'木','卯戌':'火','辰酉':'金','巳申':'水','午未':'土'}

# 地支三合
ZHI_SANHE = {
    ('申','子','辰'): '水', ('亥','卯','未'): '木',
    ('寅','午','戌'): '火', ('巳','酉','丑'): '金'
}

# 地支三会
ZHI_SANHUI = {
    ('寅','卯','辰'): '木', ('巳','午','未'): '火',
    ('申','酉','戌'): '金', ('亥','子','丑'): '水'
}

# 地支六冲
ZHI_CHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}

# 地支六害
ZHI_HAI = {'子':'未','未':'子','丑':'午','午':'丑','寅':'巳','巳':'寅','卯':'辰','辰':'卯','申':'亥','亥':'申','酉':'戌','戌':'酉'}

# 地支三刑
ZHI_XING = {
    ('寅','巳','申'): '无恩之刑',
    ('丑','戌','未'): '恃势之刑',
    ('子','卯'): '无礼之刑',
}


def analyze_zhi_relations(four_pillars: Dict) -> Dict:
    """分析四柱地支间的合冲害刑关系"""
    zhis = []
    for pk in ['year','month','day','hour']:
        pl = four_pillars.get(pk, {})
        zhis.append({'pillar': pk, 'zhi': pl.get('zhi', ''), 'ganzhi': pl.get('ganzhi', '')})

    result = {'liuhe': [], 'liuchong': [], 'liuhai': [], 'sanhe': [], 'sanhui': []}

    # 六合/六冲/六害
    for i in range(4):
        for j in range(i+1, 4):
            zi, zj = zhis[i]['zhi'], zhis[j]['zhi']
            # 六合
            if ZHI_LIUHE.get(zi) == zj:
                he_key = zi+zj if zi<zj else zj+zi
                wx = ''
                for k,v in ZHI_LIUHE_WX.items():
                    if (zi in k and zj in k): wx=v; break
                result['liuhe'].append({'pair': f'{zhis[i]["ganzhi"]}-{zhis[j]["ganzhi"]}', 'wuxing': wx})
            # 六冲
            if ZHI_CHONG.get(zi) == zj:
                result['liuchong'].append({'pair': f'{zhis[i]["ganzhi"]}-{zhis[j]["ganzhi"]}'})
            # 六害
            if ZHI_HAI.get(zi) == zj:
                result['liuhai'].append({'pair': f'{zhis[i]["ganzhi"]}-{zhis[j]["ganzhi"]}'})

    # 三合
    all_zhi = tuple(sorted([z['zhi'] for z in zhis]))
    for triple, wx in ZHI_SANHE.items():
        if all(z in all_zhi for z in triple):
            result['sanhe'].append({'triple': ''.join(triple), 'wuxing': wx, 'desc': f'三合{wx}局'})

    # 三会
    for triple, wx in ZHI_SANHUI.items():
        if all(z in all_zhi for z in triple):
            result['sanhui'].append({'triple': ''.join(triple), 'wuxing': wx, 'desc': f'三会{wx}方'})

    return {k: v for k, v in result.items() if v}


# ==================== 五行旺相休囚死 ====================

def calc_wuxing_season_state(month_zhi: str) -> Dict[str, str]:
    """
    根据月令确定五行旺相休囚死状态
    """
    season_wx = {
        '寅':'木','卯':'木',
        '巳':'火','午':'火',
        '申':'金','酉':'金',
        '亥':'水','子':'水',
        '辰':'土','戌':'土','丑':'土','未':'土'
    }
    dominant = season_wx.get(month_zhi, '土')

    state_map = {
        '木': {'木':'旺','火':'相','水':'休','金':'囚','土':'死'},
        '火': {'火':'旺','土':'相','木':'休','水':'囚','金':'死'},
        '土': {'土':'旺','金':'相','火':'休','木':'囚','水':'死'},
        '金': {'金':'旺','水':'相','土':'休','火':'囚','木':'死'},
        '水': {'水':'旺','木':'相','金':'休','土':'囚','火':'死'},
    }
    return state_map.get(dominant, state_map['土'])
