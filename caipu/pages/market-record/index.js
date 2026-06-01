const api = require('../../utils/request')

Page({
  data: {
    materialId: null,
    material: null,
    price: '',
    unit: '斤',
    units: ['斤', '克', '个', '只', '条'],
    date: '',
    place: '',
    places: ['菜市场', '盒马', '京东买菜', '叮咚买菜', '美团买菜', '超市', '路边摊'],
    remark: '',
  },

  onLoad(options) {
    const now = new Date()
    const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
    const materialId = options.id
    this.setData({ materialId, date: dateStr })

    // 加载食材信息
    api.get(`/price/analysis/${materialId}`).then(res => {
      if (res.code === 0) {
        this.setData({
          material: res.data,
          unit: res.data.default_unit || '斤',
        })
      }
    }).catch(() => {})
  },

  onInput(e) {
    this.setData({ [e.currentTarget.dataset.field]: e.detail.value })
  },

  onSelectTap(e) {
    this.setData({ [e.currentTarget.dataset.field]: e.currentTarget.dataset.val })
  },

  onDateChange(e) {
    this.setData({ date: e.detail.value })
  },

  save() {
    const price = parseFloat(this.data.price)
    if (!price || price <= 0) {
      wx.showToast({ title: '请输入有效价格', icon: 'none' })
      return
    }
    const data = {
      material_id: parseInt(this.data.materialId),
      price,
      unit: this.data.unit,
      date: this.data.date,
      place: this.data.place,
      remark: this.data.remark,
    }
    api.post('/price/record/add', data).then(res => {
      if (res.code === 0) {
        wx.showToast({ title: '记价成功', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 1000)
      }
    })
  },
})
