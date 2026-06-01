const api = require('../../utils/request')

Page({
  data: {
    materials: [],
    categories: [],
    activeCategoryId: 0,
    keyword: '',
  },

  onLoad() {
    this.loadCategories()
  },

  onShow() {
    this.loadMaterials()
  },

  loadCategories() {
    api.get('/material/categories').then(res => {
      if (res.code === 0) {
        this.setData({ categories: [{ id: 0, name: '全部' }, ...res.data] })
      }
    }).catch(() => {})
  },

  loadMaterials() {
    const { activeCategoryId, keyword } = this.data
    const params = {}
    if (activeCategoryId > 0) params.category_id = activeCategoryId
    if (keyword) params.keyword = keyword
    api.get('/material/list', params).then(res => {
      if (res.code === 0) {
        this.setData({ materials: res.data })
      }
    }).catch(() => {})
  },

  onCategoryTap(e) {
    this.setData({ activeCategoryId: e.currentTarget.dataset.id })
    this.loadMaterials()
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    this.loadMaterials()
  },

  onMaterialTap(e) {
    wx.navigateTo({ url: `/pages/market-detail/index?id=${e.currentTarget.dataset.id}` })
  },

  onAddTap() {
    wx.navigateTo({ url: '/pages/market-create/index' })
  },
})
