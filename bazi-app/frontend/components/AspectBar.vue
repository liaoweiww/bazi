<template>
  <view class="aspect-bar" :class="'aspect-bar--' + nature">
    <text class="aspect-bar__p1">{{ planet1 }}</text>
    <view class="aspect-bar__mid">
      <text class="aspect-bar__symbol">{{ symbol }}</text>
      <text class="aspect-bar__type">{{ type }}</text>
      <text class="aspect-bar__keyword">{{ keyword }}</text>
    </view>
    <text class="aspect-bar__p2">{{ planet2 }}</text>
  </view>
</template>

<script setup>
defineProps({
  planet1: { type: String, required: true },
  planet2: { type: String, required: true },
  symbol: { type: String, default: '' },
  type: { type: String, default: '' },
  keyword: { type: String, default: '' },
  nature: { type: String, default: '中性' }
})
</script>

<style lang="scss" scoped>
.aspect-bar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12rpx; padding: 16rpx 20rpx; margin-bottom: 10rpx;
  border-radius: 10rpx; border: 1rpx solid var(--border-50);
  background: var(--bg-input);
  &__p1, &__p2 { font-size: 24rpx; color: var(--text-primary); min-width: 70rpx; text-align: center; letter-spacing: 2rpx; }
  &__mid { display: flex; flex-direction: column; align-items: center; gap: 2rpx; }
  &__symbol { font-size: 28rpx; }
  &__type { font-size: 20rpx; color: var(--text-muted); }
  &__keyword { font-size: 18rpx; color: var(--text-placeholder); }

  &--和谐 { border-left: 4rpx solid #5a9a6a; }
  &--紧张 { border-left: 4rpx solid #e06070; }
  &--中性 { border-left: 4rpx solid var(--accent); }
}
</style>
