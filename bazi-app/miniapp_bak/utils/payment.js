// 微信小程序支付模块
var app = getApp()
var IS_TEST = true
var PRICE_FEN = 88
var UNLOCK_DESC = '易经八字-解锁完整命盘解读'

function isPurchased() {
  try { return wx.getStorageSync('bazi_purchased') || false } catch(e) { return false }
}

function markPurchased() {
  try { wx.setStorageSync('bazi_purchased', true) } catch(e) {}
}

function doPay() {
  return new Promise(function(resolve, reject) {
    if (IS_TEST) {
      // 测试模式：弹窗确认即解锁，不调后端
      wx.showModal({
        title: '解锁完整解读',
        content: '当前测试价 ¥' + (PRICE_FEN / 100).toFixed(2) + '\n正式上线后调起微信支付',
        confirmText: '确认解锁',
        cancelText: '取消',
        success: function(res) {
          if (res.confirm) {
            markPurchased()
            resolve(true)
          } else {
            reject('cancel')
          }
        }
      })
    } else {
      // 正式模式：走完整支付流程
      wx.showModal({
        title: '支付', content: '微信支付功能需配置商户号后启用', showCancel: false,
        success: function() { reject('not_configured') }
      })
    }
  })
}

function checkPurchaseStatus() {
  // 纯本地检查
  if (isPurchased()) return Promise.resolve(true)
  return Promise.resolve(false)
}

// 重置购买状态（调试用）
function resetPurchase() {
  try { wx.removeStorageSync('bazi_purchased') } catch(e) {}
}

module.exports = {
  IS_TEST: IS_TEST,
  PRICE_FEN: PRICE_FEN,
  doPay: doPay,
  isPurchased: isPurchased,
  checkPurchaseStatus: checkPurchaseStatus,
  resetPurchase: resetPurchase
}
