<template>
  <!-- 十神徽章组件 -->
  <view class="shishen-badge" :class="[`shishen-badge--${type}`]">
    <text class="shishen-badge__text">{{ label }}</text>
  </view>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'default',
    validator: (val) => [
      'default',
      'rizhu',       // 日主 - 金色
      'bijian',      // 比肩
      'jiecai',      // 劫财
      'shishen',     // 食神
      'shangguan',   // 伤官
      'zhengcai',    // 正财
      'piancai',     // 偏财
      'zhengguan',   // 正官
      'pianguan',    // 偏官/七杀
      'zhengyin',    // 正印
      'pianyin'      // 偏印/枭神
    ].includes(val)
  }
})
</script>

<style lang="scss" scoped>
.shishen-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2rpx 12rpx;
  border-radius: 20rpx;
  min-width: 56rpx;
  height: 36rpx;
  font-size: 20rpx;
  font-weight: 500;

  &__text {
    white-space: nowrap;
  }

  // 日主 - 鎏金
  &--rizhu {
    background: linear-gradient(135deg, var(--accent-30), var(--accent-20));
    border: 1rpx solid var(--accent-50);
    .shishen-badge__text { color: var(--accent-light); }
  }

  // 比肩
  &--bijian {
    background: rgba(74, 124, 89, 0.15);
    border: 1rpx solid rgba(74, 124, 89, 0.4);
    .shishen-badge__text { color: var(--color-positive); }
  }

  // 劫财
  &--jiecai {
    background: rgba(74, 124, 89, 0.1);
    border: 1rpx solid rgba(74, 124, 89, 0.3);
    .shishen-badge__text { color: var(--wx-wood-light); }
  }

  // 食神
  &--shishen {
    background: var(--vermillion-12);
    border: 1rpx solid var(--vermillion-30);
    .shishen-badge__text { color: var(--vermillion-light); }
  }

  // 伤官
  &--shangguan {
    background: rgba(196, 30, 58, 0.18);
    border: 1rpx solid var(--vermillion-40);
    .shishen-badge__text { color: var(--vermillion-light); }
  }

  // 正财
  &--zhengcai {
    background: var(--accent-12);
    border: 1rpx solid rgba(201, 169, 110, 0.35);
    .shishen-badge__text { color: var(--accent); }
  }

  // 偏财
  &--piancai {
    background: rgba(201, 169, 110, 0.18);
    border: 1rpx solid var(--accent-50);
    .shishen-badge__text { color: var(--accent-light); }
  }

  // 正官
  &--zhengguan {
    background: rgba(245, 240, 232, 0.12);
    border: 1rpx solid rgba(245, 240, 232, 0.35);
    .shishen-badge__text { color: var(--text-primary); }
  }

  // 偏官
  &--pianguan {
    background: rgba(245, 240, 232, 0.08);
    border: 1rpx solid rgba(245, 240, 232, 0.25);
    .shishen-badge__text { color: var(--wx-metal-light); }
  }

  // 正印
  &--zhengyin {
    background: rgba(44, 62, 107, 0.15);
    border: 1rpx solid rgba(44, 62, 107, 0.4);
    .shishen-badge__text { color: var(--wx-water-light); }
  }

  // 偏印
  &--pianyin {
    background: rgba(44, 62, 107, 0.2);
    border: 1rpx solid rgba(44, 62, 107, 0.5);
    .shishen-badge__text { color: var(--wx-water-light); }
  }

  // 默认
  &--default {
    background: rgba(61, 43, 26, 0.3);
    border: 1rpx solid var(--border-50);
    .shishen-badge__text { color: var(--text-muted); }
  }
}
</style>
