<template>
  <view class="page-index">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-bar__content">
        <text class="nav-bar__title">易经八字</text>
      </view>
    </view>

    <scroll-view class="page-index__scroll" scroll-y enhanced :show-scrollbar="false">
      <!-- 顶部标题区 -->
      <view class="hero-section">
        <!-- 装饰云纹 -->
        <view class="hero-clouds" aria-hidden="true">
          <view class="cloud cloud--1"></view>
          <view class="cloud cloud--2"></view>
        </view>

        <!-- 主标题 -->
        <view class="hero-title">
          <text class="hero-title__main">易经八字</text>
          <text class="hero-title__sub">探寻命理玄机，洞悉人生轨迹</text>
        </view>

        <!-- 装饰线 -->
        <view class="hero-divider">
          <view class="hero-divider__line"></view>
          <view class="hero-divider__diamond"></view>
          <view class="hero-divider__line"></view>
        </view>
      </view>

      <!-- 界面风格选择 -->
      <view class="theme-bar">
        <view class="theme-bar__header">
          <text class="theme-bar__title">界面风格</text>
        </view>
        <view class="theme-bar__list">
          <view
            v-for="t in themeList"
            :key="t.id"
            class="theme-chip"
            :class="{ 'theme-chip--active': currentTheme === t.id }"
            @tap="switchTheme(t.id)"
          >
            <view class="theme-chip__swatches">
              <view class="theme-chip__swatch" :style="{ background: t.swatch1 }"></view>
              <view class="theme-chip__swatch" :style="{ background: t.swatch2 }"></view>
              <view class="theme-chip__swatch" :style="{ background: t.swatch3 }"></view>
            </view>
            <text class="theme-chip__name">{{ t.name }}</text>
            <view class="theme-chip__check" v-if="currentTheme === t.id">
              <text class="theme-chip__check-icon">&#x2713;</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 输入表单区域 -->
      <view class="form-section">
        <classic-border variant="gold">
          <view class="form-card">
            <!-- 姓名 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">姓</text>
                <text class="label-text">姓名</text>
              </view>
              <input class="form-item__input" v-model="formData.name" placeholder="请输入姓名…" placeholder-style="color: var(--text-placeholder)" maxlength="20" />
            </view>

            <!-- 性别 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">性</text>
                <text class="label-text">性别</text>
              </view>
              <view class="gender-switch">
                <view class="gender-switch__option" :class="{ 'gender-switch__option--active': formData.gender === 1 }" @tap="formData.gender = 1">
                  <text class="gender-icon">♂</text><text>乾造</text>
                </view>
                <view class="gender-switch__option" :class="{ 'gender-switch__option--active': formData.gender === 0 }" @tap="formData.gender = 0">
                  <text class="gender-icon">♀</text><text>坤造</text>
                </view>
              </view>
            </view>

            <!-- 出生日期 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">诞</text>
                <text class="label-text">出生日期</text>
              </view>
              <picker mode="date" :value="formData.birthDate" :end="today" @change="onDateChange">
                <view class="form-item__picker">
                  <text :class="{ 'picker-placeholder': !formData.birthDate }">{{ formData.birthDate || '请选择公历出生日期…' }}</text>
                  <text class="picker-arrow">▼</text>
                </view>
              </picker>
            </view>

            <!-- 出生时间 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">时</text>
                <text class="label-text">出生时间</text>
              </view>
              <picker mode="time" :value="formData.birthTime" @change="onTimeChange">
                <view class="form-item__picker">
                  <text :class="{ 'picker-placeholder': !formData.birthTime }">{{ formData.birthTime || '请选择出生时间…' }}</text>
                  <text class="picker-arrow">▼</text>
                </view>
              </picker>
            </view>

            <!-- 出生地 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">地</text>
                <text class="label-text">出生地</text>
              </view>
              <picker mode="region" :value="regionIndexes" @change="onRegionChange">
                <view class="form-item__picker">
                  <text :class="{ 'picker-placeholder': !formData.location }">{{ formData.location || '请选择省/市/区…' }}</text>
                  <text class="picker-arrow">▼</text>
                </view>
              </picker>
            </view>

            <!-- 经纬度 -->
            <view class="form-item form-item--row" v-if="formData.lng && formData.lat">
              <text class="form-item__coord-label">经纬度：</text>
              <input class="form-item__coord-input" v-model="formData.lng" placeholder="经度" placeholder-style="color: var(--text-placeholder)" />
              <text class="form-item__coord-sep">,</text>
              <input class="form-item__coord-input" v-model="formData.lat" placeholder="纬度" placeholder-style="color: var(--text-placeholder)" />
            </view>
          </view>
        </classic-border>

        <!-- 排盘按钮 -->
        <view class="submit-section">
          <view class="submit-btn" @tap="handleCalculate">
            <view class="submit-btn__glow"></view>
            <text class="submit-btn__text">开 始 排 盘</text>
            <text class="submit-btn__sub">探寻命理玄机</text>
          </view>
        </view>

        <!-- 古籍引用 -->
        <view class="quote-section">
          <view class="quote-divider">
            <view class="quote-divider__line"></view>
            <text class="quote-divider__text">古 籍 参 照</text>
            <view class="quote-divider__line"></view>
          </view>
          <swiper class="quote-swiper" vertical autoplay circular :interval="4000" :duration="800">
            <swiper-item v-for="(quote, index) in quotes" :key="index">
              <view class="quote-item">
                <text class="quote-item__text">{{ quote.text }}</text>
                <text class="quote-item__source">——《{{ quote.source }}》</text>
              </view>
            </swiper-item>
          </swiper>
        </view>
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import ClassicBorder from '@/components/ClassicBorder.vue'

// ---- 主题系统 (内联，无外部依赖) ----
const THEME_KEY = 'bazi_app_theme'
const themeList = [
  { id: 'classic',  name: '经典暗金', swatch1: '#1a0a00', swatch2: '#d4af37', swatch3: '#f5f0e8' },
  { id: 'ink-wash', name: '墨韵',     swatch1: '#0a0a0c', swatch2: '#c8c0b6', swatch3: '#e0dcd6' },
  { id: 'imperial', name: '宫廷',     swatch1: '#0d0005', swatch2: '#e8c840', swatch3: '#fff5e8' },
  { id: 'celadon',  name: '青瓷',     swatch1: '#0a1512', swatch2: '#a0d8b8', swatch3: '#e8f0ec' },
]

const currentTheme = ref(_getStoredTheme())

function _getStoredTheme() {
  try { const t = uni.getStorageSync(THEME_KEY); if (t && themeList.some(x => x.id === t)) return t } catch (e) {}
  return 'classic'
}

function _applyTheme(themeId) {
  currentTheme.value = themeId
  uni.setStorageSync(THEME_KEY, themeId)
  // H5
  try {
    if (typeof document !== 'undefined' && document.documentElement) {
      document.documentElement.setAttribute('data-theme', themeId)
    }
  } catch (e) {}
  // 尝试更新小程序页面样式
  try {
    uni.setPageStyle && uni.setPageStyle({ style: { '--theme': themeId } })
  } catch (e) {}
  // 更新 TabBar
  const tabStyles = {
    'classic':  { color: '#8b7355', selectedColor: '#d4af37', backgroundColor: '#2a1a10' },
    'ink-wash': { color: '#70685e', selectedColor: '#b0a89e', backgroundColor: '#141418' },
    'imperial': { color: '#9a7a6a', selectedColor: '#e8c840', backgroundColor: '#1c0a12' },
    'celadon':  { color: '#5a7a6a', selectedColor: '#8cc4a8', backgroundColor: '#10201c' },
  }
  const s = tabStyles[themeId]
  if (s) { try { uni.setTabBarStyle(s) } catch (e) {} }
}

function switchTheme(themeId) {
  if (currentTheme.value === themeId) return
  _applyTheme(themeId)
  const name = themeList.find(t => t.id === themeId)?.name || themeId
  uni.showToast({ title: '已切换至「' + name + '」', icon: 'none', duration: 1500 })
}

// 初始化主题
_applyTheme(currentTheme.value)

// ---- 排盘表单 ----
const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 20)
const today = new Date().toISOString().split('T')[0]

const formData = reactive({
  name: '', gender: 1, birthDate: '', birthTime: '', location: '', lng: '', lat: ''
})
const regionIndexes = ref([])

const quotes = [
  { text: '天尊地卑，乾坤定矣。卑高以陈，贵贱位矣。', source: '周易·系辞上' },
  { text: '易有太极，是生两仪，两仪生四象，四象生八卦。', source: '周易·系辞上' },
  { text: '一阴一阳之谓道，继之者善也，成之者性也。', source: '周易·系辞上' },
  { text: '夫大人者，与天地合其德，与日月合其明，与四时合其序，与鬼神合其吉凶。', source: '周易·乾文言' },
  { text: '天行健，君子以自强不息。地势坤，君子以厚德载物。', source: '周易·象传' }
]

function onDateChange(e) { formData.birthDate = e.detail.value }
function onTimeChange(e) { formData.birthTime = e.detail.value }
function onRegionChange(e) {
  const values = e.detail.value
  regionIndexes.value = e.detail.index || []
  formData.location = values.join(' ')
}

function handleCalculate() {
  if (!formData.name.trim()) { uni.showToast({ title: '请输入姓名', icon: 'none' }); return }
  if (!formData.birthDate) { uni.showToast({ title: '请选择出生日期', icon: 'none' }); return }
  if (!formData.birthTime) { uni.showToast({ title: '请选择出生时间', icon: 'none' }); return }
  uni.setStorageSync('baziFormData', { ...formData })
  uni.switchTab({ url: '/pages/result/result' })
  uni.showToast({ title: '排盘进行中…', icon: 'loading', duration: 1500 })
}
</script>

<style lang="scss" scoped>
.page-index { min-height: 100vh; position: relative; }
.page-index__scroll { height: 100vh; }

// 导航栏
.nav-bar {
  position: sticky; top: 0; z-index: 100;
  background: linear-gradient(180deg, var(--bg-nav) 0%, var(--bg-nav-transparent) 100%);
  backdrop-filter: blur(10rpx);
  &__content {
    display: flex; align-items: center; justify-content: center;
    height: 88rpx; padding: 0 32rpx;
  }
  &__title {
    font-size: 36rpx; color: var(--accent-light);
    font-family: 'STKaiti','KaiTi','楷体',serif; font-weight: bold; letter-spacing: 8rpx;
  }
}

// 主标题
.hero-section { position: relative; display: flex; flex-direction: column; align-items: center; padding: 30rpx 32rpx 12rpx; overflow: hidden; }
.hero-clouds { position: absolute; inset: 0; pointer-events: none; }
.cloud {
  position: absolute; width: 120rpx; height: 60rpx;
  background: radial-gradient(ellipse at center, var(--accent-08) 0%, transparent 70%);
  border-radius: 50%;
  &--1 { top: 10%; left: 10%; animation: cloud-drift 8s ease-in-out infinite; }
  &--2 { top: 30%; right: 5%; width: 80rpx; height: 40rpx; animation: cloud-drift 10s ease-in-out infinite reverse; }
}
@keyframes cloud-drift { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-15rpx); } }

.hero-title { display: flex; flex-direction: column; align-items: center; position: relative; z-index: 1;
  &__main { font-size: 72rpx; color: var(--accent-light); font-family: 'STKaiti','KaiTi','楷体',serif; font-weight: bold; letter-spacing: 16rpx; text-shadow: 0 2rpx 10rpx var(--accent-30), 0 0 40rpx var(--accent-15); margin-bottom: 12rpx; }
  &__sub { font-size: 26rpx; color: var(--text-muted); font-family: 'STKaiti','KaiTi','楷体',serif; letter-spacing: 4rpx; }
}
.hero-divider { display: flex; align-items: center; gap: 20rpx; margin-top: 24rpx; width: 80%;
  &__line { flex: 1; height: 1rpx; background: linear-gradient(90deg, transparent, var(--accent-40), transparent); }
  &__diamond { width: 12rpx; height: 12rpx; background: var(--accent-light); transform: rotate(45deg); box-shadow: 0 0 8rpx var(--accent-50); }
}

// ===== 主题选择条 =====
.theme-bar {
  margin: 0 24rpx 16rpx;
  padding: 16rpx 0;
  border-top: 1rpx solid var(--border-50);
  border-bottom: 1rpx solid var(--border-50);
  &__header { margin-bottom: 12rpx; padding-left: 4rpx; }
  &__title { font-size: 22rpx; color: var(--text-muted); font-family: 'STKaiti','KaiTi','楷体',serif; letter-spacing: 4rpx; }
  &__scroll { width: 100%; white-space: nowrap; }
  &__list { display: flex; gap: 12rpx; padding: 0 4rpx; }
}

.theme-chip {
  display: flex; align-items: center; gap: 10rpx;
  padding: 10rpx 18rpx; border-radius: 28rpx;
  background: var(--bg-card); border: 1.5rpx solid var(--border-color);
  transition: border-color 0.25s, background 0.25s; cursor: pointer; flex-shrink: 0;
  &--active { border-color: var(--accent-light); background: var(--accent-08); }
  &__swatches { display: flex; gap: 2rpx; }
  &__swatch { width: 20rpx; height: 20rpx; border-radius: 4rpx; border: 1rpx solid var(--border-50); }
  &__name { font-size: 24rpx; color: var(--text-primary); font-family: 'STKaiti','KaiTi','楷体',serif; font-weight: bold; }
  &__check { width: 28rpx; height: 28rpx; border-radius: 50%; background: var(--accent-light); display: flex; align-items: center; justify-content: center; }
  &__check-icon { font-size: 16rpx; color: var(--bg-root); font-weight: bold; }
}

// 表单区
.form-section { padding: 0 24rpx; }
.form-card { padding: 8px; }
.form-item { margin-bottom: 24rpx; padding: 8rpx 0; border-bottom: 1rpx solid var(--border-50);
  &:last-child { border-bottom: none; margin-bottom: 0; }
  &--row { display: flex; align-items: center; flex-wrap: wrap; }
  &__label { display: flex; align-items: center; margin-bottom: 12rpx; gap: 8rpx; }
  .label-icon { display: flex; align-items: center; justify-content: center; width: 40rpx; height: 40rpx; background: var(--accent-15); border: 1rpx solid var(--accent-30); border-radius: 8rpx; font-size: 22rpx; color: var(--accent); font-family: 'STKaiti','KaiTi','楷体',serif; }
  .label-text { font-size: 28rpx; color: var(--accent); font-family: 'STKaiti','KaiTi','楷体',serif; }
  &__input { width: 100%; height: 72rpx; background: var(--bg-input); border: 1rpx solid var(--border-50); border-radius: 10rpx; padding: 0 20rpx; font-size: 28rpx; color: var(--text-primary); box-sizing: border-box; }
  &__picker { display: flex; align-items: center; justify-content: space-between; height: 72rpx; background: var(--bg-input); border: 1rpx solid var(--border-50); border-radius: 10rpx; padding: 0 20rpx; font-size: 28rpx; color: var(--text-primary); }
  .picker-placeholder { color: var(--text-placeholder); }
  .picker-arrow { font-size: 22rpx; color: var(--text-muted); }
  &__coord-label { font-size: 24rpx; color: var(--text-muted); margin-right: 8rpx; }
  &__coord-input { flex: 1; height: 56rpx; background: var(--bg-input); border: 1rpx solid var(--border-50); border-radius: 8rpx; padding: 0 12rpx; font-size: 24rpx; color: var(--text-primary); max-width: 180rpx; }
  &__coord-sep { margin: 0 8rpx; color: var(--text-muted); }
}

// 性别切换
.gender-switch { display: flex; gap: 0; border-radius: 12rpx; overflow: hidden; border: 1rpx solid var(--border-50); width: 100%;
  &__option { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6rpx; height: 72rpx; background: var(--bg-input); font-size: 28rpx; color: var(--text-muted); font-family: 'STKaiti','KaiTi','楷体',serif; transition: color 0.3s, background 0.3s;
    .gender-icon { font-size: 28rpx; }
    &--active { background: linear-gradient(135deg, var(--accent-20), var(--accent-15)); color: var(--accent-light); box-shadow: inset 0 0 20rpx var(--accent-10);
      .gender-icon { color: var(--accent-light); } }
  }
}

// 提交按钮
.submit-section { padding: 36rpx 24rpx 10rpx; }
.submit-btn { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 130rpx; background: linear-gradient(135deg, var(--vermillion) 0%, var(--vermillion-dark) 100%); border-radius: var(--btn-radius, 16rpx); overflow: hidden; box-shadow: var(--shadow-btn); transition: transform 0.15s, box-shadow 0.15s;
  &:active { transform: scale(0.98); }
  &__glow { position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(ellipse at center, rgba(255,255,255,0.1) 0%, transparent 60%); animation: btn-shine 3s ease-in-out infinite; }
  &__text { position: relative; z-index: 1; font-size: var(--btn-font-size, 40rpx); color: var(--accent-light); font-family: 'STKaiti','KaiTi','楷体',serif; font-weight: bold; letter-spacing: 12rpx; }
  &__sub { position: relative; z-index: 1; font-size: 22rpx; color: var(--accent-70); font-family: 'STKaiti','KaiTi','楷体',serif; letter-spacing: 6rpx; margin-top: 4rpx; }
}
@keyframes btn-shine { 0%,100% { opacity: 0.3; } 50% { opacity: 0.6; transform: translate(5%,5%) rotate(5deg); } }

// 古籍引用
.quote-section { padding: 20rpx 24rpx 40rpx; }
.quote-divider { display: flex; align-items: center; gap: 16rpx; margin-bottom: 20rpx;
  &__line { flex: 1; height: 1rpx; background: linear-gradient(90deg, transparent, var(--text-muted), transparent); opacity: 0.4; }
  &__text { font-size: 22rpx; color: var(--text-muted); font-family: 'STKaiti','KaiTi','楷体',serif; letter-spacing: 4rpx; }
}
.quote-swiper { height: 100rpx; }
.quote-item { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 0 16rpx;
  &__text { font-size: 24rpx; color: var(--text-muted); font-family: 'STKaiti','KaiTi','楷体',serif; text-align: center; line-height: 1.6; margin-bottom: 6rpx; }
  &__source { font-size: 20rpx; color: var(--text-placeholder); font-family: 'STKaiti','KaiTi','楷体',serif; }
}

.safe-bottom { height: calc(20rpx + env(safe-area-inset-bottom)); }
</style>
