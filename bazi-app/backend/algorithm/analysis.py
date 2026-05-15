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
        from calendar.solar_terms import get_current_solar_term
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
