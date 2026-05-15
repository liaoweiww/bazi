App({
  globalData: {
    apiBase: 'https://worrisome-fraternal-scared.ngrok-free.dev/api',
    paipanResult: null
  },
  onLaunch() {
    wx.showShareMenu({ withShareTicket: true })
  }
})
