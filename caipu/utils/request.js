const app = getApp()

function request(url, options = {}) {
  const apiBase = app.globalData.apiBase
  return new Promise((resolve, reject) => {
    wx.request({
      url: apiBase + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      timeout: 30000,
      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          wx.showToast({ title: '网络异常', icon: 'none' })
          reject(res)
        }
      },
      fail(err) {
        wx.showToast({ title: '请求失败，检查网络', icon: 'none' })
        reject(err)
      }
    })
  })
}

module.exports = {
  get(url, data) { return request(url, { method: 'GET', data }) },
  post(url, data) { return request(url, { method: 'POST', data }) },
  put(url, data) { return request(url, { method: 'PUT', data }) },
  del(url) { return request(url, { method: 'DELETE' }) },
}
