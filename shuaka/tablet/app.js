/**
 * 签到叫号大屏 — 前端逻辑
 * 自动轮询 /api/signins，实时刷新签到列表
 * 加载 /api/settings 应用主题和显示偏好
 */

(function () {
  'use strict';

  // ---- 默认配置（会被后台设置覆盖） ----
  let config = {
    display: {
      title: '签到叫号大屏',
      subtitle: '',
      logo_url: '',
      theme: 'dark',
      font_scale: 'normal',
      refresh_interval: 5,
      mask_names: true,
      show_location: true,
      show_id_number: false,
      show_status: true
    },
    timer: { remind_minutes: 40, warning_minutes: 35 }
  };

  let REFRESH_INTERVAL = 5;
  let WARNING_MINUTES = 35;
  let OVERDUE_MINUTES = 40;

  // ---- DOM 引用 ----
  const $clock = document.getElementById('clock');
  const $tableBody = document.getElementById('table-body');
  const $statToday = document.getElementById('stat-today');
  const $statWaiting = document.getElementById('stat-waiting');
  const $statOverdue = document.getElementById('stat-overdue');
  const $statusDot = document.getElementById('status-dot');
  const $statusText = document.getElementById('status-text');
  const $countdown = document.getElementById('countdown');
  const $headerTitle = document.getElementById('header-title');
  const $headerSubtitle = document.getElementById('header-subtitle');
  const $headerLogo = document.getElementById('header-logo');
  const $pageTitle = document.getElementById('page-title');

  // ---- 状态 ----
  let records = [];
  let countdown = REFRESH_INTERVAL;

  // ---- 加载后台设置 ----
  async function loadSettings() {
    try {
      const resp = await fetch('/api/settings');
      if (!resp.ok) return;
      const data = await resp.json();
      config = deepMerge(config, data);

      const d = config.display || {};
      const t = config.timer || {};

      REFRESH_INTERVAL = d.refresh_interval || 5;
      WARNING_MINUTES = t.warning_minutes || 35;
      OVERDUE_MINUTES = t.remind_minutes || 40;

      applyDisplaySettings(d);
      applyTheme(d);
    } catch (e) {
      console.warn('无法加载后台设置，使用默认配置');
    }
  }

  function deepMerge(base, override) {
    const result = JSON.parse(JSON.stringify(base));
    for (const key of Object.keys(override || {})) {
      if (override[key] && typeof override[key] === 'object' && !Array.isArray(override[key])) {
        result[key] = deepMerge(result[key] || {}, override[key]);
      } else {
        result[key] = override[key];
      }
    }
    return result;
  }

  function applyDisplaySettings(d) {
    $headerTitle.textContent = d.title || '签到叫号大屏';
    $pageTitle.textContent = d.title || '签到叫号大屏';

    if (d.subtitle) {
      $headerSubtitle.textContent = d.subtitle;
    } else {
      $headerSubtitle.textContent = '';
    }

    if (d.logo_url) {
      $headerLogo.src = d.logo_url;
      $headerLogo.style.display = 'block';
    } else {
      $headerLogo.style.display = 'none';
    }
  }

  function applyTheme(d) {
    const root = document.documentElement;
    const themes = config.themes || {};
    const theme = themes[d.theme] || {};

    // 从预设主题或自定义颜色中获取
    const bgPrimary = d.bg_primary || theme.bg_primary || '#0f1923';
    const accent = d.accent || theme.accent || '#3b82f6';

    root.style.setProperty('--bg-primary', bgPrimary);
    root.style.setProperty('--bg-secondary', theme.bg_secondary || '#1a2736');
    root.style.setProperty('--bg-row', theme.bg_row || '#152230');
    root.style.setProperty('--bg-row-alt', theme.bg_row_alt || '#1a2a3a');
    root.style.setProperty('--text-primary', theme.text_primary || '#e8edf2');
    root.style.setProperty('--text-secondary', theme.text_secondary || '#8899aa');
    root.style.setProperty('--accent', accent);
    root.style.setProperty('--border', theme.border || '#1e3044');
    root.style.setProperty('--header-bg', theme.header_bg || '#0d1520');

    // 字体缩放
    const scales = { small: 0.85, normal: 1, large: 1.2, xlarge: 1.5 };
    root.style.setProperty('--font-scale', scales[d.font_scale] || 1);
  }

  // ---- 时钟 ----
  function updateClock() {
    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    $clock.textContent =
      `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ` +
      `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  }
  updateClock();
  setInterval(updateClock, 1000);

  // ---- 倒计时 ----
  setInterval(() => {
    countdown--;
    if (countdown < 0) countdown = REFRESH_INTERVAL;
    $countdown.textContent = countdown;
  }, 1000);

  // ---- 姓名脱敏 ----
  function maskName(name) {
    if (!name || name === '未知') return name;
    if (name.length <= 1) return name + '*';
    return name[0] + '*'.repeat(name.length - 1);
  }

  // ---- 计算等待时长 ----
  function getWaitMinutes(signTimeStr) {
    try {
      const signTime = new Date(signTimeStr.replace(' ', 'T'));
      const now = new Date();
      return Math.floor((now - signTime) / 60000);
    } catch (e) {
      return 0;
    }
  }

  function formatWait(minutes) {
    if (minutes < 0) return '--';
    if (minutes < 60) return minutes + ' 分钟';
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return h + ' 小时 ' + m + ' 分钟';
  }

  function getStatusInfo(minutes) {
    if (minutes >= OVERDUE_MINUTES) {
      return { cls: 'status-overdue', text: '超时请呼叫' };
    }
    if (minutes >= WARNING_MINUTES) {
      return { cls: 'status-warning', text: '即将超时' };
    }
    return { cls: 'status-normal', text: '等待中' };
  }

  // ---- 渲染表格 ----
  function renderTable(newRecords) {
    const d = config.display || {};
    const prevIds = new Set(records.map(r => r.seq + '|' + r.location));
    const newIds = new Set(newRecords.map(r => r.seq + '|' + r.location));
    const freshIds = new Set([...newIds].filter(id => !prevIds.has(id)));

    // 更新列可见性
    document.querySelectorAll('.col-idnum').forEach(el => {
      el.classList.toggle('show', d.show_id_number === true);
    });
    document.querySelectorAll('.col-loc').forEach(el => {
      el.classList.toggle('hide', d.show_location === false);
    });
    document.querySelectorAll('.col-status').forEach(el => {
      el.classList.toggle('hide', d.show_status === false);
    });

    $tableBody.innerHTML = '';

    const totalCols = 7;

    if (newRecords.length === 0) {
      $tableBody.innerHTML =
        `<tr class="empty-row"><td colspan="${totalCols}">暂无签到记录</td></tr>`;
    } else {
      const sorted = [...newRecords].sort(
        (a, b) => a.sign_time.localeCompare(b.sign_time)
      );

      sorted.forEach((r, idx) => {
        const minutes = getWaitMinutes(r.sign_time);
        const statusInfo = getStatusInfo(minutes);
        const isNew = freshIds.has(r.seq + '|' + r.location);
        const name = d.mask_names !== false ? maskName(r.name) : r.name;

        const tr = document.createElement('tr');
        if (isNew) tr.className = 'row-new';

        let rowHtml =
          `<td>${idx + 1}</td>` +
          `<td>${escHtml(name)}</td>`;

        // 身份证号列
        if (d.show_id_number) {
          rowHtml += `<td class="col-idnum show">${escHtml(r.id_number)}</td>`;
        } else {
          rowHtml += `<td class="col-idnum"></td>`;
        }

        rowHtml +=
          `<td>${r.sign_time.slice(11, 19)}</td>` +
          `<td>${formatWait(minutes)}</td>`;

        if (d.show_location !== false) {
          rowHtml += `<td class="col-loc">${escHtml(r.location)}</td>`;
        } else {
          rowHtml += `<td class="col-loc hide"></td>`;
        }

        if (d.show_status !== false) {
          rowHtml +=
            `<td class="col-status">` +
            `<span class="status-tag ${statusInfo.cls}">${statusInfo.text}</span></td>`;
        } else {
          rowHtml += `<td class="col-status hide"></td>`;
        }

        tr.innerHTML = rowHtml;
        $tableBody.appendChild(tr);
      });
    }

    // 更新统计
    const today = new Date().toISOString().slice(0, 10);
    const todayRecords = newRecords.filter(r => r.sign_time.startsWith(today));
    const overdueCount = newRecords.filter(
      r => getWaitMinutes(r.sign_time) >= OVERDUE_MINUTES
    ).length;

    $statToday.textContent = todayRecords.length;
    $statWaiting.textContent = newRecords.length;
    $statOverdue.textContent = overdueCount;

    records = newRecords;
  }

  function escHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  // ---- 数据获取 ----
  async function fetchData() {
    try {
      const resp = await fetch('/api/signins');
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const data = await resp.json();
      renderTable(data);
      setConnected(true);
    } catch (err) {
      console.error('获取签到数据失败:', err);
      setConnected(false);
    }
  }

  function setConnected(ok) {
    $statusDot.className = 'footer-dot ' + (ok ? 'connected' : 'disconnected');
    $statusText.textContent = ok ? '已连接' : '连接失败，正在重试...';
  }

  // ---- 定时刷新 ----
  function refreshLoop() {
    fetchData();
    countdown = REFRESH_INTERVAL;
  }

  setInterval(refreshLoop, REFRESH_INTERVAL * 1000);

  // ---- 页面可见性 ----
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      fetchData();
      countdown = REFRESH_INTERVAL;
    }
  });

  // ---- 全屏按钮 ----
  function addFullscreenBtn() {
    const btn = document.createElement('button');
    btn.className = 'fullscreen-btn';
    btn.innerHTML = '⛶';
    btn.title = '全屏显示';
    btn.addEventListener('click', () => {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        document.documentElement.requestFullscreen().catch(() => {});
      }
    });
    document.body.appendChild(btn);
  }

  // ---- 监听设置变化（长轮询） ----
  function watchSettings() {
    // 每 30 秒检查一次设置是否变化
    setInterval(async () => {
      try {
        const resp = await fetch('/api/settings');
        if (!resp.ok) return;
        const data = await resp.json();
        const newInterval = (data.display || {}).refresh_interval;
        if (newInterval && newInterval !== REFRESH_INTERVAL) {
          loadSettings(); // 重新加载所有设置
        }
      } catch (e) { /* ignore */ }
    }, 30000);
  }

  // ---- 启动 ----
  async function init() {
    await loadSettings();
    fetchData();
    addFullscreenBtn();
    watchSettings();

    // 定时刷新
    setInterval(refreshLoop, REFRESH_INTERVAL * 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
