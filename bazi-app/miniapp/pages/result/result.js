const app = getApp()
Page({
  data: {
    loaded: false,
    // 折叠状态
    showBirth: false,
    showShensha: false,
    showDayunDetail: false,
    showYearFortune: true,
    showCurrentFortune: true,
    showRemedy: true,
    showControl: false,
    showBooks: false,
    showVernacular: true,
    // 年运年份
    fortuneYear: new Date().getFullYear()
  },
  onLoad() {
    const d = app.globalData.paipanResult
    if (!d) {
      wx.showToast({ title: '请先排盘', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }
    const now = new Date()
    this.setData({
      loaded: true,
      name: d.name || '',
      pillars: d.four_pillars,
      dm: d.day_master,
      dmWx: d.day_master_wuxing,
      birth: d.birth_info,
      wxCount: d.wuxing_count,
      strength: d.strength,
      geju: d.geju,
      yongji: d.yongji,
      dayun: d.dayun,
      shensha: d.shensha || {},
      changsheng: d.changsheng || {},
      taiyuan: d.taiyuan || '',
      minggong: d.minggong || '',
      shengong: d.shengong || '',
      kongwang: (d.kongwang || []).join('、'),
      currentAge: now.getFullYear() - parseInt(d.birth_info.solar_date.split('-')[0]),
      fortuneYear: now.getFullYear()
    })

    const api = app.globalData.apiBase
    const postData = { paipan_result: d }

    // 加载白话解读
    wx.request({
      url: api + '/vernacular', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: postData,
      success: resp => {
        if (resp.data.success) this.setData({ vernacular: resp.data.data })
      }
    })

    // 加载年运
    wx.request({
      url: api + '/year-fortune', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { ...postData, year: now.getFullYear() },
      success: resp => {
        if (resp.data.success) this.setData({ yearFortune: resp.data.data })
      }
    })

    // 加载时运
    wx.request({
      url: api + '/current-fortune', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: postData,
      success: resp => {
        if (resp.data.success) this.setData({ currentFortune: resp.data.data })
      }
    })

    // 加载破解法
    wx.request({
      url: api + '/remedy', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: postData,
      success: resp => {
        if (resp.data.success) this.setData({ remedy: resp.data.data })
      }
    })

    // 加载把控指南
    wx.request({
      url: api + '/control-guide', method: 'GET',
      success: resp => {
        if (resp.data.success) this.setData({ controlGuide: resp.data.data })
      }
    })

    // 加载参考书籍
    wx.request({
      url: api + '/reference-books', method: 'GET',
      success: resp => {
        if (resp.data.success) this.setData({ books: resp.data.data })
      }
    })
  },

  // 折叠切换
  toggleSection(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ [key]: !this.data[key] })
  },

  // 切换年运年份
  prevYear() { this.setData({ fortuneYear: this.data.fortuneYear - 1 }); this.loadYearFortune() },
  nextYear() { this.setData({ fortuneYear: this.data.fortuneYear + 1 }); this.loadYearFortune() },

  loadYearFortune() {
    const d = app.globalData.paipanResult
    const api = app.globalData.apiBase
    wx.request({
      url: api + '/year-fortune', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { paipan_result: d, year: this.data.fortuneYear },
      success: resp => {
        if (resp.data.success) this.setData({ yearFortune: resp.data.data })
      }
    })
  },

  goBack() { wx.navigateBack() }
})
