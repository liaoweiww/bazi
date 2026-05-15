<template>
  <!-- 古籍参考页 -->
  <view class="page-reference">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-bar__content">
        <text class="nav-bar__title">古籍参考</text>
      </view>
    </view>

    <scroll-view
      class="page-reference__scroll"
      scroll-y
      enhanced
      :show-scrollbar="false"
    >
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
            @tap="toggleShishen(item.name)"
          >
            <view class="shishen-card__header">
              <ShishenBadge :label="item.name" :type="item.badgeType" />
              <text class="shishen-card__alias">{{ item.alias }}</text>
              <text class="shishen-card__arrow">
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
  background: linear-gradient(180deg, rgba(26, 10, 0, 0.98) 0%, rgba(26, 10, 0, 0.85) 100%);
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
    color: #d4af37;
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
    background: rgba(201, 169, 110, 0.15);
    border: 1rpx solid rgba(201, 169, 110, 0.3);
    border-radius: 8rpx;
    font-size: 24rpx;
    color: #c9a96e;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;

    &--wood {
      background: rgba(74, 124, 89, 0.2);
      border-color: rgba(74, 124, 89, 0.3);
      color: #5a9a6a;
    }

    &--fire {
      background: rgba(196, 30, 58, 0.15);
      border-color: rgba(196, 30, 58, 0.3);
      color: #c41e3a;
    }

    &--gold {
      background: rgba(212, 175, 55, 0.15);
      border-color: rgba(212, 175, 55, 0.3);
      color: #d4af37;
    }

    &--water {
      background: rgba(44, 62, 107, 0.2);
      border-color: rgba(44, 62, 107, 0.3);
      color: #5a7ec0;
    }

    &--vermillion {
      background: rgba(196, 30, 58, 0.12);
      border-color: rgba(196, 30, 58, 0.35);
      color: #e06070;
    }
  }

  &__text {
    font-size: 30rpx;
    color: #f5f0e8;
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
  background: rgba(42, 26, 16, 0.6);
  border: 1rpx solid #3d2b1a;
  border-radius: 12rpx;
  overflow: hidden;
  transition: all 0.3s ease;

  &--expanded {
    border-color: rgba(201, 169, 110, 0.3);
    background: rgba(42, 26, 16, 0.8);
    box-shadow: 0 0 20rpx rgba(201, 169, 110, 0.06);
  }

  &__header {
    display: flex;
    align-items: center;
    padding: 16rpx 20rpx;
    gap: 12rpx;
  }

  &__alias {
    flex: 1;
    font-size: 24rpx;
    color: #8b7355;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }

  &__arrow {
    font-size: 20rpx;
    color: #5a4a3a;
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
  background: rgba(26, 10, 0, 0.4);
  border-radius: 8rpx;
  border-top: 1rpx solid rgba(61, 43, 26, 0.5);

  &__row {
    display: flex;
    gap: 4rpx;
  }

  .detail-label {
    font-size: 22rpx;
    color: #c9a96e;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    white-space: nowrap;
  }

  .detail-value {
    font-size: 22rpx;
    color: #c0b090;
    line-height: 1.6;
    flex: 1;

    &--good {
      color: #5a9a6a;
    }

    &--bad {
      color: #e06070;
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
    border: 2rpx solid rgba(201, 169, 110, 0.2);
    border-radius: 50%;
  }
}

.wuxing-node {
  transition: transform 0.3s ease;

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
    color: #5a9a6a;
  }

  &--ke {
    color: #c41e3a;
  }
}

.legend-text {
  font-size: 24rpx;
  color: #c0b090;
  line-height: 1.6;
}

// ===== 神煞表格 =====
.shensha-table {
  &__header {
    display: flex;
    padding: 12rpx 0;
    border-bottom: 1rpx solid rgba(201, 169, 110, 0.3);
    margin-bottom: 8rpx;
  }

  &__row {
    display: flex;
    padding: 14rpx 0;
    border-bottom: 1rpx solid rgba(61, 43, 26, 0.4);

    &:last-child {
      border-bottom: none;
    }
  }
}

.shensha-col {
  font-size: 24rpx;
  color: #c0b090;

  &--name {
    width: 160rpx;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    color: #f5f0e8;
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
    color: #5a9a6a;
  }

  &.shensha-type--neutral {
    background: rgba(201, 169, 110, 0.15);
    color: #c9a96e;
  }

  &.shensha-type--bad {
    background: rgba(196, 30, 58, 0.15);
    color: #e06070;
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
    color: #d4af37;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
    letter-spacing: 8rpx;
    margin-bottom: 6rpx;
  }

  &__ver {
    font-size: 22rpx;
    color: #8b7355;
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
    background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.3), transparent);
  }

  &__diamond {
    width: 10rpx;
    height: 10rpx;
    background: rgba(212, 175, 55, 0.5);
    transform: rotate(45deg);
  }
}

.about-desc {
  font-size: 24rpx;
  color: #c0b090;
  line-height: 1.8;
  text-indent: 2em;
  margin-bottom: 20rpx;
}

.about-disclaimer {
  display: flex;
  gap: 8rpx;
  padding: 16rpx;
  background: rgba(196, 30, 58, 0.06);
  border: 1rpx solid rgba(196, 30, 58, 0.15);
  border-radius: 10rpx;
  margin-bottom: 20rpx;

  &__icon {
    width: 36rpx;
    height: 36rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(196, 30, 58, 0.15);
    border-radius: 50%;
    font-size: 20rpx;
    color: #e06070;
    font-weight: bold;
    flex-shrink: 0;
  }

  &__text {
    font-size: 22rpx;
    color: #c0a090;
    line-height: 1.6;
    flex: 1;
  }
}

.about-credits {
  &__text {
    font-size: 22rpx;
    color: #8b7355;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    letter-spacing: 4rpx;
  }
}

.safe-bottom {
  height: calc(20rpx + env(safe-area-inset-bottom));
}
</style>
