const app = getApp()
Page({
  data: {
    name:'', gender:'男', calType:'solar', leap:false,
    sy:'1990',sm:'6',sd:'15', ly:'1990',lm:'5',ld:'21', fh:'8',fm:'0'
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
        wx.request({url:api+'/paipan',method:'POST',header:{'Content-Type':'application/json'},data:body,timeout:30000,success:resolve,fail:reject})
      })
      wx.hideLoading()
      if(resp.data.success){
        app.globalData.paipanResult = resp.data.data
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
