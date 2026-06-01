/** 价格分析工具 */

function changeRate(oldPrice, newPrice) {
  if (oldPrice <= 0) return 0
  return parseFloat(((newPrice - oldPrice) / oldPrice * 100).toFixed(1))
}

function priceLevel(current, minP, maxP) {
  if (minP <= 0 || maxP <= 0) return '无参考数据'
  const mid = (minP + maxP) / 2
  if (current <= mid * 0.9) return '偏低，适合购入'
  if (current >= mid * 1.1) return '偏高，不建议购入'
  return '适中'
}

module.exports = { changeRate, priceLevel }
