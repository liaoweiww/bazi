/**
 * API请求封装
 * 后端API接口统一管理（八字 + 星座）
 */

// 基础配置
const BASE_URL = 'http://localhost:5001'

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

// ===== 八字排盘 API =====

export function calculateBazi(params) {
  return request({
    url: '/api/paipan',
    method: 'POST',
    data: params,
    showLoading: true
  })
}

export function getBaziInterpret(paipanResult) {
  return request({
    url: '/api/interpret',
    method: 'POST',
    data: { paipan_result: paipanResult },
    showLoading: true
  })
}

// ===== 星座星盘 API =====

export function calculateZodiacChart(params) {
  return request({
    url: '/api/astrology/chart',
    method: 'POST',
    data: params,
    showLoading: true
  })
}

export function getZodiacInterpret(chartResult) {
  return request({
    url: '/api/astrology/interpret',
    method: 'POST',
    data: { chart_result: chartResult },
    showLoading: true
  })
}

export function getDailyHoroscope(sign) {
  return request({
    url: '/api/astrology/daily',
    method: 'POST',
    data: { sign: sign }
  })
}

export function getZodiacReferenceSigns(name) {
  return request({
    url: '/api/astrology/reference/signs',
    method: 'GET',
    data: name ? { name } : {}
  })
}

// ===== Mock 数据（开发阶段使用） =====

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
    wuxing_count: { '金': 2, '木': 2, '水': 3, '火': 2, '土': 1 },
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
      year: 2026, gan: '丙', zhi: '午', nayin: '天河水', rating: '吉',
      desc: '流年丙午，火旺暖局，用神得力。事业有贵人相助，财运上升，人际关系和谐。'
    }
  }
}

export function mockZodiacChart() {
  return {
    name: '李四',
    gender: '女',
    birth_datetime: '1995-08-20 14:30',
    birth_location: { longitude: 121.5, latitude: 31.2, timezone: 8.0 },
    planets: [
      { name_cn: '太阳', sign: '狮子座', sign_symbol: '♌', sign_element: '火', sign_modality: '固定',
        degree_in_sign: 26.79, lon: 146.79, house: 1, house_name: '命宫', is_retrograde: false },
      { name_cn: '月亮', sign: '双子座', sign_symbol: '♊', sign_element: '风', sign_modality: '变动',
        degree_in_sign: 19.08, lon: 79.08, house: 2, house_name: '财帛宫', is_retrograde: false },
      { name_cn: '水星', sign: '处女座', sign_symbol: '♍', sign_element: '土', sign_modality: '变动',
        degree_in_sign: 12.5, lon: 162.5, house: 3, house_name: '兄弟宫', is_retrograde: false },
      { name_cn: '金星', sign: '天秤座', sign_symbol: '♎', sign_element: '风', sign_modality: '基本',
        degree_in_sign: 8.3, lon: 188.3, house: 4, house_name: '田宅宫', is_retrograde: false },
      { name_cn: '火星', sign: '天蝎座', sign_symbol: '♏', sign_element: '水', sign_modality: '固定',
        degree_in_sign: 15.7, lon: 225.7, house: 5, house_name: '子女宫', is_retrograde: false },
      { name_cn: '木星', sign: '射手座', sign_symbol: '♐', sign_element: '火', sign_modality: '变动',
        degree_in_sign: 5.2, lon: 245.2, house: 6, house_name: '奴仆宫', is_retrograde: false },
      { name_cn: '土星', sign: '双鱼座', sign_symbol: '♓', sign_element: '水', sign_modality: '变动',
        degree_in_sign: 22.1, lon: 352.1, house: 7, house_name: '夫妻宫', is_retrograde: true },
      { name_cn: '天王星', sign: '摩羯座', sign_symbol: '♑', sign_element: '土', sign_modality: '基本',
        degree_in_sign: 28.5, lon: 298.5, house: 8, house_name: '疾厄宫', is_retrograde: false },
      { name_cn: '海王星', sign: '摩羯座', sign_symbol: '♑', sign_element: '土', sign_modality: '基本',
        degree_in_sign: 23.8, lon: 293.8, house: 8, house_name: '疾厄宫', is_retrograde: false },
      { name_cn: '冥王星', sign: '天蝎座', sign_symbol: '♏', sign_element: '水', sign_modality: '固定',
        degree_in_sign: 0.5, lon: 210.5, house: 5, house_name: '子女宫', is_retrograde: false }
    ],
    houses: [
      { number: 1, name_cn: '命宫', cusp_degree: 67.8, sign: '双子座', sign_symbol: '♊',
        keywords: '自我、外貌、第一印象、人格面具' },
      { number: 2, name_cn: '财帛宫', cusp_degree: 62.5, sign: '双子座', sign_symbol: '♊',
        keywords: '财富、价值观、物质资源、自我价值' },
      { number: 3, name_cn: '兄弟宫', cusp_degree: 52.5, sign: '金牛座', sign_symbol: '♉',
        keywords: '沟通、学习、短途旅行、兄弟姐妹' },
      { number: 4, name_cn: '田宅宫', cusp_degree: 107.8, sign: '巨蟹座', sign_symbol: '♋',
        keywords: '家庭、根源、房产、安全感' },
      { number: 5, name_cn: '子女宫', cusp_degree: 150.5, sign: '处女座', sign_symbol: '♍',
        keywords: '创造力、恋爱、子女、娱乐' },
      { number: 6, name_cn: '奴仆宫', cusp_degree: 210.5, sign: '天蝎座', sign_symbol: '♏',
        keywords: '工作、健康、日常事务、服务' },
      { number: 7, name_cn: '夫妻宫', cusp_degree: 247.8, sign: '射手座', sign_symbol: '♐',
        keywords: '伴侣、合作、一对一关系、公开敌人' },
      { number: 8, name_cn: '疾厄宫', cusp_degree: 232.5, sign: '天蝎座', sign_symbol: '♏',
        keywords: '深层转变、他人资源、性、生死' },
      { number: 9, name_cn: '迁移宫', cusp_degree: 287.8, sign: '摩羯座', sign_symbol: '♑',
        keywords: '高等教育、旅行、哲学、信仰' },
      { number: 10, name_cn: '官禄宫', cusp_degree: 330.5, sign: '水瓶座', sign_symbol: '♒',
        keywords: '事业、社会地位、名声、人生目标' },
      { number: 11, name_cn: '福德宫', cusp_degree: 30.5, sign: '金牛座', sign_symbol: '♉',
        keywords: '朋友、社群、理想、希望' },
      { number: 12, name_cn: '玄秘宫', cusp_degree: 58.5, sign: '金牛座', sign_symbol: '♉',
        keywords: '潜意识、灵性、隐秘、牺牲' }
    ],
    angles: {
      ascendant: 67.8, ascendant_sign: '双子座', ascendant_symbol: '♊',
      midheaven: 330.5, midheaven_sign: '水瓶座', midheaven_symbol: '♒',
      descendant: 247.8, descendant_sign: '射手座',
      imum_coeli: 150.5, imum_coeli_sign: '处女座'
    },
    aspects: [
      { planet1: '太阳', planet2: '月亮', aspect_name_cn: '六分相', aspect_symbol: '⚹',
        angle_diff: 2.3, nature: '和谐', keyword: '机会' },
      { planet1: '太阳', planet2: '火星', aspect_name_cn: '四分相', aspect_symbol: '□',
        angle_diff: 1.1, nature: '紧张', keyword: '挑战' },
      { planet1: '月亮', planet2: '金星', aspect_name_cn: '三分相', aspect_symbol: '△',
        angle_diff: 3.2, nature: '和谐', keyword: '天赋' },
      { planet1: '金星', planet2: '火星', aspect_name_cn: '四分相', aspect_symbol: '□',
        angle_diff: 4.7, nature: '紧张', keyword: '挑战' },
      { planet1: '水星', planet2: '木星', aspect_name_cn: '对分相', aspect_symbol: '☍',
        angle_diff: 2.5, nature: '紧张', keyword: '对立' },
      { planet1: '太阳', planet2: '木星', aspect_name_cn: '三分相', aspect_symbol: '△',
        angle_diff: 1.8, nature: '和谐', keyword: '天赋' },
      { planet1: '火星', planet2: '冥王星', aspect_name_cn: '合相', aspect_symbol: '☌',
        angle_diff: 4.2, nature: '中性', keyword: '融合' },
      { planet1: '土星', planet2: '海王星', aspect_name_cn: '六分相', aspect_symbol: '⚹',
        angle_diff: 5.1, nature: '和谐', keyword: '机会' }
    ],
    patterns: [],
    analysis: {
      elements: {
        '火': { count: 2, percentage: 20.0, planets: ['太阳', '木星'],
                name_cn: '火象', traits: '热情、行动力、自信、创造力',
                assessment: '火象元素适中。' },
        '土': { count: 3, percentage: 30.0, planets: ['水星', '天王星', '海王星'],
                name_cn: '土象', traits: '务实、稳定、耐心、可靠',
                assessment: '土象元素较强，具备一定的务实、稳定、耐心、可靠。' },
        '风': { count: 2, percentage: 20.0, planets: ['月亮', '金星'],
                name_cn: '风象', traits: '理性、沟通、社交、灵活',
                assessment: '风象元素适中。' },
        '水': { count: 3, percentage: 30.0, planets: ['火星', '土星', '冥王星'],
                name_cn: '水象', traits: '感性、直觉、情感、同理心',
                assessment: '水象元素较强，具备一定的感性、直觉、情感、同理心。' }
      },
      modalities: {
        '基本': { count: 3, percentage: 30.0, name_cn: '基本星座', traits: '开创、主动、领导力' },
        '固定': { count: 4, percentage: 40.0, name_cn: '固定星座', traits: '坚持、稳定、执着' },
        '变动': { count: 3, percentage: 30.0, name_cn: '变动星座', traits: '适应、灵活、多变' }
      },
      dominant_element: '土',
      dominant_modality: '固定',
      hemispheres: {
        above_horizon: { count: 3, meaning: '行星集中在上半球，人生重心偏向外界、社会成就、公共生活。' },
        below_horizon: { count: 7, meaning: '行星集中在下半球，人生重心偏向内在、家庭、个人成长。' },
        east: { count: 6, meaning: '行星集中在东方(自我主导)，人生偏重主动开拓、自我表达。' },
        west: { count: 4, meaning: '行星集中在西方(他人导向)，人生偏重合作关系、回应外界。' }
      },
      summary: '你的星盘元素以土象为主导，模式以固定星座为主。缺乏风元素，可以通过后天学习来弥补这部分特质。'
    }
  }
}

export default {
  calculateBazi,
  getBaziInterpret,
  calculateZodiacChart,
  getZodiacInterpret,
  getDailyHoroscope,
  getZodiacReferenceSigns,
  mockBaziResult,
  mockZodiacChart
}
