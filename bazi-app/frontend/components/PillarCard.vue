<template>
  <!-- 单柱展示组件 -->
  <view class="pillar-card" :class="{ 'pillar-card--rizhu': isRizhu }">
    <!-- 顶部标签 -->
    <view class="pillar-card__header">
      <text class="pillar-card__label">{{ pillarLabel }}</text>
      <ShishenBadge
        v-if="shishen"
        :label="shishen"
        :type="isRizhu ? 'rizhu' : shishenType"
      />
    </view>

    <!-- 天干 -->
    <view class="pillar-card__ganzhi">
      <GanzhiTag
        :label="gan"
        :wuxing="ganWuxing"
        shape="square"
        size="lg"
      />
      <GanzhiTag
        :label="zhi"
        :wuxing="zhiWuxing"
        shape="square"
        size="lg"
      />
    </view>

    <!-- 藏干 -->
    <view class="pillar-card__canggan" v-if="canggan && canggan.length">
      <text class="pillar-card__canggan-label">藏干</text>
      <view class="pillar-card__canggan-list">
        <text
          v-for="(cg, idx) in canggan"
          :key="idx"
          class="pillar-card__canggan-item"
        >{{ cg }}</text>
      </view>
    </view>

    <!-- 纳音 -->
    <text class="pillar-card__nayin" v-if="nayin">{{ nayin }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import GanzhiTag from './GanzhiTag.vue'
import ShishenBadge from './ShishenBadge.vue'

const props = defineProps({
  label: { type: String, required: true },  // 年柱/月柱/日柱/时柱
  gan: { type: String, required: true },
  zhi: { type: String, required: true },
  canggan: { type: Array, default: () => [] },
  shishen: { type: String, default: '' },
  nayin: { type: String, default: '' },
  isRizhu: { type: Boolean, default: false }
})

const pillarLabel = computed(() => props.label)

// 天干五行映射
const ganWuxingMap = {
  '甲': 'wood', '乙': 'wood',
  '丙': 'fire', '丁': 'fire',
  '戊': 'earth', '己': 'earth',
  '庚': 'metal', '辛': 'metal',
  '壬': 'water', '癸': 'water'
}

const zhiWuxingMap = {
  '子': 'water', '丑': 'earth',
  '寅': 'wood', '卯': 'wood',
  '辰': 'earth', '巳': 'fire',
  '午': 'fire', '未': 'earth',
  '申': 'metal', '酉': 'metal',
  '戌': 'earth', '亥': 'water'
}

const ganWuxing = computed(() => ganWuxingMap[props.gan] || 'earth')
const zhiWuxing = computed(() => zhiWuxingMap[props.zhi] || 'earth')

// 十神类型映射
const shishenTypeMap = {
  '比肩': 'bijian', '劫财': 'jiecai',
  '食神': 'shishen', '伤官': 'shangguan',
  '正财': 'zhengcai', '偏财': 'piancai',
  '正官': 'zhengguan', '偏官': 'pianguan', '七杀': 'pianguan',
  '正印': 'zhengyin', '偏印': 'pianyin', '枭神': 'pianyin',
  '日主': 'rizhu'
}
const shishenType = computed(() => shishenTypeMap[props.shishen] || 'default')
</script>

<style lang="scss" scoped>
.pillar-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 12rpx;
  border: 1rpx solid var(--border-color);
  background: var(--bg-card);
  min-width: 130rpx;
  transition: border-color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease;

  &--rizhu {
    border-color: var(--accent-40);
    background: var(--accent-08);
    box-shadow: 0 0 20rpx var(--accent-10);
  }

  &__header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4rpx;
    margin-bottom: 8rpx;
  }

  &__label {
    font-size: 22rpx;
    color: var(--accent);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }

  &__ganzhi {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6rpx;
    margin-bottom: 6rpx;
  }

  &__canggan {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 4rpx;
  }

  &__canggan-label {
    font-size: 18rpx;
    color: var(--text-muted);
    margin-bottom: 2rpx;
  }

  &__canggan-list {
    display: flex;
    gap: 4rpx;
  }

  &__canggan-item {
    font-size: 18rpx;
    color: var(--text-muted);
    background: rgba(61, 43, 26, 0.3);
    padding: 1rpx 8rpx;
    border-radius: 4rpx;
  }

  &__nayin {
    font-size: 18rpx;
    color: var(--text-subtle);
    margin-top: 6rpx;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }
}
</style>
