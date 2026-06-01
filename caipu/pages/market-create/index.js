const api = require('../../utils/request')

Page({
  data: {
    categories: [],
    materialName: '',
    categoryId: 1,
    defaultUnit: '斤',
    units: ['斤', '克', '个', '只', '条'],
    marketMinPrice: 0,
    marketMaxPrice: 0,
    lastUserPrice: 0,
    place: '',
    remark: '',
  },

  onLoad() {
    api.get('/material/categories').then(res => {
      if (res.code === 0) this.setData({ categories: res.data })
    }).catch(() => {})
  },

  onInput(e) {
    const { field } = e.currentTarget.dataset
    const val = e.detail.value
    this.setData({ [field]: val })
  },

  onSelectTap(e) {
    const { field, val } = e.currentTarget.dataset
    this.setData({ [field]: val })
  },

  save() {
    const name = this.data.materialName.trim()
    if (!name) {
      wx.showToast({ title: '请输入食材名称', icon: 'none' })
      return
    }
    const data = {
      material_name: name,
      category_id: this.data.categoryId,
      default_unit: this.data.defaultUnit,
      market_min_price: parseFloat(this.data.marketMinPrice) || 0,
      market_max_price: parseFloat(this.data.marketMaxPrice) || 0,
      last_user_price: parseFloat(this.data.lastUserPrice) || 0,
      place: this.data.place.trim(),
      remark: this.data.remark.trim(),
    }
    api.post('/material/create', data).then(res => {
      if (res.code === 0) {
        wx.showToast({ title: '添加成功', icon: 'success' })
        wx.navigateBack()
      } else {
        wx.showToast({ title: res.msg, icon: 'none' })
      }
    })
  },
})
