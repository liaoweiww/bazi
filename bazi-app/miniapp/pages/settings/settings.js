const theme = require('../../utils/theme')
const app = getApp()

Page({
  data: {
    themes: theme.themeMeta,
    current: theme.getCurrentTheme(),
    themeStyle: theme.getThemeStyle(),
    currentTheme: theme.getCurrentTheme(),
    icons: {}
  },

  onShow() {
    const t = theme.getCurrentTheme()
    this.setData({ current: t, currentTheme: t, themeStyle: theme.getThemeStyle(t), icons: theme.getIconSet(t) })
    const nc = theme.navBarColors[t]
    if (nc) wx.setNavigationBarColor({ frontColor: nc.front, backgroundColor: nc.bg })
  },

  onSelect(e) {
    const id = e.currentTarget.dataset.id
    if (id === this.data.current) return

    if (theme.setTheme(id)) {
      this.setData({ current: id, currentTheme: id, themeStyle: theme.getThemeStyle(id), icons: theme.getIconSet(id) })
      const nc = theme.navBarColors[id]
      if (nc) wx.setNavigationBarColor({ frontColor: nc.front, backgroundColor: nc.bg })
      app.globalData.theme = id
      app.globalData.themeStyle = theme.getThemeStyle(id)
      wx.showToast({ title: '已切换', icon: 'success', duration: 1000 })
    }
  }
})
