App({
  globalData: {
    // API 服务器地址 - 部署后需替换为实际服务器地址
    apiBase: 'http://192.168.50.226:8080/api',
    paipanResult: null
  },
  onLaunch() {
    wx.showShareMenu({ withShareTicket: true })
  }
})
