<template>
  <!-- 中式边框装饰组件 -->
  <view class="classic-border" :class="[`classic-border--${variant}`]">
    <!-- 四角装饰 -->
    <view class="classic-border__corner classic-border__corner--tl" aria-hidden="true">
      <view class="corner-pattern"></view>
    </view>
    <view class="classic-border__corner classic-border__corner--tr" aria-hidden="true">
      <view class="corner-pattern"></view>
    </view>
    <view class="classic-border__corner classic-border__corner--bl" aria-hidden="true">
      <view class="corner-pattern"></view>
    </view>
    <view class="classic-border__corner classic-border__corner--br" aria-hidden="true">
      <view class="corner-pattern"></view>
    </view>
    <!-- 内容区域 -->
    <view class="classic-border__content">
      <slot></slot>
    </view>
  </view>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'default', // default | gold | vermillion
    validator: (val) => ['default', 'gold', 'vermillion'].includes(val)
  }
})
</script>

<style lang="scss" scoped>
.classic-border {
  position: relative;
  padding: 4px;
  border: 2rpx solid var(--border-color);
  border-radius: 12px;
  background: linear-gradient(135deg, var(--bg-card), var(--bg-card));

  &--gold {
    border-color: var(--accent-50);

    .corner-pattern {
      border-color: var(--accent);
    }
  }

  &--vermillion {
    border-color: var(--vermillion-40);

    .corner-pattern {
      border-color: var(--vermillion);
    }
  }

  &__corner {
    position: absolute;
    width: 24rpx;
    height: 24rpx;
    z-index: 2;

    &--tl { top: -2rpx; left: -2rpx; }
    &--tr { top: -2rpx; right: -2rpx; transform: scaleX(-1); }
    &--bl { bottom: -2rpx; left: -2rpx; transform: scaleY(-1); }
    &--br { bottom: -2rpx; right: -2rpx; transform: scale(-1, -1); }

    .corner-pattern {
      width: 24rpx;
      height: 24rpx;
      border-top: 4rpx solid var(--border-light);
      border-left: 4rpx solid var(--border-light);
      border-radius: 4rpx 0 0 0;
    }
  }

  &__content {
    position: relative;
    z-index: 1;
    padding: 16px;
  }
}
</style>
