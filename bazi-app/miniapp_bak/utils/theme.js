// 易经八字 - 小程序多主题管理器
// 4套完全不同的视觉主题：颜色 + 排版 + 间距 + 造型 + 装饰 + 图标
// 通过 CSS 变量注入 + WXML 条件渲染实现

var STORAGE_KEY = 'bazi_app_theme'
var DEFAULT_THEME = 'classic'

// ===== 色板（66 变量/主题）=====
var themeColors = {
  classic: {
    '--bg-root': '#0d0a05', '--bg-secondary': '#1a1008',
    '--bg-card': 'rgba(19,12,6,0.6)', '--bg-card-hover': 'rgba(42,26,16,0.7)',
    '--bg-card-solid': '#2a1a10', '--bg-input': 'rgba(0,0,0,0.15)',
    '--bg-nav': 'rgba(26,10,0,0.98)',
    '--text-primary': '#f5f0e8', '--text-secondary': '#c9a96e',
    '--text-muted': '#8b7355', '--text-placeholder': '#5a4a3a', '--text-subtle': '#6a5a4a',
    '--text-body': '#c0b090',
    '--accent': '#c9a96e', '--accent-light': '#d4af37', '--accent-dark': '#a08040',
    '--accent-rgb': '201,169,110', '--accent-light-rgb': '212,175,55',
    '--accent-04': 'rgba(201,169,110,0.04)', '--accent-06': 'rgba(201,169,110,0.06)',
    '--accent-08': 'rgba(201,169,110,0.08)', '--accent-10': 'rgba(201,169,110,0.10)',
    '--accent-12': 'rgba(201,169,110,0.12)', '--accent-15': 'rgba(201,169,110,0.15)',
    '--accent-20': 'rgba(201,169,110,0.20)', '--accent-25': 'rgba(201,169,110,0.25)',
    '--accent-30': 'rgba(201,169,110,0.30)', '--accent-40': 'rgba(201,169,110,0.40)',
    '--accent-50': 'rgba(201,169,110,0.50)',
    '--vermillion': '#b22222', '--vermillion-dark': '#8b0000', '--vermillion-light': '#e06070',
    '--vermillion-rgb': '178,34,34',
    '--vermillion-06': 'rgba(178,34,34,0.06)', '--vermillion-08': 'rgba(178,34,34,0.08)',
    '--vermillion-10': 'rgba(178,34,34,0.10)', '--vermillion-12': 'rgba(178,34,34,0.12)',
    '--vermillion-15': 'rgba(178,34,34,0.15)', '--vermillion-20': 'rgba(178,34,34,0.20)',
    '--vermillion-30': 'rgba(178,34,34,0.30)', '--vermillion-40': 'rgba(178,34,34,0.40)',
    '--border-color': '#2a1f14', '--border-light': '#3d2b1a',
    '--border-40': 'rgba(51,36,24,0.4)', '--border-50': 'rgba(51,36,24,0.5)',
    '--shadow-card': '0 4px 20px rgba(0,0,0,0.4), 0 1px 3px rgba(201,169,110,0.1)',
    '--shadow-glow': '0 2px 12px rgba(201,169,110,0.3)',
    '--shadow-btn': '0 6px 24px rgba(178,34,34,0.2)',
    '--tap-highlight': 'rgba(201,169,110,0.12)',
    '--wx-wood': '#4a7c59', '--wx-wood-light': '#5a9a6a',
    '--wx-fire': '#c41e3a', '--wx-fire-light': '#e04050',
    '--wx-earth': '#c9a96e', '--wx-earth-light': '#d4af37',
    '--wx-metal': '#ddd5c5', '--wx-metal-light': '#f5f0e8',
    '--wx-water': '#4a7098', '--wx-water-light': '#7aa8d0',
    '--color-positive': '#5a9a6a', '--color-negative': '#e06070', '--color-neutral': '#8b7355',
    '--color-blue': '#7aa8d0', '--color-blue-bg': 'rgba(74,112,152,0.15)', '--color-blue-border': 'rgba(74,112,152,0.3)',
    '--btn-go-bg': 'linear-gradient(135deg, #8b1a1a, #b22222, #c44536)', '--nav-bg': '#1a1008'
  },
  'ink-wash': {
    '--bg-root': '#0a0a0c', '--bg-secondary': '#121215',
    '--bg-card': 'rgba(22,22,26,0.88)', '--bg-card-hover': 'rgba(22,22,26,0.75)',
    '--bg-card-solid': '#16161a', '--bg-input': 'rgba(16,16,20,0.6)',
    '--bg-nav': 'rgba(10,10,12,0.98)',
    '--text-primary': '#e0dcd6', '--text-secondary': '#b0a89e',
    '--text-muted': '#70685e', '--text-placeholder': '#484038', '--text-subtle': '#585048',
    '--text-body': '#a09890',
    '--accent': '#b0a89e', '--accent-light': '#c8c0b6', '--accent-dark': '#90887e',
    '--accent-rgb': '176,168,158', '--accent-light-rgb': '200,192,182',
    '--accent-04': 'rgba(176,168,158,0.04)', '--accent-06': 'rgba(176,168,158,0.06)',
    '--accent-08': 'rgba(176,168,158,0.08)', '--accent-10': 'rgba(176,168,158,0.10)',
    '--accent-12': 'rgba(176,168,158,0.12)', '--accent-15': 'rgba(176,168,158,0.15)',
    '--accent-20': 'rgba(176,168,158,0.20)', '--accent-25': 'rgba(176,168,158,0.25)',
    '--accent-30': 'rgba(176,168,158,0.30)', '--accent-40': 'rgba(176,168,158,0.40)',
    '--accent-50': 'rgba(176,168,158,0.50)',
    '--vermillion': '#a07070', '--vermillion-dark': '#604040', '--vermillion-light': '#c09090',
    '--vermillion-rgb': '160,112,112',
    '--vermillion-06': 'rgba(160,112,112,0.06)', '--vermillion-08': 'rgba(160,112,112,0.08)',
    '--vermillion-10': 'rgba(160,112,112,0.10)', '--vermillion-12': 'rgba(160,112,112,0.12)',
    '--vermillion-15': 'rgba(160,112,112,0.15)', '--vermillion-20': 'rgba(160,112,112,0.20)',
    '--vermillion-30': 'rgba(160,112,112,0.30)', '--vermillion-40': 'rgba(160,112,112,0.40)',
    '--border-color': '#26262a', '--border-light': '#36363a',
    '--border-40': 'rgba(38,38,42,0.4)', '--border-50': 'rgba(38,38,42,0.5)',
    '--shadow-card': '0 1px 3px rgba(0,0,0,0.3)',
    '--shadow-glow': '0 1px 4px rgba(176,168,158,0.1)',
    '--shadow-btn': '0 2px 8px rgba(160,112,112,0.1)',
    '--tap-highlight': 'rgba(176,168,158,0.1)',
    '--wx-wood': '#3a6a4a', '--wx-wood-light': '#4a8a5a',
    '--wx-fire': '#a05050', '--wx-fire-light': '#c07060',
    '--wx-earth': '#a09880', '--wx-earth-light': '#b8b098',
    '--wx-metal': '#d8d4ce', '--wx-metal-light': '#e8e4de',
    '--wx-water': '#4a6080', '--wx-water-light': '#6a90b0',
    '--color-positive': '#4a8a5a', '--color-negative': '#c09090', '--color-neutral': '#70685e',
    '--color-blue': '#5a7aaa', '--color-blue-bg': 'rgba(90,122,170,0.15)', '--color-blue-border': 'rgba(90,122,170,0.3)',
    '--btn-go-bg': 'linear-gradient(180deg, #604040, #806060, #907070)', '--nav-bg': '#121215'
  },
  imperial: {
    '--bg-root': '#0d0005', '--bg-secondary': '#1a0812',
    '--bg-card': 'rgba(28,10,18,0.88)', '--bg-card-hover': 'rgba(28,10,18,0.75)',
    '--bg-card-solid': '#1c0a12', '--bg-input': 'rgba(13,0,5,0.55)',
    '--bg-nav': 'rgba(13,0,5,0.98)',
    '--text-primary': '#fff5e8', '--text-secondary': '#e8c840',
    '--text-muted': '#9a7a6a', '--text-placeholder': '#5a3035', '--text-subtle': '#6a4045',
    '--text-body': '#c0a898',
    '--accent': '#e8c840', '--accent-light': '#f0d860', '--accent-dark': '#c0a020',
    '--accent-rgb': '232,200,64', '--accent-light-rgb': '240,216,96',
    '--accent-04': 'rgba(232,200,64,0.04)', '--accent-06': 'rgba(232,200,64,0.06)',
    '--accent-08': 'rgba(232,200,64,0.08)', '--accent-10': 'rgba(232,200,64,0.10)',
    '--accent-12': 'rgba(232,200,64,0.12)', '--accent-15': 'rgba(232,200,64,0.15)',
    '--accent-20': 'rgba(232,200,64,0.20)', '--accent-25': 'rgba(232,200,64,0.25)',
    '--accent-30': 'rgba(232,200,64,0.30)', '--accent-40': 'rgba(232,200,64,0.40)',
    '--accent-50': 'rgba(232,200,64,0.50)',
    '--vermillion': '#d42030', '--vermillion-dark': '#8b1018', '--vermillion-light': '#f05050',
    '--vermillion-rgb': '212,32,48',
    '--vermillion-06': 'rgba(212,32,48,0.06)', '--vermillion-08': 'rgba(212,32,48,0.08)',
    '--vermillion-10': 'rgba(212,32,48,0.10)', '--vermillion-12': 'rgba(212,32,48,0.12)',
    '--vermillion-15': 'rgba(212,32,48,0.15)', '--vermillion-20': 'rgba(212,32,48,0.20)',
    '--vermillion-30': 'rgba(212,32,48,0.30)', '--vermillion-40': 'rgba(212,32,48,0.40)',
    '--border-color': '#3d1520', '--border-light': '#5a2030',
    '--border-40': 'rgba(61,21,32,0.4)', '--border-50': 'rgba(61,21,32,0.5)',
    '--shadow-card': '0 6px 30px rgba(0,0,0,0.5), 0 0 0 1px rgba(232,200,64,0.15)',
    '--shadow-glow': '0 4px 20px rgba(232,200,64,0.4)',
    '--shadow-btn': '0 8px 30px rgba(212,32,48,0.3)',
    '--tap-highlight': 'rgba(232,200,64,0.15)',
    '--wx-wood': '#4a7c59', '--wx-wood-light': '#5a9a6a',
    '--wx-fire': '#d42030', '--wx-fire-light': '#f05050',
    '--wx-earth': '#e8c840', '--wx-earth-light': '#f0d860',
    '--wx-metal': '#fff8ee', '--wx-metal-light': '#ffffff',
    '--wx-water': '#2c3e6b', '--wx-water-light': '#5a7ec0',
    '--color-positive': '#5a9a6a', '--color-negative': '#f05050', '--color-neutral': '#9a7a6a',
    '--color-blue': '#7aa8d0', '--color-blue-bg': 'rgba(74,112,152,0.15)', '--color-blue-border': 'rgba(74,112,152,0.3)',
    '--btn-go-bg': 'linear-gradient(135deg, #8b1018, #d42030, #e84050)', '--nav-bg': '#1a0812'
  },
  celadon: {
    '--bg-root': '#0a1512', '--bg-secondary': '#142520',
    '--bg-card': 'rgba(16,32,28,0.88)', '--bg-card-hover': 'rgba(16,32,28,0.75)',
    '--bg-card-solid': '#10201c', '--bg-input': 'rgba(10,21,18,0.55)',
    '--bg-nav': 'rgba(10,21,18,0.98)',
    '--text-primary': '#e8f0ec', '--text-secondary': '#8cc4a8',
    '--text-muted': '#5a7a6a', '--text-placeholder': '#3a5045', '--text-subtle': '#4a6055',
    '--text-body': '#a0c0b0',
    '--accent': '#8cc4a8', '--accent-light': '#a0d8b8', '--accent-dark': '#6a9a80',
    '--accent-rgb': '140,196,168', '--accent-light-rgb': '160,216,184',
    '--accent-04': 'rgba(140,196,168,0.04)', '--accent-06': 'rgba(140,196,168,0.06)',
    '--accent-08': 'rgba(140,196,168,0.08)', '--accent-10': 'rgba(140,196,168,0.10)',
    '--accent-12': 'rgba(140,196,168,0.12)', '--accent-15': 'rgba(140,196,168,0.15)',
    '--accent-20': 'rgba(140,196,168,0.20)', '--accent-25': 'rgba(140,196,168,0.25)',
    '--accent-30': 'rgba(140,196,168,0.30)', '--accent-40': 'rgba(140,196,168,0.40)',
    '--accent-50': 'rgba(140,196,168,0.50)',
    '--vermillion': '#c08060', '--vermillion-dark': '#8a5040', '--vermillion-light': '#e0a080',
    '--vermillion-rgb': '192,128,96',
    '--vermillion-06': 'rgba(192,128,96,0.06)', '--vermillion-08': 'rgba(192,128,96,0.08)',
    '--vermillion-10': 'rgba(192,128,96,0.10)', '--vermillion-12': 'rgba(192,128,96,0.12)',
    '--vermillion-15': 'rgba(192,128,96,0.15)', '--vermillion-20': 'rgba(192,128,96,0.20)',
    '--vermillion-30': 'rgba(192,128,96,0.30)', '--vermillion-40': 'rgba(192,128,96,0.40)',
    '--border-color': '#1a3028', '--border-light': '#2a4038',
    '--border-40': 'rgba(26,48,40,0.4)', '--border-50': 'rgba(26,48,40,0.5)',
    '--shadow-card': '0 4px 20px rgba(0,0,0,0.35), 0 0 15px rgba(140,196,168,0.1)',
    '--shadow-glow': '0 2px 20px rgba(140,196,168,0.3)',
    '--shadow-btn': '0 6px 24px rgba(192,128,96,0.2)',
    '--tap-highlight': 'rgba(140,196,168,0.12)',
    '--wx-wood': '#4a7c59', '--wx-wood-light': '#5a9a6a',
    '--wx-fire': '#c08060', '--wx-fire-light': '#e0a080',
    '--wx-earth': '#a0b898', '--wx-earth-light': '#b8d0b0',
    '--wx-metal': '#e8f0ec', '--wx-metal-light': '#f0f8f4',
    '--wx-water': '#305060', '--wx-water-light': '#4a7080',
    '--color-positive': '#5a9a6a', '--color-negative': '#e0a080', '--color-neutral': '#5a7a6a',
    '--color-blue': '#5a9aaa', '--color-blue-bg': 'rgba(90,154,170,0.15)', '--color-blue-border': 'rgba(90,154,170,0.3)',
    '--btn-go-bg': 'linear-gradient(90deg, #7a4030, #c08060, #d09070)', '--nav-bg': '#142520'
  }
}

// ===== 排版+间距+造型+阴影+装饰（46 变量/主题）=====
var themeLayout = {
  classic: {
    '--font-family-base': "'STKaiti','PingFang SC',serif",
    '--font-family-title': "'STKaiti',serif",
    '--font-family-display': "'STKaiti',serif",
    '--font-size-hero': '42px',
    '--font-size-title': '17px',
    '--font-size-body': '15px',
    '--font-size-caption': '11px',
    '--font-size-display': '24px',
    '--letter-spacing-hero': '12px',
    '--font-weight-hero': '700',
    '--font-weight-title': '700',
    '--font-weight-body': '400',
    '--font-weight-strong': '700',
    '--spacing-page-padding': '10px 14px 20px',
    '--spacing-section-gap': '14px',
    '--spacing-card-padding': '16px',
    '--spacing-card-inner-gap': '12px',
    '--spacing-input-padding': '11px 14px',
    '--spacing-btn-padding': '16px',
    '--radius-card': '10px',
    '--radius-btn': '9px',
    '--radius-input': '7px',
    '--radius-tag': '13px',
    '--radius-toggle': '8px',
    '--border-width-card': '1px',
    '--border-style-card': 'solid',
    '--shadow-card-spread': '20px',
    '--shadow-btn-spread': '24px',
    '--decoration-hero-opacity': '1',
    '--decoration-card-accent-line': '1px',
    '--decoration-divider-style': 'solid',
    '--decoration-divider-width': '2px',
    '--decoration-card-inner-glow': 'none',
    '--btn-go-gradient-angle': '135deg',
    '--btn-go-border-radius': '9px',
    '--btn-go-font-size': '20px',
    '--btn-go-letter-spacing': '8px',
    '--hero-layout-mode': 'center',
    '--yy-wrap-bg': 'rgba(0,0,0,.2)',
    '--yy-right-bg': 'rgba(139,115,85,.08)'
  },
  'ink-wash': {
    '--font-family-base': "'PingFang SC','Helvetica Neue',sans-serif",
    '--font-family-title': "'PingFang SC',sans-serif",
    '--font-family-display': "'PingFang SC',sans-serif",
    '--font-size-hero': '32px',
    '--font-size-title': '14px',
    '--font-size-body': '14px',
    '--font-size-caption': '10px',
    '--font-size-display': '18px',
    '--letter-spacing-hero': '4px',
    '--font-weight-hero': '300',
    '--font-weight-title': '300',
    '--font-weight-body': '300',
    '--font-weight-strong': '500',
    '--spacing-page-padding': '20px 24px 24px',
    '--spacing-section-gap': '22px',
    '--spacing-card-padding': '20px',
    '--spacing-card-inner-gap': '16px',
    '--spacing-input-padding': '14px 16px',
    '--spacing-btn-padding': '18px',
    '--radius-card': '2px',
    '--radius-btn': '2px',
    '--radius-input': '2px',
    '--radius-tag': '2px',
    '--radius-toggle': '2px',
    '--border-width-card': '0.5px',
    '--border-style-card': 'solid',
    '--shadow-card-spread': '2px',
    '--shadow-btn-spread': '6px',
    '--decoration-hero-opacity': '0.25',
    '--decoration-card-accent-line': '0px',
    '--decoration-divider-style': 'dotted',
    '--decoration-divider-width': '0.5px',
    '--decoration-card-inner-glow': 'none',
    '--btn-go-gradient-angle': '180deg',
    '--btn-go-border-radius': '2px',
    '--btn-go-font-size': '15px',
    '--btn-go-letter-spacing': '10px',
    '--hero-layout-mode': 'left',
    '--yy-wrap-bg': 'transparent',
    '--yy-right-bg': 'rgba(176,168,158,.05)'
  },
  imperial: {
    '--font-family-base': "'STSong','PingFang SC',serif",
    '--font-family-title': "'STSong',serif",
    '--font-family-display': "'STSong',serif",
    '--font-size-hero': '52px',
    '--font-size-title': '18px',
    '--font-size-body': '16px',
    '--font-size-caption': '12px',
    '--font-size-display': '28px',
    '--letter-spacing-hero': '16px',
    '--font-weight-hero': '900',
    '--font-weight-title': '700',
    '--font-weight-body': '500',
    '--font-weight-strong': '900',
    '--spacing-page-padding': '10px 14px 16px',
    '--spacing-section-gap': '10px',
    '--spacing-card-padding': '12px',
    '--spacing-card-inner-gap': '10px',
    '--spacing-input-padding': '10px 12px',
    '--spacing-btn-padding': '14px',
    '--radius-card': '0px',
    '--radius-btn': '0px',
    '--radius-input': '0px',
    '--radius-tag': '0px',
    '--radius-toggle': '0px',
    '--border-width-card': '2px',
    '--border-style-card': 'solid',
    '--shadow-card-spread': '30px',
    '--shadow-btn-spread': '30px',
    '--decoration-hero-opacity': '1',
    '--decoration-card-accent-line': '3px',
    '--decoration-divider-style': 'double',
    '--decoration-divider-width': '3px',
    '--decoration-card-inner-glow': 'none',
    '--btn-go-gradient-angle': '135deg',
    '--btn-go-border-radius': '0px',
    '--btn-go-font-size': '18px',
    '--btn-go-letter-spacing': '10px',
    '--hero-layout-mode': 'framed',
    '--yy-wrap-bg': 'rgba(0,0,0,.3)',
    '--yy-right-bg': 'rgba(232,200,64,.12)'
  },
  celadon: {
    '--font-family-base': "'PingFang SC','STKaiti',sans-serif",
    '--font-family-title': "'PingFang SC',sans-serif",
    '--font-family-display': "'PingFang SC',sans-serif",
    '--font-size-hero': '44px',
    '--font-size-title': '17px',
    '--font-size-body': '15px',
    '--font-size-caption': '11px',
    '--font-size-display': '22px',
    '--letter-spacing-hero': '10px',
    '--font-weight-hero': '600',
    '--font-weight-title': '500',
    '--font-weight-body': '400',
    '--font-weight-strong': '600',
    '--spacing-page-padding': '14px 18px 20px',
    '--spacing-section-gap': '16px',
    '--spacing-card-padding': '18px',
    '--spacing-card-inner-gap': '14px',
    '--spacing-input-padding': '12px 16px',
    '--spacing-btn-padding': '16px',
    '--radius-card': '20px',
    '--radius-btn': '20px',
    '--radius-input': '14px',
    '--radius-tag': '20px',
    '--radius-toggle': '18px',
    '--border-width-card': '1px',
    '--border-style-card': 'solid',
    '--shadow-card-spread': '16px',
    '--shadow-btn-spread': '20px',
    '--decoration-hero-opacity': '0.8',
    '--decoration-card-accent-line': '2px',
    '--decoration-divider-style': 'solid',
    '--decoration-divider-width': '1px',
    '--decoration-card-inner-glow': 'none',
    '--btn-go-gradient-angle': '90deg',
    '--btn-go-border-radius': '20px',
    '--btn-go-font-size': '17px',
    '--btn-go-letter-spacing': '8px',
    '--hero-layout-mode': 'center',
    '--yy-wrap-bg': 'rgba(0,0,0,.15)',
    '--yy-right-bg': 'rgba(140,196,168,.1)'
  }
}

// ===== 图标集（24 图标/主题）=====
var themeIcons = {
  classic: {
    name: '👤', gender: '⚧', gender_male: '☰', gender_female: '☷',
    calendar: '📅', calendar_solar: '☀', calendar_lunar: '🌙',
    birth: '🎂', time: '🕐', settings: '⚙', back: '🔄',
    bagua: '☯', birth_info: '📋', geju: '🏛', wuxing: '⭐',
    year_fortune: '🔮', current_fortune: '⏳', dayun: '📈',
    remedy: '💡', taiyuan: '🏠', shensha: '🔱', changsheng: '🌱',
    vernacular: '📜', control: '🎯', books: '📚', life_summary: '🌟',
    section_collapse: '▼', section_expand: '▲'
  },
  'ink-wash': {
    name: '◇', gender: '◇', gender_male: '【乾】', gender_female: '【坤】',
    calendar: '◇', calendar_solar: '【阳】', calendar_lunar: '【阴】',
    birth: '◇', time: '◇', settings: '⚙', back: '←',
    bagua: '⊙', birth_info: '◇', geju: '◇', wuxing: '◇',
    year_fortune: '◇', current_fortune: '◇', dayun: '◇',
    remedy: '◇', taiyuan: '◇', shensha: '◇', changsheng: '◇',
    vernacular: '◇', control: '◇', books: '◇', life_summary: '◇',
    section_collapse: '∨', section_expand: '∧'
  },
  imperial: {
    name: '▣', gender: '▣', gender_male: '乾', gender_female: '坤',
    calendar: '▣', calendar_solar: '公', calendar_lunar: '农',
    birth: '▣', time: '▣', settings: '⚙', back: '⟵',
    bagua: '⚜', birth_info: '▣', geju: '▣', wuxing: '▣',
    year_fortune: '▣', current_fortune: '▣', dayun: '▣',
    remedy: '▣', taiyuan: '▣', shensha: '▣', changsheng: '▣',
    vernacular: '▣', control: '▣', books: '▣', life_summary: '▣',
    section_collapse: '▽', section_expand: '△'
  },
  celadon: {
    name: '🍂', gender: '⚧', gender_male: '🌿乾', gender_female: '🍃坤',
    calendar: '📅', calendar_solar: '☀', calendar_lunar: '🌙',
    birth: '🌱', time: '💧', settings: '⚙', back: '🔄',
    bagua: '◎', birth_info: '📋', geju: '🏺', wuxing: '🌊',
    year_fortune: '🔮', current_fortune: '⏳', dayun: '📈',
    remedy: '💡', taiyuan: '🏠', shensha: '🍀', changsheng: '🌱',
    vernacular: '📜', control: '🎯', books: '📚', life_summary: '✨',
    section_collapse: '▼', section_expand: '▲'
  }
}

var themeMeta = [
  { id: 'classic',  name: '经典暗金', subtitle: 'Classic Gold',   desc: '温暖深棕底色，鎏金点缀，传统中式美学' },
  { id: 'ink-wash', name: '墨韵',     subtitle: 'Ink Wash',       desc: '纯黑水墨基调，银白素雅，极简禅意画风' },
  { id: 'imperial', name: '宫廷',     subtitle: 'Imperial',       desc: '深红宫墙底色，明亮鎏金，皇家奢华气质' },
  { id: 'celadon',  name: '青瓷',     subtitle: 'Celadon',        desc: '青绿釉色基底，瓷质温润，江南雅致韵味' }
]

var navBarColors = {
  classic:  { bg: '#1a0a00', front: '#ffffff' },
  'ink-wash': { bg: '#0a0a0c', front: '#ffffff' },
  imperial: { bg: '#0d0005', front: '#ffffff' },
  celadon:  { bg: '#0a1512', front: '#ffffff' }
}

function getCurrentTheme() {
  try {
    var stored = wx.getStorageSync(STORAGE_KEY)
    if (stored && themeColors[stored]) return stored
  } catch (e) {}
  return DEFAULT_THEME
}

function setTheme(themeId) {
  if (!themeColors[themeId]) return false
  wx.setStorageSync(STORAGE_KEY, themeId)
  var app = getApp()
  if (app) {
    app.globalData.theme = themeId
    app.globalData.themeStyle = buildStyleString(themeId)
  }
  return true
}

function buildStyleString(themeId) {
  var colors = themeColors[themeId] || themeColors[DEFAULT_THEME]
  var layout = themeLayout[themeId] || themeLayout[DEFAULT_THEME]
  var merged = {}
  var k
  for (k in colors) { merged[k] = colors[k] }
  for (k in layout) { merged[k] = layout[k] }
  var pairs = []
  for (k in merged) { pairs.push(k + ':' + merged[k]) }
  return pairs.join(';')
}

function getThemeStyle(themeId) {
  return buildStyleString(themeId || getCurrentTheme())
}

function getIcon(iconKey, themeId) {
  var t = themeId || getCurrentTheme()
  var icons = themeIcons[t] || themeIcons[DEFAULT_THEME]
  return icons[iconKey] || iconKey
}

function getIconSet(themeId) {
  var t = themeId || getCurrentTheme()
  var icons = themeIcons[t] || themeIcons[DEFAULT_THEME]
  var result = {}
  var k
  for (k in icons) { result[k] = icons[k] }
  return result
}

module.exports = {
  STORAGE_KEY: STORAGE_KEY,
  DEFAULT_THEME: DEFAULT_THEME,
  themeColors: themeColors,
  themeLayout: themeLayout,
  themeIcons: themeIcons,
  themeMeta: themeMeta,
  navBarColors: navBarColors,
  getCurrentTheme: getCurrentTheme,
  setTheme: setTheme,
  getThemeStyle: getThemeStyle,
  buildStyleString: buildStyleString,
  getIcon: getIcon,
  getIconSet: getIconSet
}
