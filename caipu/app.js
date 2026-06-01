App({
  globalData: {
    apiBase: 'http://192.168.50.226:5002/api',
    categories: ['全部', '家常菜', '快手菜', '汤品', '荤菜', '素菜'],
    materialCategories: [],
  },
  onLaunch() {
    wx.showShareMenu({ withShareTicket: true })
  }
})
