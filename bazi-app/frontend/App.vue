<template>
  <view class="app-root">
    <!-- 全局背景纹样 -->
    <view class="bg-pattern" aria-hidden="true"></view>
    <view class="bg-overlay" aria-hidden="true"></view>

    <!-- 主题切换条 (全局，所有页面可见，纯 inline style 不依赖 CSS 变量) -->
    <view
      style="position:fixed;bottom:100rpx;left:50%;transform:translateX(-50%);z-index:9999;
             display:flex;gap:8rpx;padding:10rpx 16rpx;border-radius:32rpx;
             background:rgba(30,20,10,0.95);border:1px solid rgba(180,150,100,0.4);
             box-shadow:0 4rpx 20rpx rgba(0,0,0,0.5);"
    >
      <view
        v-for="t in themes"
        :key="t.id"
        @tap="doSwitchTheme(t.id)"
        :style="{
          padding: '8rpx 18rpx',
          borderRadius: '24rpx',
          fontSize: '22rpx',
          fontFamily: 'STKaiti,KaiTi,楷体,serif',
          background: curTheme === t.id ? t.accent : 'rgba(255,255,255,0.06)',
          color: curTheme === t.id ? '#1a0a00' : '#bbb',
          fontWeight: curTheme === t.id ? 'bold' : 'normal',
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '6rpx'
        }"
      >
        <view :style="{width:'16rpx',height:'16rpx',borderRadius:'50%',background:t.accent,flexShrink:0}"></view>
        <text>{{ t.name }}</text>
      </view>
    </view>

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
const THEME_KEY = 'bazi_app_theme'
const THEMES = [
  { id: 'classic',  name: '经典暗金', accent: '#d4af37' },
  { id: 'ink-wash', name: '墨韵',     accent: '#c8c0b6' },
  { id: 'imperial', name: '宫廷',     accent: '#e8c840' },
  { id: 'celadon',  name: '青瓷',     accent: '#a0d8b8' },
]

export default {
  data() {
    return {
      curTheme: 'classic',
      themes: THEMES
    }
  },
  onLaunch() {
    console.log('App Launch')
    this.curTheme = uni.getStorageSync(THEME_KEY) || 'classic'
    this._applyTheme(this.curTheme)
  },
  onShow() {
    this.curTheme = uni.getStorageSync(THEME_KEY) || 'classic'
    this._applyTheme(this.curTheme)
  },
  methods: {
    doSwitchTheme(id) {
      this.curTheme = id
      uni.setStorageSync(THEME_KEY, id)
      this._applyTheme(id)
      const name = THEMES.find(t => t.id === id)?.name || id
      uni.showToast({ title: '已切换至「' + name + '」', icon: 'none', duration: 1200 })
    },
    _applyTheme(t) {
      try {
        if (typeof document !== 'undefined' && document.documentElement) {
          document.documentElement.setAttribute('data-theme', t)
        }
      } catch (e) {}
      const tabStyles = {
        'classic':  { color: '#8b7355', selectedColor: '#d4af37', backgroundColor: '#2a1a10' },
        'ink-wash': { color: '#70685e', selectedColor: '#b0a89e', backgroundColor: '#141418' },
        'imperial': { color: '#9a7a6a', selectedColor: '#e8c840', backgroundColor: '#1c0a12' },
        'celadon':  { color: '#5a7a6a', selectedColor: '#8cc4a8', backgroundColor: '#10201c' },
      }
      const s = tabStyles[t]
      if (s) { try { uni.setTabBarStyle(s) } catch (e) {} }
    }
  }
}
</script>

<style lang="scss">
/* ===== 全局样式 ===== */
page {
  background: var(--bg-root);
  color: var(--text-primary);
  color-scheme: dark;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif;
  font-size: 30rpx;
  min-height: 100vh;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  touch-action: manipulation;
  -webkit-tap-highlight-color: var(--tap-highlight);
  overscroll-behavior: contain;
}

.app-root {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(180deg, var(--bg-root) 0%, var(--bg-secondary) 50%, var(--bg-root) 100%);
  overflow: hidden;
}

/* 背景纹理：不同主题不同密度/形状 */
.bg-pattern {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 0;
  opacity: var(--bg-pattern-opacity, 0.06);
  background:
    radial-gradient(ellipse at 20% 15%, var(--accent-light) 0%, transparent 40%),
    radial-gradient(ellipse at 80% 30%, var(--accent-light) 0%, transparent 35%),
    radial-gradient(ellipse at 50% 60%, var(--accent-light) 0%, transparent 45%),
    radial-gradient(ellipse at 10% 90%, var(--vermillion) 0%, transparent 30%),
    radial-gradient(ellipse at 90% 85%, var(--vermillion) 0%, transparent 25%);
}

.bg-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 0;
  opacity: var(--bg-overlay-opacity, 1);
  background:
    repeating-linear-gradient(90deg,
      transparent, transparent 38rpx,
      var(--accent-04) 38rpx, var(--accent-04) 40rpx),
    repeating-linear-gradient(0deg,
      transparent, transparent 38rpx,
      var(--accent-04) 38rpx, var(--accent-04) 40rpx);
}

.app-content {
  position: relative; z-index: 1; min-height: 100vh;
}

/* 页面过渡 */
.ink-fade-enter-active {
  transition: opacity 0.5s cubic-bezier(0.25,0.46,0.45,0.94), transform 0.5s cubic-bezier(0.25,0.46,0.45,0.94);
}
.ink-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.55,0.085,0.68,0.53), transform 0.3s cubic-bezier(0.55,0.085,0.68,0.53);
}
.ink-fade-enter-from { opacity: 0; transform: scale(0.98); }
.ink-fade-leave-to { opacity: 0; transform: scale(1.02); }

/* 工具类 */
.text-gold { color: var(--accent); }
.text-vermillion { color: var(--vermillion); }
.text-muted { color: var(--text-muted); }
.text-center { text-align: center; }

:focus-visible { outline: 2rpx solid var(--focus-outline); outline-offset: 2rpx; }

::-webkit-scrollbar { width: 4rpx; }
::-webkit-scrollbar-track { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 2rpx; }
</style>
