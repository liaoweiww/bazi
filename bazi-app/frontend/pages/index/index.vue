<template>
  <!-- 排盘首页 -->
  <view class="page-index">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-bar__content">
        <text class="nav-bar__title">易经八字</text>
      </view>
    </view>

    <!-- 可滚动内容 -->
    <scroll-view class="page-index__scroll" scroll-y enhanced :show-scrollbar="false">
      <!-- 顶部标题区 -->
      <view class="hero-section">
        <!-- 装饰云纹 -->
        <view class="hero-clouds">
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

      <!-- 输入表单区域 -->
      <view class="form-section">
        <classic-border variant="gold">
          <view class="form-card">
            <!-- 姓名输入 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">姓</text>
                <text class="label-text">姓名</text>
              </view>
              <input
                class="form-item__input"
                v-model="formData.name"
                placeholder="请输入姓名"
                placeholder-style="color: #5a4a3a"
                maxlength="20"
              />
            </view>

            <!-- 性别选择 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">性</text>
                <text class="label-text">性别</text>
              </view>
              <view class="gender-switch">
                <view
                  class="gender-switch__option"
                  :class="{ 'gender-switch__option--active': formData.gender === 1 }"
                  @tap="formData.gender = 1"
                >
                  <text class="gender-icon">♂</text>
                  <text>乾造</text>
                </view>
                <view
                  class="gender-switch__option"
                  :class="{ 'gender-switch__option--active': formData.gender === 0 }"
                  @tap="formData.gender = 0"
                >
                  <text class="gender-icon">♀</text>
                  <text>坤造</text>
                </view>
              </view>
            </view>

            <!-- 出生日期 -->
            <view class="form-item">
              <view class="form-item__label">
                <text class="label-icon">诞</text>
                <text class="label-text">出生日期</text>
              </view>
              <picker
                mode="date"
                :value="formData.birthDate"
                :end="today"
                @change="onDateChange"
              >
                <view class="form-item__picker">
                  <text :class="{ 'picker-placeholder': !formData.birthDate }">
                    {{ formData.birthDate || '请选择公历出生日期' }}
                  </text>
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
              <picker
                mode="time"
                :value="formData.birthTime"
                @change="onTimeChange"
              >
                <view class="form-item__picker">
                  <text :class="{ 'picker-placeholder': !formData.birthTime }">
                    {{ formData.birthTime || '请选择出生时间' }}
                  </text>
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
              <picker
                mode="region"
                :value="regionIndexes"
                @change="onRegionChange"
              >
                <view class="form-item__picker">
                  <text :class="{ 'picker-placeholder': !formData.location }">
                    {{ formData.location || '请选择省/市/区' }}
                  </text>
                  <text class="picker-arrow">▼</text>
                </view>
              </picker>
            </view>

            <!-- 经纬度展示/输入 -->
            <view class="form-item form-item--row" v-if="formData.lng && formData.lat">
              <text class="form-item__coord-label">经纬度：</text>
              <input
                class="form-item__coord-input"
                v-model="formData.lng"
                placeholder="经度"
                placeholder-style="color: #5a4a3a"
              />
              <text class="form-item__coord-sep">,</text>
              <input
                class="form-item__coord-input"
                v-model="formData.lat"
                placeholder="纬度"
                placeholder-style="color: #5a4a3a"
              />
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

        <!-- 古籍引用滚动文字 -->
        <view class="quote-section">
          <view class="quote-divider">
            <view class="quote-divider__line"></view>
            <text class="quote-divider__text">古 籍 参 照</text>
            <view class="quote-divider__line"></view>
          </view>
          <swiper
            class="quote-swiper"
            vertical
            autoplay
            circular
            :interval="4000"
            :duration="800"
          >
            <swiper-item v-for="(quote, index) in quotes" :key="index">
              <view class="quote-item">
                <text class="quote-item__text">{{ quote.text }}</text>
                <text class="quote-item__source">——《{{ quote.source }}》</text>
              </view>
            </swiper-item>
          </swiper>
        </view>
      </view>

      <!-- 底部安全区 -->
      <view class="safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import ClassicBorder from '@/components/ClassicBorder.vue'

// 状态栏高度
const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 20)

// 今日日期
const today = new Date().toISOString().split('T')[0]

// 表单数据
const formData = reactive({
  name: '',
  gender: 1, // 1-男(乾造) 0-女(坤造)
  birthDate: '',
  birthTime: '',
  location: '',
  lng: '',
  lat: ''
})

const regionIndexes = ref([])

// 古籍引用列表
const quotes = [
  { text: '天尊地卑，乾坤定矣。卑高以陈，贵贱位矣。', source: '周易·系辞上' },
  { text: '易有太极，是生两仪，两仪生四象，四象生八卦。', source: '周易·系辞上' },
  { text: '一阴一阳之谓道，继之者善也，成之者性也。', source: '周易·系辞上' },
  { text: '夫大人者，与天地合其德，与日月合其明，与四时合其序，与鬼神合其吉凶。', source: '周易·乾文言' },
  { text: '天行健，君子以自强不息。地势坤，君子以厚德载物。', source: '周易·象传' }
]

// 日期选择
function onDateChange(e) {
  formData.birthDate = e.detail.value
}

// 时间选择
function onTimeChange(e) {
  formData.birthTime = e.detail.value
}

// 地区选择
function onRegionChange(e) {
  const values = e.detail.value
  regionIndexes.value = e.detail.index || []
  formData.location = values.join(' ')
  // 可以在这里调用地理位置API获取经纬度
}

// 开始排盘
function handleCalculate() {
  // 表单验证
  if (!formData.name.trim()) {
    uni.showToast({ title: '请输入姓名', icon: 'none' })
    return
  }
  if (!formData.birthDate) {
    uni.showToast({ title: '请选择出生日期', icon: 'none' })
    return
  }
  if (!formData.birthTime) {
    uni.showToast({ title: '请选择出生时间', icon: 'none' })
    return
  }

  // 跳转到命盘解读页
  uni.switchTab({
    url: '/pages/result/result'
  })

  // 同时存储排盘参数到全局，在result页使用
  uni.setStorageSync('baziFormData', {
    ...formData
  })

  uni.showToast({
    title: '排盘进行中...',
    icon: 'loading',
    duration: 1500
  })
}
</script>

<style lang="scss" scoped>
.page-index {
  min-height: 100vh;
  position: relative;

  &__scroll {
    height: 100vh;
  }
}

// ===== 自定义导航栏 =====
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
    padding: 0 32rpx;
  }

  &__title {
    font-size: 36rpx;
    color: #d4af37;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
    letter-spacing: 8rpx;
  }
}

// ===== 顶部标题区 =====
.hero-section {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 32rpx 20rpx;
  overflow: hidden;
}

.hero-clouds {
  position: absolute;
  inset: 0;
  pointer-events: none;

  .cloud {
    position: absolute;
    width: 120rpx;
    height: 60rpx;
    background: radial-gradient(ellipse at center, rgba(201, 169, 110, 0.08) 0%, transparent 70%);
    border-radius: 50%;

    &--1 {
      top: 10%;
      left: 10%;
      animation: cloud-drift 8s ease-in-out infinite;
    }
    &--2 {
      top: 30%;
      right: 5%;
      width: 80rpx;
      height: 40rpx;
      animation: cloud-drift 10s ease-in-out infinite reverse;
    }
  }
}

@keyframes cloud-drift {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15rpx); }
}

.hero-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;

  &__main {
    font-size: 72rpx;
    color: #d4af37;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
    letter-spacing: 16rpx;
    text-shadow: 0 2rpx 10rpx rgba(212, 175, 55, 0.3),
                 0 0 40rpx rgba(212, 175, 55, 0.15);
    margin-bottom: 12rpx;
  }

  &__sub {
    font-size: 26rpx;
    color: #8b7355;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    letter-spacing: 4rpx;
  }
}

.hero-divider {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-top: 30rpx;
  width: 80%;

  &__line {
    flex: 1;
    height: 1rpx;
    background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.4), transparent);
  }

  &__diamond {
    width: 12rpx;
    height: 12rpx;
    background: #d4af37;
    transform: rotate(45deg);
    box-shadow: 0 0 8rpx rgba(212, 175, 55, 0.5);
  }
}

// ===== 表单区域 =====
.form-section {
  padding: 0 24rpx;
}

.form-card {
  padding: 8px;
}

.form-item {
  margin-bottom: 24rpx;
  padding: 8rpx 0;
  border-bottom: 1rpx solid rgba(61, 43, 26, 0.5);

  &:last-child {
    border-bottom: none;
    margin-bottom: 0;
  }

  &--row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  &__label {
    display: flex;
    align-items: center;
    margin-bottom: 12rpx;
    gap: 8rpx;

    .label-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40rpx;
      height: 40rpx;
      background: rgba(201, 169, 110, 0.15);
      border: 1rpx solid rgba(201, 169, 110, 0.3);
      border-radius: 8rpx;
      font-size: 22rpx;
      color: #c9a96e;
      font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    }

    .label-text {
      font-size: 28rpx;
      color: #c9a96e;
      font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    }
  }

  &__input {
    width: 100%;
    height: 72rpx;
    background: rgba(26, 10, 0, 0.5);
    border: 1rpx solid rgba(61, 43, 26, 0.5);
    border-radius: 10rpx;
    padding: 0 20rpx;
    font-size: 28rpx;
    color: #f5f0e8;
    box-sizing: border-box;

    &:focus {
      border-color: rgba(201, 169, 110, 0.5);
    }
  }

  &__picker {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 72rpx;
    background: rgba(26, 10, 0, 0.5);
    border: 1rpx solid rgba(61, 43, 26, 0.5);
    border-radius: 10rpx;
    padding: 0 20rpx;
    font-size: 28rpx;
    color: #f5f0e8;

    .picker-placeholder {
      color: #5a4a3a;
    }

    .picker-arrow {
      font-size: 22rpx;
      color: #8b7355;
    }
  }

  &__coord-label {
    font-size: 24rpx;
    color: #8b7355;
    margin-right: 8rpx;
  }

  &__coord-input {
    flex: 1;
    height: 56rpx;
    background: rgba(26, 10, 0, 0.5);
    border: 1rpx solid rgba(61, 43, 26, 0.5);
    border-radius: 8rpx;
    padding: 0 12rpx;
    font-size: 24rpx;
    color: #f5f0e8;
    max-width: 180rpx;
  }

  &__coord-sep {
    margin: 0 8rpx;
    color: #8b7355;
  }
}

// 性别切换
.gender-switch {
  display: flex;
  gap: 0;
  border-radius: 12rpx;
  overflow: hidden;
  border: 1rpx solid rgba(61, 43, 26, 0.5);
  width: 100%;

  &__option {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6rpx;
    height: 72rpx;
    background: rgba(26, 10, 0, 0.5);
    font-size: 28rpx;
    color: #8b7355;
    transition: all 0.3s ease;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;

    .gender-icon {
      font-size: 28rpx;
    }

    &--active {
      background: linear-gradient(135deg, rgba(201, 169, 110, 0.2), rgba(212, 175, 55, 0.15));
      color: #d4af37;
      box-shadow: inset 0 0 20rpx rgba(212, 175, 55, 0.1);

      .gender-icon {
        color: #d4af37;
      }
    }
  }
}

// ===== 提交按钮 =====
.submit-section {
  padding: 40rpx 24rpx 20rpx;
}

.submit-btn {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 130rpx;
  background: linear-gradient(135deg, #c41e3a 0%, #8b0000 100%);
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 30rpx rgba(139, 0, 0, 0.4);
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.98);
    box-shadow: 0 4rpx 15rpx rgba(139, 0, 0, 0.3);
  }

  &__glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(255, 255, 255, 0.1) 0%, transparent 60%);
    animation: btn-shine 3s ease-in-out infinite;
  }

  &__text {
    position: relative;
    z-index: 1;
    font-size: 40rpx;
    color: #d4af37;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    font-weight: bold;
    letter-spacing: 12rpx;
    text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.3);
  }

  &__sub {
    position: relative;
    z-index: 1;
    font-size: 22rpx;
    color: rgba(212, 175, 55, 0.7);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    letter-spacing: 6rpx;
    margin-top: 4rpx;
  }
}

@keyframes btn-shine {
  0%, 100% { opacity: 0.3; transform: translate(0, 0) rotate(0deg); }
  50% { opacity: 0.6; transform: translate(5%, 5%) rotate(5deg); }
}

// ===== 古籍引用 =====
.quote-section {
  padding: 20rpx 24rpx 40rpx;
}

.quote-divider {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;

  &__line {
    flex: 1;
    height: 1rpx;
    background: linear-gradient(90deg, transparent, rgba(139, 115, 85, 0.4), transparent);
  }

  &__text {
    font-size: 22rpx;
    color: #8b7355;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    letter-spacing: 4rpx;
  }
}

.quote-swiper {
  height: 100rpx;
}

.quote-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 16rpx;

  &__text {
    font-size: 24rpx;
    color: #8b7355;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    text-align: center;
    line-height: 1.6;
    margin-bottom: 6rpx;
  }

  &__source {
    font-size: 20rpx;
    color: #5a4a3a;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }
}

// 底部安全区
.safe-bottom {
  height: calc(20rpx + env(safe-area-inset-bottom));
}
</style>
