<template>
  <!-- 大运时间轴组件 -->
  <view class="dayun-timeline">
    <!-- 时间轴线 -->
    <view class="dayun-timeline__track">
      <scroll-view
        class="dayun-timeline__scroll"
        scroll-x
        :show-scrollbar="false"
        :scroll-left="scrollLeft"
        @scroll="onScroll"
      >
        <view class="dayun-timeline__list">
          <view
            v-for="(item, index) in dayunList"
            :key="index"
            class="dayun-timeline__item"
            :class="{
              'dayun-timeline__item--active': activeIndex === index,
              'dayun-timeline__item--current': item.isCurrent
            }"
            role="option"
            :aria-selected="activeIndex === index ? 'true' : 'false'"
            @tap="selectDayun(index)"
          >
            <!-- 节点 -->
            <view class="dayun-timeline__node">
              <view class="dayun-timeline__node-inner"></view>
            </view>
            <!-- 年龄标签 -->
            <text class="dayun-timeline__age">{{ item.age }}岁</text>
            <!-- 干支 -->
            <view class="dayun-timeline__ganzhi">
              <text class="dayun-timeline__gan">{{ item.gan }}</text>
              <text class="dayun-timeline__zhi">{{ item.zhi }}</text>
            </view>
            <!-- 年份 -->
            <text class="dayun-timeline__years">{{ item.years }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 选中大运详情 -->
    <view class="dayun-timeline__detail" v-if="selectedDayun">
      <classic-border variant="gold">
        <view class="detail-header">
          <text class="detail-age">{{ selectedDayun.age }}岁起运</text>
          <view class="detail-ganzhi-row">
            <ganzhi-tag :label="selectedDayun.gan" wuxing="earth" size="lg" />
            <ganzhi-tag :label="selectedDayun.zhi" wuxing="water" size="lg" />
          </view>
        </view>
        <view class="detail-info">
          <text class="detail-years">运势期间：{{ selectedDayun.years }}</text>
          <text class="detail-nayin">纳音：{{ selectedDayun.nayin }}</text>
        </view>
      </classic-border>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import ClassicBorder from './ClassicBorder.vue'
import GanzhiTag from './GanzhiTag.vue'

const props = defineProps({
  dayunList: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select'])

const activeIndex = ref(0)
const scrollLeft = ref(0)

const selectedDayun = computed(() => {
  if (props.dayunList.length === 0) return null
  return props.dayunList[activeIndex.value] || null
})

function selectDayun(index) {
  activeIndex.value = index
  emit('select', { index, data: props.dayunList[index] })
}

function onScroll(e) {
  // 处理滚动
}

// 初始选中当前大运
watch(() => props.dayunList, (list) => {
  if (list.length > 0) {
    const currentIdx = list.findIndex(item => item.isCurrent)
    if (currentIdx >= 0) {
      activeIndex.value = currentIdx
    }
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
.dayun-timeline {
  &__track {
    position: relative;
    padding: 20rpx 0;

    // 背景时间轴线
    &::before {
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      top: 48rpx;
      height: 2rpx;
      background: linear-gradient(90deg, transparent 0%, var(--accent-30) 10%, var(--accent-50) 50%, var(--accent-30) 90%, transparent 100%);
    }
  }

  &__scroll {
    width: 100%;
    white-space: nowrap;
  }

  &__list {
    display: flex;
    padding: 0 30rpx;
    gap: 0;
  }

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 140rpx;
    padding: 20rpx 10rpx;
    cursor: pointer;
    transition: color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    user-select: none;
    -webkit-user-select: none;

    &--active {
      .dayun-timeline__node-inner {
        background: var(--accent-light);
        box-shadow: 0 0 12rpx rgba(212, 175, 55, 0.6);
        width: 16rpx;
        height: 16rpx;
      }
      .dayun-timeline__age {
        color: var(--accent-light);
      }
      .dayun-timeline__gan,
      .dayun-timeline__zhi {
        color: var(--text-primary);
      }
    }

    &--current {
      .dayun-timeline__node {
        &::after {
          content: '';
          position: absolute;
          top: -4rpx;
          left: -4rpx;
          right: -4rpx;
          bottom: -4rpx;
          border-radius: 50%;
          border: 2rpx solid var(--accent-40);
          animation: pulse-ring 2s ease-out infinite;
        }
      }
    }
  }

  &__node {
    position: relative;
    width: 24rpx;
    height: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
    margin-bottom: 10rpx;

    &-inner {
      width: 10rpx;
      height: 10rpx;
      border-radius: 50%;
      background: var(--accent-30);
      transition: color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease;
    }
  }

  &__age {
    font-size: 22rpx;
    color: var(--text-muted);
    margin-bottom: 4rpx;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    transition: color 0.3s ease;
  }

  &__ganzhi {
    display: flex;
    gap: 4rpx;
    margin-bottom: 4rpx;
  }

  &__gan,
  &__zhi {
    font-size: 24rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    background: var(--bg-card);
    padding: 2rpx 10rpx;
    border-radius: 6rpx;
    transition: color 0.3s ease;
  }

  &__years {
    font-size: 18rpx;
    color: var(--text-placeholder);
  }

  // 详情区
  &__detail {
    margin-top: 16rpx;
  }

  .detail-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 12rpx;
  }

  .detail-age {
    font-size: 28rpx;
    color: var(--accent-light);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }

  .detail-ganzhi-row {
    display: flex;
    gap: 12rpx;
  }

  .detail-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6rpx;
  }

  .detail-years {
    font-size: 24rpx;
    color: var(--text-primary);
  }

  .detail-nayin {
    font-size: 22rpx;
    color: var(--text-muted);
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  }
}

@keyframes pulse-ring {
  0% {
    opacity: 0.8;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(2);
  }
}
</style>
