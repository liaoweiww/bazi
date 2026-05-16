// 易经八字 - 多主题管理器
// 通过 JS 直接注入 CSS 变量到 DOM，无需 SCSS 导入

const STORAGE_KEY = 'bazi_app_theme'
const DEFAULT_THEME = 'classic'

// ===== 4 套主题的完整色板 =====
const themeColors = {
  // 经典暗金
  'classic': {
    '--bg-root': '#1a0a00',
    '--bg-secondary': '#2d1810',
    '--bg-card': 'rgba(42,26,16,0.85)',
    '--bg-card-hover': 'rgba(42,26,16,0.7)',
    '--bg-card-solid': '#2a1a10',
    '--bg-input': 'rgba(26,10,0,0.5)',
    '--bg-nav': 'rgba(26,10,0,0.98)',
    '--bg-nav-transparent': 'rgba(26,10,0,0.85)',
    '--text-primary': '#f5f0e8',
    '--text-secondary': '#c9a96e',
    '--text-muted': '#8b7355',
    '--text-placeholder': '#5a4a3a',
    '--text-subtle': '#6a5a4a',
    '--text-body': '#c0b090',
    '--accent': '#c9a96e',
    '--accent-light': '#d4af37',
    '--accent-dark': '#a08040',
    '--accent-04': 'rgba(201,169,110,0.04)',
    '--accent-06': 'rgba(201,169,110,0.06)',
    '--accent-08': 'rgba(201,169,110,0.08)',
    '--accent-10': 'rgba(201,169,110,0.10)',
    '--accent-12': 'rgba(201,169,110,0.12)',
    '--accent-15': 'rgba(201,169,110,0.15)',
    '--accent-20': 'rgba(201,169,110,0.20)',
    '--accent-25': 'rgba(201,169,110,0.25)',
    '--accent-30': 'rgba(201,169,110,0.30)',
    '--accent-40': 'rgba(201,169,110,0.40)',
    '--accent-50': 'rgba(201,169,110,0.50)',
    '--accent-70': 'rgba(201,169,110,0.70)',
    '--vermillion': '#c41e3a',
    '--vermillion-dark': '#8b0000',
    '--vermillion-light': '#e06070',
    '--vermillion-06': 'rgba(196,30,58,0.06)',
    '--vermillion-12': 'rgba(196,30,58,0.12)',
    '--vermillion-15': 'rgba(196,30,58,0.15)',
    '--vermillion-20': 'rgba(196,30,58,0.20)',
    '--vermillion-30': 'rgba(196,30,58,0.30)',
    '--vermillion-40': 'rgba(196,30,58,0.40)',
    '--border-color': '#3d2b1a',
    '--border-light': '#5a3e2a',
    '--border-50': 'rgba(61,43,26,0.5)',
    '--border-40': 'rgba(61,43,26,0.4)',
    '--shadow-card': '0 4px 20px rgba(0,0,0,0.4), 0 1px 3px rgba(201,169,110,0.1)',
    '--shadow-glow': '0 2px 12px rgba(201,169,110,0.3)',
    '--shadow-btn': '0 8rpx 30rpx rgba(139,0,0,0.4)',
    '--shadow-btn-hover': '0 12rpx 36rpx rgba(139,0,0,0.5)',
    '--scrollbar-track': 'rgba(26,10,0,0.5)',
    '--scrollbar-thumb': 'rgba(201,169,110,0.3)',
    '--tap-highlight': 'rgba(201,169,110,0.15)',
    '--focus-outline': 'rgba(201,169,110,0.6)',
    '--wx-wood': '#4a7c59', '--wx-wood-light': '#5a9a6a',
    '--wx-fire': '#c41e3a', '--wx-fire-light': '#e04050',
    '--wx-earth': '#c9a96e', '--wx-earth-light': '#d4af37',
    '--wx-metal': '#f5f0e8', '--wx-metal-light': '#ffffff',
    '--wx-water': '#2c3e6b', '--wx-water-light': '#5a7ec0',
    '--color-positive': '#5a9a6a',
    '--color-negative': '#e06070',
    '--color-neutral': '#8b7355',
    '--bg-root-80': 'rgba(26,10,0,0.8)',
    '--bg-root-40': 'rgba(26,10,0,0.4)',
  },
  // 墨韵
  'ink-wash': {
    '--bg-root': '#0a0a0c', '--bg-secondary': '#121215',
    '--bg-card': 'rgba(22,22,26,0.88)', '--bg-card-hover': 'rgba(22,22,26,0.75)',
    '--bg-card-solid': '#16161a', '--bg-input': 'rgba(16,16,20,0.6)',
    '--bg-nav': 'rgba(10,10,12,0.98)', '--bg-nav-transparent': 'rgba(10,10,12,0.85)',
    '--text-primary': '#e0dcd6', '--text-secondary': '#b0a89e',
    '--text-muted': '#70685e', '--text-placeholder': '#484038', '--text-subtle': '#585048',
    '--text-body': '#a09890',
    '--accent': '#b0a89e', '--accent-light': '#c8c0b6', '--accent-dark': '#90887e',
    '--accent-04': 'rgba(176,168,158,0.04)', '--accent-06': 'rgba(176,168,158,0.06)',
    '--accent-08': 'rgba(176,168,158,0.08)', '--accent-10': 'rgba(176,168,158,0.10)',
    '--accent-12': 'rgba(176,168,158,0.12)', '--accent-15': 'rgba(176,168,158,0.15)',
    '--accent-20': 'rgba(176,168,158,0.20)', '--accent-25': 'rgba(176,168,158,0.25)',
    '--accent-30': 'rgba(176,168,158,0.30)', '--accent-40': 'rgba(176,168,158,0.40)',
    '--accent-50': 'rgba(176,168,158,0.50)', '--accent-70': 'rgba(176,168,158,0.70)',
    '--vermillion': '#a07070', '--vermillion-dark': '#604040', '--vermillion-light': '#c09090',
    '--vermillion-06': 'rgba(160,112,112,0.06)', '--vermillion-12': 'rgba(160,112,112,0.12)',
    '--vermillion-15': 'rgba(160,112,112,0.15)', '--vermillion-20': 'rgba(160,112,112,0.20)',
    '--vermillion-30': 'rgba(160,112,112,0.30)', '--vermillion-40': 'rgba(160,112,112,0.40)',
    '--border-color': '#26262a', '--border-light': '#36363a',
    '--border-50': 'rgba(38,38,42,0.5)', '--border-40': 'rgba(38,38,42,0.4)',
    '--shadow-card': '0 4px 20px rgba(0,0,0,0.5), 0 1px 3px rgba(176,168,158,0.06)',
    '--shadow-glow': '0 2px 12px rgba(176,168,158,0.2)',
    '--shadow-btn': '0 8rpx 30rpx rgba(96,64,64,0.4)',
    '--shadow-btn-hover': '0 12rpx 36rpx rgba(96,64,64,0.5)',
    '--scrollbar-track': 'rgba(16,16,20,0.5)', '--scrollbar-thumb': 'rgba(176,168,158,0.2)',
    '--tap-highlight': 'rgba(176,168,158,0.1)',
    '--focus-outline': 'rgba(176,168,158,0.5)',
    '--wx-wood': '#3a6a4a', '--wx-wood-light': '#4a8a5a',
    '--wx-fire': '#a05050', '--wx-fire-light': '#c07060',
    '--wx-earth': '#a09880', '--wx-earth-light': '#b8b098',
    '--wx-metal': '#d8d4ce', '--wx-metal-light': '#e8e4de',
    '--wx-water': '#2a3a5a', '--wx-water-light': '#4a6aaa',
    '--color-positive': '#4a8a5a', '--color-negative': '#c09090', '--color-neutral': '#70685e',
    '--bg-root-80': 'rgba(10,10,12,0.8)', '--bg-root-40': 'rgba(10,10,12,0.4)',
  },
  // 宫廷
  'imperial': {
    '--bg-root': '#0d0005', '--bg-secondary': '#1a0812',
    '--bg-card': 'rgba(28,10,18,0.88)', '--bg-card-hover': 'rgba(28,10,18,0.75)',
    '--bg-card-solid': '#1c0a12', '--bg-input': 'rgba(13,0,5,0.55)',
    '--bg-nav': 'rgba(13,0,5,0.98)', '--bg-nav-transparent': 'rgba(13,0,5,0.85)',
    '--text-primary': '#fff5e8', '--text-secondary': '#e8c840',
    '--text-muted': '#9a7a6a', '--text-placeholder': '#5a3035', '--text-subtle': '#6a4045',
    '--text-body': '#c0a898',
    '--accent': '#e8c840', '--accent-light': '#f0d860', '--accent-dark': '#c0a020',
    '--accent-04': 'rgba(232,200,64,0.04)', '--accent-06': 'rgba(232,200,64,0.06)',
    '--accent-08': 'rgba(232,200,64,0.08)', '--accent-10': 'rgba(232,200,64,0.10)',
    '--accent-12': 'rgba(232,200,64,0.12)', '--accent-15': 'rgba(232,200,64,0.15)',
    '--accent-20': 'rgba(232,200,64,0.20)', '--accent-25': 'rgba(232,200,64,0.25)',
    '--accent-30': 'rgba(232,200,64,0.30)', '--accent-40': 'rgba(232,200,64,0.40)',
    '--accent-50': 'rgba(232,200,64,0.50)', '--accent-70': 'rgba(232,200,64,0.70)',
    '--vermillion': '#d42030', '--vermillion-dark': '#8b1018', '--vermillion-light': '#f05050',
    '--vermillion-06': 'rgba(212,32,48,0.06)', '--vermillion-12': 'rgba(212,32,48,0.12)',
    '--vermillion-15': 'rgba(212,32,48,0.15)', '--vermillion-20': 'rgba(212,32,48,0.20)',
    '--vermillion-30': 'rgba(212,32,48,0.30)', '--vermillion-40': 'rgba(212,32,48,0.40)',
    '--border-color': '#3d1520', '--border-light': '#5a2030',
    '--border-50': 'rgba(61,21,32,0.5)', '--border-40': 'rgba(61,21,32,0.4)',
    '--shadow-card': '0 4px 20px rgba(0,0,0,0.45), 0 1px 3px rgba(232,200,64,0.1)',
    '--shadow-glow': '0 2px 12px rgba(232,200,64,0.35)',
    '--shadow-btn': '0 8rpx 30rpx rgba(139,16,24,0.45)',
    '--shadow-btn-hover': '0 12rpx 36rpx rgba(139,16,24,0.55)',
    '--scrollbar-track': 'rgba(13,0,5,0.5)', '--scrollbar-thumb': 'rgba(232,200,64,0.25)',
    '--tap-highlight': 'rgba(232,200,64,0.15)',
    '--focus-outline': 'rgba(232,200,64,0.6)',
    '--wx-wood': '#4a7c59', '--wx-wood-light': '#5a9a6a',
    '--wx-fire': '#d42030', '--wx-fire-light': '#f05050',
    '--wx-earth': '#e8c840', '--wx-earth-light': '#f0d860',
    '--wx-metal': '#fff8ee', '--wx-metal-light': '#ffffff',
    '--wx-water': '#2c3e6b', '--wx-water-light': '#5a7ec0',
    '--color-positive': '#5a9a6a', '--color-negative': '#f05050', '--color-neutral': '#9a7a6a',
    '--bg-root-80': 'rgba(13,0,5,0.8)', '--bg-root-40': 'rgba(13,0,5,0.4)',
  },
  // 青瓷
  'celadon': {
    '--bg-root': '#0a1512', '--bg-secondary': '#142520',
    '--bg-card': 'rgba(16,32,28,0.88)', '--bg-card-hover': 'rgba(16,32,28,0.75)',
    '--bg-card-solid': '#10201c', '--bg-input': 'rgba(10,21,18,0.55)',
    '--bg-nav': 'rgba(10,21,18,0.98)', '--bg-nav-transparent': 'rgba(10,21,18,0.85)',
    '--text-primary': '#e8f0ec', '--text-secondary': '#8cc4a8',
    '--text-muted': '#5a7a6a', '--text-placeholder': '#3a5045', '--text-subtle': '#4a6055',
    '--text-body': '#a0c0b0',
    '--accent': '#8cc4a8', '--accent-light': '#a0d8b8', '--accent-dark': '#6a9a80',
    '--accent-04': 'rgba(140,196,168,0.04)', '--accent-06': 'rgba(140,196,168,0.06)',
    '--accent-08': 'rgba(140,196,168,0.08)', '--accent-10': 'rgba(140,196,168,0.10)',
    '--accent-12': 'rgba(140,196,168,0.12)', '--accent-15': 'rgba(140,196,168,0.15)',
    '--accent-20': 'rgba(140,196,168,0.20)', '--accent-25': 'rgba(140,196,168,0.25)',
    '--accent-30': 'rgba(140,196,168,0.30)', '--accent-40': 'rgba(140,196,168,0.40)',
    '--accent-50': 'rgba(140,196,168,0.50)', '--accent-70': 'rgba(140,196,168,0.70)',
    '--vermillion': '#c08060', '--vermillion-dark': '#8a5040', '--vermillion-light': '#e0a080',
    '--vermillion-06': 'rgba(192,128,96,0.06)', '--vermillion-12': 'rgba(192,128,96,0.12)',
    '--vermillion-15': 'rgba(192,128,96,0.15)', '--vermillion-20': 'rgba(192,128,96,0.20)',
    '--vermillion-30': 'rgba(192,128,96,0.30)', '--vermillion-40': 'rgba(192,128,96,0.40)',
    '--border-color': '#1a3028', '--border-light': '#2a4038',
    '--border-50': 'rgba(26,48,40,0.5)', '--border-40': 'rgba(26,48,40,0.4)',
    '--shadow-card': '0 4px 20px rgba(0,0,0,0.4), 0 1px 3px rgba(140,196,168,0.08)',
    '--shadow-glow': '0 2px 12px rgba(140,196,168,0.25)',
    '--shadow-btn': '0 8rpx 30rpx rgba(138,80,64,0.4)',
    '--shadow-btn-hover': '0 12rpx 36rpx rgba(138,80,64,0.5)',
    '--scrollbar-track': 'rgba(10,21,18,0.5)', '--scrollbar-thumb': 'rgba(140,196,168,0.2)',
    '--tap-highlight': 'rgba(140,196,168,0.12)',
    '--focus-outline': 'rgba(140,196,168,0.5)',
    '--wx-wood': '#4a7c59', '--wx-wood-light': '#5a9a6a',
    '--wx-fire': '#c08060', '--wx-fire-light': '#e0a080',
    '--wx-earth': '#a0b898', '--wx-earth-light': '#b8d0b0',
    '--wx-metal': '#e8f0ec', '--wx-metal-light': '#f0f8f4',
    '--wx-water': '#305060', '--wx-water-light': '#4a7080',
    '--color-positive': '#5a9a6a', '--color-negative': '#e0a080', '--color-neutral': '#5a7a6a',
    '--bg-root-80': 'rgba(10,21,18,0.8)', '--bg-root-40': 'rgba(10,21,18,0.4)',
  }
}

// 主题列表（供 UI 使用）
export const themes = [
  { id: 'classic',  name: '经典暗金', subtitle: 'Classic Gold',   desc: '温暖深棕底色，鎏金点缀，传统中式美学' },
  { id: 'ink-wash', name: '墨韵',     subtitle: 'Ink Wash',       desc: '纯黑水墨基调，银白素雅，极简禅意画风' },
  { id: 'imperial', name: '宫廷',     subtitle: 'Imperial',       desc: '深红宫墙底色，明亮鎏金，皇家奢华气质' },
  { id: 'celadon',  name: '青瓷',     subtitle: 'Celadon',        desc: '青绿釉色基底，瓷质温润，江南雅致韵味' }
]

// 主题预览色块
export const themePreview = {
  'classic':   { bg: '#1a0a00', accent: '#d4af37', text: '#f5f0e8', card: '#2a1a10' },
  'ink-wash':  { bg: '#0a0a0c', accent: '#c8c0b6', text: '#e0dcd6', card: '#16161a' },
  'imperial':  { bg: '#0d0005', accent: '#e8c840', text: '#fff5e8', card: '#1c0a12' },
  'celadon':   { bg: '#0a1512', accent: '#a0d8b8', text: '#e8f0ec', card: '#10201c' }
}

// TabBar 样式
const tabBarStyles = {
  'classic':   { color: '#8b7355', selectedColor: '#d4af37', backgroundColor: '#2a1a10' },
  'ink-wash':  { color: '#70685e', selectedColor: '#b0a89e', backgroundColor: '#141418' },
  'imperial':  { color: '#9a7a6a', selectedColor: '#e8c840', backgroundColor: '#1c0a12' },
  'celadon':   { color: '#5a7a6a', selectedColor: '#8cc4a8', backgroundColor: '#10201c' }
}

// 注入 CSS 变量到 DOM
function injectCSSVariables(themeId) {
  const colors = themeColors[themeId] || themeColors[DEFAULT_THEME]
  try {
    if (typeof document !== 'undefined' && document.documentElement) {
      const root = document.documentElement
      root.setAttribute('data-theme', themeId)
      Object.entries(colors).forEach(([key, value]) => {
        root.style.setProperty(key, value)
      })
      return true
    }
  } catch (e) {
    console.warn('injectCSSVariables failed:', e)
  }
  return false
}

// 获取当前主题
export function getCurrentTheme() {
  try {
    const stored = uni.getStorageSync(STORAGE_KEY)
    if (stored && themeColors[stored]) return stored
  } catch (e) { /* ignore */ }
  return DEFAULT_THEME
}

// 应用主题
export function applyTheme(themeId) {
  return injectCSSVariables(themeId)
}

// 切换主题
export function setTheme(themeId) {
  if (!themeColors[themeId]) return false
  uni.setStorageSync(STORAGE_KEY, themeId)
  const ok = injectCSSVariables(themeId)
  // 更新 TabBar
  const style = tabBarStyles[themeId]
  if (style) {
    try { uni.setTabBarStyle(style) } catch (e) { /* ignore */ }
  }
  return ok
}

// 初始化
export function initTheme() {
  const themeId = getCurrentTheme()
  injectCSSVariables(themeId)
  const style = tabBarStyles[themeId]
  if (style) {
    setTimeout(() => {
      try { uni.setTabBarStyle(style) } catch (e) { /* ignore */ }
    }, 300)
  }
}

export { STORAGE_KEY, DEFAULT_THEME, themeColors, tabBarStyles }
