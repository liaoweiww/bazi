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
    background: linear-gradient(135deg, rgba(201, 169, 110, 0.3), rgba(212, 175, 55, 0.2));
    border: 1rpx solid rgba(212, 175, 55, 0.5);
    .shishen-badge__text { color: #d4af37; }
  }

  // 比肩
  &--bijian {
    background: rgba(74, 124, 89, 0.15);
    border: 1rpx solid rgba(74, 124, 89, 0.4);
    .shishen-badge__text { color: #5a9a6a; }
  }

  // 劫财
  &--jiecai {
    background: rgba(74, 124, 89, 0.1);
    border: 1rpx solid rgba(74, 124, 89, 0.3);
    .shishen-badge__text { color: #6aaa7a; }
  }

  // 食神
  &--shishen {
    background: rgba(196, 30, 58, 0.12);
    border: 1rpx solid rgba(196, 30, 58, 0.35);
    .shishen-badge__text { color: #e06070; }
  }

  // 伤官
  &--shangguan {
    background: rgba(196, 30, 58, 0.18);
    border: 1rpx solid rgba(196, 30, 58, 0.5);
    .shishen-badge__text { color: #f05060; }
  }

  // 正财
  &--zhengcai {
    background: rgba(201, 169, 110, 0.12);
    border: 1rpx solid rgba(201, 169, 110, 0.35);
    .shishen-badge__text { color: #c9a96e; }
  }

  // 偏财
  &--piancai {
    background: rgba(201, 169, 110, 0.18);
    border: 1rpx solid rgba(201, 169, 110, 0.5);
    .shishen-badge__text { color: #e0c080; }
  }

  // 正官
  &--zhengguan {
    background: rgba(245, 240, 232, 0.12);
    border: 1rpx solid rgba(245, 240, 232, 0.35);
    .shishen-badge__text { color: #f5f0e8; }
  }

  // 偏官
  &--pianguan {
    background: rgba(245, 240, 232, 0.08);
    border: 1rpx solid rgba(245, 240, 232, 0.25);
    .shishen-badge__text { color: #ddd5c8; }
  }

  // 正印
  &--zhengyin {
    background: rgba(44, 62, 107, 0.15);
    border: 1rpx solid rgba(44, 62, 107, 0.4);
    .shishen-badge__text { color: #5a7ec0; }
  }

  // 偏印
  &--pianyin {
    background: rgba(44, 62, 107, 0.2);
    border: 1rpx solid rgba(44, 62, 107, 0.5);
    .shishen-badge__text { color: #7090d0; }
  }

  // 默认
  &--default {
    background: rgba(61, 43, 26, 0.3);
    border: 1rpx solid rgba(61, 43, 26, 0.5);
    .shishen-badge__text { color: #8b7355; }
  }
}
</style>
