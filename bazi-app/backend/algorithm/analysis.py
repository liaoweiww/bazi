"""
八字分析模块 - 五行量化、身强身弱、格局、喜用神、大运流年
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
GAN_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
GAN_YINYANG = {'甲':'阳','乙':'阴','丙':'阳','丁':'阴','戊':'阳','己':'阴','庚':'阳','辛':'阴','壬':'阳','癸':'阴'}
ZHI_WUXING = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
ZHI_BENQI = {'子':'癸','丑':'己','寅':'甲','卯':'乙','辰':'戊','巳':'丙','午':'丁','未':'己','申':'庚','酉':'辛','戌':'戊','亥':'壬'}
ZHI_CANGGAN = {'子':['癸'],'丑':['己','癸','辛'],'寅':['甲','丙','戊'],'卯':['乙'],'辰':['戊','乙','癸'],'巳':['丙','戊','庚'],'午':['丁','己'],'未':['己','丁','乙'],'申':['庚','壬','戊'],'酉':['辛'],'戌':['戊','辛','丁'],'亥':['壬','甲']}
WUXING_SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
WUXING_KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
NAYIN_TABLE = ['海中金','炉中火','大林木','路旁土','剑锋金','山头火','涧下水','城头土','白蜡金','杨柳木','泉中水','屋上土','霹雳火','松柏木','长流水','沙中金','山下火','平地木','壁上土','金箔金','覆灯火','天河水','大驿土','钗钏金','桑柘木','大溪水','沙中土','天上火','石榴木','大海水']

def get_nayin(ganzhi): gan,zhi=ganzhi[0],ganzhi[1]; idx=(TIANGAN.index(gan)//2*12+DIZHI.index(zhi))//2; return NAYIN_TABLE[idx%30]

def get_shishen_key(ri_gan, other_gan):
    ri_wx=GAN_WUXING[ri_gan]; other_wx=GAN_WUXING[other_gan]; same=GAN_YINYANG[ri_gan]==GAN_YINYANG[other_gan]
    if ri_wx==other_wx: return '比肩' if same else '劫财'
    if WUXING_SHENG[ri_wx]==other_wx: return '食神' if same else '伤官'
    if WUXING_KE[ri_wx]==other_wx: return '偏财' if same else '正财'
    if WUXING_SHENG.get(other_wx)==ri_wx: return '偏印' if same else '正印'
    if WUXING_KE.get(other_wx)==ri_wx: return '七杀' if same else '正官'
    return '未知'

def count_wuxing(four_pillars):
    wc={'金':{'count':0,'score':0.0},'木':{'count':0,'score':0.0},'水':{'count':0,'score':0.0},'火':{'count':0,'score':0.0},'土':{'count':0,'score':0.0}}
    for pn,pl in four_pillars.items():
        gan=pl.get('gan',''); wx=GAN_WUXING.get(gan,'')
        if wx: wc[wx]['count']+=1; wc[wx]['score']+=1.0
        for i,cg in enumerate(pl.get('canggan',[])):
            cg_wx=GAN_WUXING.get(cg,'')
            if cg_wx: wc[cg_wx]['count']+=1 if i==0 else 0.5; wc[cg_wx]['score']+=1.0 if i==0 else 0.5
    for wx in wc: wc[wx]['score']=round(wc[wx]['score'],1)
    return wc

def determine_strength(four_pillars, day_gan, month_zhi):
    day_wx=GAN_WUXING[day_gan]; month_wx=ZHI_WUXING[month_zhi]; score=50
    if day_wx==month_wx: score+=25; dt=f'日主{day_wx}与月令同五行，得令'
    elif WUXING_SHENG.get(month_wx)==day_wx: score+=15; dt=f'月令生扶日主，得令相助'
    elif WUXING_SHENG.get(day_wx)==month_wx: score-=15; dt=f'日主生月令，泄气'
    elif WUXING_KE.get(month_wx)==day_wx: score-=25; dt=f'月令克日主，受制'
    else: dt='日主与月令关系一般'
    root=sum(1 for pn,pl in four_pillars.items() if pn!='day' for cg in pl.get('canggan',[]) if GAN_WUXING.get(cg)==day_wx)
    if root>=2: score+=15; rt='地支通根多处，得地'
    elif root>=1: score+=8; rt='略有根气'
    else: score-=10; rt='地支无通根'
    sup=sum(1 for pn,pl in four_pillars.items() if pn!='day' and (GAN_WUXING.get(pl.get('gan',''))==day_wx or WUXING_SHENG.get(GAN_WUXING.get(pl.get('gan','')))==day_wx))
    if sup>=3: score+=10; st='生助多，得势'
    elif sup>=1: score+=3; st='略有生助'
    else: score-=5; st='少生助'
    if score>=70: lv='身强'
    elif score>=55: lv='偏强'
    elif score>=45: lv='中和'
    elif score>=30: lv='偏弱'
    else: lv='身弱'
    return {'level':lv,'score':score,'details':f'{dt}；{rt}；{st}'}

def determine_geju(four_pillars, day_gan, month_zhi, strength):
    month_gan=four_pillars.get('month',{}).get('gan','')
    month_shishen=get_shishen_key(day_gan, month_gan)
    geju_name=f'{month_shishen}格'; geju_type='正格'
    analysis=f'月令{month_zhi}，月干{month_gan}为{month_shishen}。'
    if strength['score']>=85:
        geju_type='专旺格'; names={'木':'曲直格','火':'炎上格','土':'稼穑格','金':'从革格','水':'润下格'}
        geju_name=names.get(GAN_WUXING[day_gan],'专旺格'); analysis=f'日主极旺，成{geju_name}。'
    elif strength['score']<=15:
        geju_type='变格'
        cc={}
        for pn,pl in four_pillars.items():
            if pn=='day': continue
            ss=get_shishen_key(day_gan, pl.get('gan','')); cc[ss]=cc.get(ss,0)+1
        mx=max(cc,key=cc.get)
        if mx in ('七杀','正官'): geju_name='从杀格'
        elif mx in ('正财','偏财'): geju_name='从财格'
        elif mx in ('食神','伤官'): geju_name='从儿格'
        else: geju_name='从弱格'
        analysis=f'日主极弱，成{geju_name}。'
    return {'type':geju_type,'name':geju_name,'analysis':analysis}

def determine_yongji(four_pillars, day_gan, strength, geju, month_zhi):
    day_wx=GAN_WUXING[day_gan]; level=strength['level']
    sheng_wo=[wx for wx,s in WUXING_SHENG.items() if s==day_wx]
    ke_wo=[wx for wx,k in WUXING_KE.items() if k==day_wx]
    wo_sheng=[WUXING_SHENG[day_wx]]; wo_ke=[WUXING_KE[day_wx]]
    ys,js=[],[]
    if '强' in level:
        for wx in ke_wo: ys.append({'wuxing':wx,'shishen':'官杀','reason':f'{day_wx}强需{wx}克制'})
        for wx in wo_sheng: ys.append({'wuxing':wx,'shishen':'食伤','reason':f'{day_wx}强需{wx}泄秀'})
        for wx in wo_ke: ys.append({'wuxing':wx,'shishen':'财星','reason':f'{day_wx}强可担{wx}财'})
        for wx in sheng_wo: js.append({'wuxing':wx,'shishen':'印星','reason':f'{day_wx}已强勿再生'})
        js.append({'wuxing':day_wx,'shishen':'比劫','reason':'同五行加重'})
    elif '弱' in level:
        for wx in sheng_wo: ys.append({'wuxing':wx,'shishen':'印星','reason':f'{day_wx}弱需{wx}生扶'})
        ys.append({'wuxing':day_wx,'shishen':'比劫','reason':f'同五行帮扶{day_wx}'})
        for wx in ke_wo: js.append({'wuxing':wx,'shishen':'官杀','reason':f'{day_wx}弱勿再受{wx}克'})
        for wx in wo_sheng: js.append({'wuxing':wx,'shishen':'食伤','reason':f'{day_wx}弱勿再泄气'})
    th=''; th+='冬月需火调候。' if month_zhi in '亥子丑' else ''; th+='夏月需水调候。' if month_zhi in '巳午未' else ''
    return {'yong_shen':ys,'ji_shen':js,'xian_shen':[],'tiao_hou':th}

def calculate_dayun(solar_date, four_pillars, gender):
    year_gan=four_pillars['year']['gan']; is_yang=GAN_YINYANG[year_gan]=='阳'
    direction='顺排' if (is_yang and gender=='男') or (not is_yang and gender=='女') else '逆排'
    try:
        from lunarcal.solar_terms import get_current_solar_term
        prev_term, prev_date, next_term, next_date = get_current_solar_term(solar_date)
        tgt=next_date if direction=='顺排' else prev_date
        days_diff=abs((solar_date-tgt).days) if tgt else 0
    except: days_diff=0
    start_age=max(1, round(days_diff/3.0))
    mg,mz=four_pillars['month']['gan'],four_pillars['month']['zhi']
    gi,zi=TIANGAN.index(mg),DIZHI.index(mz)
    dylist=[]
    for i in range(1,9):
        ng=TIANGAN[(gi+i)%10] if direction=='顺排' else TIANGAN[(gi-i)%10]
        nz=DIZHI[(zi+i)%12] if direction=='顺排' else DIZHI[(zi-i)%12]
        gz=ng+nz
        dylist.append({'age_range':f'{start_age+(i-1)*10}-{start_age+i*10-1}','start_age':start_age+(i-1)*10,'gan':ng,'zhi':nz,'ganzhi':gz,'nayin':get_nayin(gz)})
    now=datetime.now(); age=now.year - solar_date.year
    cur=next((d for d in dylist if d['start_age']<=age<d['start_age']+10), None)
    return {'start_age':start_age,'direction':direction,'dayun_list':dylist,'current_dayun':cur or {}}

def calculate_liunian(four_pillars, dayun, year, day_gan):
    yg=TIANGAN[(year-4)%10]; yz=DIZHI[(year-4)%12]; gz=yg+yz
    parts=[]; dz=four_pillars.get('day',{}).get('zhi','')
    if yz==dz: parts.append('流年伏吟日柱')
    elif DIZHI.index(yz)==(DIZHI.index(dz)+6)%12: parts.append('流年反吟日柱')
    cur=dayun.get('current_dayun',{})
    if cur and yz==cur.get('zhi',''): parts.append('岁运并临')
    return {'year':year,'ganzhi':gz,'gan':yg,'zhi':yz,'wuxing':GAN_WUXING[yg],'shishen':get_shishen_key(day_gan,yg),'nayin':get_nayin(gz),'analysis':'；'.join(parts) if parts else '流年平稳'}

def generate_dayun_analysis(four_pillars, day_master, dayun_list, yongji, strength, month_zhi):
    """为每步大运生成详细分析"""
    dm_wx = GAN_WUXING[day_master]
    day_zhi = four_pillars['day']['zhi']
    yong_wx = [y['wuxing'] for y in yongji.get('yong_shen', [])]
    yong_reason = {y['wuxing']: y.get('reason', '') for y in yongji.get('yong_shen', [])}
    ji_wx = [j['wuxing'] for j in yongji.get('ji_shen', [])]
    level = strength.get('level', '')

    life_stages = ['童年奠基期', '少年求学成长期', '青年奋斗立业期', '壮年发展高峰期',
                   '中年稳固转型期', '中年沉淀收获期', '知天命感悟期', '晚年颐养天年期']

    for i, dy in enumerate(dayun_list):
        gz = dy['ganzhi']
        gan = dy.get('gan', '')
        zhi = dy.get('zhi', '')
        g_wx = GAN_WUXING.get(gan, '')
        z_wx = ZHI_WUXING.get(zhi, '')
        shishen = get_shishen_key(day_master, gan)
        nayin = dy.get('nayin', '')
        age_range = dy.get('age_range', '')
        stage = life_stages[min(i, len(life_stages) - 1)]
        canggan = ZHI_CANGGAN.get(zhi, [])

        lines = []

        # ===== 第一条：基本定性 =====
        lines.append(f'【{age_range}岁 · {stage}】')
        lines.append(f'大运干支「{gz}」，纳音「{nayin}」。天干{gan}属{g_wx}，逢日主{day_master}（{dm_wx}）为{shishen}；地支{zhi}属{z_wx}，藏干{"、".join(canggan)}。')

        # ===== 第二条：喜忌与整体运势 =====
        g_is_yong = g_wx in yong_wx
        z_is_yong = z_wx in yong_wx
        g_is_ji = g_wx in ji_wx
        z_is_ji = z_wx in ji_wx

        if g_is_yong and z_is_yong:
            lines.append(f'天干{g_wx}、地支{z_wx}皆为喜用神，是人生运势最为顺遂的黄金十年。外在机遇与内在根基双双助力，事业发展顺利、人际遇贵、大事可成。务必珍惜这段宝贵时期，大胆进取，为人生奠定坚实的高峰。')
        elif g_is_ji and z_is_ji:
            lines.append(f'天干{g_wx}、地支{z_wx}皆为忌神，此十年是人生的考验期。外部压力大、内部根基不稳，宜以稳守为主，韬光养晦，减少重大决策与激进扩张。重在积累经验、磨砺心性，待运势转好时方可发力。')
        elif g_is_yong and z_is_ji:
            lines.append(f'天干{g_wx}为喜用神，主外在机遇、贵人扶持、事业名声方面表现亮眼；但地支{z_wx}为忌神，内部根基不稳，容易出现表面风光暗藏隐患的局面。此十年前五年得天干之助较为顺利，后五年地支承压，需提前储备、防范风险，不可因前期顺利而放松警惕。')
        elif z_is_yong and g_is_ji:
            lines.append(f'地支{z_wx}为喜用神，基础稳固，家宅安宁，宜扎根深耕、厚积薄发；但天干{g_wx}为忌神，外部环境不太友好，事业推进、人际交往中阻力较多。此十年是「养精蓄锐」的好时机，少出头、多做事，靠稳重扎实取胜。')
        else:
            lines.append(f'天干地支喜忌参半、力量均衡。此十年运势平稳，没有大起大落。关键在于把握流年的细微变化——遇喜用流年则积极进取，逢忌神流年则谨慎守成。总体以稳中求进为策略。')

        # ===== 第三条：身强身弱 + 十神的深度解读 =====
        shishen_map = {
            '正官': ('官星', '克我', f'正官为贵气之星，代表事业、职位、规章与约束。此大运利于职业发展、考取功名、获得官方认可。但也意味着需遵守规则、承担责任。', f'正官本为克制日主之力，身弱再逢正官压力倍增，工作中容易感到力不从心，健康上需注意精神状态。建议量力而行，不必强求高位。'),
            '七杀': ('杀星', '克我', f'七杀为威权之星，代表魄力、竞争、变革与突破。此大运利于创业、竞争、掌握权力，可成非常之事。但也伴随风险和压力，需要足够的勇气和智慧去应对挑战。', f'七杀为忌时压力极大，身弱难敌七杀之克，容易遭遇小人排挤、突发困难。此十年需以「退一步海阔天空」为座右铭，避免正面对抗，学会借力化力。'),
            '正财': ('财星', '我克', f'正财为稳定财源，代表薪水、积蓄、实业投资。此大运利于积累财富、购置资产、建立稳定的经济基础。正财求稳不求快，可在本职工作或稳健投资中获得良好回报。', f'身弱财旺为「财多身弱」之象，虽有赚钱机会却难以把握，或赚到钱后反而影响健康与人际。此十年投资理财需特别谨慎，守住已有比盲目扩张更重要。'),
            '偏财': ('财星', '我克', f'偏财为横财、流动之财，代表投资、副业、意外收入。此大运比正财更灵动，利于开拓多元收入渠道。但偏财来得快去得也快，需有理财规划，不可太过随性。', f'身弱遇偏财尤需谨慎，偏财来得突然却难以留住。此十年商机虽多，但陷阱也多，不可贪图高回报而轻信他人。'),
            '食神': ('食伤', '我生', f'食神为福星，代表才华、创意、享受与艺术天赋。此大运利于发挥个人特长、进行创作或艺术表达。食神也主人际和谐、生活品质提升。是学习、创作和拓展人脉的好时期。', f'食神虽能泄秀，但身弱再泄气则精力分散、效率下降。此十年需聚焦核心领域，避免才华过度分散（多而不精），同时注意身体健康、避免劳累过度。'),
            '伤官': ('食伤', '我生', f'伤官代表突破常规的创新力、独特的才华表现。此大运利于转行、创新、追求独立事业。伤官人思维敏捷、表现欲强，适合从事需要创造力和表达力的工作。但伤官也易冲动，需注意言行分寸。', f'伤官为忌时易逞强好胜、口舌是非多，职场上可能得罪人。身弱更需收敛锋芒，避免因过于高调而树敌。'),
            '正印': ('印星', '生我', f'正印为贵人星、学识星，代表长辈扶持、学习机遇、名誉地位。此大运有贵人相助，适合深造学习、提升专业能力、获取认证资格。正印也主仁德之心，待人宽厚者自获福报。', f'正印生扶日主，身弱逢印乃是绝佳之运，如逢甘霖。长辈贵人提携，学习能力增强，健康状况改善。此十年是「打基础」的黄金时期，建议多学习、积累资源和人脉。'),
            '偏印': ('印星', '生我', f'偏印代表独特思维、偏门技艺、另类智慧。此大运利于研究深造、钻研特殊领域、发挥独特天赋。偏印格局的人常有非常之能，适合从事学术研究、技术攻关等工作。但偏印也代表孤僻倾向，需保持社交。', f'偏印生扶日主，身弱得印助则精力回升。但偏印为忌时容易思虑过多、钻牛角尖，人际关系趋于冷淡。需注意保持开放心态，多与人交流合作。'),
            '比肩': ('比劫', '同我', f'比肩代表兄弟朋友、竞争与合作。此大运人脉拓展，适合团队合作、合伙创业。比肩助身，精力充沛，自信心增强。但比肩过多则竞争加剧，需处理好合作与竞争的关系。', f'比肩帮身，身弱逢之则获得友人的实质性帮助，单打独斗的困境得以缓解。此十年宜融入团队、借助他人力量共同发展。'),
            '劫财': ('比劫', '同我', f'劫财代表勇气、魄力与冒险精神。此大运利于突破现状、大胆开拓。但劫财也主财来财去、投资风险较高，需理性对待财务。人际关系上朋友虽多，但合作的稳定性需留意。', f'劫财帮身力度强，身弱逢之人脉与力量明显提升。但劫财也克财，期间需注意财务管理，避免被所谓「朋友」搭车消耗资源。'),
        }

        si = shishen_map.get(shishen, None)
        if si:
            category, relation, desc_strong, desc_weak = si
            is_strong = '强' in level
            if is_strong and shishen in ['正官', '七杀', '正财', '偏财', '食神', '伤官']:
                lines.append(desc_strong)
            elif not is_strong and shishen in ['正印', '偏印', '比肩', '劫财']:
                lines.append(desc_weak)
            else:
                lines.append(desc_strong if is_strong else desc_weak)

        # ===== 第四条：地支藏干影响 =====
        if len(canggan) >= 2:
            cg_analysis = []
            for cg in canggan:
                cg_wx = GAN_WUXING.get(cg, '')
                cg_ss = get_shishen_key(day_master, cg)
                tag = '喜' if cg_wx in yong_wx else ('忌' if cg_wx in ji_wx else '平')
                cg_analysis.append(f'{cg}（{cg_wx}·{cg_ss}·{tag}）')
            lines.append(f'地支{zhi}藏干中的{"、".join(cg_analysis)}各具影响。其中藏干力量随流年引动而显现，需结合具体流年综合判断。')

        # ===== 第五条：调候 =====
        if month_zhi in '亥子丑' and g_wx == '火':
            lines.append('命主生于冬月，命局偏寒，此步大运带火，恰如寒冬暖阳，调候之功显著。万物遇暖则生发，事业、情感、健康均有回暖之势。')
        elif month_zhi in '巳午未' and g_wx == '水':
            lines.append('命主生于夏月，命局偏燥，此步大运带水，犹如盛夏甘霖，调候润泽。燥热得解，心绪趋于平和，做事更显沉稳周全。')

        # ===== 第六条：年龄段建议 =====
        stage_advice = {
            0: '童年时期，大运主要影响身体健康与学业启蒙。此阶段根基是否稳固，直接影响后续发展。家长宜关注孩子的健康、性格培养和基础教育。',
            1: '青少年求学阶段，大运关乎学业成绩和性格塑造。此十年是知识积累和价值观形成的关键期，宜专注学业、培养良好习惯。',
            2: '青年奋斗期，大运决定了进入社会后的起步高度。此十年是事业、婚恋的重要窗口期，宜勇于尝试、建立职业方向和家庭基础。',
            3: '壮年发展期，大运关乎事业能否更上一层楼。此十年精力充沛，适合开拓进取，是人生最容易取得重大突破的阶段。',
            4: '中年转型期，大运影响事业转型和财富积累。此十年需平衡守成与创新，稳健为主但有合适时机也要果断出手。',
            5: '中年收获期，大运关乎前期积累的兑现。此十年是检验过往努力成果的阶段，宜整合资源、精耕细作。',
            6: '知天命期，大运影响晚年生活质量和智慧沉淀。此十年心态趋于从容，宜注重健康、享受生活、传承经验。',
            7: '颐养天年期，大运关乎晚景安宁。此十年以养生为主，心态平和即是最大的福气。',
        }
        lines.append(stage_advice.get(i, ''))

        dy['analysis'] = '\n\n'.join(lines)

    return dayun_list
