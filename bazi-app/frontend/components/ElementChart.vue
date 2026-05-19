<template>
  <view class="element-chart">
    <view class="element-chart__bars">
      <view class="el-bar" v-for="el in elementList" :key="el.key">
        <text class="el-bar__label">{{ el.icon }} {{ el.name }}</text>
        <view class="el-bar__track">
          <view class="el-bar__fill" :style="{ width: el.pct + '%', background: el.color }"></view>
        </view>
        <text class="el-bar__count">{{ el.count }}颗</text>
      </view>
    </view>
    <view class="element-chart__summary">{{ summary }}</view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  elements: { type: Object, default: () => ({}) },
  dominant: { type: String, default: '' },
  summary: { type: String, default: '' }
})

const elementList = computed(() => {
  const config = {
    '火': { icon: '🔥', name: '火象', color: 'linear-gradient(90deg, #e04030, #f08050)' },
    '土': { icon: '🌍', name: '土象', color: 'linear-gradient(90deg, #8a7a40, #b8a060)' },
    '风': { icon: '💨', name: '风象', color: 'linear-gradient(90deg, #b0b840, #d8d860)' },
    '水': { icon: '💧', name: '水象', color: 'linear-gradient(90deg, #4060c0, #6080e0)' }
  }
  return Object.entries(props.elements).map(([key, val]) => ({
    key, name: config[key]?.name || key, icon: config[key]?.icon || '',
    color: config[key]?.color || '#888', count: val.count || 0,
    pct: val.percentage || 0
  }))
})
</script>

<style lang="scss" scoped>
.element-chart { padding: 8rpx 0; }
.element-chart__bars { display: flex; flex-direction: column; gap: 14rpx; }
.el-bar {
  display: flex; align-items: center; gap: 12rpx;
  &__label { font-size: 22rpx; color: var(--text-secondary); min-width: 100rpx; }
  &__track { flex: 1; height: 18rpx; background: var(--bg-input); border-radius: 9rpx; overflow: hidden; }
  &__fill { height: 100%; border-radius: 9rpx; transition: width 0.6s ease; }
  &__count { font-size: 20rpx; color: var(--text-muted); min-width: 50rpx; text-align: right; }
}
.element-chart__summary { margin-top: 16rpx; font-size: 22rpx; color: var(--text-muted); line-height: 1.6; }
</style>
