<template>
  <view class="app-root">
    <!-- 全局背景纹样 -->
    <view class="bg-pattern"></view>
    <view class="bg-overlay"></view>
    <!-- 路由页面 -->
    <view class="app-content">
      <router-view v-slot="{ Component }">
        <transition name="ink-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </view>
  </view>
</template>

<script>
export default {
  onLaunch() {
    console.log('易经八字 App Launch')
    // 检查更新等初始化逻辑
  },
  onShow() {
    console.log('App Show')
  },
  onHide() {
    console.log('App Hide')
  }
}
</script>

<style lang="scss">
/* ===== 全局样式 ===== */
page {
  background: #1a0a00;
  color: #f5f0e8;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif;
  font-size: 28rpx;
  min-height: 100vh;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

.app-root {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(180deg, #1a0a00 0%, #2d1810 50%, #1a0a00 100%);
  overflow: hidden;
}

/* ===== 背景中式纹理 ===== */
.bg-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.08;
  background:
    /* 云纹1 */
    radial-gradient(ellipse at 20% 15%, #d4af37 0%, transparent 40%),
    /* 云纹2 */
    radial-gradient(ellipse at 80% 30%, #d4af37 0%, transparent 35%),
    /* 云纹3 */
    radial-gradient(ellipse at 50% 60%, #d4af37 0%, transparent 45%),
    /* 暗角 */
    radial-gradient(ellipse at 10% 90%, #c41e3a 0%, transparent 30%),
    radial-gradient(ellipse at 90% 85%, #c41e3a 0%, transparent 25%);
}

.bg-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  background:
    /* 回纹装饰线条 - 顶部 */
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 38rpx,
      rgba(201, 169, 110, 0.04) 38rpx,
      rgba(201, 169, 110, 0.04) 40rpx
    ),
    /* 回纹装饰线条 - 底部 */
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 38rpx,
      rgba(201, 169, 110, 0.03) 38rpx,
      rgba(201, 169, 110, 0.03) 40rpx
    );
}

.app-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

/* ===== 水墨淡入过渡 ===== */
.ink-fade-enter-active {
  transition: opacity 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.ink-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.55, 0.085, 0.68, 0.53),
              transform 0.3s cubic-bezier(0.55, 0.085, 0.68, 0.53);
}
.ink-fade-enter-from {
  opacity: 0;
  transform: scale(0.98);
}
.ink-fade-leave-to {
  opacity: 0;
  transform: scale(1.02);
}

/* ===== 全局工具类 ===== */
.text-gold {
  color: #c9a96e;
}
.text-vermillion {
  color: #c41e3a;
}
.text-muted {
  color: #8b7355;
}
.text-center {
  text-align: center;
}

/* ===== 全局滚动条 ===== */
::-webkit-scrollbar {
  width: 4rpx;
}
::-webkit-scrollbar-track {
  background: rgba(26, 10, 0, 0.5);
}
::-webkit-scrollbar-thumb {
  background: rgba(201, 169, 110, 0.3);
  border-radius: 2rpx;
}
</style>
