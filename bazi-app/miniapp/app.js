const theme = require('./utils/theme')

App({
  globalData: {
    apiBase: 'https://worrisome-fraternal-scared.ngrok-free.dev/api',
    paipanResult: null,
    theme: 'classic',
    themeStyle: ''
  },
  onLaunch() {
    const t = theme.getCurrentTheme()
    this.globalData.theme = t
    this.globalData.themeStyle = theme.getThemeStyle(t)
    wx.showShareMenu({ withShareTicket: true })
  }
})
