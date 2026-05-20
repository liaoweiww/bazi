/**
 * 报表页面逻辑 - 动态图表 + 人员名单 + 导出
 */
(function () {
  'use strict';

  let chartTrend, chartHourly, chartStatus, chartLocation;
  let allRecords = [];
  let settings = {};

  const $ = (id) => document.getElementById(id);

  // ===== 加载数据 =====
  async function init() {
    try {
      const [sr, rr] = await Promise.all([
        fetch('/api/settings'),
        fetch('/api/signins')
      ]);
      settings = await sr.json();
      allRecords = await rr.json();
    } catch(e) { console.error(e); }

    loadOverview();
    loadTable();
    loadCharts();
  }

  // ===== 概览卡片 =====
  async function loadOverview() {
    try {
      const r = await fetch('/api/stats?period=all');
      const d = await r.json();
      $('rp-cards').innerHTML = `
        <div class="rp-card"><div class="rp-card-val">${d.total||0}</div><div class="rp-card-lbl">总签到数</div></div>
        <div class="rp-card"><div class="rp-card-val green">${d.today||0}</div><div class="rp-card-lbl">今日签到</div></div>
        <div class="rp-card"><div class="rp-card-val">${d.this_week||0}</div><div class="rp-card-lbl">本周签到</div></div>
        <div class="rp-card"><div class="rp-card-val">${d.this_month||0}</div><div class="rp-card-lbl">本月签到</div></div>`;
      $('rp-location').textContent = d.location || '';
    } catch(e) {}
  }

  // ===== 人员名单 =====
  function loadTable() {
    const recs = [...allRecords].sort((a,b) => b.sign_time.localeCompare(a.sign_time));
    const dd = settings.display || {};
    const tt = settings.timer || {};
    const overMin = tt.remind_minutes || 40;
    const warnMin = tt.warning_minutes || 35;
    const cdMin = tt.countdown_minutes || 40;
    const cdOn = tt.countdown_enabled !== false;
    const mask = dd.mask_names !== false;

    // 填充地点筛选
    const locs = [...new Set(recs.map(r => r.location).filter(Boolean))];
    const locSel = $('table-loc-filter');
    locSel.innerHTML = '<option value="">全部地点</option>' +
      locs.map(l => `<option value="${l}">${l}</option>`).join('');

    renderTable(recs, dd, overMin, warnMin, cdMin, cdOn, mask);
  }

  function renderTable(recs, dd, overMin, warnMin, cdMin, cdOn, mask) {
    const tbody = $('table-body');
    if (!recs.length) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--text3);">暂无签到记录</td></tr>`;
      $('table-count').textContent = '共 0 人';
      return;
    }

    tbody.innerHTML = recs.map((r, i) => {
      const name = mask ? (r.name[0] + '*'.repeat(r.name.length-1)) : r.name;
      const min = Math.floor((new Date() - new Date(r.sign_time.replace(' ','T'))) / 60000);
      const remaining = cdMin - min;
      const status = min >= overMin ? ['bad','已超时'] : min >= warnMin ? ['warn','即将超时'] : ['ok','正常'];
      const cdText = cdOn ? (remaining <= 0 ? '已超时' : `剩余${remaining}分钟`) : '--';
      const idShow = r.id_number && r.id_number !== '手动录入' ? r.id_number : '--';

      return `<tr>
        <td>${i+1}</td>
        <td>${esc(name)}</td>
        <td style="font-variant-numeric:tabular-nums">${idShow}</td>
        <td>${r.sign_time}</td>
        <td>${min<0?'--':min+'分钟'}</td>
        <td style="color:${remaining<=0?'var(--red)':remaining<=10?'var(--yellow)':'var(--green)'}">${cdText}</td>
        <td>${esc(r.location)}</td>
        <td><span class="tag-sm tag-${status[0]}">${status[1]}</span></td>
      </tr>`;
    }).join('');

    $('table-count').textContent = `共 ${recs.length} 人`;
    window._allRecs = recs;
  }

  function esc(s) { const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

  // ===== 搜索/筛选 =====
  window.filterTable = function() {
    const q = ($('table-search').value || '').toLowerCase();
    const loc = $('table-loc-filter').value;
    const dd = settings.display || {};
    const tt = settings.timer || {};
    let recs = allRecords;
    if (q) recs = recs.filter(r => r.name.toLowerCase().includes(q));
    if (loc) recs = recs.filter(r => r.location === loc);
    recs.sort((a,b) => b.sign_time.localeCompare(a.sign_time));
    renderTable(recs, dd, tt.remind_minutes||40, tt.warning_minutes||35, tt.countdown_minutes||40, tt.countdown_enabled!==false, dd.mask_names!==false);
  };

  // ===== 导出Excel =====
  window.exportExcel = function() {
    const recs = window._allRecs || allRecords;
    if (!recs.length) { alert('无数据可导出'); return; }

    // 构建CSV
    const BOM = '﻿';
    const headers = ['序号','姓名','身份证号','签到时间','签到地点','状态'];
    const rows = recs.map((r,i) => [
      i+1,
      r.name,
      r.id_number || '',
      r.sign_time,
      r.location || '',
      r.status || '等待中'
    ]);
    const csv = BOM + headers.join(',') + '\n' +
      rows.map(r => r.map(c => '"' + String(c).replace(/"/g,'""') + '"').join(',')).join('\n');

    const blob = new Blob([csv], {type:'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `签到记录_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ===== 动态图表 =====
  async function loadCharts() {
    const period = $('period-select').value;
    try {
      const r = await fetch(`/api/stats?period=${period}`);
      const d = await r.json();

      const labels = d.labels || [];
      const values = d.values || [];
      const maxVal = Math.max(...values, 1);

      // 趋势柱状图
      const ctx1 = $('chart-trend').getContext('2d');
      if (chartTrend) chartTrend.destroy();
      chartTrend = new Chart(ctx1, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            data: values,
            backgroundColor: values.map(v =>
              v === maxVal ? 'rgba(0,214,143,0.8)' : `rgba(79,143,255,${0.35+(v/maxVal)*0.55})`
            ),
            borderColor: values.map(v => v === maxVal ? '#00d68f' : '#4f8fff'),
            borderWidth: 1,
            borderRadius: 8,
            borderSkipped: false,
          }]
        },
        options: {
          responsive:true, maintainAspectRatio:true,
          animation: { duration: 800, easing: 'easeOutQuart' },
          plugins: { legend:{display:false} },
          scales: {
            x: { ticks:{color:'#545d6b',font:{size:11}}, grid:{color:'rgba(255,255,255,0.04)'} },
            y: { ticks:{color:'#545d6b',stepSize:1}, grid:{color:'rgba(255,255,255,0.04)'}, beginAtZero:true }
          }
        }
      });

      // 时段折线
      const hours = d.hourly || [];
      const ctx2 = $('chart-hourly').getContext('2d');
      if (chartHourly) chartHourly.destroy();
      chartHourly = new Chart(ctx2, {
        type: 'line',
        data: {
          labels: hours.map(h => h.hour+':00'),
          datasets: [{
            data: hours.map(h => h.count),
            borderColor: '#4f8fff',
            backgroundColor: 'rgba(79,143,255,0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: hours.map(h => h.count>0 ? 5 : 2),
            pointBackgroundColor: hours.map(h => h.count>0 ? '#4f8fff' : '#545d6b'),
            pointBorderWidth: 0,
          }]
        },
        options: {
          responsive:true, maintainAspectRatio:true,
          animation: { duration: 1000, easing: 'easeInOutCubic' },
          plugins: { legend:{display:false} },
          scales: {
            x: { ticks:{color:'#545d6b',font:{size:10}}, grid:{color:'rgba(255,255,255,0.04)'} },
            y: { ticks:{color:'#545d6b',stepSize:1}, grid:{color:'rgba(255,255,255,0.04)'}, beginAtZero:true }
          }
        }
      });

      // 状态环图
      const statusData = d.status_dist || {};
      const ctx3 = $('chart-status').getContext('2d');
      if (chartStatus) chartStatus.destroy();
      chartStatus = new Chart(ctx3, {
        type: 'doughnut',
        data: {
          labels: Object.keys(statusData),
          datasets: [{
            data: Object.values(statusData),
            backgroundColor: ['#00d68f','#ffaa00','#ff3d57','#4f8fff'],
            borderWidth: 2,
            borderColor: '#161c26',
            hoverBorderWidth: 4,
          }]
        },
        options: {
          responsive:true, maintainAspectRatio:true,
          animation: { animateRotate:true, duration:1200, easing:'easeOutBounce' },
          plugins: {
            legend: { position:'bottom', labels:{color:'#8b95a5',font:{size:11},padding:16} }
          }
        }
      });

      // 地点雷达
      const locData = d.location_dist || {};
      const ctx4 = $('chart-location').getContext('2d');
      if (chartLocation) chartLocation.destroy();
      chartLocation = new Chart(ctx4, {
        type: 'polarArea',
        data: {
          labels: Object.keys(locData),
          datasets: [{
            data: Object.values(locData),
            backgroundColor: ['rgba(79,143,255,0.55)','rgba(108,92,231,0.55)','rgba(0,214,143,0.55)','rgba(255,170,0,0.55)'],
            borderWidth: 1,
            borderColor: '#161c26',
          }]
        },
        options: {
          responsive:true, maintainAspectRatio:true,
          animation: { animateRotate:true, duration:1000 },
          plugins: {
            legend: { position:'bottom', labels:{color:'#8b95a5',font:{size:11},padding:16} }
          },
          scales: { r:{ ticks:{display:false}, grid:{color:'rgba(255,255,255,0.06)'} } }
        }
      });

    } catch(e) { console.error(e); }
  }

  // ===== 启动 =====
  window.loadCharts = loadCharts;
  init();
})();
