<template>
  <!-- 主题切换器：浮动按钮 + 底部弹出面板 -->
  <view class="theme-picker">
    <!-- 触发按钮 -->
    <view
      class="theme-picker__trigger"
      :class="{ 'theme-picker__trigger--pulse': !hasInteracted }"
      @tap="openSheet"
    >
      <view class="theme-picker__trigger-dot"></view>
      <text class="theme-picker__trigger-text">主题</text>
    </view>

    <!-- 遮罩层 -->
    <view
      class="theme-picker__backdrop"
      :class="{ 'theme-picker__backdrop--visible': visible }"
      v-if="visible"
      @tap="closeSheet"
      @touchmove.stop.prevent="() => {}"
    ></view>

    <!-- 底部弹出面板 -->
    <view
      class="theme-picker__sheet"
      :class="{ 'theme-picker__sheet--visible': visible }"
    >
      <!-- 拖拽手柄 -->
      <view class="theme-picker__handle"></view>

      <!-- 标题区 -->
      <view class="theme-picker__header">
        <text class="theme-picker__title">界面风格</text>
        <text class="theme-picker__subtitle">选择你喜欢的视觉主题</text>
      </view>

      <!-- 主题卡片列表 -->
      <view class="theme-picker__list">
        <view
          v-for="t in allThemes"
          :key="t.id"
          class="theme-picker__item"
          :class="{ 'theme-picker__item--active': currentTheme === t.id }"
          @tap="selectTheme(t.id)"
        >
          <!-- 迷你色彩预览 -->
          <view class="theme-picker__preview">
            <view
              class="theme-picker__preview-swatch"
              :style="{ background: previewColors[t.id].bg }"
            ></view>
            <view
              class="theme-picker__preview-swatch"
              :style="{ background: previewColors[t.id].card }"
            ></view>
            <view
              class="theme-picker__preview-swatch"
              :style="{ background: previewColors[t.id].accent }"
            ></view>
            <view
              class="theme-picker__preview-swatch"
              :style="{ background: previewColors[t.id].text }"
            ></view>
          </view>

          <!-- 主题信息 -->
          <view class="theme-picker__info">
            <text class="theme-picker__name">{{ t.name }}</text>
            <text class="theme-picker__desc">{{ t.desc }}</text>
          </view>

          <!-- 选中标记 -->
          <view class="theme-picker__check" v-if="currentTheme === t.id">
            <text class="theme-picker__check-mark">&#x2713;</text>
          </view>
        </view>
      </view>

      <!-- 底部安全区 -->
      <view class="theme-picker__safe"></view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { themes, themePreview, getCurrentTheme, setTheme } from '@/theme/index.js'

const visible = ref(false)
const hasInteracted = ref(false)
const currentTheme = ref(getCurrentTheme())

const allThemes = themes
const previewColors = themePreview

function openSheet() {
  hasInteracted.value = true
  visible.value = true
}

function closeSheet() {
  visible.value = false
}

function selectTheme(themeId) {
  if (currentTheme.value === themeId) {
    closeSheet()
    return
  }
  currentTheme.value = themeId
  setTheme(themeId)
  uni.showToast({ title: '已切换至 ' + (themes.find(t => t.id === themeId)?.name || themeId), icon: 'none', duration: 1500 })
  setTimeout(() => closeSheet(), 300)
}
</script>

<style lang="scss" scoped>
/* ===== 浮动触发按钮 ===== */
.theme-picker__trigger {
  position: fixed;
  bottom: calc(140rpx + env(safe-area-inset-bottom));
  right: 20rpx;
  z-index: 999;
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 14rpx 22rpx;
  border-radius: 40rpx;
  background: var(--bg-card);
  border: 1.5rpx solid var(--accent-30);
  box-shadow: var(--shadow-card);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.3s ease, border-color 0.3s ease;

  @media (hover: hover) {
    &:hover {
      transform: scale(1.05);
      border-color: var(--accent-50);
    }
  }
  &:active {
    transform: scale(0.95);
  }

  &--pulse {
    animation: theme-pulse 2.5s ease-in-out infinite;
  }
}

@keyframes theme-pulse {
  0%, 100% {
    box-shadow: var(--shadow-card);
    border-color: var(--accent-30);
  }
  50% {
    box-shadow: 0 0 0 6rpx var(--accent-15), var(--shadow-card);
    border-color: var(--accent-50);
  }
}

.theme-picker__trigger-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-light), var(--vermillion-light));
  flex-shrink: 0;
}

.theme-picker__trigger-text {
  font-size: 24rpx;
  color: var(--accent);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  letter-spacing: 2rpx;
}

/* ===== 遮罩层 ===== */
.theme-picker__backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0);
  transition: background 0.35s ease;

  &--visible {
    background: rgba(0, 0, 0, 0.55);
  }
}

/* ===== 底部弹出面板 ===== */
.theme-picker__sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1001;
  background: var(--bg-card-solid);
  border-radius: 32rpx 32rpx 0 0;
  padding: 0 28rpx;
  transform: translateY(100%);
  transition: transform 0.35s cubic-bezier(0.32, 0.72, 0, 1);
  box-shadow: 0 -8rpx 40rpx rgba(0, 0, 0, 0.5);

  &--visible {
    transform: translateY(0);
  }
}

.theme-picker__handle {
  width: 56rpx;
  height: 6rpx;
  background: var(--border-light);
  border-radius: 3rpx;
  margin: 16rpx auto 0;
}

.theme-picker__header {
  padding: 28rpx 0 20rpx;
  text-align: center;
}

.theme-picker__title {
  display: block;
  font-size: 34rpx;
  color: var(--text-primary);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-weight: bold;
  letter-spacing: 4rpx;
  margin-bottom: 6rpx;
}

.theme-picker__subtitle {
  display: block;
  font-size: 24rpx;
  color: var(--text-muted);
}

/* ===== 主题列表 ===== */
.theme-picker__list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding-bottom: 12rpx;
}

.theme-picker__item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 18rpx 20rpx;
  border-radius: 16rpx;
  background: var(--bg-card);
  border: 1.5rpx solid var(--border-color);
  transition: border-color 0.25s ease, background 0.25s ease;
  cursor: pointer;

  @media (hover: hover) {
    &:hover {
      border-color: var(--accent-30);
      background: var(--bg-card-hover);
    }
  }

  &--active {
    border-color: var(--accent-40);
    background: var(--accent-08);
    box-shadow: 0 0 16rpx var(--accent-10);
  }
}

/* ===== 迷你色彩预览 ===== */
.theme-picker__preview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 3rpx;
  width: 72rpx;
  height: 72rpx;
  border-radius: 12rpx;
  overflow: hidden;
  flex-shrink: 0;
  border: 1rpx solid var(--border-50);
}

.theme-picker__preview-swatch {
  width: 100%;
  height: 100%;
}

/* ===== 主题信息 ===== */
.theme-picker__info {
  flex: 1;
  min-width: 0;
}

.theme-picker__name {
  display: block;
  font-size: 28rpx;
  color: var(--text-primary);
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-weight: bold;
  margin-bottom: 4rpx;
}

.theme-picker__desc {
  display: block;
  font-size: 22rpx;
  color: var(--text-muted);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== 选中标记 ===== */
.theme-picker__check {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.theme-picker__check-mark {
  font-size: 24rpx;
  color: var(--bg-root);
  font-weight: bold;
}

/* ===== 底部安全区 ===== */
.theme-picker__safe {
  height: calc(16rpx + env(safe-area-inset-bottom));
}
</style>
