/**
 * 后台管理面板逻辑
 */
(function () {
  'use strict';

  // 自定义确认弹窗（不退出全屏）
  var _cfResolve=null;
  window.cfDlg=function(ok){var el=document.getElementById('confirm-dialog');if(el)el.style.display='none';if(_cfResolve)_cfResolve(ok);};
  window.cfConfirm=function(msg){return new Promise(function(resolve){_cfResolve=resolve;var el=document.getElementById('confirm-msg');if(el)el.textContent=msg;var d=document.getElementById('confirm-dialog');if(d)d.style.display='flex';});};
  // 密码验证弹窗
  var _pwResolve=null;
  window.pwDlg=function(ok){var el=document.getElementById('pw-dialog');if(el)el.style.display='none';if(_pwResolve)_pwResolve(ok?document.getElementById('pw-input').value:null);var inp=document.getElementById('pw-input');if(inp)inp.value='';};
  window.verifyAdmin=function(msg){return new Promise(function(resolve){_pwResolve=resolve;var el=document.getElementById('pw-msg');if(el)el.textContent=msg||'请输入管理员密码';var d=document.getElementById('pw-dialog');if(d)d.style.display='flex';var inp=document.getElementById('pw-input');if(inp)inp.focus();});};
  document.addEventListener('keydown',function(e){if(e.key==='Enter'){var pwD=document.getElementById('pw-dialog');if(pwD&&pwD.style.display==='flex')pwDlg(true);}});

  const BUILTIN_THEMES = [
    { id: 'dark', name: '暗夜黑', preview: 'linear-gradient(135deg, #0f1923 0%, #1a2736 50%, #3b82f6 100%)' },
    { id: 'blue', name: '深海蓝', preview: 'linear-gradient(135deg, #0a1628 0%, #112240 50%, #64ffda 100%)' },
    { id: 'green', name: '商务绿', preview: 'linear-gradient(135deg, #0a1f14 0%, #0f2d1f 50%, #4ade80 100%)' },
    { id: 'purple', name: '科技紫', preview: 'linear-gradient(135deg, #120c1e 0%, #1a1035 50%, #a78bfa 100%)' },
    { id: 'light', name: '简约白', preview: 'linear-gradient(135deg, #e8eaed 0%, #ffffff 50%, #2563eb 100%)' }
  ];

  let currentSettings = {};
  let selectedTheme = 'dark';

  // ========== 认证 ==========

  function getToken() {
    return localStorage.getItem('signin_token');
  }

  function authHeaders(jsonContentType) {
    const h = {};
    const token = getToken();
    if (token) h['X-Auth-Token'] = token;
    if (jsonContentType !== false) h['Content-Type'] = 'application/json';
    return h;
  }

  function showLoginOverlay() {
    const lo = document.getElementById('login-overlay');
    if (lo) lo.style.display = 'flex';
  }

  function hideLoginOverlay() {
    const lo = document.getElementById('login-overlay');
    if (lo) lo.style.display = 'none';
  }

  async function doLogin() {
    const u = document.getElementById('login-user').value.trim();
    const p = document.getElementById('login-pass').value;
    const err = document.getElementById('login-error');
    err.style.display = 'none';
    if (!u || !p) { err.textContent = '请输入用户名和密码'; err.style.display = 'block'; return; }
    try {
      const resp = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p })
      });
      const data = await resp.json();
      if (data.ok) {
        localStorage.setItem('signin_token', data.token);
        localStorage.setItem('signin_user', JSON.stringify(data.user));
        hideLoginOverlay();
        startAdmin(data.user);
      } else {
        err.textContent = data.error || '用户名或密码错误';
        err.style.display = 'block';
      }
    } catch (e) {
      err.textContent = '无法连接服务器';
      err.style.display = 'block';
    }
  }

  async function checkLogin() {
    const token = getToken();
    if (!token) { showLoginOverlay(); return false; }
    try {
      const resp = await fetch('/api/me', { headers: { 'X-Auth-Token': token } });
      const data = await resp.json();
      if (!data.ok) {
        localStorage.removeItem('signin_token');
        localStorage.removeItem('signin_user');
        showLoginOverlay();
        return false;
      }
      return data.user;
    } catch (e) { showLoginOverlay(); return false; }
  }

  // ========== 初始化 ==========

  function startAdmin(user) {
    const el = document.getElementById('user-info');
    if (el) el.textContent = `${user.name || user.username} (${user.role === 'admin' ? '管理员' : '普通用户'})`;
    if (user.role !== 'admin') {
      const tab = document.querySelector('[data-tab="users"]');
      if (tab) tab.style.display = 'none';
    }

    initColorSync();
    initLogoUpload();
    initCropDrag();

    fetch('/api/settings')
      .then(r => r.json())
      .then(d => {
        loadSettingsToForm(d);
        // 备份路径
        var bp = document.getElementById('cfg-backup-path');
        if (bp && d.backup && d.backup.path) bp.value = d.backup.path;
      })
      .catch(() => {});

    const dataTab = document.querySelector('[data-tab="data"]');
    if (dataTab) dataTab.addEventListener('click', loadStats);

    const usersTab = document.querySelector('[data-tab="users"]');
    if (usersTab) usersTab.addEventListener('click', loadUsers);
    // people tab merged into data panel
    const marqueeTab = document.querySelector('[data-tab="marquee"]');
    if (marqueeTab) marqueeTab.addEventListener('click', loadMarquees);

    const syncTab = document.querySelector('[data-tab="sync"]');
    if (syncTab) syncTab.addEventListener('click', loadSyncSettings);

    // 光晕强度滑块标签
    const glowSlider = document.getElementById('cfg-glow-intensity');
    if (glowSlider) {
      glowSlider.addEventListener('input', function() {
        updateGlowLabel(parseInt(this.value));
      });
    }

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveAllSettings();
      }
    });
  }

  function updateGlowLabel(val) {
    const el = document.getElementById('glow-label');
    if (!el) return;
    const labels = {1: '当前：淡雅', 2: '当前：标准', 3: '当前：加强'};
    el.textContent = labels[val] || '当前：标准';
  }

  async function init() {
    const loading = document.getElementById('loading-overlay');
    if (loading) loading.style.display = 'none';

    // 登录按钮事件
    const loginBtn = document.getElementById('login-btn');
    if (loginBtn) loginBtn.addEventListener('click', doLogin);
    // 回车登录
    const loginPass = document.getElementById('login-pass');
    if (loginPass) loginPass.addEventListener('keydown', (e) => { if (e.key === 'Enter') doLogin(); });

    // 退出登录
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        await fetch('/api/logout', { method: 'POST', headers: authHeaders(false) });
        localStorage.removeItem('signin_token');
        localStorage.removeItem('signin_user');
        location.reload();
      });
    }

    const user = await checkLogin();
    if (user) startAdmin(user);
  }

  // ========== Tab 切换 ==========

  function switchTab(tabId) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    const navItem = document.querySelector(`[data-tab="${tabId}"]`);
    const panel = document.getElementById('panel-' + tabId);
    if (navItem) navItem.classList.add('active');
    if (panel) panel.classList.add('active');
    else console.warn('面板不存在: panel-' + tabId);
  }
  window._switchTab = switchTab;

  function initTabs() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => switchTab(item.dataset.tab));
    });
  }

  // ========== 主题 ==========

  function renderThemeGrid(themes) {
    const grid = document.getElementById('theme-grid');
    if (!grid) return;
    grid.innerHTML = '';
    BUILTIN_THEMES.forEach(t => {
      const card = document.createElement('div');
      card.className = 'theme-card' + (t.id === selectedTheme ? ' selected' : '');
      card.innerHTML = `<div class="theme-preview" style="background:${t.preview}"></div><div class="theme-name">${t.name}</div>`;
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
    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    setVal('cfg-bg-primary', t.bg_primary);
    setVal('cfg-bg-primary-txt', t.bg_primary);
    setVal('cfg-accent', t.accent);
    setVal('cfg-accent-txt', t.accent);
  }

  function initColorSync() {
    [['cfg-bg-primary', 'cfg-bg-primary-txt'], ['cfg-accent', 'cfg-accent-txt']].forEach(([cid, tid]) => {
      const ce = document.getElementById(cid), te = document.getElementById(tid);
      if (!ce || !te) return;
      ce.addEventListener('input', () => { te.value = ce.value; });
      te.addEventListener('change', () => { if (/^#[0-9a-fA-F]{6}$/.test(te.value)) ce.value = te.value; });
    });
  }

  // ========== Logo ==========

  function showLogo(url) {
    const img = document.getElementById('logo-img');
    const ph = document.getElementById('logo-placeholder');
    if (!img || !ph) return;
    if (url) {
      const u = url.includes('?') ? url : url + '?v=' + Date.now();
      img.src = u;
      img.style.display = 'block';
      ph.style.display = 'none';
      document.getElementById('btn-crop-logo').style.display = '';
    } else {
      img.src = '';
      img.style.display = 'none';
      ph.style.display = 'block';
      document.getElementById('btn-crop-logo').style.display = 'none';
    }
  }

  function removeLogo() {
    showLogo('');
    if (currentSettings.display) currentSettings.display.logo_url = '';
  }

  function initLogoUpload() {
    const input = document.getElementById('logo-input');
    if (!input) return;
    input.addEventListener('change', async () => {
      const file = input.files[0];
      if (!file) return;

      // 前端校验
      const maxSize = 5 * 1024 * 1024;
      if (file.size > maxSize) {
        alert('上传失败: 图片大小不能超过 5MB');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);

      try {
        const token = getToken();
        const headers = token ? { 'X-Auth-Token': token } : {};
        const resp = await fetch('/api/upload/logo', { method: 'POST', headers, body: formData });
        const data = await resp.json();
        if (data.ok) {
          showLogo(data.logo_url + '?v=' + Date.now());
          if (currentSettings.display) currentSettings.display.logo_url = data.logo_url;
          document.getElementById('save-status').textContent = '✓ 图片已上传，可点击"调整图片"裁剪';
          document.getElementById('save-status').classList.add('visible');
          setTimeout(() => document.getElementById('save-status').classList.remove('visible'), 3000);
          document.getElementById('save-status').textContent = '✓ 图片已上传，请在调整窗口中裁剪';
          document.getElementById('save-status').classList.add('visible');
          setTimeout(() => document.getElementById('save-status').classList.remove('visible'), 3000);
        } else {
          alert('上传失败: ' + (data.error || '服务器拒绝'));
        }
      } catch (e) {
        alert('上传失败: 网络错误，请确认服务器运行中\n' + e.message);
      }
    });
  }

  // ========== 设置表单 ==========

  function loadSettingsToForm(s) {
    currentSettings = JSON.parse(JSON.stringify(s));
    const d = s.display || {}, v = s.voice || {}, t = s.timer || {}, themes = s.themes || {};

    setVal('cfg-title', d.title || '签到叫号大屏');
    setVal('cfg-location-input', d.location || '');
    setVal('cfg-subtitle', d.subtitle || '');
    setVal('cfg-font-scale', d.font_scale || 'normal');
    setVal('cfg-refresh', d.refresh_interval || 5);
    setChecked('cfg-mask-names', d.mask_names !== false);
    setChecked('cfg-show-location', d.show_location !== false);
    setChecked('cfg-show-status', d.show_status !== false);
    setChecked('cfg-glow-enabled', d.glow_enabled !== false);
    const gi = d.glow_intensity || 2;
    setVal('cfg-glow-intensity', gi);
    updateGlowLabel(gi);

    selectedTheme = d.theme || 'dark';
    renderThemeGrid(themes);

    const theme = themes[selectedTheme] || {};
    setVal('cfg-bg-primary', d.bg_primary || theme.bg_primary || '#0f1923');
    setVal('cfg-bg-primary-txt', d.bg_primary || theme.bg_primary || '#0f1923');
    setVal('cfg-accent', d.accent || theme.accent || '#3b82f6');
    setVal('cfg-accent-txt', d.accent || theme.accent || '#3b82f6');

    setChecked('cfg-voice-enabled', v.enabled !== false);
    setVal('cfg-welcome-tpl', v.welcome_template || '{name}，欢迎签到！');
    setVal('cfg-remind-tpl', v.remind_template || '{name}，您的等待时间已到，请留意叫号。');
    let vt = v.templates || {};
    setVal('cfg-tpl-call', vt.call || '有请{name}嘉宾到检测室');
    setVal('cfg-tpl-recall', vt.recall || '再次叫号，请{name}嘉宾到检测室');
    setVal('cfg-tpl-recall-nth', vt.recall_nth || '第{n}次叫号，请{name}嘉宾到检测室');
    setVal('cfg-tpl-done', vt.done || '{name}嘉宾检测完毕');
    setVal('cfg-tpl-pass', vt.pass || '过号，请{name}稍后重叫');
    setVal('cfg-tpl-startup', vt.startup || '签到系统已启动');
    setVal('cfg-tpl-shutdown', vt.shutdown || '签到系统已关闭');

    setVal('cfg-remind-minutes', t.remind_minutes || 40);
    setVal('cfg-warning-minutes', t.warning_minutes || 35);
    setChecked('cfg-countdown-enabled', t.countdown_enabled !== false);
    setVal('cfg-countdown-minutes', t.countdown_minutes || 40);

    showLogo(d.logo_url || '');
    // 同步地点到数据面板只读字段
    var locDP = document.getElementById('cfg-location');
    if (locDP && d.location) locDP.value = d.location;
    const logoUrl = d.logo_url || '';
    document.getElementById('btn-crop-logo').style.display = logoUrl ? '' : 'none';
    // 加载自定义数据路径
    var dpEl = document.getElementById('cfg-data-path');
    if (dpEl) dpEl.value = s.data_path || '';
  }

  function collectSettingsFromForm() {
    const d = currentSettings.display || {}, v = currentSettings.voice || {}, t = currentSettings.timer || {};
    d.title = getVal('cfg-title') || '签到叫号大屏';
    d.location = getVal('cfg-location-input') || getVal('cfg-location');
    d.subtitle = getVal('cfg-subtitle');
    d.font_scale = getVal('cfg-font-scale');
    d.refresh_interval = parseInt(getVal('cfg-refresh')) || 5;
    d.mask_names = isChecked('cfg-mask-names');
    d.show_location = isChecked('cfg-show-location');
    d.show_status = isChecked('cfg-show-status');
    d.theme = selectedTheme;
    d.bg_primary = getVal('cfg-bg-primary');
    d.accent = getVal('cfg-accent');
    d.glow_enabled = isChecked('cfg-glow-enabled');
    d.glow_intensity = parseInt(getVal('cfg-glow-intensity')) || 2;

    v.enabled = isChecked('cfg-voice-enabled');
    v.welcome_template = getVal('cfg-welcome-tpl');
    v.remind_template = getVal('cfg-remind-tpl');
    if (!v.templates) v.templates = {};
    v.templates.call = getVal('cfg-tpl-call');
    v.templates.recall = getVal('cfg-tpl-recall');
    v.templates.recall_nth = getVal('cfg-tpl-recall-nth');
    v.templates.done = getVal('cfg-tpl-done');
    v.templates.pass = getVal('cfg-tpl-pass');
    v.templates.startup = getVal('cfg-tpl-startup');
    v.templates.shutdown = getVal('cfg-tpl-shutdown');

    t.remind_minutes = parseInt(getVal('cfg-remind-minutes')) || 40;
    t.warning_minutes = parseInt(getVal('cfg-warning-minutes')) || 35;
    t.countdown_enabled = isChecked('cfg-countdown-enabled');
    t.countdown_minutes = parseInt(getVal('cfg-countdown-minutes')) || 40;

    // 跑马灯（仅在已加载表单时才读取，否则保留原值）
    const mqFormExists = document.getElementById('mq-text-0');
    let mqs = currentSettings.marquees || [];
    if (mqFormExists) {
      mqs = [];
      for (let i = 0; i < 3; i++) {
        mqs.push({
          enabled: isChecked('mq-enabled-' + i),
          text: getVal('mq-text-' + i),
          size: getVal('mq-size-' + i),
          color: getVal('mq-color-' + i),
          speed: parseInt(getVal('mq-speed-' + i)) || 12,
          delay: parseFloat(getVal('mq-delay-' + i)) || 0,
          gradient: isChecked('mq-gradient-' + i)
        });
      }
    }

    return { display: d, voice: v, timer: t, themes: currentSettings.themes, marquees: mqs };
  }

  function setVal(id, val) { const el = document.getElementById(id); if (el) el.value = val; }
  function getVal(id) { const el = document.getElementById(id); return el ? el.value.trim() : ''; }
  function setChecked(id, v) { const el = document.getElementById(id); if (el) el.checked = v; }
  function isChecked(id) { const el = document.getElementById(id); return el ? el.checked : false; }

  // ========== 自定义数据路径 + 文件夹选择器 ==========

  var _fpSelected = '';
  window._loadDataPath = function(s) {
    var el = document.getElementById('cfg-data-path');
    if (el) el.value = s.data_path || '';
  };

  window.openFolderPicker = function() {
    var existing = document.getElementById('folder-picker-overlay');
    if (existing) { existing.remove(); return; }
    var overlay = document.createElement('div');
    overlay.id = 'folder-picker-overlay';
    overlay.innerHTML =
      '<div id="folder-picker">' +
      '<div class="fp-hd">' +
        '<input id="fp-path" readonly>' +
        '<button onclick="navigateFolder(document.getElementById(\'fp-path\').value+\'/..\')" title="上级目录">⬆</button>' +
        '<button onclick="document.getElementById(\'folder-picker-overlay\').remove()" title="关闭">✕</button>' +
      '</div>' +
      '<div class="fp-list" id="fp-list">加载中...</div>' +
      '<div class="fp-ft">' +
        '<button onclick="document.getElementById(\'folder-picker-overlay\').remove()" style="background:var(--admin-bg);color:var(--text);border:1px solid var(--border);">取消</button>' +
        '<button id="fp-confirm" onclick="confirmFolder()" style="background:var(--primary);color:#fff;border:none;">选择此目录</button>' +
      '</div>' +
      '</div>';
    overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });
    document.body.appendChild(overlay);
    navigateFolder('');
  };

  window.navigateFolder = async function(path) {
    var list = document.getElementById('fp-list');
    var input = document.getElementById('fp-path');
    if (!list || !input) return;
    list.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-secondary);">加载中...</div>';
    try {
      var resp = await fetch('/api/browse-dirs?path=' + encodeURIComponent(path || ''));
      var data = await resp.json();
      if (!data.ok) { list.innerHTML = '<div style="padding:20px;color:var(--danger);">' + (data.error || 'Error') + '</div>'; return; }
      input.value = data.path;
      _fpSelected = data.path;
      list.innerHTML = '';
      (data.items || []).forEach(function(item) {
        var div = document.createElement('div');
        div.className = 'fp-item';
        div.textContent = (item.type === 'parent' ? '📁 ..' : '📁 ') + item.name;
        div.addEventListener('click', function() { navigateFolder(item.path); });
        list.appendChild(div);
      });
      var cfm = document.getElementById('fp-confirm');
      if (cfm) cfm.textContent = '选择: ' + (data.path || '/');
    } catch(e) {
      list.innerHTML = '<div style="padding:20px;color:var(--danger);">网络错误</div>';
    }
  };

  window.confirmFolder = function() {
    var el = document.getElementById('cfg-data-path');
    if (el) el.value = _fpSelected;
    document.getElementById('folder-picker-overlay').remove();
  };

  window.saveDataPath = async function() {
    var el = document.getElementById('cfg-data-path');
    if (!el) return;
    var path = el.value.trim();
    var btn = document.querySelector('#panel-data button.btn-primary');
    var origText = btn ? btn.textContent : '';

    // Step 1: Validate path
    try {
      var vResp = await fetch('/api/validate-data-path?path=' + encodeURIComponent(path));
      var vData = await vResp.json();
      if (!vData.ok || vData.status === 'invalid') {
        showToast(vData.message || '路径无效', 'error'); return;
      }
      if (vData.status === 'missing') {
        var create = await showConfirm(
          '目录不存在',
          '是否在以下位置创建数据目录结构？\n\n' + path
        );
        if (!create) return;
        var cResp = await fetch('/api/create-data-dirs', {
          method: 'POST', headers: authHeaders(),
          body: JSON.stringify({ path: path })
        });
        var cData = await cResp.json();
        if (!cData.ok) { showToast(cData.error || '创建失败', 'error'); return; }
        showToast('目录已创建', 'ok');
      } else if (vData.status === 'empty') {
        var createEmpty = await showConfirm(
          '暂无签到数据',
          '该目录下没有找到签到数据文件，是否创建初始数据文件？\n\n' + path
        );
        if (createEmpty) {
          await fetch('/api/create-data-dirs', {
            method: 'POST', headers: authHeaders(),
            body: JSON.stringify({ path: path })
          });
          showToast('初始文件已创建', 'ok');
        }
      }
      // Step 2: Save settings
      var resp = await fetch('/api/settings', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ data_path: path })
      });
      var data = await resp.json();
      if (data.ok) {
        if (btn) { btn.textContent = '✓ 已保存，5秒后刷新...'; btn.style.background = 'var(--success)'; }
        try { await fetch('/api/restart', { method: 'POST', headers: authHeaders() }); } catch(e) {}
        setTimeout(function() { if (btn) { btn.textContent = '💾 保存并重启'; btn.style.background = ''; } }, 5000);
      } else {
        if (btn) { btn.textContent = '✗ 失败'; btn.style.background = 'var(--danger)'; }
        setTimeout(function() { if (btn) { btn.textContent = '💾 保存并重启'; btn.style.background = ''; } }, 2000);
      }
    } catch(e) {
      if (btn) { btn.textContent = '✗ 网络错误'; btn.style.background = 'var(--danger)'; }
      setTimeout(function() { if (btn) { btn.textContent = '💾 保存并重启'; btn.style.background = ''; } }, 2000);
    }
  };

  // Simple confirm dialog
  function showConfirm(title, msg) {
    return new Promise(function(resolve) {
      var ov = document.createElement('div');
      ov.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.55);z-index:9999;display:flex;align-items:center;justify-content:center;';
      var dlg = document.createElement('div');
      dlg.style.cssText = 'background:var(--card-bg,#fff);border:1px solid var(--border,#e5e7eb);border-radius:12px;padding:24px;max-width:420px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.4);';
      dlg.innerHTML = '<h3 style="margin:0 0 8px;color:var(--text);font-size:1.05rem;">' + title + '</h3>' +
        '<p style="margin:0 0 20px;color:var(--text-secondary,#6b7280);font-size:0.9rem;white-space:pre-wrap;word-break:break-all;">' + msg + '</p>' +
        '<div style="display:flex;justify-content:flex-end;gap:8px;">' +
        '<button id="_dlg-cancel" style="padding:6px 16px;border:1px solid var(--border);border-radius:6px;background:var(--admin-bg);color:var(--text);cursor:pointer;">取消</button>' +
        '<button id="_dlg-ok" style="padding:6px 16px;border:none;border-radius:6px;background:var(--primary,#3b82f6);color:#fff;cursor:pointer;">确认创建</button>' +
        '</div>';
      ov.appendChild(dlg); document.body.appendChild(ov);
      document.getElementById('_dlg-ok').onclick = function() { ov.remove(); resolve(true); };
      document.getElementById('_dlg-cancel').onclick = function() { ov.remove(); resolve(false); };
      ov.addEventListener('click', function(e) { if (e.target === ov) { ov.remove(); resolve(false); } });
    });
  }

  function showToast(msg, type) {
    var t = document.createElement('div');
    t.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);padding:10px 24px;border-radius:8px;z-index:9999;font-size:0.9rem;color:#fff;' +
      (type === 'ok' ? 'background:#22c55e;' : 'background:#ef4444;');
    t.textContent = msg; document.body.appendChild(t);
    setTimeout(function() { t.remove(); }, 2500);
  }

  // ========== 保存设置 ==========

  async function saveAllSettings() {
    const s = collectSettingsFromForm();
    currentSettings = s;
    try {
      const resp = await fetch('/api/settings', {
        method: 'POST', headers: authHeaders(), body: JSON.stringify(s)
      });
      const data = await resp.json();
      const status = document.getElementById('save-status');
      if (data.ok) {
        status.textContent = '✓ 设置已保存';
        status.classList.add('visible');
      } else {
        status.textContent = '✗ 保存失败: ' + (data.error || '未知错误');
        status.classList.add('visible');
        status.style.color = '#ef4444';
        alert('保存失败: ' + (data.error || '请确认已登录为管理员'));
      }
      setTimeout(() => { status.classList.remove('visible'); status.style.color = ''; }, 3000);
    } catch (e) {
      alert('保存失败: 网络错误\n' + e.message);
    }
  }

  // ========== 数据统计 ==========

  async function loadStats() {
    try {
      var resp = await fetch('/api/status');
      var data = await resp.json();
      var today = data.today_count || 0;
      var total = data.record_count || 0;
      var ngrok = data.ngrok_url ? '外网已通' : '仅内网';
      var status = data.status || '运行中';
      // 同时获取详细统计
      var statsResp = await fetch('/api/stats?period=all').catch(function(){return null});
      var statsData = statsResp ? await statsResp.json() : {};
      var thisWeek = statsData.this_week || 0;
      var thisMonth = statsData.this_month || 0;

      var cards = document.getElementById('stat-cards');
      if (cards) cards.innerHTML =
        '<div class="sc-item sc-today"><div class="sc-icon-wrap"><span class="sc-icon">📅</span><span class="sc-pulse"></span></div><div class="sc-body"><div class="sc-val" data-target="'+today+'">0</div><div class="sc-lbl">今日签到</div></div><div class="sc-bar" style="height:'+Math.min(today*8,40)+'px"></div></div>'+
        '<div class="sc-item sc-total"><div class="sc-icon-wrap"><span class="sc-icon">👥</span><span class="sc-pulse"></span></div><div class="sc-body"><div class="sc-val" data-target="'+total+'">0</div><div class="sc-lbl">总记录数</div></div><div class="sc-bar" style="height:'+Math.min(total*0.4,40)+'px"></div></div>'+
        '<div class="sc-item sc-week"><div class="sc-icon-wrap"><span class="sc-icon">📆</span><span class="sc-pulse"></span></div><div class="sc-body"><div class="sc-val" data-target="'+thisWeek+'">0</div><div class="sc-lbl">本周签到</div></div><div class="sc-bar" style="height:'+Math.min(thisWeek*5,40)+'px"></div></div>'+
        '<div class="sc-item sc-month"><div class="sc-icon-wrap"><span class="sc-icon">📊</span><span class="sc-pulse"></span></div><div class="sc-body"><div class="sc-val" data-target="'+thisMonth+'">0</div><div class="sc-lbl">本月签到</div></div><div class="sc-bar" style="height:'+Math.min(thisMonth*2,40)+'px"></div></div>';
      // 数字滚动动画
      setTimeout(function(){
        document.querySelectorAll('.sc-val').forEach(function(el){
          var target=parseInt(el.dataset.target)||0;
          var cur=0,step=target>60?Math.ceil(target/30):1;
          var timer=setInterval(function(){
            cur+=step;if(cur>=target){cur=target;clearInterval(timer)}
            el.textContent=cur;
          },20);
        });
      },100);

      // 填充路径信息
      var dirEl=document.getElementById('cfg-excel-dir');
      var locEl=document.getElementById('cfg-location');
      if(dirEl&&!dirEl.value)dirEl.value='加载中...';
      if(locEl)locEl.value=statsData.location||'';
      try{
        var mr=await fetch('/api/monitor');
        var md=await mr.json();
        if(dirEl)dirEl.value=(md.excel_dir&&md.excel_dir.path)||dirEl.value;
      var locInp=document.getElementById('cfg-location-input');
      if(locInp&&!locInp.value&&statsData.location)locInp.value=statsData.location;
      // 同步状态
      var syncDot=document.getElementById('sync-dot');
      var syncText=document.getElementById('sync-text');
      var syncItems=document.getElementById('sync-items');
      var roleEl=document.getElementById('machine-role');
      var cardStatusEl=document.getElementById('card-reader-status');
      var multiSyncEl=document.getElementById('multi-sync-status');
      var cr = md.card_reader || {};
      if(syncDot&&md.sync){
        if(md.sync.enabled){
          syncDot.style.background='#22c55e';syncDot.style.boxShadow='0 0 8px #22c55e';
          syncText.textContent='多机同步已启用 · '+md.sync.provider;
          syncItems.textContent='共享：'+(md.sync.shared_items||[]).join(' · ');
          syncText.style.color='#22c55e';
        }else{
          syncDot.style.background='#f59e0b';syncDot.style.boxShadow='0 0 6px #f59e0b';
          syncText.textContent='仅本机存储 · 未检测到同步目录';
          syncItems.textContent='安装百度网盘并开启同步即可多机共享';
          syncText.style.color='#f59e0b';
        }
      }
      // 多机联动状态
      if(multiSyncEl){
        try{
          var ssResp=await fetch('/api/sync-status');
          var ss=await ssResp.json();
          multiSyncEl.textContent='联动中 · ID:'+ss.machine_id+(ss.pending_events>0?' · 待处理:'+ss.pending_events:'');
          multiSyncEl.style.color=ss.pending_events>0?'#f59e0b':'#22c55e';
        }catch(e){}
      }
      // 本机角色 + 读卡器状态
      if(roleEl){
        if(cr.enabled){
          roleEl.textContent = '🟢 刷卡主机'; roleEl.style.color='#22c55e';
          if(cardStatusEl) cardStatusEl.textContent = cr.online ? '· 读卡器在线' : '· 读卡器待连接';
        }else{
          roleEl.textContent = '🔵 同步终端'; roleEl.style.color='#3b82f6';
          if(cardStatusEl) cardStatusEl.textContent = '· 仅手动签到';
        }
      }
      // 按钮状态
      var hostBtn = document.getElementById('btn-card-host');
      var termBtn = document.getElementById('btn-card-terminal');
      var roleText = document.getElementById('machine-role-text');
      if(hostBtn&&termBtn){
        if(cr.enabled){
          hostBtn.style.background='#22c55e';termBtn.style.background='';
          if(roleText)roleText.textContent='刷卡主机';
        }else{
          hostBtn.style.background='';termBtn.style.background='#3b82f6';
          if(roleText)roleText.textContent='同步终端';
        }
      }
      }catch(e){}
    } catch(e){}
    if(typeof loadPeople==='function')loadPeople();
    if(typeof window._loadRecycle==='function')window._loadRecycle();
  }

  // ========== 用户管理 ==========

  async function loadUsers() {
    try {
      const resp = await fetch('/api/users', { headers: authHeaders() });
      const data = await resp.json();
      if (!data.ok) return;
      const container = document.getElementById('user-list');
      if (!container) return;
      container.innerHTML = Object.entries(data.users).map(([u, info]) =>
        '<div class="dm-card" style="margin-bottom:0.3rem;padding:0">'+
        '<div style="display:flex;justify-content:space-between;align-items:center;padding:0.55rem 0.8rem;">'+
        '<div><strong>'+u+'</strong><span style="color:#6b7280;margin-left:0.5rem;font-size:0.82rem;">'+escHtml(info.name||'')+' · '+(info.role==='admin'?'管理员':'普通用户')+'</span></div>'+
        (u!=='admin'?'<button class="btn btn-danger-outline btn-sm" onclick="window._deleteUser(\''+u+'\')">删除</button>':'<span style="color:#9ca3af;font-size:0.75rem;">系统管理员</span>')+
        '</div></div>').join('');
    } catch (e) { /* ignore */ }
    // 同时加载人员列表和回收站
    if (typeof loadPeople === 'function') loadPeople();
    if (typeof window._loadRecycle === 'function') window._loadRecycle();
  }

  async function _addUser() {
    const u = getVal('new-username'), p = getVal('new-password'), n = getVal('new-displayname'), r = getVal('new-role');
    if (!u || !p) { alert('用户名和密码不能为空'); return; }
    if (p.length < 6) { alert('密码至少6位'); return; }
    try {
      const resp = await fetch('/api/users', { method: 'POST', headers: authHeaders(), body: JSON.stringify({ username: u, password: p, name: n, role: r }) });
      const data = await resp.json();
      if (data.ok) {
        setVal('new-username', ''); setVal('new-password', ''); setVal('new-displayname', '');
        loadUsers();
      } else { alert('添加失败: ' + (data.error || '')); }
    } catch (e) { alert('请求失败'); }
  }

  async function _deleteUser(username) {
    if (!(await cfConfirm('确定删除用户 ' + username + '？'))) return;
    try {
      const resp = await fetch('/api/users/' + username, { method: 'DELETE', headers: authHeaders() });
      const data = await resp.json();
      if (data.ok) { loadUsers(); } else { alert('删除失败: ' + (data.error || '')); }
    } catch (e) { alert('请求失败'); }
  }

  // ========== 导出到全局 ==========

  window.saveAllSettings = saveAllSettings;
  window.removeLogo = removeLogo;
  window.addUser = _addUser;
  window.deleteUser = _deleteUser;
  window._deleteUser = _deleteUser;
  window._changePwd = async function() {
    var u = document.getElementById('pwd-user')?.value?.trim();
    var p = document.getElementById('pwd-new')?.value?.trim();
    if (!u || !p) { alert('请输入用户名和新密码'); return; }
    if (p.length < 6) { alert('密码至少6位'); return; }
    if (!(await cfConfirm('确定修改用户 ' + u + ' 的密码？'))) return;
    try {
      var resp = await fetch('/api/change_password', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ username: u, new_password: p })
      });
      var data = await resp.json();
      alert(data.message || (data.ok ? '密码已修改' : '修改失败'));
      if (data.ok) {
        var uEl=document.getElementById('pwd-user');if(uEl)uEl.value='';
        var pEl=document.getElementById('pwd-new');if(pEl)pEl.value='';
      }
    } catch(e) { alert('请求失败'); }
  };

  window._adminLogin = doLogin;

  async function _manualSignin() {
    const name = getVal('manual-name');
    const id_number = getVal('manual-id') || '';
    if (!name) { alert('请输入姓名'); return; }
    try {
      const resp = await fetch('/api/manual_signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, id_number })
      });
      const data = await resp.json();
      const el = document.getElementById('manual-result');
      if (data.ok) {
        el.textContent = `✓ ${name} 签到成功！时间: ${data.record.sign_time}`;
        el.style.display = 'block';
        el.style.color = '#16a34a';
        setVal('manual-name', '');
        setVal('manual-id', '');
        setTimeout(() => { el.style.display = 'none'; }, 3000);
      } else {
        el.textContent = '✗ ' + (data.error || '签到失败');
        el.style.display = 'block';
        el.style.color = '#ef4444';
      }
    } catch (e) {
      alert('签到失败: ' + e.message);
    }
  }
  window._manualSignin = _manualSignin;

  // ===== Logo 裁剪 =====
  let cropScale = 1, cropX = 0, cropY = 0, cropDragging = false, cropStart = {}, cropImg = null;

  window._openCrop = function() {
    const logoImg = document.getElementById('logo-img');
    if (!logoImg || !logoImg.src || logoImg.style.display === 'none') { alert('请先上传图片'); return; }
    cropImg = document.getElementById('crop-image');
    // 用原始URL（去掉?v=参数）
    const src = logoImg.src.replace(/\?v=.*/, '');
    cropImg.src = src;
    document.getElementById('crop-preview-img').src = src;
    cropScale = 1; cropX = 0; cropY = 0;
    setTimeout(() => {
      cropImg.style.transform = 'translate(0px, 0px) scale(1)';
    }, 200);
    document.getElementById('crop-zoom').value = 100;
    document.getElementById('crop-zoom-val').textContent = '100%';
    document.getElementById('crop-modal').style.display = 'flex';
  };

  window._cropReset = function() {
    cropScale = 1; cropX = 0; cropY = 0;
    if (cropImg) cropImg.style.transform = 'translate(0px, 0px) scale(1)';
    document.getElementById('crop-zoom').value = 100;
    document.getElementById('crop-zoom-val').textContent = '100%';
  };

  window._cropZoom = function(val) {
    cropScale = parseInt(val) / 100;
    if (cropImg) cropImg.style.transform = `translate(${cropX}px, ${cropY}px) scale(${cropScale})`;
    document.getElementById('crop-zoom-val').textContent = val + '%';
  };

  function initCropDrag() {
    const vp = document.getElementById('crop-viewport');
    if (!vp) return;
    vp.addEventListener('mousedown', (e) => {
      cropDragging = true; cropStart = { x: e.clientX - cropX, y: e.clientY - cropY }; e.preventDefault();
    });
    document.addEventListener('mousemove', (e) => {
      if (!cropDragging || !cropImg) return;
      cropX = e.clientX - cropStart.x; cropY = e.clientY - cropStart.y;
      cropImg.style.transform = `translate(${cropX}px, ${cropY}px) scale(${cropScale})`;
    });
    document.addEventListener('mouseup', () => { cropDragging = false; });
    vp.addEventListener('touchstart', (e) => {
      cropDragging = true; cropStart = { x: e.touches[0].clientX - cropX, y: e.touches[0].clientY - cropY };
    });
    document.addEventListener('touchmove', (e) => {
      if (!cropDragging || !cropImg) return;
      cropX = e.touches[0].clientX - cropStart.x; cropY = e.touches[0].clientY - cropStart.y;
      cropImg.style.transform = `translate(${cropX}px, ${cropY}px) scale(${cropScale})`;
    });
    document.addEventListener('touchend', () => { cropDragging = false; });
  }

  window._cropSave = function() {
    if (!cropImg || !cropImg.complete) { alert('图片加载中，请稍候'); return; }
    // 直接用原图重新上传（裁剪参数只做视觉参考，原图保持完整质量）
    const canvas = document.createElement('canvas');
    const nw = cropImg.naturalWidth || 400;
    const nh = cropImg.naturalHeight || 200;
    canvas.width = Math.min(nw, 800);
    canvas.height = Math.round(canvas.width * (nh / nw));
    const ctx = canvas.getContext('2d');
    ctx.drawImage(cropImg, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async (blob) => {
      if (!blob || blob.size < 100) { alert('裁剪失败，图片数据异常'); return; }
      const fd = new FormData(); fd.append('file', blob, 'logo.png');
      try {
        const h = getToken() ? { 'X-Auth-Token': getToken() } : {};
        const resp = await fetch('/api/upload/logo', { method:'POST', headers:h, body:fd });
        const d = await resp.json();
        if (d.ok) {
          const newUrl = d.logo_url + '?v=' + Date.now();
          showLogo(newUrl);
          if (currentSettings.display) currentSettings.display.logo_url = d.logo_url;
          document.getElementById('crop-modal').style.display = 'none';
          document.getElementById('save-status').textContent = '✓ Logo 已保存，请 Ctrl+S 保存设置';
          document.getElementById('save-status').classList.add('visible');
          setTimeout(() => document.getElementById('save-status').classList.remove('visible'), 3000);
        } else { alert('上传失败: '+(d.error||'')); }
      } catch(e) { alert('上传失败: '+e.message); }
    }, 'image/png');
  };

  async function _clearRecords(mode) {
    var label = mode === 'all' ? '全部' : '今日';
    if (!(await cfConfirm('⚠️ 即将清除' + label + '签到记录，请输入管理员密码确认'))) return;
    var pwd = await verifyAdmin('清除' + label + '记录需要验证管理员身份');
    if (!pwd) return;
    try {
      var check = await fetch('/api/verify_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pwd })
      });
      var checkData = await check.json();
      if (!checkData.ok) { alert('密码错误，操作取消'); return; }
      const resp = await fetch('/api/clear_records', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ mode })
      });
      const data = await resp.json();
      alert(data.message || (data.ok ? '操作完成' : '操作失败'));
      loadStats();
    } catch (e) { alert('请求失败'); }
  }
  window._clearToday = () => _clearRecords('today');
  window._clearAll = () => _clearRecords('all');

  // 跑马灯表单
  function loadMarquees() {
    const mqs = currentSettings.marquees || [];
    const names = ['叫号框下方', '等待队列上方', '已叫号/超时上方'];
    const container = document.getElementById('marquee-forms');
    if (!container) return;
    container.innerHTML = names.map((name, i) => {
      const m = mqs[i] || { enabled: false, text: '', size: '0.8rem', color: '#4f8fff', speed: 12, delay: 0, gradient: false };
      return '<div class="dm-card" style="margin-bottom:0.5rem">'+
        '<div class="dm-card-hd"><span class="dm-card-icon">📟</span><h3>位置'+(i+1)+'：'+name+'</h3>'+
        '<label class="checkbox-label" style="margin-right:0.8rem"><input type="checkbox" id="mq-enabled-'+(i)+'" '+(m.enabled?'checked':'')+'> 启用</label>'+
        '<button class="dm-collapse" onclick="this.closest(\'.dm-card\').classList.toggle(\'collapsed\')">−</button></div>'+
        '<div class="dm-card-bd">'+
        '<div class="dm-field" style="margin-bottom:0.5rem"><label>滚动文字</label><input type="text" id="mq-text-'+i+'" class="dm-input" value="'+escAttr1(m.text)+'" style="width:100%"></div>'+
        '<div class="dm-row">'+
        '<div class="dm-field"><label>字体大小</label><select id="mq-size-'+i+'" class="dm-input" style="width:100%">'+['0.65rem','0.7rem','0.75rem','0.8rem','0.9rem','1rem','1.1rem','1.2rem'].map(s => '<option value="'+s+'" '+(m.size===s?'selected':'')+'>'+s+'</option>').join('')+'</select></div>'+
        '<div class="dm-field"><label>滚动速度</label><select id="mq-speed-'+i+'" class="dm-input" style="width:100%">'+[{v:120,t:'极慢'},{v:80,t:'慢'},{v:50,t:'中'},{v:30,t:'快'},{v:15,t:'极快'}].map(o => '<option value="'+o.v+'" '+(m.speed==o.v?'selected':'')+'>'+o.t+' ('+o.v+'秒)</option>').join('')+'</select></div>'+
        '<div class="dm-field"><label>延迟(秒)</label><input type="number" id="mq-delay-'+i+'" class="dm-input" value="'+(m.delay||0)+'" min="0" max="60" step="0.5" style="width:100%"></div>'+
        '</div>'+
        '<div class="dm-row" style="margin-top:0.4rem">'+
        '<div class="dm-field"><label>文字颜色</label><div class="color-input-row"><input type="color" id="mq-color-'+i+'" value="'+(m.color||'#4f8fff')+'"><input type="text" id="mq-color-'+i+'-txt" value="'+(m.color||'#4f8fff')+'" maxlength="7"></div></div>'+
        '<div class="dm-field"><label class="checkbox-label"><input type="checkbox" id="mq-gradient-'+i+'" '+(m.gradient?'checked':'')+'> 渐变效果</label></div>'+
        '</div></div></div>';
    }).join('');

    // 颜色同步
    for (let i = 0; i < 3; i++) {
      const ce = document.getElementById('mq-color-'+i), te = document.getElementById('mq-color-'+i+'-txt');
      if (!ce || !te) continue;
      ce.addEventListener('input', () => { te.value = ce.value; });
      te.addEventListener('change', () => { if (/^#[0-9a-fA-F]{6}$/.test(te.value)) ce.value = te.value; });
    }
  }
  function escAttr1(s) { return String(s||'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  // 人员管理（已合并到数据面板）
  var _allPeople=[];
  async function loadPeople() {
    try {
      const resp = await fetch('/api/signins');
      _allPeople = await resp.json();
      _allPeople.sort((a,b) => b.sign_time.localeCompare(a.sign_time));
      // 填充地点下拉
      var locs={};
      _allPeople.forEach(r=>{if(r.location)locs[r.location]=1});
      var ppLoc=document.getElementById('pp-loc');
      if(ppLoc&&!ppLoc.dataset.filled){ppLoc.innerHTML='<option value="">全部地点</option>'+Object.keys(locs).map(l=>'<option value="'+escAttr(l)+'">'+l+'</option>').join('');ppLoc.dataset.filled='1';}
      _renderPeople(_allPeople);
    } catch(e) {}
  }

  window._filterPeople=function(){
    var q=(document.getElementById('pp-search')?.value||'').toLowerCase();
    var loc=document.getElementById('pp-loc')?.value||'';
    var st=document.getElementById('pp-status')?.value||'';
    var recs=_allPeople.filter(r=>{
      if(q&&r.name.toLowerCase().indexOf(q)<0)return false;
      if(loc&&r.location!==loc)return false;
      if(st&&r.status!==st)return false;
      return true;
    });
    _renderPeople(recs);
  };

  window._selectByStatus=function(st){
    document.querySelectorAll('.people-cb').forEach(cb=>{cb.checked=false});
    document.querySelectorAll('.people-cb').forEach(cb=>{
      if(cb.dataset.status===st)cb.checked=true;
    });
    _updateSelectedCount();
  };

  function _updateSelectedCount(){
    var cbs=document.querySelectorAll('.people-cb:checked');
    var el=document.getElementById('pp-selected-count');
    if(el)el.textContent=cbs.length?'已选 '+cbs.length+' 人':'';
  }

  window._showSigninForm=function(){
    var f=document.getElementById('quick-signin-form');
    if(!f)return;
    var isOpen=f.style.display==='flex';
    f.style.display=isOpen?'none':'flex';
    if(!isOpen){document.getElementById('manual-name')?.focus();}
  };

  function _renderPeople(recs){
    var container=document.getElementById('people-list');
    var countEl=document.getElementById('people-count');
    if(countEl)countEl.textContent='共 '+recs.length+' 人';
    if(!container)return;
    container.innerHTML=recs.map(r=>`
      <tr>
        <td><input type="checkbox" class="people-cb" data-seq="${r.seq}" data-loc="${escAttr(r.location)}" data-status="${escAttr(r.status||'等待中')}" onclick="event.stopPropagation();_updateSelectedCount()"></td>
        <td>${r.seq}</td>
        <td><strong>${escHtml(r.name)}</strong></td>
        <td style="font-variant-numeric:tabular-nums;">${r.id_number||'--'}</td>
        <td style="font-variant-numeric:tabular-nums;font-size:0.8rem;">${r.sign_time}</td>
        <td>${escHtml(r.location)}</td>
        <td><span class="tg tg-${r.status==='已完成'?'ok':r.status==='已过号'?'warn':r.status==='已叫号'?'ok':'ok'}">${r.status||'等待中'}</span></td>
        <td>
          <button class="btn btn-secondary" style="font-size:0.7rem;padding:0.2rem 0.4rem;" onclick="window._editRecord(${r.seq},'${escAttr(r.location)}','${escAttr(r.name)}','${escAttr(r.id_number||'')}')">编辑</button>
          <button class="btn btn-danger-outline" style="font-size:0.7rem;padding:0.2rem 0.4rem;" onclick="window._delOne(${r.seq},'${escAttr(r.location)}')">删除</button>
        </td>
      </tr>`).join('');
    _updateSelectedCount();
  }

  function escAttr(s) { return String(s||'').replace(/'/g,"\\'").replace(/"/g,'&quot;'); }
  function escHtml(s) { const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

  window._toggleSelectAll = function(cb) {
    document.querySelectorAll('.people-cb').forEach(c => c.checked = cb.checked);
  };

  window._deleteSelected = async function() {
    const cbs = document.querySelectorAll('.people-cb:checked');
    if (!cbs.length) { alert('请先选择要删除的记录'); return; }
    if (!(await cfConfirm('确定删除选中的 ' + cbs.length + ' 条记录？'))) return;
    const targets = Array.from(cbs).map(cb => ({
      seq: parseInt(cb.dataset.seq),
      location: cb.dataset.loc
    }));
    try {
      const resp = await fetch('/api/delete_records', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ targets })
      });
      const data = await resp.json();
      alert(data.message || (data.ok ? '删除成功' : '删除失败'));
      loadPeople();
    } catch(e) { alert('请求失败'); }
  };

  window._delOne = async function(seq, location) {
    if (!(await cfConfirm('确定删除该记录？'))) return;
    try {
      const resp = await fetch('/api/delete_records', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ targets: [{seq, location}] })
      });
      const data = await resp.json();
      alert(data.message || '已删除');
      loadPeople();
    } catch(e) { alert('请求失败'); }
  };

  window._editRecord = function(seq, location, name, id_number) {
    document.getElementById('edit-seq').value = seq;
    document.getElementById('edit-loc').value = location;
    document.getElementById('edit-name').value = name;
    document.getElementById('edit-id').value = id_number;
    document.getElementById('edit-modal').style.display = 'flex';
  };

  window._saveEdit = async function() {
    const seq = parseInt(document.getElementById('edit-seq').value);
    const location = document.getElementById('edit-loc').value;
    const name = document.getElementById('edit-name').value.trim();
    const id_number = document.getElementById('edit-id').value.trim();
    if (!name) { alert('姓名不能为空'); return; }
    try {
      const resp = await fetch('/api/update_record', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ seq, location, name, id_number })
      });
      const data = await resp.json();
      if (data.ok) {
        document.getElementById('edit-modal').style.display = 'none';
        loadPeople();
      } else { alert('保存失败: ' + (data.error||'')); }
    } catch(e) { alert('请求失败'); }
  };

  // ===== 备份与回收站 =====
  window._manualBackup = async function() {
    try {
      var resp = await fetch('/api/backup', { method: 'POST', headers: authHeaders() });
      var data = await resp.json();
      alert(data.message || '备份完成');
      window._loadRecycle();
    } catch(e) { alert('备份失败'); }
  };

  window._loadRecycle = async function() {
    var el = document.getElementById('recycle-list');
    if (!el) return;
    try {
      var resp = await fetch('/api/recycle');
      var data = await resp.json();
      if (!data.files || !data.files.length) {
        el.innerHTML = '<span style="color:#9ca3af;font-size:0.85rem;">回收站为空</span>';
        return;
      }
      var rows = [];
      for (var i = 0; i < data.files.length; i++) {
        var f = data.files[i];
        var safeName = f.name.replace(/'/g, "\\'");
        rows.push('<div style="display:flex;justify-content:space-between;align-items:center;padding:0.35rem 0.5rem;border-bottom:1px solid #f0f0f0;font-size:0.82rem;">'
          + '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="' + safeName + '">' + safeName + '</span>'
          + '<span style="color:#9ca3af;margin:0 0.5rem;white-space:nowrap;">' + f.size_kb + 'KB</span>'
          + '<button class="btn btn-secondary" onclick="window._restoreRecycle(\'' + safeName + '\')" style="font-size:0.7rem;padding:0.15rem 0.4rem;margin-right:0.2rem;">恢复</button>'
          + '<button class="btn btn-danger-outline" onclick="window._delRecycle(\'' + safeName + '\')" style="font-size:0.7rem;padding:0.15rem 0.4rem;">删除</button>'
          + '</div>');
      }
      el.innerHTML = rows.join('');
    } catch(e) { el.innerHTML = '<span style="color:#ef4444;">加载失败</span>'; }
  };

  window._restoreRecycle = async function(filename) {
    if (!(await cfConfirm('确定恢复 ' + filename + ' ？'))) return;
    try {
      var resp = await fetch('/api/recycle/restore', { method:'POST', headers:authHeaders(), body:JSON.stringify({filename}) });
      var data = await resp.json();
      alert(data.message || '已恢复');
      window._loadRecycle();
    } catch(e) { alert('恢复失败'); }
  };

  window._delRecycle = async function(filename) {
    if (!(await cfConfirm('永久删除 ' + filename + ' ？'))) return;
    try {
      var resp = await fetch('/api/recycle/delete', { method:'POST', headers:authHeaders(), body:JSON.stringify({filename}) });
      var data = await resp.json();
      alert(data.message || '已删除');
      window._loadRecycle();
    } catch(e) { alert('删除失败'); }
  };

  window._clearRecycle = async function() {
    var pwd = await verifyAdmin('清空回收站需要验证管理员身份');
    if (!pwd) return;
    var check = await fetch('/api/verify_password', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({password:pwd}) });
    var cd = await check.json();
    if (!cd.ok) { alert('密码错误'); return; }
    try {
      await fetch('/api/recycle/delete', { method:'POST', headers:authHeaders(), body:JSON.stringify({mode:'all'}) });
      alert('回收站已清空');
      window._loadRecycle();
    } catch(e) { alert('清空失败'); }
  };

  window._saveBackupPath = async function() {
    var p = document.getElementById('cfg-backup-path');
    if (!p) return;
    var path = p.value.trim();
    if (!path) { alert('请输入备份路径'); return; }
    try {
      var resp = await fetch('/api/settings', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ backup: { path: path } })
      });
      var data = await resp.json();
      if (data.ok) {
        alert('备份路径已保存，重启服务后生效');
      } else {
        alert('保存失败: ' + (data.error || ''));
      }
    } catch(e) { alert('保存失败'); }
  };

  // ========== 百度云同步设置 ==========

  async function loadSyncSettings() {
    try {
      var resp = await fetch('/api/monitor', { headers: authHeaders() });
      var data = await resp.json();
      var dirInput = document.getElementById('cfg-sync-dir');
      var statusEl = document.getElementById('sync-dir-status');
      var pathDisplay = document.getElementById('sync-path-display');
      var syncDir = (data.sync && data.sync.data_dir) || '';
      if (dirInput) dirInput.value = syncDir;
      if (pathDisplay) pathDisplay.textContent = syncDir;
      if (statusEl) {
        if (syncDir) {
          statusEl.innerHTML = '✅ 数据统一存储在此目录，将百度云同步文件夹指向这里即可';
          statusEl.style.color = '#22c55e';
        } else {
          statusEl.innerHTML = '⚠️ 同步目录未就绪';
          statusEl.style.color = '#f59e0b';
        }
      }
    } catch(e) {}
  }

  window.saveMachineCfg = async function(enabled) {
    try {
      var resp = await fetch('/api/machine-settings', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ card_reader: { enabled: !!enabled } })
      });
      var data = await resp.json();
      if (data.ok) {
        var roleEl = document.getElementById('machine-role');
        var cardStatusEl = document.getElementById('card-reader-status');
        var roleText = document.getElementById('machine-role-text');
        var hostBtn = document.getElementById('btn-card-host');
        var termBtn = document.getElementById('btn-card-terminal');
        if (enabled) {
          if(roleEl){roleEl.textContent='🟢 刷卡主机';roleEl.style.color='#22c55e';}
          if(cardStatusEl)cardStatusEl.textContent='· 重启中...';
          if(roleText)roleText.textContent='刷卡主机';
          if(hostBtn)hostBtn.style.background='#22c55e';
          if(termBtn)termBtn.style.background='';
        } else {
          if(roleEl){roleEl.textContent='🔵 同步终端';roleEl.style.color='#3b82f6';}
          if(cardStatusEl)cardStatusEl.textContent='· 重启中...';
          if(roleText)roleText.textContent='同步终端';
          if(hostBtn)hostBtn.style.background='';
          if(termBtn)termBtn.style.background='#3b82f6';
        }
        // 自动重启服务
        try {
          var rr = await fetch('/api/restart', { method: 'POST', headers: authHeaders() });
          var rd = await rr.json();
          if (rd.ok) {
            // 等待3秒后自动刷新
            setTimeout(function(){ location.reload(); }, 3000);
          }
        } catch(e) {}
      } else {
        alert(data.error || '保存失败');
      }
    } catch(e) { alert('保存失败: ' + e.message); }
  };

  window.saveReaderMode = async function() {
    var mode = document.getElementById('cfg-reader-mode');
    var port = document.getElementById('cfg-com-port');
    if (!mode) return;
    try {
      await fetch('/api/machine-settings', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ card_reader: { reader_mode: mode.value, com_port: (port ? port.value.trim() : '') } })
      });
    } catch(e) {}
  };

  // 加载读卡模式设置
  (async function loadReaderMode(){
    try {
      var resp = await fetch('/api/machine-settings', { headers: authHeaders() });
      var data = await resp.json();
      var cr = data.card_reader || {};
      var modeEl = document.getElementById('cfg-reader-mode');
      var portEl = document.getElementById('cfg-com-port');
      if (modeEl && cr.reader_mode) modeEl.value = cr.reader_mode;
      if (portEl && cr.com_port) portEl.value = cr.com_port;
    } catch(e) {}
  })();

  // ====== 授权管理 ======
  var _licensePeriod = 1;
  var _licenseUnlocked = false;
  window._selectPeriod = function(m, el) {
    _licensePeriod = m;
    document.querySelectorAll('.license-period').forEach(function(b) { b.classList.remove('active'); });
    if (el) el.classList.add('active');
  };
  window._unlockLicense = function() {
    var pwd = document.getElementById('license-pwd').value;
    var errEl = document.getElementById('license-pwd-err');
    if (pwd === 'liaowei88') {
      _licenseUnlocked = true;
      document.getElementById('license-lock').style.display = 'none';
      document.getElementById('license-main').style.display = '';
      errEl.style.display = 'none';
    } else {
      errEl.textContent = '密码错误';
      errEl.style.display = '';
    }
  };
  window._genLicense = function() {
    if (!_licenseUnlocked) { window._unlockLicense(); return; }
    var mc = document.getElementById('license-machine').value.trim();
    var resEl = document.getElementById('license-result');
    var codeEl = document.getElementById('license-code');
    var infoEl = document.getElementById('license-info');
    var errEl = document.getElementById('license-err');
    resEl.style.display = 'none';
    errEl.style.display = 'none';
    if (!mc) { errEl.textContent = '请输入目标机器码'; errEl.style.display = ''; return; }
    var btn = event.target;
    btn.disabled = true; btn.textContent = '生成中...';
    fetch('/api/gen-license', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ machine_code: mc, months: _licensePeriod, password: 'liaowei88' })
    }).then(function(r) { return r.json(); }).then(function(d) {
      btn.disabled = false; btn.textContent = '生成授权码';
      if (d.ok) {
        codeEl.textContent = d.license;
        infoEl.textContent = '机器码: ' + d.machine_code + '  有效期: ' + d.expiry + ' (' + d.months + '个月)';
        resEl.style.display = '';
      } else {
        errEl.textContent = d.error || '生成失败';
        errEl.style.display = '';
      }
    }).catch(function(e) {
      btn.disabled = false; btn.textContent = '生成授权码';
      errEl.textContent = '网络错误: ' + e.message;
      errEl.style.display = '';
    });
  };

  // 切到授权面板时如果锁着就重置密码输入
  var _origNavClick = function(e) {
    var n = e.target.closest('.nav-item');
    if (!n) return;
    var tab = n.getAttribute('data-tab');
    if (tab === 'license' && !_licenseUnlocked) {
      document.getElementById('license-lock').style.display = '';
      document.getElementById('license-main').style.display = 'none';
      document.getElementById('license-pwd').value = '';
      document.getElementById('license-pwd-err').style.display = 'none';
    }
  };
  document.querySelector('.sidebar-nav').addEventListener('click', _origNavClick);

  document.addEventListener('DOMContentLoaded', init);
})();
