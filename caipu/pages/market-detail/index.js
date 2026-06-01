const api = require('../../utils/request')
const { changeRate, priceLevel } = require('../../utils/price')

Page({
  data: {
    materialId: null,
    material: null,
    activeTab: 'chart', // 'chart' | 'records'
    marketCurve: [],
    personalCurve: [],

    // 分析数据
    priceAnalysis: '',
    trend: '',
    changeVs30d: 0,
    historyMin: 0,
    historyMax: 0,
    avg: 0,
    count: 0,
  },

  onLoad(options) {
    this.setData({ materialId: options.id })
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  loadData() {
    api.get(`/price/analysis/${this.data.materialId}`).then(res => {
      if (res.code === 0) {
        const d = res.data
        this.setData({
          material: d,
          marketCurve: d.market_curve || [],
          personalCurve: d.personal_curve || [],
          priceAnalysis: d.price_analysis,
          trend: d.trend,
          changeVs30d: d.change_vs_30d_avg || 0,
          historyMin: d.min,
          historyMax: d.max,
          avg: d.avg,
          count: d.count,
        })
      }
    }).catch(() => {})
  },

  onTabSwitch(e) {
    this.setData({ activeTab: e.currentTarget.dataset.tab })
  },

  onQuickRecord() {
    wx.navigateTo({ url: `/pages/market-record/index?id=${this.data.materialId}` })
  },
})
