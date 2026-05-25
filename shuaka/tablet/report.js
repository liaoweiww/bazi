/**
 * 报表页面逻辑 v2 — 动态图表 + 动画 + 搜索筛选
 */
(function(){
'use strict';

var chartTrend,chartHourly,chartStatus,chartLocation;
var allRecords=[];
var settings={};
var $=function(id){return document.getElementById(id)};

// ===== 全局梯度色板 =====
var GRADIENTS={
  blue:['rgba(79,143,255,0.7)','rgba(79,143,255,0.3)','rgba(79,143,255,0.05)'],
  green:['rgba(0,214,143,0.7)','rgba(0,214,143,0.3)','rgba(0,214,143,0.05)'],
  purple:['rgba(108,92,231,0.7)','rgba(108,92,231,0.3)','rgba(108,92,231,0.05)'],
  orange:['rgba(255,170,0,0.7)','rgba(255,170,0,0.3)','rgba(255,170,0,0.05)'],
  red:['rgba(255,61,87,0.7)','rgba(255,61,87,0.3)','rgba(255,61,87,0.05)'],
};

// ===== 数字滚动动画 =====
function animateValue(el,start,end,duration){
  var range=end-start;
  var stepTime=Math.abs(Math.floor(duration/range))||20;
  var current=start;
  var increment=end>start?1:-1;
  var timer=setInterval(function(){
    current+=increment;
    el.textContent=current;
    if(current===end)clearInterval(timer);
  },stepTime);
}

// ===== 初始化 =====
async function init(){
  try{
    var res=await Promise.all([fetch('/api/settings'),fetch('/api/signins')]);
    settings=await res[0].json();
    allRecords=await res[1].json();
  }catch(e){console.error(e)}
  loadOverview();
  loadTable();
  loadCharts();

  // 概览卡片点击
  $('rp-overview').addEventListener('click',function(e){
    var card=e.target.closest('.rp-ov-card');
    if(!card)return;
    var act=card.dataset.action;
    if(act==='scroll'){document.querySelector('.rp-table-panel').scrollIntoView({behavior:'smooth'});}
    else if(act==='today'){$('rp-search').value='';$('rp-loc-filter').value='';$('rp-status').value='';filterToday();}
    else{
      document.querySelectorAll('.rp-tab').forEach(function(b){b.classList.remove('active')});
      var tab=document.querySelector('.rp-tab[data-p="'+act+'"]');
      if(tab)tab.classList.add('active');
      loadCharts();
      document.querySelector('.rp-row').scrollIntoView({behavior:'smooth'});
    }
  });

  // 周期切换按钮
  document.querySelectorAll('.rp-tab').forEach(function(btn){
    btn.addEventListener('click',function(){
      document.querySelectorAll('.rp-tab').forEach(function(b){b.classList.remove('active')});
      btn.classList.add('active');
      loadCharts();
    });
  });
}

// ===== 概览卡片 =====
async function loadOverview(){
  try{
    var r=await fetch('/api/stats?period=all');
    var d=await r.json();
    var cards=[
      {icon:'👥',cls:'i1',val:d.total||0,lbl:'总签到数',action:'scroll'},
      {icon:'📅',cls:'i2',val:d.today||0,lbl:'今日签到',action:'today'},
      {icon:'📆',cls:'i3',val:d.this_week||0,lbl:'本周签到',action:'week'},
      {icon:'📊',cls:'i4',val:d.this_month||0,lbl:'本月签到',action:'month'}
    ];
    var html=cards.map(function(c,i){
      return '<div class="rp-ov-card rp-clickable" data-action="'+c.action+'" title="点击查看详情"><div class="rp-ov-icon '+c.cls+'">'+c.icon+'</div><div><div class="rp-ov-val" data-target="'+c.val+'">0</div><div class="rp-ov-lbl">'+c.lbl+'</div></div></div>';
    }).join('');
    $('rp-overview').innerHTML=html;
    // 数字滚动
    setTimeout(function(){
      document.querySelectorAll('.rp-ov-val').forEach(function(el){
        animateValue(el,0,parseInt(el.dataset.target)||0,600);
      });
    },200);
    $('rp-loc').textContent=d.location||'';
  }catch(e){}
}

// ===== 人员表格 =====
function loadTable(){
  var recs=[].concat(allRecords).sort(function(a,b){return b.sign_time.localeCompare(a.sign_time)});
  var dd=settings.display||{},tt=settings.timer||{};
  var overMin=tt.remind_minutes||40,warnMin=tt.warning_minutes||35;
  var cdMin=tt.countdown_minutes||40,cdOn=tt.countdown_enabled!==false;
  var mask=dd.mask_names!==false;
  // 地点筛选选项
  var locs={};
  recs.forEach(function(r){if(r.location)locs[r.location]=1});
  var locOpts='<option value="">全部地点</option>'+Object.keys(locs).map(function(l){return '<option value="'+l+'">'+l+'</option>'}).join('');
  var rpLoc=$('rp-loc-filter');if(rpLoc&&!rpLoc.dataset.filled){rpLoc.innerHTML=locOpts;rpLoc.dataset.filled='1';}
  renderTable(recs,mask,overMin,warnMin,cdMin,cdOn);
}

function renderTable(recs,mask,overMin,warnMin,cdMin,cdOn){
  var body=$('tbl-body');
  if(!recs.length){
    body.innerHTML='<tr><td colspan="8" style="text-align:center;padding:2.5rem;color:var(--text3);">暂无签到记录</td></tr>';
    $('tbl-count').textContent='共 0 人';
    return;
  }
  body.innerHTML=recs.map(function(r,i){
    var name=mask?r.name[0]+'*'.repeat(r.name.length-1):r.name;
    var min=Math.floor((new Date()-new Date(r.sign_time.replace(' ','T')))/60000);
    var remaining=cdMin-min;
    var stArr=min>=overMin?['bad','已超时']:min>=warnMin?['warn','即将超时']:['ok','正常'];
    var cdText=cdOn?(remaining<=0?'已超时':'剩余'+remaining+'分钟'):'--';
    var idShow=r.id_number&&r.id_number!=='手动录入'?r.id_number:'--';
    var cdColor=remaining<=0?'var(--red)':remaining<=10?'var(--yellow)':'var(--green)';
    return '<tr>'
      +'<td>'+(i+1)+'</td>'
      +'<td><strong>'+esc(name)+'</strong></td>'
      +'<td style="font-variant-numeric:tabular-nums">'+idShow+'</td>'
      +'<td style="font-variant-numeric:tabular-nums">'+r.sign_time+'</td>'
      +'<td>'+(min<0?'--':min+'分钟')+'</td>'
      +'<td style="color:'+cdColor+';font-weight:600">'+cdText+'</td>'
      +'<td>'+esc(r.location)+'</td>'
      +'<td><span class="tg tg-'+stArr[0]+'">'+stArr[1]+'</span></td>'
      +'</tr>';
  }).join('');
  $('tbl-count').textContent='共 '+recs.length+' 人';
  window._allRecs=recs;
}

function esc(s){var d=document.createElement('div');d.textContent=s||'';return d.innerHTML}

window.filterToday=function(){
  var today=new Date().toISOString().slice(0,10);
  $('rp-from').value=today;$('rp-to').value=today;
  $('rp-search').value='';$('rp-loc-filter').value='';$('rp-status').value='';
  filterTable();
  document.querySelector('.rp-table-panel').scrollIntoView({behavior:'smooth'});
};

// ===== 日期快捷 =====
window.quickRange=function(type){
  var now=new Date(),d=new Date(now);
  function fmt(d){return d.toISOString().slice(0,10)}
  if(type==='today'){$('rp-from').value=fmt(now);$('rp-to').value=fmt(now)}
  else if(type==='week'){var wd=now.getDay()||7;d.setDate(now.getDate()-wd+1);$('rp-from').value=fmt(d);$('rp-to').value=fmt(now)}
  else if(type==='month'){$('rp-from').value=fmt(new Date(now.getFullYear(),now.getMonth(),1));$('rp-to').value=fmt(now)}
  else{$('rp-from').value='';$('rp-to').value=''}
  filterTable();
};

// ===== 筛选 =====
window.filterTable=function(){
  var from=$('rp-from').value,to=$('rp-to').value;
  var loc=$('rp-loc-filter').value,st=$('rp-status').value;
  var q=($('rp-search').value||'').toLowerCase();
  var dd=settings.display||{},tt=settings.timer||{};
  var recs=allRecords.filter(function(r){
    if(from&&r.sign_time<from)return false;
    if(to&&r.sign_time>to+' 23:59:59')return false;
    if(loc&&r.location!==loc)return false;
    if(st&&r.status!==st)return false;
    if(q&&r.name.toLowerCase().indexOf(q)<0)return false;
    return true;
  });
  recs.sort(function(a,b){return b.sign_time.localeCompare(a.sign_time)});
  // 统计
  var done=recs.filter(function(r){return r.status==='已完成'}).length;
  var wait=recs.filter(function(r){return r.status==='等待中'}).length;
  $('rp-fs-total').textContent=recs.length;
  $('rp-fs-done').textContent=done;
  $('rp-fs-wait').textContent=wait;
  $('rp-filter-stats').style.display=recs.length?'flex':'none';
  renderTable(recs,dd.mask_names!==false,tt.remind_minutes||40,tt.warning_minutes||35,tt.countdown_minutes||40,tt.countdown_enabled!==false);
};

// ===== 导出 =====
window.doExport=function(){
  var dd=settings.display||{},tt=settings.timer||{};
  var recs=window._allRecs||allRecords;
  if(!recs.length){alert('无数据可导出');return}
  var BOM='\uFEFF';
  var hdrs=['序号','姓名','身份证号','签到时间','签到地点','状态'];
  var rows=recs.map(function(r,i){return [i+1,r.name,r.id_number||'',r.sign_time,r.location||'',r.status||'等待中']});
  var csv=BOM+hdrs.join(',')+'\n'+rows.map(function(r){return r.map(function(c){return '"'+String(c).replace(/"/g,'""')+'"'}).join(',')}).join('\n');
  var blob=new Blob([csv],{type:'text/csv;charset=utf-8'});
  var url=URL.createObjectURL(blob);
  var a=document.createElement('a');
  var ts=new Date().toISOString().slice(0,10);
  a.download='签到记录_'+ts+'.csv';a.click();
  URL.revokeObjectURL(url);
  // 反馈
  var btn=document.querySelector('.rp-btn-export');
  if(btn){var t=btn.textContent;btn.textContent='\u2713 已导出';btn.style.background='linear-gradient(135deg,#00d68f,#059669)';setTimeout(function(){btn.textContent=t;btn.style.background=''},2000)}
};

// ===== 导出CSV =====
window.exportExcel=function(){
  var recs=window._allRecs||allRecords;
  if(!recs.length){alert('无数据可导出');return}
  var BOM='﻿';
  var hdrs=['序号','姓名','身份证号','签到时间','签到地点','状态'];
  var rows=recs.map(function(r,i){return [i+1,r.name,r.id_number||'',r.sign_time,r.location||'',r.status||'等待中']});
  var csv=BOM+hdrs.join(',')+'\n'+rows.map(function(r){return r.map(function(c){return '"'+String(c).replace(/"/g,'""')+'"'}).join(',')}).join('\n');
  var blob=new Blob([csv],{type:'text/csv;charset=utf-8'});
  var url=URL.createObjectURL(blob);
  var a=document.createElement('a');a.href=url;
  a.download='签到记录_'+new Date().toISOString().slice(0,10)+'.csv';a.click();
  URL.revokeObjectURL(url);
};

// ===== 动态图表 =====
async function loadCharts(){
  var period=document.querySelector('.rp-tab.active')?.dataset.p||'week';
  try{
    var r=await fetch('/api/stats?period='+period);
    var d=await r.json();
    var labels=d.labels||[],values=d.values||[];
    var maxVal=Math.max.apply(null,values.concat(1));

    // ---- 趋势柱状图（渐变色+弹入动画） ----
    var ctx1=$('chart-trend').getContext('2d');
    if(chartTrend)chartTrend.destroy();
    var gradBars=values.map(function(v,i){
      var alpha=0.35+(v/maxVal)*0.55;
      return v===maxVal?'rgba(0,214,143,0.85)':'rgba(79,143,255,'+alpha.toFixed(1)+')';
    });
    var borderBars=values.map(function(v){return v===maxVal?'#00d68f':'var(--accent)'});
    chartTrend=new Chart(ctx1,{
      type:'bar',
      data:{labels:labels,datasets:[{data:values,backgroundColor:gradBars,borderColor:borderBars,borderWidth:1,borderRadius:8,borderSkipped:false}]},
      options:{
        responsive:true,maintainAspectRatio:true,
        animation:{duration:900,easing:'easeOutBounce',
          onProgress:function(anim){var w=anim.currentStep/anim.numSteps;ctx1.canvas.style.opacity=Math.min(w*1.2,1)}},
        plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(20,28,38,0.95)',titleFont:{size:12},bodyFont:{size:13},padding:12,cornerRadius:8,displayColors:false}},
        scales:{
          x:{ticks:{color:'#4a5568',font:{size:10}},grid:{display:false}},
          y:{ticks:{color:'#4a5568',stepSize:1,font:{size:10}},grid:{color:'rgba(255,255,255,0.04)'},beginAtZero:true}
        }
      }
    });

    // ---- 时段热力图（渐变面积曲线） ----
    var hours=d.hourly||[];
    var hLabels=hours.map(function(h){return h.hour+':00'});
    var hValues=hours.map(function(h){return h.count});
    var ctx2=$('chart-hourly').getContext('2d');
    if(chartHourly)chartHourly.destroy();
    var gradLine=ctx2.createLinearGradient(0,0,0,260);
    gradLine.addColorStop(0,'rgba(108,92,231,0.3)');
    gradLine.addColorStop(1,'rgba(108,92,231,0.02)');
    chartHourly=new Chart(ctx2,{
      type:'line',
      data:{labels:hLabels,datasets:[{data:hValues,borderColor:'#6c5ce7',backgroundColor:gradLine,fill:true,tension:0.45,pointRadius:function(ctx){return ctx.raw>0?5:1},pointBackgroundColor:function(ctx){return ctx.raw>0?'#6c5ce7':'#4a5568'},pointBorderWidth:0,borderWidth:2.5}]},
      options:{
        responsive:true,maintainAspectRatio:true,
        animation:{duration:1200,easing:'easeInOutQuart'},
        plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(20,28,38,0.95)',titleFont:{size:12},bodyFont:{size:13},padding:12,cornerRadius:8,displayColors:false,callbacks:{label:function(ctx){return ' '+ctx.raw+' 人签到'}}}},
        scales:{
          x:{ticks:{color:'#4a5568',font:{size:10}},grid:{display:false}},
          y:{ticks:{color:'#4a5568',stepSize:1,font:{size:10}},grid:{color:'rgba(255,255,255,0.04)'},beginAtZero:true}
        }
      }
    });

    // ---- 状态环图 ----
    var stData=d.status_dist||{};
    var stLabels=Object.keys(stData);
    var stValues=Object.values(stData);
    if(!stLabels.length){stLabels=['暂无数据'];stValues=[1]}
    var ctx3=$('chart-status').getContext('2d');
    if(chartStatus)chartStatus.destroy();
    chartStatus=new Chart(ctx3,{
      options:{
        onClick:function(e,els){
          if(!els.length)return;
          var idx=els[0].index;
          var st=stLabels[idx];
          $('rp-search').value='';$('rp-status').value='';
          $('rp-loc-filter').value='';
          var dd=settings.display||{},tt=settings.timer||{};
          var ov=tt.remind_minutes||40,wn=tt.warning_minutes||35;
          var recs=allRecords.filter(function(r){
            var min=Math.floor((new Date()-new Date(r.sign_time.replace(' ','T')))/60000);
            if(st==='正常等待')return min<ov&&!['已叫号','已过号','已完成'].includes(r.status||'');
            if(st==='即将超时')return min>=wn&&min<ov&&!['已叫号','已过号','已完成'].includes(r.status||'');
            if(st==='已超时')return min>=ov&&!['已叫号','已过号','已完成'].includes(r.status||'');
            return false;
          });
          renderTable(recs,dd.mask_names!==false,ov,wn,tt.countdown_minutes||40,tt.countdown_enabled!==false);
          document.querySelector('.rp-table-panel').scrollIntoView({behavior:'smooth'});
        }
      },
      type:'doughnut',
      data:{labels:stLabels,datasets:[{data:stValues,backgroundColor:['#00d68f','#ffaa00','#ff3d57','#4f8fff','#6c5ce7'],borderWidth:3,borderColor:'#141c26',hoverBorderWidth:5,hoverBorderColor:'#141c26'}]},
      options:{
        responsive:true,maintainAspectRatio:true,
        animation:{animateRotate:true,duration:1500,easing:'easeOutBounce'},
        plugins:{legend:{position:'bottom',labels:{color:'#8896a8',font:{size:10},padding:14,usePointStyle:true,pointStyleWidth:8}},tooltip:{backgroundColor:'rgba(20,28,38,0.95)',padding:12,cornerRadius:8}}
      }
    });

    // ---- 地点分布条形图 ----
    var locData=d.location_dist||{};
    var locLabels=Object.keys(locData);
    var locValues=Object.values(locData);
    if(!locLabels.length){locLabels=['暂无'];locValues=[1]}
    var ctx4=$('chart-location').getContext('2d');
    if(chartLocation)chartLocation.destroy();
    var locColors=['rgba(79,143,255,0.65)','rgba(108,92,231,0.65)','rgba(0,214,143,0.65)','rgba(255,170,0,0.65)','rgba(255,61,87,0.6)'];
    chartLocation=new Chart(ctx4,{
      options:{
        onClick:function(e,els){
          if(!els.length)return;
          var idx=els[0].index;
          var loc=locLabels[idx];
          $('rp-search').value='';$('rp-loc-filter').value=loc;$('rp-status').value='';
          filterTable();
          document.querySelector('.rp-table-panel').scrollIntoView({behavior:'smooth'});
        }
      },
      type:'bar',
      data:{labels:locLabels,datasets:[{data:locValues,backgroundColor:locColors,borderRadius:6,borderSkipped:false}]},
      options:{
        indexAxis:'y',
        responsive:true,maintainAspectRatio:true,
        animation:{duration:800,easing:'easeOutQuart'},
        plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(20,28,38,0.95)',padding:12,cornerRadius:8,displayColors:false}},
        scales:{
          x:{ticks:{color:'#4a5568',stepSize:1,font:{size:10}},grid:{color:'rgba(255,255,255,0.04)'},beginAtZero:true},
          y:{ticks:{color:'#8896a8',font:{size:10}},grid:{display:false}}
        }
      }
    });

  }catch(e){console.error(e)}
}

window.loadCharts=loadCharts;
init();
})();
