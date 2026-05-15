/**
 * 易经八字 - API请求封装
 * 后端API接口统一管理
 */

// 基础配置
const BASE_URL = 'https://api.bazi.example.com/v1'

// 请求超时时间
const TIMEOUT = 15000

/**
 * 通用请求方法
 */
function request(options) {
  return new Promise((resolve, reject) => {
    const {
      url,
      method = 'GET',
      data = {},
      header = {},
      showLoading = false
    } = options

    if (showLoading) {
      uni.showLoading({
        title: '加载中...',
        mask: true
      })
    }

    uni.request({
      url: BASE_URL + url,
      method,
      data,
      timeout: TIMEOUT,
      header: {
        'Content-Type': 'application/json',
        ...header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          uni.showToast({
            title: res.data?.message || '请求失败',
            icon: 'none'
          })
          reject(res)
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络异常，请稍后重试',
          icon: 'none'
        })
        reject(err)
      },
      complete: () => {
        if (showLoading) {
          uni.hideLoading()
        }
      }
    })
  })
}

// ===== 排盘相关 API =====

/**
 * 排盘计算
 * @param {Object} params
 * @param {string} params.name - 姓名
 * @param {number} params.gender - 性别 0:女 1:男
 * @param {string} params.birth_date - 公历出生日期 YYYY-MM-DD
 * @param {string} params.birth_time - 出生时间 HH:mm
 * @param {Object} params.location - 出生地 {province, city, district, lng, lat}
 */
export function calculateBazi(params) {
  return request({
    url: '/bazi/calculate',
    method: 'POST',
    data: params,
    showLoading: true
  })
}

/**
 * 获取排盘结果（加密ID查询）
 */
export function getBaziResult(id) {
  return request({
    url: `/bazi/result/${id}`,
    method: 'GET'
  })
}

/**
 * 获取大运详情
 */
export function getDayunDetail(baziId, dayunIndex) {
  return request({
    url: `/bazi/${baziId}/dayun/${dayunIndex}`,
    method: 'GET'
  })
}

/**
 * 获取流年详情
 */
export function getLiunianDetail(baziId, year) {
  return request({
    url: `/bazi/${baziId}/liunian/${year}`,
    method: 'GET'
  })
}

/**
 * 获取神煞列表
 */
export function getShensha(query = {}) {
  return request({
    url: '/reference/shensha',
    method: 'GET',
    data: query
  })
}

/**
 * 获取十神详解
 */
export function getShishenDetail(name) {
  return request({
    url: `/reference/shishen/${name}`,
    method: 'GET'
  })
}

// ===== Mock 数据（开发阶段使用） =====

/**
 * Mock 排盘结果
 */
export function mockBaziResult() {
  return {
    id: 'mock_001',
    name: '张三',
    gender: '男',
    birth_date: '1990-05-15',
    birth_time: '08:30',
    location: '北京市朝阳区',
    bazi: {
      year: { gan: '庚', zhi: '午', canggan: ['丁', '己'], nayin: '路旁土', shishen: '偏印' },
      month: { gan: '辛', zhi: '巳', canggan: ['丙', '戊', '庚'], nayin: '白蜡金', shishen: '劫财' },
      day: { gan: '壬', zhi: '子', canggan: ['癸'], nayin: '桑柘木', shishen: '日主' },
      hour: { gan: '甲', zhi: '辰', canggan: ['戊', '乙', '癸'], nayin: '佛灯火', shishen: '食神' }
    },
    wuxing_count: {
      '金': 2,
      '木': 2,
      '水': 3,
      '火': 2,
      '土': 1
    },
    rizhu_strong: '身强',
    pattern: '伤官生财格',
    pattern_desc: '日主壬水得月令之气，食神生财为用，富贵双全之象。为人聪慧，善于表达，有艺术天赋，财运亨通。',
    yongshen: {
      god: ['木', '火'],
      ji: ['土', '金'],
      tiaohou: '冬季出生，喜火调候暖局，木生火助旺。忌金水过旺，寒气侵体。'
    },
    dayun_start_age: 6,
    dayun_list: [
      { age: 6, gan: '壬', zhi: '午', nayin: '杨柳木', years: '1996-2005' },
      { age: 16, gan: '癸', zhi: '未', nayin: '杨柳木', years: '2006-2015' },
      { age: 26, gan: '甲', zhi: '申', nayin: '井泉水', years: '2016-2025' },
      { age: 36, gan: '乙', zhi: '酉', nayin: '井泉水', years: '2026-2035' },
      { age: 46, gan: '丙', zhi: '戌', nayin: '屋上土', years: '2036-2045' },
      { age: 56, gan: '丁', zhi: '亥', nayin: '屋上土', years: '2046-2055' },
      { age: 66, gan: '戊', zhi: '子', nayin: '霹雳火', years: '2056-2065' }
    ],
    current_liunian: {
      year: 2026,
      gan: '丙',
      zhi: '午',
      nayin: '天河水',
      rating: '吉',
      desc: '流年丙午，火旺暖局，用神得力。事业有贵人相助，财运上升，人际关系和谐。注意夏季火过旺，宜冷静行事。'
    }
  }
}

export default {
  calculateBazi,
  getBaziResult,
  getDayunDetail,
  getLiunianDetail,
  getShensha,
  getShishenDetail,
  mockBaziResult
}
