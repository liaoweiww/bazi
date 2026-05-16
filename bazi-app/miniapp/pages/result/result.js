const app = getApp()
const theme = require('../../utils/theme')

Page({
  data: {
    loaded: false,
    themeStyle: '', currentTheme: '', icons: {},
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
    showLifeSummary: true,
    // 年运年份
    fortuneYear: new Date().getFullYear(),
    // 大运选中
    selectedDayunIndex: -1
  },

  applyTheme() {
    const t = app.globalData.theme || theme.getCurrentTheme()
    const style = theme.getThemeStyle(t)
    const icons = theme.getIconSet(t)
    this.setData({ themeStyle: style, currentTheme: t, icons: icons })
  },

  onLoad() {
    this.applyTheme()
    const d = app.globalData.paipanResult
    if (!d) {
      wx.showToast({ title: '请先排盘', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }
    const now = new Date()
    const [by, bm, bd] = d.birth_info.solar_date.split('-').map(Number)
    const age = now.getFullYear() - by - ((now.getMonth() + 1 < bm) || (now.getMonth() + 1 === bm && now.getDate() < bd) ? 1 : 0)
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
      currentAge: age,
      fortuneYear: now.getFullYear()
    })

    const api = app.globalData.apiBase
    const postData = { paipan_result: d }

    const fail = (label, err) => console.error('API fail:', label, err)

    // 加载白话解读
    wx.request({
      url: api + '/vernacular', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: postData, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ vernacular: resp.data.data })
      },
      fail: err => fail('vernacular', err)
    })

    // 加载年运
    wx.request({
      url: api + '/year-fortune', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { ...postData, year: now.getFullYear() }, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ yearFortune: resp.data.data })
      },
      fail: err => fail('year-fortune', err)
    })

    // 加载时运
    wx.request({
      url: api + '/current-fortune', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: postData, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ currentFortune: resp.data.data })
      },
      fail: err => fail('current-fortune', err)
    })

    // 加载破解法
    wx.request({
      url: api + '/remedy', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: postData, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ remedy: resp.data.data })
      },
      fail: err => fail('remedy', err)
    })

    // 加载把控指南
    wx.request({
      url: api + '/control-guide', method: 'GET', timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ controlGuide: resp.data.data })
      },
      fail: err => fail('control-guide', err)
    })

    // 加载参考书籍
    wx.request({
      url: api + '/reference-books', method: 'GET', timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ books: resp.data.data })
      },
      fail: err => fail('reference-books', err)
    })

    // 加载四大运势总结
    wx.request({
      url: api + '/life-summary', method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: postData, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ lifeSummary: resp.data.data })
      },
      fail: err => fail('life-summary', err)
    })
  },

  onShow() {
    this.applyTheme()
    const t = app.globalData.theme || theme.getCurrentTheme()
    const nc = theme.navBarColors[t]
    if (nc) wx.setNavigationBarColor({ frontColor: nc.front, backgroundColor: nc.bg })
  },

  // 折叠切换
  toggleSection(e) {
    const key = e.currentTarget.dataset.key
    this.setData({ [key]: !this.data[key] })
  },

  // 选中大运节点
  selectDayun(e) {
    const idx = e.currentTarget.dataset.index
    this.setData({ selectedDayunIndex: this.data.selectedDayunIndex === idx ? -1 : idx })
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
