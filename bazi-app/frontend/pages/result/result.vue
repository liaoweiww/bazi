<template>
  <!-- 命盘解读页 -->
  <view class="page-result">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-bar__content">
        <view class="nav-back" @tap="goBack" aria-label="返回排盘页">
          <text class="nav-back__arrow" aria-hidden="true">&#xe600;</text>
        </view>
        <text class="nav-bar__title">{{ activeSystem === 'zodiac' ? '星盘解读' : '命盘解读' }}</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <scroll-view
      class="page-result__scroll"
      scroll-y
      enhanced
      :show-scrollbar="false"
    >
      <!-- 加载状态 -->
      <view class="loading-section" v-if="loading">
        <view class="loading-yinyang"></view>
        <text class="loading-text">推演命盘中...</text>
      </view>

      <!-- 排盘结果 -->
      <template v-if="!loading && baziData">
        <!-- 用户信息条 -->
        <view class="user-info-bar">
          <view class="user-info-item">
            <text class="info-label">姓名</text>
            <text class="info-value">{{ baziData.name }}</text>
          </view>
          <view class="user-info-item">
            <text class="info-label">性别</text>
            <text class="info-value">{{ baziData.gender }}</text>
          </view>
          <view class="user-info-item">
            <text class="info-label">{{ baziData.gender === '男' ? '乾造' : '坤造' }}</text>
            <text class="info-value">{{ baziData.birth_date }}</text>
          </view>
        </view>

        <!-- 八字命盘卡 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon">命</view>
            <text class="section-title__text">八字命盘</text>
          </view>
          <classic-border variant="gold">
            <view class="bazi-grid">
              <!-- 四柱表头 -->
              <view class="bazi-grid__header">
                <text class="bazi-grid__header-label">年柱</text>
                <text class="bazi-grid__header-label">月柱</text>
                <text class="bazi-grid__header-label bazi-grid__header-label--rizhu">日柱</text>
                <text class="bazi-grid__header-label">时柱</text>
              </view>
              <!-- 天干行 -->
              <view class="bazi-grid__row">
                <PillarCard
                  v-for="(pillar, key) in pillars"
                  :key="key"
                  :label="pillar.label"
                  :gan="pillar.gan"
                  :zhi="pillar.zhi"
                  :canggan="pillar.canggan"
                  :shishen="pillar.shishen"
                  :nayin="pillar.nayin"
                  :isRizhu="pillar.isRizhu"
                />
              </view>
            </view>
          </classic-border>
        </view>

        <!-- 五行力量卡 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--fire">五</view>
            <text class="section-title__text">五行力量</text>
          </view>
          <classic-border>
            <WuxingChart
              :wuxingData="baziData.wuxing_count"
              :riStrength="baziData.rizhu_strong"
            />
            <!-- 五行数量统计 -->
            <view class="wuxing-stats">
              <view
                v-for="(count, name) in baziData.wuxing_count"
                :key="name"
                class="wuxing-stat"
              >
                <ganzhi-tag :label="name" :wuxing="wuxingKey(name)" size="sm" />
                <text class="wuxing-stat__count">×{{ count }}</text>
              </view>
            </view>
          </classic-border>
        </view>

        <!-- 格局分析卡 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--gold">格</view>
            <text class="section-title__text">格局分析</text>
          </view>
          <classic-border variant="gold">
            <view class="pattern-card">
              <view class="pattern-name">
                <text class="pattern-name__icon">局</text>
                <text class="pattern-name__text">{{ baziData.pattern }}</text>
              </view>
              <view class="pattern-desc">
                <text class="pattern-desc__text">{{ baziData.pattern_desc }}</text>
              </view>
            </view>
          </classic-border>
        </view>

        <!-- 喜用神卡 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--water">用</view>
            <text class="section-title__text">喜用神</text>
          </view>
          <classic-border>
            <view class="yongshen-card">
              <!-- 用神 -->
              <view class="yongshen-row">
                <text class="yongshen-label yongshen-label--god">用 神</text>
                <view class="yongshen-tags">
                  <ganzhi-tag
                    v-for="g in baziData.yongshen.god"
                    :key="'god-' + g"
                    :label="g"
                    :wuxing="wuxingKey(g)"
                    size="md"
                  />
                </view>
              </view>
              <!-- 忌神 -->
              <view class="yongshen-row">
                <text class="yongshen-label yongshen-label--ji">忌 神</text>
                <view class="yongshen-tags">
                  <ganzhi-tag
                    v-for="j in baziData.yongshen.ji"
                    :key="'ji-' + j"
                    :label="j"
                    :wuxing="wuxingKey(j)"
                    size="md"
                  />
                </view>
              </view>
              <!-- 调候建议 -->
              <view class="tiaohou-section">
                <text class="tiaohou-label">调候建议</text>
                <text class="tiaohou-text">{{ baziData.yongshen.tiaohou }}</text>
              </view>
            </view>
          </classic-border>
        </view>

        <!-- 大运流年卡 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--vermillion">运</view>
            <text class="section-title__text">大运流年</text>
          </view>
          <classic-border>
            <!-- 起运年龄 -->
            <view class="dayun-start">
              <text class="dayun-start__label">起运年龄</text>
              <text class="dayun-start__age">{{ baziData.dayun_start_age }}岁</text>
            </view>
            <!-- 大运时间轴 -->
            <DayunTimeline
              :dayunList="dayunListWithCurrent"
              @select="onDayunSelect"
            />
          </classic-border>
        </view>

        <!-- 流年分析卡 -->
        <view class="section-card" v-if="baziData.current_liunian">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--vermillion">年</view>
            <text class="section-title__text">流年分析</text>
          </view>
          <classic-border variant="vermillion">
            <view class="liunian-card">
              <view class="liunian-header">
                <text class="liunian-year">{{ baziData.current_liunian.year }}年</text>
                <view class="liunian-ganzhi">
                  <ganzhi-tag :label="baziData.current_liunian.gan" wuxing="fire" size="lg" />
                  <ganzhi-tag :label="baziData.current_liunian.zhi" wuxing="fire" size="lg" />
                </view>
                <view class="liunian-rating" :class="ratingClass">
                  <text>{{ baziData.current_liunian.rating }}</text>
                </view>
              </view>
              <text class="liunian-nayin">纳音：{{ baziData.current_liunian.nayin }}</text>
              <text class="liunian-desc">{{ baziData.current_liunian.desc }}</text>
            </view>
          </classic-border>
        </view>
      </template>

      <!-- ===== 星座星盘结果 ===== -->
      <template v-if="!loading && zodiacData && activeSystem === 'zodiac'">
        <!-- 用户信息条 -->
        <view class="user-info-bar">
          <view class="user-info-item">
            <text class="info-label">姓名</text>
            <text class="info-value">{{ zodiacData.name }}</text>
          </view>
          <view class="user-info-item">
            <text class="info-label">性别</text>
            <text class="info-value">{{ zodiacData.gender }}</text>
          </view>
          <view class="user-info-item">
            <text class="info-label">出生</text>
            <text class="info-value">{{ zodiacData.birth_datetime }}</text>
          </view>
        </view>

        <!-- 日月升三大标签 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon">星</view>
            <text class="section-title__text">日月升 · 三大星座</text>
          </view>
          <classic-border variant="gold">
            <view class="big-three">
              <view class="big-three__item">
                <text class="big-three__label">太阳星座</text>
                <ZodiacSignBadge
                  :name="zodiacData.bigThree?.sun?.sign || sunSign"
                  :symbol="zodiacData.bigThree?.sun?.symbol || sunSymbol"
                  :element="sunElement"
                />
                <text class="big-three__desc">你的核心自我、意志力和生命力所在</text>
              </view>
              <view class="big-three__item">
                <text class="big-three__label">月亮星座</text>
                <ZodiacSignBadge
                  :name="zodiacData.bigThree?.moon?.sign || moonSign"
                  :symbol="zodiacData.bigThree?.moon?.symbol || moonSymbol"
                  :element="moonElement"
                />
                <text class="big-three__desc">你的情感需求、潜意识和安全感</text>
              </view>
              <view class="big-three__item">
                <text class="big-three__label">上升星座</text>
                <ZodiacSignBadge
                  :name="zodiacData.bigThree?.ascendant?.sign || ascSign"
                  :symbol="zodiacData.bigThree?.ascendant?.symbol || ascSymbol"
                  :element="ascElement"
                />
                <text class="big-three__desc">你给别人的第一印象和人格面具</text>
              </view>
            </view>
          </classic-border>
        </view>

        <!-- 星盘图 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon">盘</view>
            <text class="section-title__text">星盘图</text>
          </view>
          <classic-border>
            <ZodiacWheel
              :planets="zodiacData.planets || []"
              :houses="zodiacData.houses || []"
              :ascDegree="zodiacData.angles?.ascendant || 0"
            />
          </classic-border>
        </view>

        <!-- 行星落座落宫表 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon">星</view>
            <text class="section-title__text">行星位置</text>
          </view>
          <classic-border>
            <view class="planet-table">
              <view class="planet-table__header">
                <text class="planet-table__th" style="flex:1.2">行星</text>
                <text class="planet-table__th" style="flex:1.5">落座</text>
                <text class="planet-table__th" style="flex:1.2">度数</text>
                <text class="planet-table__th" style="flex:1">宫位</text>
              </view>
              <view class="planet-table__row" v-for="p in zodiacData.planets" :key="p.name_cn">
                <text class="planet-table__td" style="flex:1.2">{{ planetSymbol(p.name_cn) }} {{ p.name_cn }}</text>
                <text class="planet-table__td" style="flex:1.5">{{ p.sign_symbol }} {{ p.sign }}</text>
                <text class="planet-table__td" style="flex:1.2">{{ p.degree_in_sign }}°</text>
                <text class="planet-table__td" style="flex:1">第{{ p.house }}宫</text>
              </view>
            </view>
          </classic-border>
        </view>

        <!-- 元素分布 -->
        <view class="section-card">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--fire">元</view>
            <text class="section-title__text">元素分布</text>
          </view>
          <classic-border>
            <ElementChart
              :elements="zodiacData.analysis?.elements || {}"
              :dominant="zodiacData.analysis?.dominant_element || ''"
              :summary="zodiacData.analysis?.summary || ''"
            />
          </classic-border>
        </view>

        <!-- 主要相位 -->
        <view class="section-card" v-if="zodiacData.aspects?.length">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--gold">相</view>
            <text class="section-title__text">主要相位</text>
          </view>
          <classic-border>
            <view class="aspects-list">
              <AspectBar
                v-for="(asp, idx) in zodiacData.aspects.slice(0, 10)"
                :key="idx"
                :planet1="asp.planet1"
                :planet2="asp.planet2"
                :symbol="asp.aspect_symbol"
                :type="asp.aspect_name_cn"
                :keyword="asp.keyword"
                :nature="asp.nature"
              />
            </view>
          </classic-border>
        </view>

        <!-- 格局检测 -->
        <view class="section-card" v-if="zodiacData.patterns?.length">
          <view class="section-title">
            <view class="section-title__icon section-title__icon--vermillion">局</view>
            <text class="section-title__text">特殊格局</text>
          </view>
          <classic-border variant="vermillion">
            <view class="patterns-list">
              <view class="pattern-tag" v-for="pat in zodiacData.patterns" :key="pat">
                <text>{{ pat }}</text>
              </view>
            </view>
          </classic-border>
        </view>
      </template>

      <!-- 空状态 -->
      <view class="empty-section" v-if="!loading && !baziData && !zodiacData">
        <view class="empty-icon">命</view>
        <text class="empty-title">暂无命盘数据</text>
        <text class="empty-desc">请先在"首页"选择排盘方式并输入信息</text>
        <view class="empty-btns">
          <view class="empty-btn" @tap="goToIndex">
            <text>八字排盘</text>
          </view>
          <view class="empty-btn" @tap="goToIndex">
            <text>星座命盘</text>
          </view>
        </view>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ClassicBorder from '@/components/ClassicBorder.vue'
import PillarCard from '@/components/PillarCard.vue'
import WuxingChart from '@/components/WuxingChart.vue'
import GanzhiTag from '@/components/GanzhiTag.vue'
import DayunTimeline from '@/components/DayunTimeline.vue'
import ZodiacSignBadge from '@/components/ZodiacSignBadge.vue'
import ZodiacWheel from '@/components/ZodiacWheel.vue'
import AspectBar from '@/components/AspectBar.vue'
import ElementChart from '@/components/ElementChart.vue'
import { mockBaziResult, mockZodiacChart } from '@/api/index.js'

const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 20)
const loading = ref(true)
const activeSystem = ref('bazi')
const baziData = ref(null)
const zodiacData = ref(null)

// 四柱数据
const pillars = computed(() => {
  if (!baziData.value) return []
  const data = baziData.value.bazi
  return [
    { ...data.year, label: '年柱', isRizhu: false },
    { ...data.month, label: '月柱', isRizhu: false },
    { ...data.day, label: '日柱', isRizhu: true },
    { ...data.hour, label: '时柱', isRizhu: false }
  ]
})

// 大运列表添加当前标记
const dayunListWithCurrent = computed(() => {
  if (!baziData.value) return []
  const currentYear = new Date().getFullYear()
  return baziData.value.dayun_list.map(item => {
    const [startYear, endYear] = (item.years || '').split('-').map(Number)
    const isCurrent = currentYear >= startYear && currentYear <= endYear
    return { ...item, isCurrent }
  })
})

// 五行文字->key
function wuxingKey(name) {
  const map = { '金': 'metal', '木': 'wood', '水': 'water', '火': 'fire', '土': 'earth' }
  return map[name] || 'earth'
}

// 流年吉凶样式
const ratingClass = computed(() => {
  if (!baziData.value?.current_liunian) return ''
  const rating = baziData.value.current_liunian.rating
  if (rating.includes('吉')) return 'rating-good'
  if (rating.includes('凶')) return 'rating-bad'
  return 'rating-neutral'
})

// 大运选择
function onDayunSelect({ index, data }) {
  console.log('选中大运：', index, data)
}

// 返回上一页
function goBack() {
  uni.switchTab({ url: '/pages/index/index' })
}

// 前往排盘
function goToIndex() {
  uni.switchTab({ url: '/pages/index/index' })
}

// === 星座相关 ===
const ELEMENT_MAP = { '火': '火', '土': '土', '风': '风', '水': '水' }

// 从zodiacData推导日月升 (若不存在interpretation)
const sunPlanet = computed(() => zodiacData.value?.planets?.find(p => p.name_cn === '太阳'))
const moonPlanet = computed(() => zodiacData.value?.planets?.find(p => p.name_cn === '月亮'))
const sunSign = computed(() => sunPlanet.value?.sign || '')
const sunSymbol = computed(() => sunPlanet.value?.sign_symbol || '')
const sunElement = computed(() => ELEMENT_MAP[sunPlanet.value?.sign_element] || '火')
const moonSign = computed(() => moonPlanet.value?.sign || '')
const moonSymbol = computed(() => moonPlanet.value?.sign_symbol || '')
const moonElement = computed(() => ELEMENT_MAP[moonPlanet.value?.sign_element] || '水')
const ascSign = computed(() => zodiacData.value?.angles?.ascendant_sign || '')
const ascSymbol = computed(() => zodiacData.value?.angles?.ascendant_symbol || '')
const ascElement = computed(() => {
  const s = zodiacData.value?.angles?.ascendant_sign
  if (!s) return '风'
  const el = zodiacData.value?.planets?.find(p => p.sign === s)
  return ELEMENT_MAP[el?.sign_element] || '风'
})

function planetSymbol(name) {
  const map = { '太阳':'☉','月亮':'☽','水星':'☿','金星':'♀','火星':'♂',
                '木星':'♃','土星':'♄','天王星':'♅','海王星':'♆','冥王星':'♇' }
  return map[name] || '•'
}

function zodiacInterpretation(planetName, signName) {
  return ''  // 后端接口可选
}

onMounted(() => {
  // 读取存储中的系统模式
  try {
    const system = uni.getStorageSync('activeSystem')
    if (system) activeSystem.value = system
  } catch (e) {}

  setTimeout(() => {
    if (activeSystem.value === 'zodiac') {
      zodiacData.value = mockZodiacChart()
      // 将后端数据结构转换为UI需要的大三角格式
      const sunP = zodiacData.value.planets.find(p => p.name_cn === '太阳')
      const moonP = zodiacData.value.planets.find(p => p.name_cn === '月亮')
      zodiacData.value.bigThree = {
        sun: { sign: sunP?.sign, symbol: sunP?.sign_symbol },
        moon: { sign: moonP?.sign, symbol: moonP?.sign_symbol },
        ascendant: {
          sign: zodiacData.value.angles.ascendant_sign,
          symbol: zodiacData.value.angles.ascendant_symbol
        }
      }
    } else {
      baziData.value = mockBaziResult()
    }
    loading.value = false
  }, 1200)
})
</script>

<style lang="scss" scoped>
.page-result {
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
    justify-content: space-between;
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

.nav-back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;

  @media (hover: hover) {
    &:hover {
      background: rgba(201, 169, 110, 0.1);
      border-radius: 12rpx;
    }
  }

  &__arrow {
    font-size: 32rpx;
    color: var(--accent);
  }
}

.nav-placeholder {
  width: 64rpx;
}

// ===== 加载状态 =====
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 0;
}

.loading-yinyang {
  width: 80rpx;
  height: 80rpx;
  border: 3rpx solid var(--accent-30);
  border-top-color: var(--accent-light);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin-bottom: 24rpx;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: var(--text-muted);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  animation: text-fade 1.5s ease-in-out infinite;
}

@keyframes text-fade {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

// ===== 用户信息条 =====
.user-info-bar {
  display: flex;
  justify-content: center;
  gap: 32rpx;
  padding: 16rpx 24rpx;
  background: var(--bg-card);
  border-bottom: 1rpx solid var(--border-50);
}

.user-info-item {
  display: flex;
  align-items: center;
  gap: 8rpx;

  .info-label {
    font-size: 22rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    padding: 2rpx 10rpx;
    border: 1rpx solid rgba(139, 115, 85, 0.4);
    border-radius: 4rpx;
  }

  .info-value {
    font-size: 24rpx;
    color: var(--text-primary);
  }
}

// ===== 区块卡片通用 =====
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

// ===== 八字命盘网格 =====
.bazi-grid {
  &__header {
    display: flex;
    justify-content: space-around;
    margin-bottom: 16rpx;
    padding-bottom: 12rpx;
    border-bottom: 1rpx solid var(--border-50);
  }

  &__header-label {
    font-size: 24rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    text-align: center;
    min-width: 130rpx;

    &--rizhu {
      color: var(--accent-light);
    }
  }

  &__row {
    display: flex;
    justify-content: space-around;
  }
}

// ===== 五行统计 =====
.wuxing-stats {
  display: flex;
  justify-content: center;
  gap: 12rpx;
  margin-top: 12rpx;
  flex-wrap: wrap;
}

.wuxing-stat {
  display: flex;
  align-items: center;
  gap: 4rpx;

  &__count {
    font-size: 22rpx;
    color: var(--text-primary);
  }
}

// ===== 格局分析 =====
.pattern-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pattern-name {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;

  &__icon {
    width: 48rpx;
    height: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-15);
    border: 1rpx solid var(--accent-40);
    border-radius: 8rpx;
    font-size: 24rpx;
    color: var(--accent-light);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }

  &__text {
    font-size: 32rpx;
    color: var(--accent-light);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
  }
}

.pattern-desc {
  &__text {
    font-size: 26rpx;
    color: var(--text-body);
    line-height: 1.8;
    text-indent: 2em;
  }
}

// ===== 喜用神 =====
.yongshen-card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.yongshen-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.yongshen-label {
  font-size: 26rpx;
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-weight: bold;
  min-width: 80rpx;

  &--god {
    color: var(--accent-light);
  }

  &--ji {
    color: var(--vermillion);
  }
}

.yongshen-tags {
  display: flex;
  gap: 12rpx;
}

.tiaohou-section {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding-top: 12rpx;
  border-top: 1rpx solid var(--border-50);
}

.tiaohou-label {
  font-size: 24rpx;
  color: var(--accent);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-weight: bold;
}

.tiaohou-text {
  font-size: 24rpx;
  color: var(--text-body);
  line-height: 1.8;
}

// ===== 大运 =====
.dayun-start {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid var(--border-50);

  &__label {
    font-size: 24rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }

  &__age {
    font-size: 36rpx;
    color: var(--accent-light);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
  }
}

// ===== 流年分析 =====
.liunian-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.liunian-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.liunian-year {
  font-size: 32rpx;
  color: var(--text-primary);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-weight: bold;
}

.liunian-ganzhi {
  display: flex;
  gap: 12rpx;
}

.liunian-rating {
  padding: 4rpx 24rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-weight: bold;

  &.rating-good {
    background: var(--accent-15);
    border: 1rpx solid var(--accent-40);
    color: var(--accent-light);
  }

  &.rating-bad {
    background: var(--vermillion-15);
    border: 1rpx solid var(--vermillion-40);
    color: var(--vermillion);
  }

  &.rating-neutral {
    background: rgba(139, 115, 85, 0.15);
    border: 1rpx solid rgba(139, 115, 85, 0.4);
    color: var(--text-muted);
  }
}

.liunian-nayin {
  font-size: 22rpx;
  color: var(--text-muted);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
}

.liunian-desc {
  font-size: 26rpx;
  color: var(--text-body);
  line-height: 1.8;
  text-indent: 2em;
}

// ===== 空状态 =====
.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 200rpx 40rpx;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-08);
  border: 2rpx solid var(--accent-20);
  border-radius: 50%;
  font-size: 48rpx;
  color: var(--accent-40);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  margin-bottom: 24rpx;
}

.empty-title {
  font-size: 32rpx;
  color: var(--text-muted);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: var(--text-placeholder);
  margin-bottom: 32rpx;
}

.empty-btn {
  padding: 14rpx 48rpx;
  background: linear-gradient(135deg, var(--accent-20), var(--accent-15));
  border: 1rpx solid var(--accent-40);
  border-radius: 12rpx;
  transition: background 0.3s ease, transform 0.15s ease;

  @media (hover: hover) {
    &:hover {
      background: linear-gradient(135deg, var(--accent-30), rgba(212, 175, 55, 0.25));
      transform: translateY(-2rpx);
    }
  }

  text {
    font-size: 28rpx;
    color: var(--accent-light);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }
}

.safe-bottom {
  height: calc(20rpx + env(safe-area-inset-bottom));
}

// ===== 星座样式 =====
.big-three {
  display: flex; flex-direction: column; gap: 20rpx;
  &__item { display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
  &__label { font-size: 22rpx; color: var(--text-muted); font-family: 'STKaiti','KaiTi','楷体',serif; }
  &__desc { font-size: 22rpx; color: var(--text-placeholder); margin-top: 4rpx; }
}

.planet-table {
  &__header { display: flex; padding: 8rpx 0 12rpx; border-bottom: 1rpx solid var(--border-50); }
  &__th { font-size: 22rpx; color: var(--text-muted); font-family: 'STKaiti','KaiTi','楷体',serif; text-align: center; }
  &__row { display: flex; padding: 14rpx 0; border-bottom: 1rpx solid var(--border-20); align-items: center;
    &:last-child { border-bottom: none; }
  }
  &__td { font-size: 24rpx; color: var(--text-primary); text-align: center; }
}

.aspects-list { padding: 8rpx 0; }

.patterns-list { display: flex; flex-wrap: wrap; gap: 12rpx; justify-content: center; padding: 16rpx 0; }
.pattern-tag {
  padding: 10rpx 24rpx; border-radius: 20rpx;
  background: var(--vermillion-10); border: 1rpx solid var(--vermillion-30);
  font-size: 22rpx; color: var(--vermillion-light); font-family: 'STKaiti','KaiTi','楷体',serif;
}

.empty-btns { display: flex; gap: 16rpx; }
</style>
