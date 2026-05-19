/**
 * 后台管理面板逻辑
 */

(function () {
  'use strict';

  // ---- 主题预设 ----
  const BUILTIN_THEMES = [
    {
      id: 'dark', name: '暗夜黑',
      preview: 'linear-gradient(135deg, #0f1923 0%, #1a2736 50%, #3b82f6 100%)'
    },
    {
      id: 'blue', name: '深海蓝',
      preview: 'linear-gradient(135deg, #0a1628 0%, #112240 50%, #64ffda 100%)'
    },
    {
      id: 'green', name: '商务绿',
      preview: 'linear-gradient(135deg, #0a1f14 0%, #0f2d1f 50%, #4ade80 100%)'
    },
    {
      id: 'purple', name: '科技紫',
      preview: 'linear-gradient(135deg, #120c1e 0%, #1a1035 50%, #a78bfa 100%)'
    },
    {
      id: 'light', name: '简约白',
      preview: 'linear-gradient(135deg, #e8eaed 0%, #ffffff 50%, #2563eb 100%)'
    }
  ];

  let currentSettings = {};
  let selectedTheme = 'dark';

  // ---- Tab 切换 ----
  function initTabs() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        const tabId = item.dataset.tab;
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        document.getElementById('panel-' + tabId).classList.add('active');
      });
    });
  }

  // ---- 主题选择器 ----
  function renderThemeGrid(themes) {
    const grid = document.getElementById('theme-grid');
    grid.innerHTML = '';

    BUILTIN_THEMES.forEach(t => {
      const card = document.createElement('div');
      card.className = 'theme-card' + (t.id === selectedTheme ? ' selected' : '');
      card.innerHTML = `
        <div class="theme-preview" style="background:${t.preview}"></div>
        <div class="theme-name">${t.name}</div>
      `;
      card.addEventListener('click', () => {
        document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedTheme = t.id;
        applyThemeToPreview(t.id, themes);
      });
      grid.appendChild(card);
    });
  }

  function applyThemeToPreview(themeId, themes) {
    const t = themes[themeId];
    if (!t) return;
    document.getElementById('cfg-bg-primary').value = t.bg_primary;
    document.getElementById('cfg-bg-primary-txt').value = t.bg_primary;
    document.getElementById('cfg-accent').value = t.accent;
    document.getElementById('cfg-accent-txt').value = t.accent;
  }

  // 颜色同步
  function initColorSync() {
    const pairs = [
      ['cfg-bg-primary', 'cfg-bg-primary-txt'],
      ['cfg-accent', 'cfg-accent-txt']
    ];
    pairs.forEach(([colorId, textId]) => {
      const colorEl = document.getElementById(colorId);
      const textEl = document.getElementById(textId);
      if (!colorEl || !textEl) return;
      colorEl.addEventListener('input', () => { textEl.value = colorEl.value; });
      textEl.addEventListener('change', () => {
        if (/^#[0-9a-fA-F]{6}$/.test(textEl.value)) {
          colorEl.value = textEl.value;
        }
      });
    });
  }

  // ---- Logo 上传 ----
  function initLogoUpload() {
    const input = document.getElementById('logo-input');
    input.addEventListener('change', async () => {
      const file = input.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const resp = await fetch('/api/upload/logo', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.ok) {
          showLogo(data.logo_url);
          currentSettings.display.logo_url = data.logo_url;
        } else {
          alert('上传失败: ' + (data.error || '未知错误'));
        }
      } catch (e) {
        alert('上传失败: ' + e.message);
      }
    });
  }

  function showLogo(url) {
    const img = document.getElementById('logo-img');
    const placeholder = document.getElementById('logo-placeholder');
    if (url) {
      img.src = url + '?t=' + Date.now();
      img.style.display = 'block';
      placeholder.style.display = 'none';
    } else {
      img.style.display = 'none';
      placeholder.style.display = 'block';
    }
  }

  function removeLogo() {
    showLogo('');
    currentSettings.display.logo_url = '';
  }

  // ---- 加载设置到表单 ----
  function loadSettingsToForm(s) {
    currentSettings = JSON.parse(JSON.stringify(s));
    const d = s.display || {};
    const v = s.voice || {};
    const t = s.timer || {};
    const themes = s.themes || {};

    document.getElementById('cfg-title').value = d.title || '签到叫号大屏';
    document.getElementById('cfg-subtitle').value = d.subtitle || '';
    document.getElementById('cfg-font-scale').value = d.font_scale || 'normal';
    document.getElementById('cfg-refresh').value = d.refresh_interval || 5;
    document.getElementById('cfg-mask-names').checked = d.mask_names !== false;
    document.getElementById('cfg-show-location').checked = d.show_location !== false;
    document.getElementById('cfg-show-status').checked = d.show_status !== false;

    selectedTheme = d.theme || 'dark';
    renderThemeGrid(themes);

    const theme = themes[selectedTheme] || {};
    document.getElementById('cfg-bg-primary').value = d.bg_primary || theme.bg_primary || '#0f1923';
    document.getElementById('cfg-bg-primary-txt').value = d.bg_primary || theme.bg_primary || '#0f1923';
    document.getElementById('cfg-accent').value = d.accent || theme.accent || '#3b82f6';
    document.getElementById('cfg-accent-txt').value = d.accent || theme.accent || '#3b82f6';

    document.getElementById('cfg-voice-enabled').checked = v.enabled !== false;
    document.getElementById('cfg-welcome-tpl').value = v.welcome_template || '{name}，欢迎签到！';
    document.getElementById('cfg-remind-tpl').value = v.remind_template || '{name}，您的等待时间已到，请留意叫号。';

    document.getElementById('cfg-remind-minutes').value = t.remind_minutes || 40;
    document.getElementById('cfg-warning-minutes').value = t.warning_minutes || 35;

    showLogo(d.logo_url || '');
  }

  // ---- 收集表单到设置 ----
  function collectSettingsFromForm() {
    const d = currentSettings.display || {};
    const v = currentSettings.voice || {};
    const t = currentSettings.timer || {};

    d.title = document.getElementById('cfg-title').value.trim() || '签到叫号大屏';
    d.subtitle = document.getElementById('cfg-subtitle').value.trim();
    d.font_scale = document.getElementById('cfg-font-scale').value;
    d.refresh_interval = parseInt(document.getElementById('cfg-refresh').value) || 5;
    d.mask_names = document.getElementById('cfg-mask-names').checked;
    d.show_location = document.getElementById('cfg-show-location').checked;
    d.show_status = document.getElementById('cfg-show-status').checked;
    d.theme = selectedTheme;
    d.bg_primary = document.getElementById('cfg-bg-primary').value;
    d.accent = document.getElementById('cfg-accent').value;

    v.enabled = document.getElementById('cfg-voice-enabled').checked;
    v.welcome_template = document.getElementById('cfg-welcome-tpl').value.trim();
    v.remind_template = document.getElementById('cfg-remind-tpl').value.trim();

    t.remind_minutes = parseInt(document.getElementById('cfg-remind-minutes').value) || 40;
    t.warning_minutes = parseInt(document.getElementById('cfg-warning-minutes').value) || 35;

    return { display: d, voice: v, timer: t, themes: currentSettings.themes };
  }

  // ---- 保存设置 ----
  async function saveAllSettings() {
    const s = collectSettingsFromForm();
    currentSettings = s;
    try {
      const resp = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(s)
      });
      const data = await resp.json();
      if (data.ok) {
        const status = document.getElementById('save-status');
        status.textContent = '✓ 设置已保存';
        status.classList.add('visible');
        setTimeout(() => status.classList.remove('visible'), 2000);
      }
    } catch (e) {
      alert('保存失败: ' + e.message);
    }
  }

  // ---- 数据面板统计 ----
  async function loadStats() {
    try {
      const resp = await fetch('/api/status');
      const data = await resp.json();
      document.getElementById('stat-cards').innerHTML = `
        <div class="stat-card">
          <div class="stat-num">${data.today_count || 0}</div>
          <div class="stat-label">今日签到</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">${data.record_count || 0}</div>
          <div class="stat-label">总记录数</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">${data.ngrok_url ? '已连接' : '仅内网'}</div>
          <div class="stat-label">外网状态</div>
        </div>
      `;
    } catch (e) {
      // ignore
    }
  }

  // ---- 初始化 ----
  async function init() {
    initTabs();
    initColorSync();
    initLogoUpload();

    try {
      const resp = await fetch('/api/settings');
      const data = await resp.json();
      loadSettingsToForm(data);
    } catch (e) {
      console.warn('无法加载设置，使用默认值');
    }

    // 加载数据面板信息
    const dataTab = document.querySelector('[data-tab="data"]');
    dataTab.addEventListener('click', loadStats);

    // 全局保存快捷键 Ctrl+S
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveAllSettings();
      }
    });
  }

  // 暴露到全局
  window.saveAllSettings = saveAllSettings;
  window.removeLogo = removeLogo;

  document.addEventListener('DOMContentLoaded', init);
})();
