const app = getApp()
const theme = require('../../utils/theme')
const PROFILE_KEY = 'bazi_profiles'
const REQ_HEADER = { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': '1' }

Page({
  data: {
    name:'', gender:'男', calType:'solar', leap:false,
    sy:'1990',sm:'6',sd:'15', ly:'1990',lm:'5',ld:'21', fh:'8',fm:'0',
    themeStyle: '', currentTheme: '', icons: {},
    // 新功能
    showForm: false,
    profiles: [],
    todayInfo: null,
    dailyFortune: null,
    activeProfileId: null
  },

  onLoad() {
    this.applyTheme()
    this.loadProfiles()
    this.loadTodayInfo()
  },

  onShow() {
    this.applyTheme()
    this.loadProfiles()
    // 如果从结果页返回，可能缓存了上次排盘结果，更新日运
    if (app.globalData.paipanResult) {
      this.loadDailyFortune()
    }
  },

  applyTheme() {
    const t = app.globalData.theme || theme.getCurrentTheme()
    const style = theme.getThemeStyle(t)
    const icons = theme.getIconSet(t)
    this.setData({ themeStyle: style, currentTheme: t, icons: icons })
    const nc = theme.navBarColors[t]
    if (nc) wx.setNavigationBarColor({ frontColor: nc.front, backgroundColor: nc.bg })
  },

  // ===== 档案管理 =====
  loadProfiles() {
    try {
      const stored = wx.getStorageSync(PROFILE_KEY) || []
      this.setData({ profiles: stored })
      if (stored.length > 0) {
        // 恢复最近用的档案
        const activeId = wx.getStorageSync('bazi_active_profile')
        this.setData({ activeProfileId: activeId || '' })
      }
    } catch(e) {}
  },

  saveProfile(paipanData) {
    const d = this.data
    const profile = {
      id: Date.now().toString(36),
      name: d.name || '未命名',
      gender: d.gender,
      calendar_type: d.calType,
      solar_year: parseInt(d.sy), solar_month: parseInt(d.sm), solar_day: parseInt(d.sd),
      lunar_year: parseInt(d.ly), lunar_month: parseInt(d.lm), lunar_day: parseInt(d.ld),
      leap_month: d.leap,
      hour: parseInt(d.fh), minute: parseInt(d.fm),
      paipanResult: paipanData,
      createdAt: new Date().toISOString()
    }
    if (d.calType === 'lunar') {
      profile.solar_year = 0; profile.solar_month = 0; profile.solar_day = 0
    }
    const profiles = this.data.profiles.slice()
    // 去重（同姓名同性别同时辰）
    const dup = profiles.findIndex(p =>
      p.name === profile.name && p.gender === profile.gender &&
      p.solar_year === profile.solar_year && p.solar_month === profile.solar_month &&
      p.solar_day === profile.solar_day && p.hour === profile.hour
    )
    if (dup >= 0) profiles.splice(dup, 1) // 替换旧的
    profiles.unshift(profile) // 最新排最前
    if (profiles.length > 10) profiles.pop() // 最多10个
    wx.setStorageSync(PROFILE_KEY, profiles)
    wx.setStorageSync('bazi_active_profile', profile.id)
    this.setData({ profiles, activeProfileId: profile.id, showForm: false })
  },

  loadFromProfile(e) {
    const id = e.currentTarget.dataset.id
    const p = this.data.profiles.find(p => p.id === id)
    if (!p) return
    // 恢复表单数据
    this.setData({
      name: p.name, gender: p.gender, calType: p.calendar_type || 'solar',
      sy: String(p.solar_year || ''), sm: String(p.solar_month || ''),
      sd: String(p.solar_day || ''), ly: String(p.lunar_year || ''),
      lm: String(p.lunar_month || ''), ld: String(p.lunar_day || ''),
      fh: String(p.hour || ''), fm: String(p.minute || ''),
      leap: !!p.leap_month, activeProfileId: id
    })
    // 直接看结果
    if (p.paipanResult) {
      app.globalData.paipanResult = p.paipanResult
      wx.setStorageSync('bazi_active_profile', id)
      wx.navigateTo({ url: '/pages/result/result' })
    }
  },

  deleteProfile(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '删除档案', content: '确定删除这条记录？', success: res => {
        if (res.confirm) {
          const profiles = this.data.profiles.filter(p => p.id !== id)
          wx.setStorageSync(PROFILE_KEY, profiles)
          this.setData({ profiles, activeProfileId: this.data.activeProfileId === id ? '' : this.data.activeProfileId })
        }
      }
    })
  },

  // ===== 今日信息 =====
  loadTodayInfo() {
    const api = app.globalData.apiBase
    wx.request({
      url: api + '/calendar/today', method: 'GET', header: REQ_HEADER, timeout: 8000,
      success: resp => {
        if (resp.data && resp.data.success) this.setData({ todayInfo: resp.data.data })
      },
      fail: () => {}
    })
  },

  loadDailyFortune() {
    const api = app.globalData.apiBase
    const d = app.globalData.paipanResult
    if (!d) return
    wx.request({
      url: api + '/daily-fortune', method: 'POST',
      header: REQ_HEADER,
      data: { paipan_result: d }, timeout: 8000,
      success: resp => {
        if (resp.data && resp.data.success) this.setData({ dailyFortune: resp.data.data })
      },
      fail: () => {}
    })
  },

  // ===== 表单 =====
  toggleForm() {
    this.setData({ showForm: !this.data.showForm })
  },
  goSettings() {
    wx.navigateTo({ url: '/pages/settings/settings' })
  },
  onName(e){ this.setData({name:e.detail.value}) },
  onGender(e){ this.setData({gender:e.currentTarget.dataset.v}) },
  onCal(e){ this.setData({calType:e.currentTarget.dataset.v}) },
  onLeap(e){ this.setData({leap:e.currentTarget.dataset.v==='1'}) },
  onSy(e){ this.setData({sy:e.detail.value}) },
  onSm(e){ this.setData({sm:e.detail.value}) },
  onSd(e){ this.setData({sd:e.detail.value}) },
  onLy(e){ this.setData({ly:e.detail.value}) },
  onLm(e){ this.setData({lm:e.detail.value}) },
  onLd(e){ this.setData({ld:e.detail.value}) },
  onFh(e){ this.setData({fh:e.detail.value}) },
  onFm(e){ this.setData({fm:e.detail.value}) },

  async doPaipan(){
    const d = this.data
    const api = app.globalData.apiBase
    const body = {name:d.name||'未命名',gender:d.gender,hour:parseInt(d.fh)||0,minute:parseInt(d.fm)||0,longitude:120,latitude:30,calendar_type:d.calType}

    if(d.calType==='lunar'){
      const ly=parseInt(d.ly), lm=parseInt(d.lm), ld=parseInt(d.ld)
      if(!ly||!lm||!ld){ wx.showToast({title:'请填写完整农历日期',icon:'none'}); return }
      body.lunar_year=ly; body.lunar_month=lm; body.lunar_day=ld; body.leap_month=d.leap
    } else {
      const sy=parseInt(d.sy), sm=parseInt(d.sm), sd=parseInt(d.sd)
      if(!sy||!sm||!sd){ wx.showToast({title:'请填写完整公历日期',icon:'none'}); return }
      body.solar_year=sy; body.solar_month=sm; body.solar_day=sd
    }

    wx.showLoading({title:'推算命盘中...',mask:true})
    try {
      const resp = await new Promise((resolve, reject) => {
        wx.request({url:api+'/paipan',method:'POST',header:REQ_HEADER,data:body,timeout:30000,success:resolve,fail:reject})
      })
      wx.hideLoading()
      if(resp.data.success){
        app.globalData.paipanResult = resp.data.data
        this.saveProfile(resp.data.data)
        this.loadDailyFortune()
        wx.navigateTo({url:'/pages/result/result'})
      } else {
        wx.showToast({title:resp.data.error||'排盘失败',icon:'none'})
      }
    } catch(e){
      wx.hideLoading()
      wx.showToast({title:'网络请求失败，请检查服务器连接',icon:'none'})
    }
  }
})
