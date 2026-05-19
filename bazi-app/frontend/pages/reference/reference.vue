<template>
  <!-- 古籍参考页 -->
  <view class="page-reference">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-bar__content">
        <text class="nav-bar__title">{{ refMode === 'zodiac' ? '星座百科' : '古籍参考' }}</text>
      </view>
    </view>

    <scroll-view
      class="page-reference__scroll"
      scroll-y
      enhanced
      :show-scrollbar="false"
    >
      <!-- 模式切换 -->
      <view class="ref-mode-switch">
        <view class="ref-mode-btn" :class="{ 'ref-mode-btn--active': refMode === 'bazi' }" @tap="refMode = 'bazi'">
          <text>八字</text>
        </view>
        <view class="ref-mode-btn" :class="{ 'ref-mode-btn--active': refMode === 'zodiac' }" @tap="refMode = 'zodiac'">
          <text>星座</text>
        </view>
      </view>

      <!-- ===== 八字知识库 ===== -->
      <template v-if="refMode === 'bazi'">
      <!-- 十神解读 -->
      <view class="section-card">
        <view class="section-title">
          <view class="section-title__icon">神</view>
          <text class="section-title__text">十神详解</text>
        </view>
        <view class="shishen-grid">
          <view
            v-for="item in shishenList"
            :key="item.name"
            class="shishen-card"
            :class="{ 'shishen-card--expanded': expandedShishen === item.name }"
            :aria-expanded="expandedShishen === item.name ? 'true' : 'false'"
            @tap="toggleShishen(item.name)"
          >
            <view class="shishen-card__header" role="button" :aria-label="'查看' + item.name + '详情'">
              <ShishenBadge :label="item.name" :type="item.badgeType" />
              <text class="shishen-card__alias">{{ item.alias }}</text>
              <text class="shishen-card__arrow" aria-hidden="true">
                {{ expandedShishen === item.name ? '▲' : '▼' }}
              </text>
            </view>

            <!-- 展开内容 -->
            <view class="shishen-card__body" v-if="expandedShishen === item.name">
              <view class="shishen-detail">
                <view class="shishen-detail__row">
                  <text class="detail-label">五行：</text>
                  <text class="detail-value">{{ item.wuxingRelation }}</text>
                </view>
                <view class="shishen-detail__row">
                  <text class="detail-label">含义：</text>
                  <text class="detail-value">{{ item.meaning }}</text>
                </view>
                <view class="shishen-detail__row">
                  <text class="detail-label">正面：</text>
                  <text class="detail-value detail-value--good">{{ item.positive }}</text>
                </view>
                <view class="shishen-detail__row">
                  <text class="detail-label">负面：</text>
                  <text class="detail-value detail-value--bad">{{ item.negative }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 五行关系图 -->
      <view class="section-card">
        <view class="section-title">
          <view class="section-title__icon section-title__icon--wood">行</view>
          <text class="section-title__text">五行生克</text>
        </view>
        <classic-border variant="gold">
          <view class="wuxing-relation">
            <!-- 五行关系图 -->
            <view class="wuxing-diagram">
              <!-- 生：外圈箭头说明 -->
              <view class="wuxing-diagram__circle">
                <view
                  v-for="(item, index) in wuxingCircleItems"
                  :key="item.name"
                  class="wuxing-node"
                  :style="wuxingNodeStyle(index)"
                >
                  <ganzhi-tag :label="item.name" :wuxing="item.key" size="lg" />
                </view>
              </view>

              <!-- 图解 -->
              <view class="wuxing-legend">
                <view class="legend-section">
                  <text class="legend-label legend-label--sheng">相 生：</text>
                  <text class="legend-text">木生火、火生土、土生金、金生水、水生木</text>
                </view>
                <view class="legend-section">
                  <text class="legend-label legend-label--ke">相 克：</text>
                  <text class="legend-text">木克土、土克水、水克火、火克金、金克木</text>
                </view>
              </view>
            </view>
          </view>
        </classic-border>
      </view>

      <!-- 神煞速查表 -->
      <view class="section-card">
        <view class="section-title">
          <view class="section-title__icon section-title__icon--vermillion">煞</view>
          <text class="section-title__text">神煞速查</text>
        </view>
        <classic-border>
          <view class="shensha-table">
            <view class="shensha-table__header">
              <text class="shensha-col shensha-col--name">神煞名</text>
              <text class="shensha-col shensha-col--type">类型</text>
              <text class="shensha-col shensha-col--desc">简要说明</text>
            </view>
            <view
              v-for="item in shenshaList"
              :key="item.name"
              class="shensha-table__row"
            >
              <text class="shensha-col shensha-col--name">{{ item.name }}</text>
              <view class="shensha-col shensha-col--type">
                <text
                  class="shensha-type-badge"
                  :class="'shensha-type--' + item.type"
                >{{ item.typeLabel }}</text>
              </view>
              <text class="shensha-col shensha-col--desc">{{ item.desc }}</text>
            </view>
          </view>
        </classic-border>
      </view>

      <!-- 关于APP -->
      <view class="section-card">
        <view class="section-title">
          <view class="section-title__icon section-title__icon--gold">易</view>
          <text class="section-title__text">关于应用</text>
        </view>
        <classic-border>
          <view class="about-card">
            <view class="about-logo">
              <text class="about-logo__text">易经八字</text>
              <text class="about-logo__ver">v1.0.0</text>
            </view>
            <view class="about-divider">
              <view class="about-divider__line"></view>
              <view class="about-divider__diamond"></view>
              <view class="about-divider__line"></view>
            </view>
            <text class="about-desc">
              本应用基于传统命理学，采用子平八字排盘法，结合《渊海子平》《三命通会》《滴天髓》等古籍算法，提供专业的八字命盘推演、格局分析、大运流年推算等功能。
            </text>
            <view class="about-disclaimer">
              <text class="about-disclaimer__icon">!</text>
              <text class="about-disclaimer__text">
                免责声明：命理分析仅供娱乐参考，请勿过度迷信。人生之途，在于自身的努力与抉择。
              </text>
            </view>
            <view class="about-credits">
              <text class="about-credits__text">传承千年智慧，弘扬中华文化</text>
            </view>
          </view>
        </classic-border>
      </view>

      </template>

      <!-- ===== 星座知识库 ===== -->
      <template v-if="refMode === 'zodiac'">
        <!-- 12星座详解 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon">座</view>
            <text class="section-title__text">十二星座详解</text>
          </view>
          <view class="shishen-grid">
            <view
              v-for="sign in zodiacSignsList"
              :key="sign.name"
              class="shishen-card"
              :class="{ 'shishen-card--expanded': expandedZodiac === sign.name }"
              @tap="toggleZodiacSign(sign.name)"
            >
              <view class="shishen-card__header">
                <text class="zodiac-ref__symbol">{{ sign.symbol }}</text>
                <text class="shishen-card__alias" style="flex:1">{{ sign.name }}</text>
                <text class="shishen-card__alias" style="color:var(--text-placeholder);font-size:20rpx;">{{ sign.date_range }}</text>
                <text class="shishen-card__arrow">{{ expandedZodiac === sign.name ? '▲' : '▼' }}</text>
              </view>
              <view class="shishen-card__body" v-if="expandedZodiac === sign.name">
                <view class="shishen-detail">
                  <view class="shishen-detail__row">
                    <text class="detail-label">元素：</text>
                    <text class="detail-value">{{ sign.element }}象 | {{ sign.modality }}星座</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">守护星：</text>
                    <text class="detail-value">{{ sign.ruling_planet }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">概述：</text>
                    <text class="detail-value">{{ sign.overview }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">性格：</text>
                    <text class="detail-value">{{ sign.personality }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">优点：</text>
                    <text class="detail-value detail-value--good">{{ sign.strengths.join('、') }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">缺点：</text>
                    <text class="detail-value detail-value--bad">{{ sign.weaknesses.join('、') }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 行星含义 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--gold">星</view>
            <text class="section-title__text">十大行星含义</text>
          </view>
          <view class="shishen-grid">
            <view
              v-for="p in planetsList"
              :key="p.name"
              class="shishen-card"
              :class="{ 'shishen-card--expanded': expandedPlanet === p.name }"
              @tap="togglePlanet(p.name)"
            >
              <view class="shishen-card__header">
                <text class="zodiac-ref__symbol">{{ p.symbol }}</text>
                <text class="shishen-card__alias" style="flex:1">{{ p.name }}</text>
                <text class="shishen-card__alias" style="color:var(--text-placeholder);font-size:20rpx;">{{ p.category }}</text>
                <text class="shishen-card__arrow">{{ expandedPlanet === p.name ? '▲' : '▼' }}</text>
              </view>
              <view class="shishen-card__body" v-if="expandedPlanet === p.name">
                <view class="shishen-detail">
                  <view class="shishen-detail__row">
                    <text class="detail-label">关键词：</text>
                    <text class="detail-value">{{ p.keywords }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">含义：</text>
                    <text class="detail-value">{{ p.meaning }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 宫位含义 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--water">宫</view>
            <text class="section-title__text">十二宫位含义</text>
          </view>
          <view class="shishen-grid">
            <view
              v-for="h in housesList"
              :key="h.number"
              class="shishen-card"
              :class="{ 'shishen-card--expanded': expandedHouse === h.number }"
              @tap="toggleHouse(h.number)"
            >
              <view class="shishen-card__header">
                <text class="zodiac-ref__num">{{ h.number }}</text>
                <text class="shishen-card__alias" style="flex:1">{{ h.name }}</text>
                <text class="shishen-card__alias" style="color:var(--text-placeholder);font-size:20rpx;">{{ h.area }}</text>
                <text class="shishen-card__arrow">{{ expandedHouse === h.number ? '▲' : '▼' }}</text>
              </view>
              <view class="shishen-card__body" v-if="expandedHouse === h.number">
                <view class="shishen-detail">
                  <view class="shishen-detail__row">
                    <text class="detail-label">领域：</text>
                    <text class="detail-value">{{ h.area }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">含义：</text>
                    <text class="detail-value">{{ h.meaning }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 相位解释 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--fire">相</view>
            <text class="section-title__text">五种主要相位</text>
          </view>
          <view class="shishen-grid">
            <view
              v-for="a in aspectsList"
              :key="a.name"
              class="shishen-card"
              :class="{ 'shishen-card--expanded': expandedAspect === a.name }"
              @tap="toggleAspect(a.name)"
            >
              <view class="shishen-card__header">
                <text class="zodiac-ref__symbol">{{ a.symbol }}</text>
                <text class="shishen-card__alias" style="flex:1">{{ a.name }}</text>
                <text class="shishen-card__alias" :style="{color: a.nature === '和谐' ? 'var(--color-positive)' : a.nature === '紧张' ? 'var(--vermillion)' : 'var(--text-muted)', fontSize:'20rpx'}">{{ a.angle }}° | {{ a.nature }}</text>
                <text class="shishen-card__arrow">{{ expandedAspect === a.name ? '▲' : '▼' }}</text>
              </view>
              <view class="shishen-card__body" v-if="expandedAspect === a.name">
                <view class="shishen-detail">
                  <view class="shishen-detail__row">
                    <text class="detail-label">角度：</text>
                    <text class="detail-value">{{ a.angle }}° (±{{ a.orb }}°容许度)</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">性质：</text>
                    <text class="detail-value">{{ a.nature }} | {{ a.intensity || '' }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">解释：</text>
                    <text class="detail-value">{{ a.general }}</text>
                  </view>
                  <view class="shishen-detail__row">
                    <text class="detail-label">建议：</text>
                    <text class="detail-value detail-value--good">{{ a.advice }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </template>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import ClassicBorder from '@/components/ClassicBorder.vue'
import ShishenBadge from '@/components/ShishenBadge.vue'
import GanzhiTag from '@/components/GanzhiTag.vue'

const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 20)

// 展开的十神项
const expandedShishen = ref('')

// 星座百科数据
const refMode = ref('bazi')
const expandedZodiac = ref('')
const expandedPlanet = ref('')
const expandedHouse = ref(null)
const expandedAspect = ref('')

const zodiacSignsList = [
  { name: '白羊座', symbol: '♈', element: '火', modality: '基本', ruling_planet: '火星',
    date_range: '3.21-4.19', overview: '白羊座是黄道第一个星座，象征着新生与开始。受火星守护，充满活力、勇气与开创精神。',
    personality: '热情直率、行动力强、充满竞争意识。做事雷厉风行，天性乐观自信，永不服输。但有时冲动鲁莽，缺乏耐心。',
    strengths: ['勇敢果断','热情积极','领导力强','真诚直率'], weaknesses: ['冲动急躁','缺乏耐心','自我中心','三分钟热度'] },
  { name: '金牛座', symbol: '♉', element: '土', modality: '固定', ruling_planet: '金星',
    date_range: '4.20-5.20', overview: '金牛座象征着物质与稳定。受金星守护，热爱美好事物，追求安定舒适的生活。',
    personality: '踏实稳重、坚韧不拔、值得信赖。重视物质安全，有很强的审美能力。但有时固执己见，过于保守。',
    strengths: ['踏实可靠','耐心持久','审美出色','忠诚专一'], weaknesses: ['固执己见','占有欲强','过于保守','记仇'] },
  { name: '双子座', symbol: '♊', element: '风', modality: '变动', ruling_planet: '水星',
    date_range: '5.21-6.21', overview: '双子座象征着沟通与智慧。受水星守护，思维敏捷、好奇心旺盛。',
    personality: '聪明机智、能言善道、适应力强。喜欢学习新事物，擅长多任务处理。但有时浮躁不定，难以专注。',
    strengths: ['聪明灵活','善于沟通','适应力强','幽默风趣'], weaknesses: ['浮躁不定','缺乏深度','容易分心','善变'] },
  { name: '巨蟹座', symbol: '♋', element: '水', modality: '基本', ruling_planet: '月亮',
    date_range: '6.22-7.22', overview: '巨蟹座象征着家庭与情感。受月亮守护，情感丰富、敏感细腻。',
    personality: '温柔体贴、善解人意、家庭观念极强。直觉力强，对身边人关怀备至。但有时过于情绪化，自我保护意识过强。',
    strengths: ['温柔体贴','直觉敏锐','家庭观念强','忠诚可靠'], weaknesses: ['情绪化','过度保护','容易受伤','难以放手'] },
  { name: '狮子座', symbol: '♌', element: '火', modality: '固定', ruling_planet: '太阳',
    date_range: '7.23-8.22', overview: '狮子座象征着创造与荣耀。受太阳守护，自信大方、光芒四射。',
    personality: '自信热情、慷慨大方、有强烈的表现欲和领导欲。喜欢成为焦点，愿意保护和照顾身边的人。但有时骄傲自负，爱面子。',
    strengths: ['自信热情','领导力强','慷慨大方','创造力丰富'], weaknesses: ['骄傲自负','爱面子','专横霸道','挥霍'] },
  { name: '处女座', symbol: '♍', element: '土', modality: '变动', ruling_planet: '水星',
    date_range: '8.23-9.22', overview: '处女座象征着服务与完美。受水星守护，追求完美、注重细节。',
    personality: '认真细致、务实可靠、追求完美。分析能力强，做事一丝不苟。但有时过于挑剔，容易焦虑。',
    strengths: ['认真细致','分析力强','务实可靠','责任心强'], weaknesses: ['过度挑剔','容易焦虑','过于谨慎','缺乏自信'] },
  { name: '天秤座', symbol: '♎', element: '风', modality: '基本', ruling_planet: '金星',
    date_range: '9.23-10.23', overview: '天秤座象征着平衡与和谐。受金星守护，优雅迷人、追求公平。',
    personality: '温文尔雅、公正客观、社交能力强。追求和谐，厌恶冲突。但有时犹豫不决，为了取悦他人而委屈自己。',
    strengths: ['优雅得体','公正客观','社交能力强','审美品位高'], weaknesses: ['犹豫不决','过于讨好','逃避冲突','缺乏主见'] },
  { name: '天蝎座', symbol: '♏', element: '水', modality: '固定', ruling_planet: '冥王星',
    date_range: '10.24-11.22', overview: '天蝎座象征着深度与转化。受冥王星守护，意志坚定、洞察力强。',
    personality: '深沉内敛、意志坚强、洞察力超群。有极强的掌控欲，不达目的不罢休。但有时多疑、嫉妒心强。',
    strengths: ['意志坚定','洞察力强','忠诚专一','执行力强'], weaknesses: ['多疑善妒','控制欲强','报复心重','过于极端'] },
  { name: '射手座', symbol: '♐', element: '火', modality: '变动', ruling_planet: '木星',
    date_range: '11.23-12.21', overview: '射手座象征着探索与自由。受木星守护，乐观开朗、热爱自由。',
    personality: '乐观豁达、坦率真诚、热爱自由和冒险。对世界充满好奇，喜欢探索未知。但有时大大咧咧，说话不经大脑。',
    strengths: ['乐观开朗','坦率真诚','热爱学习','冒险精神'], weaknesses: ['鲁莽粗心','缺乏耐心','不负责任','过于直率'] },
  { name: '摩羯座', symbol: '♑', element: '土', modality: '基本', ruling_planet: '土星',
    date_range: '12.22-1.19', overview: '摩羯座象征着成就与责任。受土星守护，勤奋自律、志存高远。',
    personality: '踏实稳重、自律严格、目标明确。有超乎常人的耐心和毅力。但有时过于严肃，不善于表达情感。',
    strengths: ['勤奋努力','责任心强','自律严格','目标明确'], weaknesses: ['过于严肃','冷漠刻板','工作狂倾向','悲观保守'] },
  { name: '水瓶座', symbol: '♒', element: '风', modality: '固定', ruling_planet: '天王星',
    date_range: '1.20-2.18', overview: '水瓶座象征着革新与人道。受天王星守护，独立创新、思想前卫。',
    personality: '独立自主、思维独特、富有创造力。关心社会进步，有人道主义精神。但有时冷漠疏离，过于理性。',
    strengths: ['独立创新','思想前卫','人道主义','聪明理性'], weaknesses: ['冷漠疏离','叛逆固执','不按常理','情感表达困难'] },
  { name: '双鱼座', symbol: '♓', element: '水', modality: '变动', ruling_planet: '海王星',
    date_range: '2.19-3.20', overview: '双鱼座象征着灵性与融合。受海王星守护，感性梦幻、富有同情心。',
    personality: '温柔善良、想象力丰富、同理心极强。有艺术创造力，能感知到别人忽略的美好。但有时过于理想化，容易逃避现实。',
    strengths: ['善良温柔','想象力丰富','同理心强','艺术天赋'], weaknesses: ['逃避现实','过于敏感','缺乏界限','优柔寡断'] }
]

const planetsList = [
  { name: '太阳', symbol: '☉', category: '发光体', keywords: '自我、意志、生命力、创造力、父亲',
    meaning: '太阳代表一个人的核心自我、意志力和生命力。它揭示了你的基本性格、人生目标和表达自我的方式。太阳所在的星座和宫位是你人生舞台的主角所在。' },
  { name: '月亮', symbol: '☽', category: '发光体', keywords: '情感、潜意识、安全感、母亲、习惯',
    meaning: '月亮代表一个人的情感需求、潜意识和安全感模式。它揭示了你的情绪反应方式、亲密关系中的需求以及与母亲和家庭的关系。' },
  { name: '水星', symbol: '☿', category: '个人行星', keywords: '思维、沟通、学习、信息处理',
    meaning: '水星代表一个人的思维模式、沟通方式和学习方法。它揭示了你怎么思考、怎么表达、怎么学习新知识。' },
  { name: '金星', symbol: '♀', category: '个人行星', keywords: '爱情、美感、价值观、金钱、人际关系',
    meaning: '金星代表一个人的爱情观、审美偏好和价值观。它揭示了你怎么表达爱、被什么吸引以及如何处理人际关系和金钱。' },
  { name: '火星', symbol: '♂', category: '个人行星', keywords: '行动力、竞争、欲望、性、勇气',
    meaning: '火星代表一个人的行动力、竞争方式、欲望和性能量。它揭示了你如何追求目标、表达愤怒和处理冲突。' },
  { name: '木星', symbol: '♃', category: '社会行星', keywords: '幸运、成长、哲学、旅行、扩张',
    meaning: '木星代表一个人的幸运、成长和扩张领域。它揭示了你获取机会的方式和人生观、信仰体系。' },
  { name: '土星', symbol: '♄', category: '社会行星', keywords: '责任、纪律、限制、成就、时间',
    meaning: '土星代表一个人的责任感、自律能力和需要面对的挑战。它揭示了你需要付出努力才能获得成就的领域。' },
  { name: '天王星', symbol: '♅', category: '世代行星', keywords: '创新、自由、突变、独立、科技',
    meaning: '天王星代表变革、创新和对自由的渴望。它揭示了你在哪些方面追求独立和突破传统。' },
  { name: '海王星', symbol: '♆', category: '世代行星', keywords: '梦想、灵感、灵性、幻象、艺术',
    meaning: '海王星代表梦想、灵性和艺术创造力。它揭示了你的灵感来源和容易迷失的领域。' },
  { name: '冥王星', symbol: '♇', category: '世代行星', keywords: '转化、权力、深层心理、重生',
    meaning: '冥王星代表深度转化、权力和重生。它揭示了你在哪里经历最深层的蜕变和重生。' }
]

const housesList = [
  { number: 1, name: '命宫', area: '自我与人格', meaning: '自我形象、外貌、气质和第一印象。上升星座落在此，决定了你看世界的方式。' },
  { number: 2, name: '财帛宫', area: '财富与价值', meaning: '个人财富、物质资源、价值观和自我价值感。' },
  { number: 3, name: '兄弟宫', area: '沟通与学习', meaning: '沟通方式、早期教育、兄弟姐妹关系、短途旅行。' },
  { number: 4, name: '田宅宫', area: '家庭与根源', meaning: '原生家庭、童年环境、房产、家族根源。天底(IC)在此。' },
  { number: 5, name: '子女宫', area: '创造与恋爱', meaning: '创造力、浪漫恋爱、子女、娱乐和表达自我的方式。' },
  { number: 6, name: '奴仆宫', area: '工作与健康', meaning: '日常工作、健康习惯、服务和下属关系。' },
  { number: 7, name: '夫妻宫', area: '伴侣与合作', meaning: '婚姻、伴侣关系、一对一的合作。下降点(DESC)在此。' },
  { number: 8, name: '疾厄宫', area: '转变与深度', meaning: '深度转化、他人资源、遗产、投资、性和权力议题。' },
  { number: 9, name: '迁移宫', area: '探索与信仰', meaning: '高等教育、长途旅行、哲学、宗教和人生信仰。' },
  { number: 10, name: '官禄宫', area: '事业与名声', meaning: '事业、社会地位、名声和人生目标。天顶(MC)在此。' },
  { number: 11, name: '福德宫', area: '社群与理想', meaning: '朋友圈、社交团体、理想抱负和人道主义关怀。' },
  { number: 12, name: '玄秘宫', area: '潜意识与灵性', meaning: '潜意识、梦境、灵性、隐秘和幕后活动。' }
]

const aspectsList = [
  { name: '合相', symbol: '☌', angle: 0, orb: 8, nature: '中性', intensity: '极强',
    general: '两颗行星的能量融合，彼此加强。这是最强大的相位，形成性格中显著的复合特质。', advice: '学会调和与平衡两种能量。' },
  { name: '六分相', symbol: '⚹', angle: 60, orb: 6, nature: '和谐', intensity: '中等偏弱',
    general: '代表机会和潜能。需要通过主动努力来激发的天赋。', advice: '机会在那里，需要你主动去开启。' },
  { name: '四分相', symbol: '□', angle: 90, orb: 7, nature: '紧张', intensity: '强',
    general: '内在的紧张和挑战。两颗行星能量冲突，造成压力和摩擦，但正是这种张力驱使我们成长。', advice: '不要逃避压力，在摩擦中寻找突破。' },
  { name: '三分相', symbol: '△', angle: 120, orb: 8, nature: '和谐', intensity: '强',
    general: '天赋和流畅的能量。两颗行星之间形成自然的共鸣，才能来得轻松自然。', advice: '善用这份天赋，但不要因舒适而失去进取心。' },
  { name: '对分相', symbol: '☍', angle: 180, orb: 8, nature: '紧张', intensity: '极强',
    general: '对立与投射。两颗行星处于对峙状态，带来自我与他人之间的张力，但也是认识自我的重要途径。', advice: '学习在自我与他人之间找到平衡。' }
]

function toggleZodiacSign(name) { expandedZodiac.value = expandedZodiac.value === name ? '' : name }
function togglePlanet(name) { expandedPlanet.value = expandedPlanet.value === name ? '' : name }
function toggleHouse(num) { expandedHouse.value = expandedHouse.value === num ? null : num }
function toggleAspect(name) { expandedAspect.value = expandedAspect.value === name ? '' : name }

// 十神列表
const shishenList = [
  {
    name: '比肩', alias: '兄弟宫', badgeType: 'bijian',
    wuxingRelation: '与日主同五行同阴阳',
    meaning: '代表兄弟姐妹、朋友、同事、同辈竞争。主自我意识、独立精神。',
    positive: '自信、独立、有主见、坚韧不拔、有领导力',
    negative: '固执、自我中心、争强好胜、人际关系紧张'
  },
  {
    name: '劫财', alias: '败财', badgeType: 'jiecai',
    wuxingRelation: '与日主同五行异阴阳',
    meaning: '代表竞争、合作、破耗。主行动力、冒险精神。',
    positive: '进取心强、合作能力强、有魄力、敢于创新',
    negative: '冲动、好斗、破财、容易树敌'
  },
  {
    name: '食神', alias: '福星', badgeType: 'shishen',
    wuxingRelation: '日主所生，阴阳相同',
    meaning: '代表才华、口才、享受、创造力、子女。主温和善良、宽厚待人。',
    positive: '聪明智慧、有艺术天赋、生活安逸、人缘好',
    negative: '过于安逸、缺乏进取心、贪图享乐'
  },
  {
    name: '伤官', alias: '才华星', badgeType: 'shangguan',
    wuxingRelation: '日主所生，阴阳相异',
    meaning: '代表才华展示、创新、叛逆、自由。主聪明傲气、不拘一格。',
    positive: '才华横溢、创造力强、思维活跃、勇于革新',
    negative: '傲慢、叛逆、言辞犀利、易招是非'
  },
  {
    name: '正财', alias: '财帛宫', badgeType: 'zhengcai',
    wuxingRelation: '日主所克，阴阳相异',
    meaning: '代表稳定收入、妻子、财产。主勤俭持家、诚实稳重。',
    positive: '勤俭节约、诚实守信、努力致富、家庭幸福',
    negative: '过于节俭、保守、计较得失、缺乏冒险精神'
  },
  {
    name: '偏财', alias: '横财星', badgeType: 'piancai',
    wuxingRelation: '日主所克，阴阳相同',
    meaning: '代表意外之财、投资、父亲。主慷慨大方、善于理财。',
    positive: '慷慨大方、善于投资、人脉广、财运旺',
    negative: '奢侈浪费、好赌、财务起伏大'
  },
  {
    name: '正官', alias: '官禄宫', badgeType: 'zhengguan',
    wuxingRelation: '克制日主，阴阳相异',
    meaning: '代表官职、名誉、法律、丈夫。主正直光明、克己复礼。',
    positive: '正直负责、遵纪守法、有威信、事业有成',
    negative: '过于保守、优柔寡断、压力大、容易受约束'
  },
  {
    name: '七杀', alias: '偏官/将星', badgeType: 'pianguan',
    wuxingRelation: '克制日主，阴阳相同',
    meaning: '代表权力、竞争、挑战、小人。主果断刚毅、不畏困难。',
    positive: '果断刚毅、不畏强权、有领导力、事业心强',
    negative: '暴躁、好斗、易招小人、压力巨大'
  },
  {
    name: '正印', alias: '印绶宫', badgeType: 'zhengyin',
    wuxingRelation: '生助日主，阴阳相异',
    meaning: '代表母亲、学业、文书、贵人。主仁慈善良、重视学问。',
    positive: '仁慈善良、学识渊博、有贵人相助、心地纯净',
    negative: '依赖性强、缺乏主见、容易满足、不切实际'
  },
  {
    name: '偏印', alias: '枭神', badgeType: 'pianyin',
    wuxingRelation: '生助日主，阴阳相同',
    meaning: '代表继母、偏门学问、宗教、灵感。主敏慧多思、善解人意。',
    positive: '领悟力强、有特殊才能、思维深刻、善解人意',
    negative: '孤僻、多疑、精神不稳定、不近人情'
  }
]

function toggleShishen(name) {
  expandedShishen.value = expandedShishen.value === name ? '' : name
}

// 五行圆环位置
const wuxingCircleItems = [
  { name: '金', key: 'metal' },
  { name: '水', key: 'water' },
  { name: '木', key: 'wood' },
  { name: '火', key: 'fire' },
  { name: '土', key: 'earth' }
]

function wuxingNodeStyle(index) {
  const total = wuxingCircleItems.length
  const radius = 110
  const angle = (index * (360 / total) - 90) * (Math.PI / 180)
  const cx = 150
  const cy = 150
  const x = cx + radius * Math.cos(angle) - 32
  const y = cy + radius * Math.sin(angle) - 32
  return {
    position: 'absolute',
    left: x + 'rpx',
    top: y + 'rpx'
  }
}

// 神煞列表
const shenshaList = [
  { name: '天乙贵人', type: 'good', typeLabel: '吉神', desc: '最尊贵之神，主贵人扶持，逢凶化吉' },
  { name: '文昌贵人', type: 'good', typeLabel: '吉神', desc: '主学业功名，文采出众，科甲之喜' },
  { name: '桃花', type: 'neutral', typeLabel: '中性', desc: '主异性缘、人缘好，但需防感情纠葛' },
  { name: '驿马', type: 'neutral', typeLabel: '中性', desc: '主奔波劳碌，迁移变动，宜外出发展' },
  { name: '羊刃', type: 'bad', typeLabel: '凶神', desc: '性刚果断，但易冲动惹祸，需修身养性' },
  { name: '华盖', type: 'neutral', typeLabel: '中性', desc: '主孤芳自赏，有艺术天赋，宜学道修行' },
  { name: '孤辰', type: 'bad', typeLabel: '凶神', desc: '主孤独，六亲缘薄，宜培养人际关系' },
  { name: '将星', type: 'good', typeLabel: '吉神', desc: '主领导才能，有权威，事业有成就' },
  { name: '劫煞', type: 'bad', typeLabel: '凶神', desc: '主意外灾祸，竞争激烈，需谨慎行事' },
  { name: '天德贵人', type: 'good', typeLabel: '吉神', desc: '主天生德性，心地善良，上天眷顾' },
  { name: '月德贵人', type: 'good', typeLabel: '吉神', desc: '主阴德护佑，女性缘佳，心地慈祥' },
  { name: '空亡', type: 'bad', typeLabel: '凶神', desc: '主虚无、空想，理想难以实现，宜务实' }
]
</script>

<style lang="scss" scoped>
.page-reference {
  min-height: 100vh;

  &__scroll {
    height: 100vh;
  }
}

// ===== 导航栏 =====
.nav-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(180deg, var(--bg-nav) 0%, var(--bg-nav-transparent) 100%);
  backdrop-filter: blur(10rpx);

  &__content {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 88rpx;
    padding: 0 24rpx;
  }

  &__title {
    font-size: 36rpx;
    color: var(--accent-light);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
    letter-spacing: 6rpx;
  }
}

// ===== 区块 =====
.section-card {
  margin: 20rpx 20rpx;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
  padding-left: 8rpx;

  &__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44rpx;
    height: 44rpx;
    background: var(--accent-15);
    border: 1rpx solid var(--accent-30);
    border-radius: 8rpx;
    font-size: 24rpx;
    color: var(--accent);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;

    &--wood {
      background: rgba(74, 124, 89, 0.2);
      border-color: rgba(74, 124, 89, 0.3);
      color: var(--color-positive);
    }

    &--fire {
      background: var(--vermillion-15);
      border-color: var(--vermillion-30);
      color: var(--vermillion);
    }

    &--gold {
      background: var(--accent-15);
      border-color: var(--accent-30);
      color: var(--accent-light);
    }

    &--water {
      background: rgba(44, 62, 107, 0.2);
      border-color: rgba(44, 62, 107, 0.3);
      color: var(--wx-water-light);
    }

    &--vermillion {
      background: var(--vermillion-12);
      border-color: var(--vermillion-30);
      color: var(--vermillion-light);
    }
  }

  &__text {
    font-size: 30rpx;
    color: var(--text-primary);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
  }
}

// ===== 十神列表 =====
.shishen-grid {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.shishen-card {
  background: var(--bg-card);
  border: 1rpx solid var(--border-color);
  border-radius: 12rpx;
  overflow: hidden;
  transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;

  @media (hover: hover) {
    &:hover {
      border-color: var(--accent-20);
      background: rgba(42, 26, 16, 0.75);
    }
  }

  &--expanded {
    border-color: var(--accent-30);
    background: var(--bg-card-hover);
    box-shadow: 0 0 20rpx var(--accent-06);
  }

  &__header {
    display: flex;
    align-items: center;
    padding: 16rpx 20rpx;
    gap: 12rpx;
    cursor: pointer;
  }

  &__alias {
    flex: 1;
    font-size: 24rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }

  &__arrow {
    font-size: 20rpx;
    color: var(--text-placeholder);
  }

  &__body {
    padding: 0 20rpx 20rpx;
    animation: expand-in 0.3s ease;
  }
}

@keyframes expand-in {
  from {
    opacity: 0;
    transform: translateY(-10rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.shishen-detail {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  padding: 12rpx;
  background: var(--bg-root-40, rgba(26,10,0,0.4));
  border-radius: 8rpx;
  border-top: 1rpx solid var(--border-50);

  &__row {
    display: flex;
    gap: 4rpx;
  }

  .detail-label {
    font-size: 22rpx;
    color: var(--accent);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    white-space: nowrap;
  }

  .detail-value {
    font-size: 22rpx;
    color: var(--text-body);
    line-height: 1.6;
    flex: 1;

    &--good {
      color: var(--color-positive);
    }

    &--bad {
      color: var(--vermillion-light);
    }
  }
}

// ===== 五行关系图 =====
.wuxing-relation {
  padding: 8px 0;
}

.wuxing-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;

  &__circle {
    position: relative;
    width: 300rpx;
    height: 300rpx;
    margin-bottom: 24rpx;
  }
}

// 五行连线用伪元素模拟（简化版）
.wuxing-diagram__circle {
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 200rpx;
    height: 200rpx;
    transform: translate(-50%, -50%);
    border: 2rpx solid var(--accent-20);
    border-radius: 50%;
  }
}

.wuxing-node {
  transition: transform 0.3s ease;
  cursor: pointer;

  @media (hover: hover) {
    &:hover {
      transform: scale(1.08);
    }
  }

  &:active {
    transform: scale(1.1);
  }
}

.wuxing-legend {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  width: 100%;
}

.legend-section {
  display: flex;
  align-items: flex-start;
  gap: 4rpx;
}

.legend-label {
  font-size: 24rpx;
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  white-space: nowrap;

  &--sheng {
    color: var(--color-positive);
  }

  &--ke {
    color: var(--vermillion);
  }
}

.legend-text {
  font-size: 24rpx;
  color: var(--text-body);
  line-height: 1.6;
}

// ===== 神煞表格 =====
.shensha-table {
  &__header {
    display: flex;
    padding: 12rpx 0;
    border-bottom: 1rpx solid var(--accent-30);
    margin-bottom: 8rpx;
  }

  &__row {
    display: flex;
    padding: 14rpx 0;
    border-bottom: 1rpx solid var(--border-40);

    &:last-child {
      border-bottom: none;
    }
  }
}

.shensha-col {
  font-size: 24rpx;
  color: var(--text-body);

  &--name {
    width: 160rpx;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    color: var(--text-primary);
  }

  &--type {
    width: 100rpx;
    display: flex;
    align-items: center;
  }

  &--desc {
    flex: 1;
    font-size: 22rpx;
  }
}

.shensha-type-badge {
  font-size: 20rpx;
  padding: 2rpx 10rpx;
  border-radius: 6rpx;

  &.shensha-type--good {
    background: rgba(74, 124, 89, 0.2);
    color: var(--color-positive);
  }

  &.shensha-type--neutral {
    background: var(--accent-15);
    color: var(--accent);
  }

  &.shensha-type--bad {
    background: var(--vermillion-15);
    color: var(--vermillion-light);
  }
}

// ===== 关于应用 =====
.about-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.about-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20rpx;

  &__text {
    font-size: 40rpx;
    color: var(--accent-light);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
    letter-spacing: 8rpx;
    margin-bottom: 6rpx;
  }

  &__ver {
    font-size: 22rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }
}

.about-divider {
  display: flex;
  align-items: center;
  gap: 16rpx;
  width: 80%;
  margin-bottom: 20rpx;

  &__line {
    flex: 1;
    height: 1rpx;
    background: linear-gradient(90deg, transparent, var(--accent-30), transparent);
  }

  &__diamond {
    width: 10rpx;
    height: 10rpx;
    background: var(--accent-50);
    transform: rotate(45deg);
  }
}

.about-desc {
  font-size: 24rpx;
  color: var(--text-body);
  line-height: 1.8;
  text-indent: 2em;
  margin-bottom: 20rpx;
}

.about-disclaimer {
  display: flex;
  gap: 8rpx;
  padding: 16rpx;
  background: var(--vermillion-06);
  border: 1rpx solid var(--vermillion-15);
  border-radius: 10rpx;
  margin-bottom: 20rpx;

  &__icon {
    width: 36rpx;
    height: 36rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--vermillion-15);
    border-radius: 50%;
    font-size: 20rpx;
    color: var(--vermillion-light);
    font-weight: bold;
    flex-shrink: 0;
  }

  &__text {
    font-size: 22rpx;
    color: var(--text-body);
    line-height: 1.6;
    flex: 1;
  }
}

.about-credits {
  &__text {
    font-size: 22rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    letter-spacing: 4rpx;
  }
}

.safe-bottom {
  height: calc(20rpx + env(safe-area-inset-bottom));
}

// 百科模式切换
.ref-mode-switch {
  display: flex; margin: 16rpx 24rpx; gap: 0;
  border-radius: 12rpx; overflow: hidden;
  border: 1rpx solid var(--border-50);
}
.ref-mode-btn {
  flex: 1; display: flex; align-items: center; justify-content: center;
  padding: 16rpx 0; background: var(--bg-input);
  font-size: 28rpx; color: var(--text-muted);
  font-family: 'STKaiti','KaiTi','楷体',serif; transition: all 0.3s;
  &--active { background: var(--accent-12); color: var(--accent-light); font-weight: bold; }
}
.zodiac-ref__symbol { font-size: 32rpx; margin-right: 12rpx; }
.zodiac-ref__num {
  width: 40rpx; height: 40rpx; display: flex; align-items: center; justify-content: center;
  background: var(--accent-12); border-radius: 8rpx; margin-right: 12rpx;
  font-size: 22rpx; color: var(--accent); font-weight: bold;
}
</style>
