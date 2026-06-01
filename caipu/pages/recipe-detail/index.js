const api = require('../../utils/request')
const { scaleByPerson, scaleByWeight, calcCost } = require('../../utils/scale')

Page({
  data: {
    recipeId: null,
    recipe: null,
    ingredients: [],
    steps: [],
    totalCost: 0,
    perPersonCost: 0,

    // 换算模式
    scaleMode: 'person', // 'person' | 'weight'
    targetPerson: 2,
    targetWeight: 0,
    scale: 1.0,
    estimatedPeople: 2,

    // 折叠
    showSteps: true,
    lockedIds: [],
  },

  onLoad(options) {
    this.setData({ recipeId: options.id })
    this.loadDetail()
  },

  loadDetail() {
    const id = this.data.recipeId
    if (!id) return
    api.get(`/recipe/detail/${id}`).then(res => {
      if (res.code === 0) {
        const r = res.data
        this.setData({
          recipe: r,
          ingredients: r.ingredients,
          steps: r.steps,
          totalCost: r.total_cost,
          perPersonCost: r.per_person_cost,
          targetPerson: r.base_person,
          targetWeight: r.main_weight,
          estimatedPeople: r.base_person,
          scale: 1.0,
        })
      }
    })
  },

  // 模式切换
  onModeSwitch(e) {
    const mode = e.currentTarget.dataset.mode
    this.setData({ scaleMode: mode })
    this.doScale()
  },

  // 人数变更
  onPersonMinus() {
    const v = Math.max(1, this.data.targetPerson - 1)
    this.setData({ targetPerson: v })
    this.doScale()
  },
  onPersonPlus() {
    const v = this.data.targetPerson + 1
    this.setData({ targetPerson: v })
    this.doScale()
  },
  onPersonInput(e) {
    const v = parseInt(e.detail.value) || 1
    this.setData({ targetPerson: Math.max(1, v) })
    this.doScale()
  },

  // 重量变更
  onWeightInput(e) {
    const v = parseFloat(e.detail.value) || 0
    this.setData({ targetWeight: v })
    this.doScale()
  },

  // 锁定/解锁某配料
  onLockToggle(e) {
    const id = e.currentTarget.dataset.id
    let locked = this.data.lockedIds
    if (locked.includes(id)) {
      locked = locked.filter(i => i !== id)
    } else {
      locked = [...locked, id]
    }
    this.setData({ lockedIds: locked })
    this.doScale()
  },

  // 手动微调某配料
  onIngAmountChange(e) {
    const { id } = e.currentTarget.dataset
    const val = parseFloat(e.detail.value) || 0
    const ings = this.data.ingredients.map(i => {
      if (i.id === id) {
        return { ...i, scaled_amount: val, is_locked: 1 }
      }
      return i
    })
    this.setData({ ingredients: ings })
    this.recalcCost()
  },

  // 重置基准
  resetScale() {
    this.loadDetail()
  },

  // 核心换算
  doScale() {
    if (!this.data.recipe) return
    const r = this.data.recipe
    const { scaleMode, targetPerson, targetWeight, lockedIds } = this.data

    let scale = 1.0
    if (scaleMode === 'person') {
      scale = scaleByPerson(r.base_person, targetPerson)
    } else {
      scale = scaleByWeight(r.main_weight || 1, targetWeight)
    }
    const estimatedPeople = Math.round(r.base_person * scale * 10) / 10

    const ings = this.data.ingredients.map(i => {
      const isLocked = lockedIds.includes(i.id)
      return {
        ...i,
        is_locked: isLocked ? 1 : 0,
        scaled_amount: isLocked ? (i.scaled_amount || i.base_amount) : parseFloat((i.base_amount * scale).toFixed(1)),
      }
    })

    this.setData({ ingredients: ings, scale, estimatedPeople })
    this.recalcCost()
  },

  // 重新计算成本
  recalcCost() {
    const ings = this.data.ingredients.map(i => ({
      ...i,
      single_cost: calcCost(i.scaled_amount || i.base_amount, i.unit, i.price_per_unit),
    }))
    const total = parseFloat(ings.reduce((s, i) => s + (i.single_cost || 0), 0).toFixed(2))
    const per = this.data.estimatedPeople > 0 ? parseFloat((total / this.data.estimatedPeople).toFixed(2)) : 0
    this.setData({ ingredients: ings, totalCost: total, perPersonCost: per })
  },

  // 编辑
  onEdit() {
    wx.navigateTo({ url: `/pages/recipe-create/index?id=${this.data.recipeId}` })
  },

  // 删除
  onDelete() {
    wx.showModal({
      title: '确认删除？',
      content: '删除后无法恢复',
      success: (res) => {
        if (res.confirm) {
          api.del(`/recipe/delete/${this.data.recipeId}`).then(() => {
            wx.showToast({ title: '已删除', icon: 'success' })
            setTimeout(() => wx.navigateBack(), 1500)
          })
        }
      }
    })
  },

  onMore() {
    wx.showActionSheet({
      itemList: ['编辑', '删除'],
      success: (res) => {
        if (res.tapIndex === 0) this.onEdit()
        if (res.tapIndex === 1) this.onDelete()
      }
    })
  },
})
