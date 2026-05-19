<template>
  <view class="sign-badge" :class="'sign-badge--' + element">
    <text class="sign-badge__symbol">{{ symbol }}</text>
    <text class="sign-badge__name">{{ name }}</text>
  </view>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  symbol: { type: String, default: '' },
  element: { type: String, default: '火' }
})
</script>

<style lang="scss" scoped>
.sign-badge {
  display: flex; align-items: center; gap: 8rpx;
  padding: 8rpx 20rpx; border-radius: 10rpx;
  border: 1.5rpx solid var(--border-50);
  &__symbol { font-size: 32rpx; }
  &__name { font-size: 24rpx; color: var(--text-primary); font-family: 'STKaiti','KaiTi','楷体',serif; letter-spacing: 2rpx; }

  &--火 { background: rgba(220, 60, 40, 0.12); border-color: rgba(220, 60, 40, 0.3); }
  &--土 { background: rgba(140, 120, 60, 0.12); border-color: rgba(180, 150, 80, 0.3); }
  &--风 { background: rgba(160, 180, 60, 0.12); border-color: rgba(200, 200, 80, 0.3); }
  &--水 { background: rgba(60, 100, 180, 0.12); border-color: rgba(80, 120, 200, 0.3); }
}
</style>
