<template>
  <!-- 干支标签组件 -->
  <view
    class="ganzhi-tag"
    :class="[`ganzhi-tag--${shape}`, `ganzhi-tag--${wuxing}`]"
    :style="{ width: sizeMap[size], height: sizeMap[size], lineHeight: sizeMap[size] }"
  >
    <text class="ganzhi-tag__text" :style="{ fontSize: fontSizeMap[size] }">{{ label }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  wuxing: {
    type: String,
    default: 'earth', // wood | fire | earth | metal | water
    validator: (val) => ['wood', 'fire', 'earth', 'metal', 'water'].includes(val)
  },
  shape: {
    type: String,
    default: 'circle', // circle | square
    validator: (val) => ['circle', 'square'].includes(val)
  },
  size: {
    type: String,
    default: 'md', // sm | md | lg | xl
    validator: (val) => ['sm', 'md', 'lg', 'xl'].includes(val)
  }
})

const sizeMap = {
  sm: '48rpx',
  md: '64rpx',
  lg: '80rpx',
  xl: '120rpx'
}

const fontSizeMap = {
  sm: '22rpx',
  md: '28rpx',
  lg: '36rpx',
  xl: '56rpx'
}

const wuxingColorMap = {
  wood: '#4a7c59',
  fire: '#c41e3a',
  earth: '#c9a96e',
  metal: '#f5f0e8',
  water: '#2c3e6b'
}
</script>

<style lang="scss" scoped>
.ganzhi-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid;
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-weight: bold;

  &--circle {
    border-radius: 50%;
  }

  &--square {
    border-radius: 8rpx;
  }

  // 五行配色
  &--wood {
    background: rgba(74, 124, 89, 0.2);
    border-color: rgba(74, 124, 89, 0.5);
    .ganzhi-tag__text { color: #5a9a6a; }
  }

  &--fire {
    background: rgba(196, 30, 58, 0.2);
    border-color: rgba(196, 30, 58, 0.5);
    .ganzhi-tag__text { color: #e04050; }
  }

  &--earth {
    background: rgba(201, 169, 110, 0.2);
    border-color: rgba(201, 169, 110, 0.5);
    .ganzhi-tag__text { color: #d4af37; }
  }

  &--metal {
    background: rgba(245, 240, 232, 0.15);
    border-color: rgba(245, 240, 232, 0.4);
    .ganzhi-tag__text { color: #f5f0e8; }
  }

  &--water {
    background: rgba(44, 62, 107, 0.25);
    border-color: rgba(44, 62, 107, 0.5);
    .ganzhi-tag__text { color: #5a7ec0; }
  }
}
</style>
