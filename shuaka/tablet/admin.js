/**
 * 后台管理面板逻辑
 */
(function () {
  'use strict';

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
      .then(d => loadSettingsToForm(d))
      .catch(() => {});

    const dataTab = document.querySelector('[data-tab="data"]');
    if (dataTab) dataTab.addEventListener('click', loadStats);

    const usersTab = document.querySelector('[data-tab="users"]');
    if (usersTab) usersTab.addEventListener('click', loadUsers);
    const peopleTab = document.querySelector('[data-tab="people"]');
    if (peopleTab) peopleTab.addEventListener('click', loadPeople);
    const marqueeTab = document.querySelector('[data-tab="marquee"]');
    if (marqueeTab) marqueeTab.addEventListener('click', loadMarquees);

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveAllSettings();
      }
    });
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
    setVal('cfg-location', d.location || '');
    setVal('cfg-subtitle', d.subtitle || '');
    setVal('cfg-font-scale', d.font_scale || 'normal');
    setVal('cfg-refresh', d.refresh_interval || 5);
    setChecked('cfg-mask-names', d.mask_names !== false);
    setChecked('cfg-show-location', d.show_location !== false);
    setChecked('cfg-show-status', d.show_status !== false);

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

    setVal('cfg-remind-minutes', t.remind_minutes || 40);
    setVal('cfg-warning-minutes', t.warning_minutes || 35);
    setChecked('cfg-countdown-enabled', t.countdown_enabled !== false);
    setVal('cfg-countdown-minutes', t.countdown_minutes || 40);

    showLogo(d.logo_url || '');
    const logoUrl = d.logo_url || '';
    document.getElementById('btn-crop-logo').style.display = logoUrl ? '' : 'none';
  }

  function collectSettingsFromForm() {
    const d = currentSettings.display || {}, v = currentSettings.voice || {}, t = currentSettings.timer || {};
    d.title = getVal('cfg-title') || '签到叫号大屏';
    d.location = getVal('cfg-location');
    d.subtitle = getVal('cfg-subtitle');
    d.font_scale = getVal('cfg-font-scale');
    d.refresh_interval = parseInt(getVal('cfg-refresh')) || 5;
    d.mask_names = isChecked('cfg-mask-names');
    d.show_location = isChecked('cfg-show-location');
    d.show_status = isChecked('cfg-show-status');
    d.theme = selectedTheme;
    d.bg_primary = getVal('cfg-bg-primary');
    d.accent = getVal('cfg-accent');

    v.enabled = isChecked('cfg-voice-enabled');
    v.welcome_template = getVal('cfg-welcome-tpl');
    v.remind_template = getVal('cfg-remind-tpl');

    t.remind_minutes = parseInt(getVal('cfg-remind-minutes')) || 40;
    t.warning_minutes = parseInt(getVal('cfg-warning-minutes')) || 35;
    t.countdown_enabled = isChecked('cfg-countdown-enabled');
    t.countdown_minutes = parseInt(getVal('cfg-countdown-minutes')) || 40;

    // 跑马灯
    const mqs = [];
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

    return { display: d, voice: v, timer: t, themes: currentSettings.themes, marquees: mqs };
  }

  function setVal(id, val) { const el = document.getElementById(id); if (el) el.value = val; }
  function getVal(id) { const el = document.getElementById(id); return el ? el.value.trim() : ''; }
  function setChecked(id, v) { const el = document.getElementById(id); if (el) el.checked = v; }
  function isChecked(id) { const el = document.getElementById(id); return el ? el.checked : false; }

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
      const resp = await fetch('/api/status');
      const data = await resp.json();
      const cards = document.getElementById('stat-cards');
      if (cards) cards.innerHTML = `
        <div class="stat-card"><div class="stat-num">${data.today_count || 0}</div><div class="stat-label">今日签到</div></div>
        <div class="stat-card"><div class="stat-num">${data.record_count || 0}</div><div class="stat-label">总记录数</div></div>
        <div class="stat-card"><div class="stat-num">${data.ngrok_url ? '已连接' : '仅内网'}</div><div class="stat-label">外网状态</div></div>`;
    } catch (e) { /* ignore */ }
  }

  // ========== 用户管理 ==========

  async function loadUsers() {
    try {
      const resp = await fetch('/api/users', { headers: authHeaders() });
      const data = await resp.json();
      if (!data.ok) return;
      const container = document.getElementById('user-list');
      if (!container) return;
      container.innerHTML = Object.entries(data.users).map(([u, info]) => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:0.6rem 0.8rem;border:1px solid #e5e7eb;border-radius:6px;margin-bottom:0.4rem;background:#fafbfc;">
          <div><strong>${u}</strong><span style="color:#6b7280;margin-left:0.5rem;font-size:0.85rem;">${info.name || ''} · ${info.role === 'admin' ? '管理员' : '普通用户'}</span></div>
          ${u !== 'admin' ? `<button class="btn btn-danger-outline" onclick="window._deleteUser('${u}')" style="font-size:0.8rem;padding:0.3rem 0.7rem;">删除</button>` : '<span style="color:#6b7280;font-size:0.8rem;">系统管理员</span>'}
        </div>`).join('');
    } catch (e) { /* ignore */ }
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
    if (!confirm('确定删除用户 ' + username + '？')) return;
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
    try {
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
      return `<div class="mq-block">
        <div class="mq-block-header">
          <strong>位置${i+1}：${name}</strong>
          <label class="checkbox-label"><input type="checkbox" id="mq-enabled-${i}" ${m.enabled?'checked':''}> 启用</label>
        </div>
        <div class="form-group"><label>滚动文字</label><input type="text" id="mq-text-${i}" value="${escAttr1(m.text)}"></div>
        <div class="form-row">
          <div class="form-group flex-1"><label>字体大小</label><select id="mq-size-${i}">${['0.65rem','0.7rem','0.75rem','0.8rem','0.9rem','1rem','1.1rem','1.2rem'].map(s => `<option value="${s}" ${m.size===s?'selected':''}>${s}</option>`).join('')}</select></div>
          <div class="form-group flex-1"><label>滚动速度</label><select id="mq-speed-${i}">${[{v:120,t:'极慢'},{v:80,t:'慢'},{v:50,t:'中'},{v:30,t:'快'},{v:15,t:'极快'}].map(o => `<option value="${o.v}" ${m.speed==o.v?'selected':''}>${o.t} (${o.v}秒)</option>`).join('')}</select></div>
          <div class="form-group flex-1"><label>延迟启动(秒)</label><input type="number" id="mq-delay-${i}" value="${m.delay||0}" min="0" max="60" step="0.5"></div>
        </div>
        <div class="form-row">
          <div class="form-group flex-1">
            <label>文字颜色</label>
            <div class="color-input-row"><input type="color" id="mq-color-${i}" value="${m.color||'#4f8fff'}"><input type="text" id="mq-color-${i}-txt" value="${m.color||'#4f8fff'}" maxlength="7"></div>
          </div>
          <div class="form-group flex-1"><label class="checkbox-label"><input type="checkbox" id="mq-gradient-${i}" ${m.gradient?'checked':''}> 渐变效果</label></div>
        </div>
      </div>`;
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

  // 人员管理
  async function loadPeople() {
    try {
      const resp = await fetch('/api/signins');
      const data = await resp.json();
      const sorted = [...data].sort((a,b) => b.sign_time.localeCompare(a.sign_time));
      const container = document.getElementById('people-list');
      const countEl = document.getElementById('people-count');
      if (countEl) countEl.textContent = `共 ${sorted.length} 人`;
      if (!container) return;
      container.innerHTML = sorted.map(r => `
        <tr>
          <td><input type="checkbox" class="people-cb" data-seq="${r.seq}" data-loc="${escAttr(r.location)}"></td>
          <td>${r.seq}</td>
          <td>${escHtml(r.name)}</td>
          <td style="font-variant-numeric:tabular-nums;">${r.id_number||'--'}</td>
          <td>${r.sign_time}</td>
          <td>${escHtml(r.location)}</td>
          <td>${r.status||'等待中'}</td>
          <td>
            <button class="btn btn-secondary" style="font-size:0.75rem;padding:0.25rem 0.5rem;" onclick="window._editRecord(${r.seq},'${escAttr(r.location)}','${escAttr(r.name)}','${escAttr(r.id_number||'')}')">编辑</button>
            <button class="btn btn-danger-outline" style="font-size:0.75rem;padding:0.25rem 0.5rem;" onclick="window._delOne(${r.seq},'${escAttr(r.location)}')">删除</button>
          </td>
        </tr>`).join('');
    } catch(e) {}
  }

  function escAttr(s) { return String(s||'').replace(/'/g,"\\'").replace(/"/g,'&quot;'); }
  function escHtml(s) { const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

  window._toggleSelectAll = function(cb) {
    document.querySelectorAll('.people-cb').forEach(c => c.checked = cb.checked);
  };

  window._deleteSelected = async function() {
    const cbs = document.querySelectorAll('.people-cb:checked');
    if (!cbs.length) { alert('请先选择要删除的记录'); return; }
    if (!confirm(`确定删除选中的 ${cbs.length} 条记录？`)) return;
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
    if (!confirm('确定删除该记录？')) return;
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

  document.addEventListener('DOMContentLoaded', init);
})();
