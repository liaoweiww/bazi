const app = getApp()
const theme = require('../../utils/theme')
const REQ_HEADER = { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': '1' }

Page({
  data: {
    loaded: false,
    themeStyle: '', currentTheme: '', icons: {},
    showCanvas: false,
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
      header: REQ_HEADER,
      data: postData, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ vernacular: resp.data.data })
      },
      fail: err => fail('vernacular', err)
    })

    // 加载年运
    wx.request({
      url: api + '/year-fortune', method: 'POST',
      header: REQ_HEADER,
      data: { ...postData, year: now.getFullYear() }, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ yearFortune: resp.data.data })
      },
      fail: err => fail('year-fortune', err)
    })

    // 加载时运
    wx.request({
      url: api + '/current-fortune', method: 'POST',
      header: REQ_HEADER,
      data: postData, timeout: 15000,
      success: resp => {
        if (resp.data.success) this.setData({ currentFortune: resp.data.data })
      },
      fail: err => fail('current-fortune', err)
    })

    // 加载破解法
    wx.request({
      url: api + '/remedy', method: 'POST',
      header: REQ_HEADER,
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
      header: REQ_HEADER,
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
      header: REQ_HEADER,
      data: { paipan_result: d, year: this.data.fortuneYear },
      success: resp => {
        if (resp.data.success) this.setData({ yearFortune: resp.data.data })
      }
    })
  },

  goBack() { wx.navigateBack() },

  // 生成分享海报
  generateSharePoster() {
    this.setData({ showCanvas: true })
    const d = this.data
    const ctx = wx.createCanvasContext('shareCanvas', this)

    // 背景
    ctx.setFillStyle('#0d0a05')
    ctx.fillRect(0, 0, 375, 600)

    // 顶部装饰线
    ctx.setFillStyle('#d4af37')
    ctx.fillRect(20, 20, 335, 2)

    // 标题
    ctx.setFillStyle('#d4af37')
    ctx.setFontSize(28)
    ctx.setTextAlign('center')
    ctx.fillText('易经八字', 187, 60)

    // 副标题
    ctx.setFillStyle('#8b7355')
    ctx.setFontSize(12)
    ctx.fillText('探寻命理玄机 · 洞悉人生轨迹', 187, 82)

    // 命盘信息
    ctx.setFillStyle('#f5f0e8')
    ctx.setFontSize(16)
    const ps = d.pillars
    const y = 115
    ctx.fillText(ps.year.ganzhi + '  ' + ps.month.ganzhi + '  ' + ps.day.ganzhi + '  ' + ps.hour.ganzhi, 187, y)

    // 日主
    ctx.setFillStyle('#d4af37')
    ctx.setFontSize(14)
    ctx.fillText('日主：' + d.dm + '（' + d.dmWx + '）', 187, y + 28)

    // 分割线
    ctx.setStrokeStyle('rgba(201,169,110,0.2)')
    ctx.setLineWidth(1)
    ctx.beginPath()
    ctx.moveTo(40, y + 45); ctx.lineTo(335, y + 45)
    ctx.stroke()

    // 格局
    const gy = y + 65
    ctx.setFillStyle('#c0b090')
    ctx.setFontSize(14)
    ctx.fillText('格局：' + d.geju.type + ' · ' + d.geju.name, 187, gy)

    // 身强身弱
    ctx.fillText('日主状态：' + d.strength.level, 187, gy + 24)

    // 运势简要
    let sy = gy + 50
    ctx.setFillStyle('#d4af37')
    ctx.setFontSize(15)
    ctx.fillText('— 近期运势 —', 187, sy)

    ctx.setFillStyle('#c0b090')
    ctx.setFontSize(13)
    if (d.currentFortune && d.currentFortune.stage_analysis) {
      const txt = d.currentFortune.stage_analysis.substring(0, 60)
      ctx.fillText(txt, 187, sy + 24)
    }

    // 底部
    ctx.setFillStyle('#d4af37')
    ctx.setFontSize(10)
    ctx.fillText('— 古籍级 · 纯正子平术 · 本地离线 —', 187, 570)
    ctx.setFillStyle('#5a4a3a')
    ctx.setFontSize(9)
    ctx.fillText('易经八字 v1.1 · 扫一扫体验', 187, 588)

    ctx.draw(false, () => {
      setTimeout(() => {
        wx.canvasToTempFilePath({
          canvasId: 'shareCanvas',
          success: res => {
            this.setData({ showCanvas: false })
            wx.saveImageToPhotosAlbum({
              filePath: res.tempFilePath,
              success: () => wx.showToast({ title: '已保存到相册', icon: 'success' }),
              fail: () => {
                wx.showToast({ title: '请允许相册权限', icon: 'none' })
              }
            })
          },
          fail: () => {
            this.setData({ showCanvas: false })
            wx.showToast({ title: '生成失败', icon: 'none' })
          }
        }, this)
      }, 500)
    })
  }
})
