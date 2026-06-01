/** 前端换算工具（本地快速算，不调接口） */

// 单位转克
function toGram(value, unit) {
  const u = (unit || '').toLowerCase()
  if (u.includes('g') || u.includes('克')) return value
  if (u.includes('斤')) return value * 500
  if (u.includes('两')) return value * 50
  if (u.includes('kg') || u.includes('千克') || u.includes('公斤')) return value * 1000
  return value
}

function gramToJin(val) { return val / 500 }

function scaleByPerson(base, target) {
  return base <= 0 ? 1.0 : target / base
}

function scaleByWeight(base, target) {
  return base <= 0 ? 1.0 : target / base
}

function calcCost(amount, unit, pricePerJin) {
  return parseFloat((gramToJin(toGram(amount, unit)) * pricePerJin).toFixed(2))
}

module.exports = {
  toGram,
  gramToJin,
  scaleByPerson,
  scaleByWeight,
  calcCost,
}
