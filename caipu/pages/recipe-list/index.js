const api = require('../../utils/request')

Page({
  data: {
    recipes: [],
    categories: ['全部', '家常菜', '快手菜', '汤品', '荤菜', '素菜'],
    activeCategory: '全部',
    keyword: '',
  },

  onLoad() {
    this.loadRecipes()
  },

  onShow() {
    this.loadRecipes()
  },

  onPullDownRefresh() {
    this.loadRecipes().then(() => wx.stopPullDownRefresh())
  },

  loadRecipes() {
    const { activeCategory, keyword } = this.data
    const params = {}
    if (activeCategory !== '全部') params.category = activeCategory
    if (keyword) params.keyword = keyword
    return api.get('/recipe/list', params).then(res => {
      if (res.code === 0) {
        this.setData({ recipes: res.data })
      }
    }).catch(() => {})
  },

  onCategoryTap(e) {
    const cat = e.currentTarget.dataset.cat
    this.setData({ activeCategory: cat })
    this.loadRecipes()
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    this.loadRecipes()
  },

  onRecipeTap(e) {
    wx.navigateTo({ url: `/pages/recipe-detail/index?id=${e.currentTarget.dataset.id}` })
  },

  onDeleteRecipe(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除？',
      content: '删除后无法恢复',
      success: (res) => {
        if (res.confirm) {
          api.del(`/recipe/delete/${id}`).then(() => this.loadRecipes())
        }
      }
    })
  },

  onAddTap() {
    wx.showActionSheet({
      itemList: ['新建空白菜谱', '取消'],
      success: (res) => {
        if (res.tapIndex === 0) {
          wx.navigateTo({ url: '/pages/recipe-create/index' })
        }
      }
    })
  },
})
