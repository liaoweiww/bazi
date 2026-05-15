<template>
  <!-- 五行力量图表组件（Canvas绘制） -->
  <view class="wuxing-chart">
    <view class="wuxing-chart__container">
      <!-- Canvas 绘制区域 -->
      <canvas
        v-if="canvasId"
        :canvas-id="canvasId"
        :id="canvasId"
        class="wuxing-chart__canvas"
        :style="{ width: canvasSize + 'px', height: canvasSize + 'px' }"
      ></canvas>

      <!-- 回退显示：简易柱状图 -->
      <view class="wuxing-chart__bars" v-if="!canvasId">
        <view
          v-for="item in chartData"
          :key="item.name"
          class="wuxing-chart__bar-item"
        >
          <text class="wuxing-chart__bar-label" :style="{ color: item.color }">{{ item.name }}</text>
          <view class="wuxing-chart__bar-track">
            <view
              class="wuxing-chart__bar-fill"
              :style="{
                width: item.percent + '%',
                background: item.color
              }"
            ></view>
          </view>
          <text class="wuxing-chart__bar-value">{{ item.count }}</text>
        </view>
      </view>
    </view>

    <!-- 身强身弱判定 -->
    <view class="wuxing-chart__conclusion" v-if="riStrength">
      <view class="conclusion-badge" :class="riStrength === '身强' ? 'conclusion-strong' : 'conclusion-weak'">
        <text class="conclusion-text">{{ riStrength }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  wuxingData: {
    type: Object,
    default: () => ({})
  },
  riStrength: {
    type: String,
    default: ''
  }
})

// canvas尺寸
const canvasSize = 200
const canvasId = ref('')

onMounted(() => {
  // 尝试生成唯一canvasId
  canvasId.value = 'wuxingChart_' + Math.random().toString(36).slice(2, 8)
  nextTick(() => {
    drawRadarChart()
  })
})

const wuxingOrder = ['金', '木', '水', '火', '土']

const wuxingColors = {
  '金': '#f5f0e8',
  '木': '#4a7c59',
  '水': '#2c3e6b',
  '火': '#c41e3a',
  '土': '#c9a96e'
}

const chartData = computed(() => {
  return wuxingOrder.map(name => {
    const count = props.wuxingData[name] || 0
    const maxCount = Math.max(...Object.values(props.wuxingData || {}), 1)
    return {
      name,
      count,
      percent: Math.round((count / maxCount) * 100),
      color: wuxingColors[name]
    }
  })
})

function drawRadarChart() {
  if (!canvasId.value) return

  // #ifdef MP-WEIXIN
  const ctx = uni.createCanvasContext(canvasId.value, this)
  // #endif

  // #ifndef MP-WEIXIN
  const query = uni.createSelectorQuery().in(this)
  query.select('#' + canvasId.value).fields({ node: true, size: true }).exec((res) => {
    if (!res[0]) return
    const canvas = res[0].node
    const ctx = canvas.getContext('2d')
    const dpr = uni.getSystemInfoSync().pixelRatio
    canvas.width = canvasSize * dpr
    canvas.height = canvasSize * dpr
    ctx.scale(dpr, dpr)
    doDrawRadar(ctx)
  })
  // #endif
}

function doDrawRadar(ctx) {
  const cx = canvasSize / 2
  const cy = canvasSize / 2
  const radius = canvasSize / 2 - 30
  const count = 5
  const angleStep = (Math.PI * 2) / count
  const startAngle = -Math.PI / 2 // 从顶部开始

  const maxVal = Math.max(...Object.values(props.wuxingData || {}), 1)

  // 绘制背景网格
  const gridLevels = 4
  for (let level = 1; level <= gridLevels; level++) {
    const r = (radius / gridLevels) * level
    ctx.beginPath()
    for (let i = 0; i < count; i++) {
      const angle = startAngle + angleStep * i
      const x = cx + r * Math.cos(angle)
      const y = cy + r * Math.sin(angle)
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    ctx.closePath()
    ctx.strokeStyle = 'rgba(201, 169, 110, 0.15)'
    ctx.lineWidth = 1
    ctx.stroke()
  }

  // 绘制轴线
  for (let i = 0; i < count; i++) {
    const angle = startAngle + angleStep * i
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + radius * Math.cos(angle), cy + radius * Math.sin(angle))
    ctx.strokeStyle = 'rgba(201, 169, 110, 0.2)'
    ctx.lineWidth = 1
    ctx.stroke()
  }

  // 绘制数据区域
  const data = wuxingOrder.map(name => props.wuxingData[name] || 0)
  ctx.beginPath()
  for (let i = 0; i < count; i++) {
    const angle = startAngle + angleStep * i
    const val = (data[i] / maxVal) * radius
    const x = cx + val * Math.cos(angle)
    const y = cy + val * Math.sin(angle)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.closePath()
  ctx.fillStyle = 'rgba(201, 169, 110, 0.12)'
  ctx.fill()
  ctx.strokeStyle = 'rgba(201, 169, 110, 0.5)'
  ctx.lineWidth = 2
  ctx.stroke()

  // 绘制数据点
  for (let i = 0; i < count; i++) {
    const angle = startAngle + angleStep * i
    const val = (data[i] / maxVal) * radius
    const x = cx + val * Math.cos(angle)
    const y = cy + val * Math.sin(angle)
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fillStyle = wuxingColors[wuxingOrder[i]]
    ctx.fill()
    ctx.strokeStyle = 'rgba(26, 10, 0, 0.8)'
    ctx.lineWidth = 1
    ctx.stroke()
  }

  // 绘制标签
  const labelRadius = radius + 22
  ctx.fillStyle = '#f5f0e8'
  ctx.font = '14px "STKaiti", "KaiTi", "楷体", serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  for (let i = 0; i < count; i++) {
    const angle = startAngle + angleStep * i
    const lx = cx + labelRadius * Math.cos(angle)
    const ly = cy + labelRadius * Math.sin(angle)
    ctx.fillText(wuxingOrder[i], lx, ly)
  }

  ctx.draw()
}
</script>

<style lang="scss" scoped>
.wuxing-chart {
  padding: 16px 0;

  &__container {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  &__canvas {
    background: transparent;
  }

  // 简易柱状图回退
  &__bars {
    width: 100%;
    padding: 0 16px;
  }

  &__bar-item {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 16rpx;
  }

  &__bar-label {
    width: 40rpx;
    font-size: 26rpx;
    font-family: 'STKaiti', 'KaiTi', '楷体', serif;
    text-align: center;
  }

  &__bar-track {
    flex: 1;
    height: 16rpx;
    background: rgba(61, 43, 26, 0.4);
    border-radius: 8rpx;
    overflow: hidden;
  }

  &__bar-fill {
    height: 100%;
    border-radius: 8rpx;
    transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    min-width: 8rpx;
  }

  &__bar-value {
    width: 40rpx;
    font-size: 22rpx;
    color: #c9a96e;
    text-align: center;
  }

  // 身强身弱判定
  &__conclusion {
    display: flex;
    justify-content: center;
    margin-top: 12rpx;
  }

  .conclusion-badge {
    padding: 6rpx 32rpx;
    border-radius: 20rpx;
    border: 1rpx solid;

    &.conclusion-strong {
      background: rgba(212, 175, 55, 0.15);
      border-color: rgba(212, 175, 55, 0.4);
      .conclusion-text {
        color: #d4af37;
      }
    }

    &.conclusion-weak {
      background: rgba(196, 30, 58, 0.12);
      border-color: rgba(196, 30, 58, 0.35);
      .conclusion-text {
        color: #e06070;
      }
    }

    .conclusion-text {
      font-size: 28rpx;
      font-family: 'STKaiti', 'KaiTi', '楷体', serif;
      font-weight: bold;
    }
  }
}
</style>
