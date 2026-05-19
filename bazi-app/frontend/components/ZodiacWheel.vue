<template>
  <view class="zodiac-wheel">
    <canvas
      :canvas-id="canvasId"
      :id="canvasId"
      :style="{ width: size + 'px', height: size + 'px' }"
      class="zodiac-wheel__canvas"
    ></canvas>
  </view>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  planets: { type: Array, default: () => [] },
  houses: { type: Array, default: () => [] },
  ascDegree: { type: Number, default: 0 }
})

const canvasId = 'zodiac-' + Math.random().toString(36).slice(2, 8)
const size = ref(320)

const SIGN_COLORS = {
  '火': '#e04030', '土': '#8a7a40', '风': '#b0b840', '水': '#4060c0'
}
const SIGN_SYMBOLS = {
  '白羊座': '♈', '金牛座': '♉', '双子座': '♊', '巨蟹座': '♋',
  '狮子座': '♌', '处女座': '♍', '天秤座': '♎', '天蝎座': '♏',
  '射手座': '♐', '摩羯座': '♑', '水瓶座': '♒', '双鱼座': '♓'
}
const PLANET_SYMBOLS = {
  '太阳': '☉', '月亮': '☽', '水星': '☿', '金星': '♀', '火星': '♂',
  '木星': '♃', '土星': '♄', '天王星': '♅', '海王星': '♆', '冥王星': '♇'
}

function draw() {
  try {
    const ctx = uni.createCanvasContext(canvasId)
    const w = size.value
    const cx = w / 2, cy = w / 2
    const outerR = cx - 8, innerR = outerR * 0.72, signR = outerR * 0.88, planetR = outerR * 0.55

    // 背景
    ctx.beginPath()
    ctx.arc(cx, cy, outerR + 4, 0, 2 * Math.PI)
    ctx.fillStyle = '#1a1a20'
    ctx.fill()

    // === 12宫位扇区 ===
    const houseColors = ['#2a2a35', '#252530', '#2a2a35', '#252530', '#2a2a35', '#252530',
                         '#2a2a35', '#252530', '#2a2a35', '#252530', '#2a2a35', '#252530']
    for (let i = 0; i < 12; i++) {
      const startAngle = -Math.PI / 2 + (i * Math.PI / 6)
      const endAngle = startAngle + Math.PI / 6
      ctx.beginPath()
      ctx.moveTo(cx, cy)
      ctx.arc(cx, cy, outerR, startAngle, endAngle)
      ctx.closePath()
      ctx.fillStyle = houseColors[i]
      ctx.fill()
      ctx.strokeStyle = '#3a3a48'
      ctx.lineWidth = 1
      ctx.stroke()

      // 宫位号
      const midAngle = startAngle + Math.PI / 12
      const numX = cx + (outerR - 24) * Math.cos(midAngle)
      const numY = cy + (outerR - 24) * Math.sin(midAngle)
      ctx.setFillStyle('#888')
      ctx.setFontSize(11)
      ctx.setTextAlign('center')
      ctx.setTextBaseline('middle')
      ctx.fillText(String(i + 1), numX, numY)
    }

    // === 内圈 ===
    ctx.beginPath()
    ctx.arc(cx, cy, innerR, 0, 2 * Math.PI)
    ctx.fillStyle = '#1a1a20'
    ctx.fill()
    ctx.strokeStyle = '#3a3a48'
    ctx.lineWidth = 2
    ctx.stroke()

    // === 星座环 ===
    // 星座从白羊座(0°)开始，在圆上从-90°(顶部)顺时针排列
    for (let i = 0; i < 12; i++) {
      // 白羊座=0° 对应圆的右边缘(-90+0=-90°)... wait
      // 在占星学中，ASC在左边(东)，所以白羊座(0°)在左侧
      // 实际上，从顶部(-90°)顺时针: 摩羯300° → 水瓶330° → 双鱼0° → ...
      // 让我简化: 直接从ASC位置开始
      const signNames = ['白羊座','金牛座','双子座','巨蟹座','狮子座','处女座',
                         '天秤座','天蝎座','射手座','摩羯座','水瓶座','双鱼座']
      const angle = -Math.PI/2 - (i * Math.PI/6)
      const sx = cx + signR * Math.cos(angle)
      const sy = cy + signR * Math.sin(angle)
      const sym = SIGN_SYMBOLS[signNames[i]] || ''
      ctx.setFillStyle(SIGN_COLORS[['火','土','风','水'][i % 4]] || '#888')
      ctx.setFontSize(16)
      ctx.setTextAlign('center')
      ctx.setTextBaseline('middle')
      ctx.fillText(sym, sx, sy)
    }

    // === 行星标记 ===
    props.planets.forEach(p => {
      if (p.lon == null) return
      const lonRad = Math.radians ? Math.radians(p.lon) : p.lon * Math.PI / 180
      // 黄经0°(白羊座0°)在标准天图中在左侧
      const angle = -Math.PI / 2 + lonRad
      const px = cx + planetR * Math.cos(angle)
      const py = cy + planetR * Math.sin(angle)

      // 行星圆点
      ctx.beginPath()
      ctx.arc(px, py, 7, 0, 2 * Math.PI)
      const pColor = ['太阳','月亮'].includes(p.name_cn) ? '#e8c840' :
                     ['火星','冥王星'].includes(p.name_cn) ? '#e04030' :
                     ['金星','木星'].includes(p.name_cn) ? '#60c040' :
                     ['土星'].includes(p.name_cn) ? '#a0a040' :
                     ['水星'].includes(p.name_cn) ? '#40a0e0' :
                     ['天王星'].includes(p.name_cn) ? '#40c0c0' :
                     ['海王星'].includes(p.name_cn) ? '#8040c0' : '#aaa'
      ctx.fillStyle = pColor
      ctx.fill()
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 1
      ctx.stroke()

      // 行星符号
      const psym = PLANET_SYMBOLS[p.name_cn] || p.name_cn[0]
      ctx.setFillStyle('#fff')
      ctx.setFontSize(10)
      ctx.setTextAlign('center')
      ctx.setTextBaseline('middle')
      ctx.fillText(psym, px, py - 12)
    })

    // === ASC 标记 ===
    if (props.ascDegree != null) {
      const ascRad = Math.PI * props.ascDegree / 180
      const ascAngle = -Math.PI / 2 + ascRad
      const ax = cx + (outerR + 12) * Math.cos(ascAngle)
      const ay = cy + (outerR + 12) * Math.sin(ascAngle)
      ctx.setFillStyle('#d4af37')
      ctx.setFontSize(14)
      ctx.setTextAlign('center')
      ctx.setTextBaseline('middle')
      ctx.fillText('ASC', ax, ay)

      // ASC 短线
      const ax2 = cx + (outerR - 4) * Math.cos(ascAngle)
      const ay2 = cy + (outerR - 4) * Math.sin(ascAngle)
      ctx.beginPath()
      ctx.moveTo(ax2, ay2)
      ctx.lineTo(ax, ay)
      ctx.strokeStyle = '#d4af37'
      ctx.lineWidth = 2
      ctx.stroke()
    }

    // === 中心文字 ===
    ctx.setFillStyle('#888')
    ctx.setFontSize(10)
    ctx.setTextAlign('center')
    ctx.setTextBaseline('middle')
    ctx.fillText('星盘', cx, cy)

    ctx.draw()
  } catch (e) {
    // Canvas 在小程序环境可能不可用
  }
}

onMounted(() => { nextTick(draw) })
watch(() => [props.planets, props.ascDegree], draw, { deep: true })
</script>

<style lang="scss" scoped>
.zodiac-wheel { display: flex; justify-content: center; padding: 16rpx 0; }
.zodiac-wheel__canvas { border-radius: 8rpx; }
</style>
