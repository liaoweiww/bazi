<template>
  <!-- 中式边框装饰组件 -->
  <view class="classic-border" :class="[`classic-border--${variant}`]">
    <!-- 四角装饰 -->
    <view class="classic-border__corner classic-border__corner--tl">
      <view class="corner-pattern"></view>
    </view>
    <view class="classic-border__corner classic-border__corner--tr">
      <view class="corner-pattern"></view>
    </view>
    <view class="classic-border__corner classic-border__corner--bl">
      <view class="corner-pattern"></view>
    </view>
    <view class="classic-border__corner classic-border__corner--br">
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
  border: 2rpx solid #3d2b1a;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(42, 26, 16, 0.9), rgba(58, 42, 26, 0.85));

  &--gold {
    border-color: rgba(201, 169, 110, 0.5);

    .corner-pattern {
      border-color: #c9a96e;
    }
  }

  &--vermillion {
    border-color: rgba(196, 30, 58, 0.4);

    .corner-pattern {
      border-color: #c41e3a;
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
      border-top: 4rpx solid #5a3e2a;
      border-left: 4rpx solid #5a3e2a;
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
