const api = require('../../utils/request')

Page({
  data: {
    isEdit: false,
    editId: null,
    name: '',
    category: '家常菜',
    categories: ['家常菜', '快手菜', '汤品', '荤菜', '素菜'],
    cookTime: 30,
    difficulty: 3,
    basePerson: 2,
    mainMaterial: '',
    mainWeight: 0,
    mainUnit: 'g',
    units: ['g', '斤', '个', '只', '条'],
    ingredients: [],
    steps: [],
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ isEdit: true, editId: options.id })
      wx.setNavigationBarTitle({ title: '编辑菜谱' })
      this.loadRecipe(options.id)
    } else {
      wx.setNavigationBarTitle({ title: '新建菜谱' })
      this.addIngredient()
      this.addStep()
    }
  },

  loadRecipe(id) {
    api.get(`/recipe/detail/${id}`).then(res => {
      if (res.code === 0) {
        const d = res.data
        this.setData({
          name: d.name, category: d.category, cookTime: d.cook_time,
          difficulty: d.difficulty, basePerson: d.base_person,
          mainMaterial: d.main_material, mainWeight: d.main_weight,
          mainUnit: d.main_unit || 'g',
          ingredients: d.ingredients.map(i => ({
            material_name: i.material_name, base_amount: i.base_amount,
            unit: i.unit, price_per_unit: i.price_per_unit
          })),
          steps: d.steps.map(s => ({ content: s.content }))
        })
      }
    })
  },

  addIngredient() {
    const ings = this.data.ingredients
    ings.push({ material_name: '', base_amount: 0, unit: 'g', price_per_unit: 0 })
    this.setData({ ingredients: ings })
  },

  removeIngredient(e) {
    const idx = e.currentTarget.dataset.idx
    const ings = this.data.ingredients
    ings.splice(idx, 1)
    this.setData({ ingredients: ings })
  },

  onIngChange(e) {
    const { idx, field } = e.currentTarget.dataset
    const val = e.detail.value
    const ings = this.data.ingredients
    ings[idx][field] = (field === 'base_amount' || field === 'price_per_unit') ? parseFloat(val) || 0 : val
    this.setData({ ingredients: ings })
  },

  addStep() {
    const steps = this.data.steps
    steps.push({ content: '' })
    this.setData({ steps })
  },

  removeStep(e) {
    const idx = e.currentTarget.dataset.idx
    const steps = this.data.steps
    steps.splice(idx, 1)
    this.setData({ steps })
  },

  onStepChange(e) {
    const idx = e.currentTarget.dataset.idx
    const steps = this.data.steps
    steps[idx].content = e.detail.value
    this.setData({ steps })
  },

  // 通用字段输入
  onFieldInput(e) {
    const { field } = e.currentTarget.dataset
    this.setData({ [field]: e.detail.value })
  },

  // 通用字段选择（分类/难度/单位等）
  onFieldTap(e) {
    const { field, val } = e.currentTarget.dataset
    this.setData({ [field]: val })
  },

  save() {
    const { name, category, cookTime, difficulty, basePerson,
            mainMaterial, mainWeight, mainUnit, ingredients, steps } = this.data

    if (!name.trim()) {
      wx.showToast({ title: '请输入菜名', icon: 'none' })
      return
    }

    const data = {
      name: name.trim(),
      category,
      cook_time: parseInt(cookTime),
      difficulty: parseInt(difficulty),
      base_person: parseInt(basePerson),
      main_material: mainMaterial,
      main_weight: parseFloat(mainWeight) || 0,
      main_unit: mainUnit,
      ingredients: ingredients.filter(i => i.material_name.trim()),
      steps: steps.filter(s => s.content.trim()).map(s => ({ content: s.content.trim() })),
    }

    if (this.data.isEdit) {
      api.put(`/recipe/update/${this.data.editId}`, data).then(res => {
        if (res.code === 0) {
          wx.showToast({ title: '更新成功', icon: 'success' })
          wx.navigateBack()
        }
      })
    } else {
      api.post('/recipe/create', data).then(res => {
        if (res.code === 0) {
          wx.showToast({ title: '创建成功', icon: 'success' })
          wx.navigateBack()
        }
      })
    }
  },
})
