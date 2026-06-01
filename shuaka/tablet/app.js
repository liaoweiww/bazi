(function(){
'use strict';
let R=5,W=35,O=40,CE=true,CM=40,recs=[],cd=5,cur=null,justCleared=false,vTpl={},cfg={display:{},timer:{}};
const $=id=>document.getElementById(id);

// ===== 模式管理 =====
let currentMode=(function(){
  let p=new URLSearchParams(location.search),m=p.get('mode');
  if(m==='ipad'||m==='mobile') return m;
  return localStorage.getItem('signin_mode')||'full';
})();
function applyMode(m){
  currentMode=m;
  localStorage.setItem('signin_mode',m);
  document.documentElement.classList.remove('mode-ipad','mode-mobile');
  if(m==='ipad') document.documentElement.classList.add('mode-ipad');
  else if(m==='mobile') document.documentElement.classList.add('mode-mobile');
  // 更新顶部图标激活状态
  document.querySelectorAll('.mode-icon').forEach(function(el){
    el.classList.toggle('active', el.dataset.mode===m);
  });
}
window.setMode=function(m){applyMode(m);};
applyMode(currentMode);
// 顶部模式图标点击
document.addEventListener('click',function(e){
  var btn=e.target.closest('.mode-icon');
  if(btn){applyMode(btn.dataset.mode);}
});

async function ls(){
  try{let r=await fetch('/api/settings');cfg=await r.json();let d=cfg.display||{},t=cfg.timer||{};
  R=d.refresh_interval||5;W=t.warning_minutes||35;O=t.remind_minutes||40;CE=t.countdown_enabled!==false;CM=t.countdown_minutes||40;
  let vc=cfg.voice||{}; vTpl=vc.templates||{};
  $('header-title').textContent=d.title||'叫号系统';$('page-title').textContent=(d.title||'叫号')+' · 叫号';
  $('header-subtitle').textContent=d.subtitle||d.location||'';
  if(d.logo_url){let l=$('header-logo');l.src=d.logo_url;l.style.display='block';}
  let t2=cfg.themes||{},th=t2[d.theme]||{};
  let s=(k,v)=>document.documentElement.style.setProperty(k,v);
  s('--bg',d.bg_primary||th.bg_primary||'#0a0e14');s('--bg2',th.bg_secondary||'#131820');s('--bg3',th.bg_row||'#1a1f2b');
  s('--card',th.bg_row_alt||'#161c26');s('--text',th.text_primary||'#e2e6ec');s('--text2',th.text_secondary||'#8b95a5');
  s('--accent',d.accent||th.accent||'#4f8fff');s('--border',th.border||'#1e2633');
  // 字体大小
  let fs = {small:'0.85', normal:'1', large:'1.18', xlarge:'1.35'}[d.font_scale] || '1';
  s('--font-scale', fs);
  // 简约白主题 class 切换（CSS 已有 html.theme-light 覆盖规则）
  document.documentElement.classList.toggle('theme-light', d.theme==='light');
  // 光晕效果
  let glowOn = d.glow_enabled !== false, glowInt = d.glow_intensity || 2;
  document.documentElement.classList.toggle('glow-off', !glowOn);
  let glowCfg = {1:[0.04,0.9,1.05,6], 2:[0.08,0.85,1.15,3], 3:[0.15,0.75,1.3,1.8]}[glowInt] || [0.08,0.85,1.15,3];
  s('--glow-opacity-idle', glowCfg[0]); s('--glow-scale-min', glowCfg[1]); s('--glow-scale-max', glowCfg[2]); s('--glow-speed', glowCfg[3]+'s');
  s('--glow-opacity-active', glowCfg[0]*2.5); s('--glow-scale-min-active', glowCfg[1]-0.05); s('--glow-scale-max-active', glowCfg[2]+0.05);
  let mqs=cfg.marquees||[];
  for(let i=0;i<3;i++){let mq=mqs[i],w=$('marquee-'+(i+1)),tx=$('marquee-'+(i+1)+'-text');
    if(!w||!tx)continue;
    if(mq&&mq.enabled&&mq.text){w.style.display='';tx.textContent=mq.text+'    ◆    '+mq.text+'    ◆    '+mq.text;
      w.style.setProperty('--mq-size',mq.size||'0.8rem');w.style.setProperty('--mq-speed',(mq.speed||12)+'s');
      tx.style.animationDelay=(mq.delay||0)+'s';
      if(mq.gradient){tx.style.background='linear-gradient(90deg,'+(mq.color||'#4f8fff')+',#fff,'+(mq.color||'#4f8fff')+')';tx.style.webkitBackgroundClip='text';tx.style.webkitTextFillColor='transparent';tx.style.backgroundClip='text';}
      else{tx.style.color=mq.color||'#4f8fff';tx.style.background='';tx.style.webkitBackgroundClip='';tx.style.webkitTextFillColor='';tx.style.backgroundClip='';}
    }else{w.style.display='none';}
  }}catch(e){}
}

function clk(){let n=new Date(),p=v=>String(v).padStart(2,'0');
  $('clock-date').textContent=n.getFullYear()+'-'+p(n.getMonth()+1)+'-'+p(n.getDate())+' 周'+'日一二三四五六'[n.getDay()];
  $('clock-time').textContent=p(n.getHours())+':'+p(n.getMinutes())+':'+p(n.getSeconds());
}
clk();setInterval(clk,1000);

function spk(t){try{let u=new SpeechSynthesisUtterance(t);u.lang='zh-CN';u.rate=0.85;speechSynthesis.cancel();speechSynthesis.speak(u);}catch(e){}}
function tpl(t,vars){let s=t||'';if(vars)for(let k in vars)s=s.replace(new RegExp('{'+k+'}','g'),vars[k]);return s;}

async function fd(){try{let r=await fetch('/api/signins');if(!r.ok)throw new Error();rd(await r.json());ss(true);}catch(e){ss(false);}}
function ss(ok){$('status-dot').className='bottombar-dot '+(ok?'online':'offline');$('status-text').textContent=ok?'实时连接':'连接断开';}

async function us(seq,loc,status,recalled,voiceText){
  let b={seq,loc,_set_status:status,name:''};if(recalled!==undefined)b._recalled=recalled;
  if(voiceText)b._peer_voice=voiceText;
  try{await fetch('/api/update_record',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});}catch(e){}
  for(let r of recs){if(r.seq===seq&&r.location===loc){r.status=status;if(recalled!==undefined)r._recalled=recalled;break;}}
}

// ======= 医院式叫号流程 =======
// 叫下一位：如有当前叫号未完成 → 自动完成；取等待队列第1人叫号
window.callNext=async function(){
  // 如果当前有正在叫号的人，先自动完成
  if(cur && cur.status==='已叫号'){
    cur.status='已完成'; await us(cur.seq,cur.location,'已完成');
  }
  let w=[...recs].filter(r=>!['已叫号','已过号','已完成'].includes(r.status||'')).sort((a,b)=>a.sign_time.localeCompare(b.sign_time));
  if(!w.length){ cur=null; justCleared=true; rcd(); rd(recs); return; }
  let p=w[0], rc=(p._recalled||0)+1;
  let vt=rc>1?tpl(vTpl.recall_nth||'第{n}次叫号，请{name}嘉宾到检测室',{n:rc,name:p.name}):tpl(vTpl.call||'有请{name}嘉宾到检测室',{name:p.name});
  await us(p.seq,p.location,'已叫号',rc,vt);
  cur=p; justCleared=false; p._recalled=rc; p.status='已叫号'; ucd(p);
  spk(vt);
  rd(recs);
};

// 已完成：立即清屏
window.markDone=async function(){
  if(!cur){alert('没有正在叫号的人员');return;}
  let vt=tpl(vTpl.done||'{name}嘉宾检测完毕',{name:cur.name});
  cur.status='已完成'; await us(cur.seq,cur.location,'已完成',undefined,vt);
  spk(vt);
  cur=null; justCleared=true; rcd(); rd(recs);
};

// 过号：立即清屏
window.markPass=async function(){
  if(!cur){alert('没有正在叫号的人员');return;}
  let vt=tpl(vTpl.pass||'过号，请{name}稍后重新叫号',{name:cur.name});
  cur.status='已过号'; await us(cur.seq,cur.location,'已过号',undefined,vt);
  spk(vt);
  cur=null; justCleared=true; rcd(); rd(recs);
};

// 重叫：有当前人 → 重播；无当前人 → 取最近过号/已叫号者重新叫
window.reCall=async function(){
  if(!cur){
    let cs=recs.filter(r=>['已过号','已叫号'].includes(r.status||''));
    if(!cs.length){alert('没有可重叫的人员');return;}
    let p=cs.sort((a,b)=>b.sign_time.localeCompare(a.sign_time))[0], rc=(p._recalled||0)+1;
    let vt=tpl(vTpl.call||'有请{name}嘉宾到检测室',{name:p.name});
    await us(p.seq,p.location,'已叫号',rc,vt);
    cur=p; justCleared=false; p.status='已叫号'; p._recalled=rc; ucd(p);
    spk(vt); rd(recs); return;
  }
  let rc=(cur._recalled||0)+1;
  let vt=tpl(vTpl.recall||'再次叫号，请{name}嘉宾到检测室',{name:cur.name});
  await us(cur.seq,cur.location,'已叫号',rc,vt);
  cur._recalled=rc; ucd(cur);
  spk(vt); rd(recs);
};

// 从历史列表指定叫号
window.callSpecific=async function(seq,loc){
  // 如有当前叫号 → 自动完成
  if(cur && cur.status==='已叫号'){
    cur.status='已完成'; await us(cur.seq,cur.location,'已完成');
  }
  let p=recs.find(r=>r.seq===seq&&r.location===loc); if(!p) return;
  let rc=(p._recalled||0)+1;
  let vt=rc>1?tpl(vTpl.recall_nth||'第{n}次叫号，请{name}嘉宾到检测室',{n:rc,name:p.name}):tpl(vTpl.call||'有请{name}嘉宾到检测室',{name:p.name});
  await us(seq,loc,'已叫号',rc,vt);
  cur=p; justCleared=false; p.status='已叫号'; p._recalled=rc; ucd(p);
  spk(vt); rd(recs);
};

function ucd(p){$('calling-num').textContent=String(p.seq).padStart(2,'0');$('calling-name').textContent=p.name;
  $('calling-window').textContent='请到窗口办理'+(p._recalled&&p._recalled>1?' (第'+p._recalled+'次叫号)':'');$('calling-card').classList.add('active');}
function rcd(){$('calling-num').textContent='--';$('calling-name').textContent='等待叫号';$('calling-window').textContent='请到窗口办理';$('calling-card').classList.remove('active');}

function rd(data){
  recs=data;let dd=cfg.display||{},srt=[...data].sort((a,b)=>a.sign_time.localeCompare(b.sign_time));
  let wt=srt.filter(r=>!['已叫号','已过号','已完成'].includes(r.status||'')&&wm(r.sign_time)<O);
  let hy=srt.filter(r=>['已叫号','已过号','已完成'].includes(r.status||'')||wm(r.sign_time)>=O);
  // 同步当前叫号状态：如果对方已完成/过号则清屏，否则恢复叫号卡片
  if(cur){
    let f=recs.find(r=>r.seq===cur.seq&&r.location===cur.location);
    if(!f||f.status!=='已叫号'){cur=null;rcd();}
    else cur=f;
  }
  if(!cur&&!justCleared&&hy.length){let lt=hy.filter(r=>r.status==='已叫号').sort((a,b)=>b.sign_time.localeCompare(a.sign_time))[0];if(lt){cur=lt;ucd(cur);}}
  justCleared=false;
  let td=new Date().toISOString().slice(0,10);
  $('stat-today').textContent=data.filter(r=>r.sign_time.startsWith(td)).length;
  $('stat-waiting').textContent=wt.length;$('stat-done').textContent=data.filter(r=>r.status==='已完成').length;
  $('stat-overdue').textContent=data.filter(r=>!['已叫号','已过号','已完成'].includes(r.status||'')&&wm(r.sign_time)>=O).length;
  $('queue-wait-count').textContent=wt.length+'人';$('queue-done-count').textContent=hy.length+'人';
  rr('table-waiting',wt,dd,false);rr('table-history',hy,dd,true);
}

function rr(tid,rows,dd,sb){
	  let tb=document.getElementById(tid);if(!tb)return;
	  let cols=sb?6:8; // 历史表6列，等待表8列
	  if(!rows.length){tb.innerHTML='<tr><td colspan="'+cols+'" style="text-align:center;padding:1.5rem;color:var(--text3);">—</td></tr>';return;}
	  tb.innerHTML=rows.map((r,i)=>{
	    let m=wm(r.sign_time),nm=dd.mask_names!==false?mk(r.name):r.name,st=r.status||'等待中';
	    let ic=st==='已叫号',ip=st==='已过号',id=st==='已完成',io=!['已叫号','已过号','已完成'].includes(st)&&m>=O;
	    let cls='ok',txt='等待中';
	    if(id){cls='ok';txt='已完成';}else if(ip){cls='warn';txt='已过号';}else if(ic){cls='ok';txt='已叫号';}else if(io){cls='bad';txt='已超时';}else if(m>=W){cls='warn';txt='即将超时';}
	    let rm=CM-m,pct=Math.max(0,Math.min(100,Math.round((rm/CM)*100))),ie=id||ip;
	    let cc=ie?'var(--text3)':ic?'var(--accent)':rm<=0?'var(--red)':rm<=10?'var(--yellow)':'var(--green)';
	    let ct=ie?'--':ic?'叫号中':rm<=0?'超时':rm<60?rm+'':Math.floor(rm/60)+'h'+rm%60+'m';
	    let circ=2*Math.PI*12,dash=ie||ic?circ:circ*(1-pct/100);
	    let cdH='<div class="cd-ring-wrap"><svg class="cd-ring" viewBox="0 0 32 32"><circle class="cd-ring-bg" cx="16" cy="16" r="12"/><circle class="cd-ring-fill" cx="16" cy="16" r="12" stroke-dasharray="'+circ.toFixed(1)+'" stroke-dashoffset="'+dash.toFixed(1)+'" style="stroke:'+cc+'"/></svg><span class="cd-ring-text" style="color:'+cc+'">'+ct+'</span></div>';
	    let rc=r._recalled||0,rct=rc>0?rc+'次':'';
	    let rs=id?'opacity:0.35':ip?'opacity:0.4':io?'background:rgba(255,61,87,0.06)!important':ic?'background:rgba(79,143,255,0.08)!important;font-weight:600':'';
	    let ah, ch='', rcl='';
	    if(sb){
	      // 历史区：精简操作按钮
	      let restoreBtn='<button class="btn-row-icon" style="font-size:0.7rem;padding:0.1rem 0.35rem;width:auto;border-radius:6px" onclick="event.stopPropagation();restoreToWait('+r.seq+',\''+ea(r.location)+'\','+(id?'true':'false')+')" title="恢复至等待队列">↩</button>';
	      if(id){
	        ah='<div class="row-actions" style="gap:0.2rem"><span class="tag tag-ok" style="font-size:0.68rem">✔ 已完成</span>'+restoreBtn+'</div>';
	        rcl='';
	      }else{
	        let callBtn='<button class="btn-call-row" onclick="event.stopPropagation();callSpecific('+r.seq+',\''+ea(r.location)+'\')">📢 叫号</button>';
	        ah='<div class="row-actions" style="gap:0.25rem">'+callBtn+restoreBtn+'</div>';
	        ch='onclick="callSpecific('+r.seq+',\''+ea(r.location)+'\')"';
	        rcl='can-call';
	      }
	      // 历史表列: # 姓名 签到 等待 次数 操作
	      var hi='';if(id)hi='<span style="font-size:1.3rem;margin-right:0.2rem;vertical-align:middle;">💪</span><span style="display:inline-block;background:rgba(16,185,129,0.12);color:#10b981;border-radius:10px;padding:0.1rem 0.4rem;font-size:0.65rem;font-weight:700;vertical-align:middle;">已检</span>';else if(ip)hi='<span style="font-size:1.3rem;margin-right:0.2rem;vertical-align:middle;">⏭</span><span style="display:inline-block;background:rgba(255,170,0,0.12);color:#ffaa00;border-radius:10px;padding:0.1rem 0.4rem;font-size:0.65rem;font-weight:700;vertical-align:middle;">过号</span>';
	      return '<tr class="'+rcl+'" style="'+rs+'" '+ch+'><td>'+(i+1)+'</td><td>'+hi+'<strong>'+eh(nm)+'</strong></td><td class="q-col-time" title="'+r.sign_time+'">'+r.sign_time.slice(11,19)+'</td><td>'+fw(m)+'</td><td>'+rct+'</td><td>'+ah+'</td></tr>';
	    }else{
	      ah='<div class="row-actions"><span class="tag tag-'+cls+'">'+txt+'</span><button class="btn-row-icon" onclick="event.stopPropagation();openQuickEdit('+r.seq+',\''+ea(r.location)+'\',\''+ea(r.name)+'\',\''+ea(r.id_number||'')+'\')">✎</button><button class="btn-row-icon btn-row-del" onclick="event.stopPropagation();delQ('+r.seq+',\''+ea(r.location)+'\')">✕</button><span class="drag-handle" draggable="true" data-seq="'+r.seq+'" data-loc="'+ea(r.location)+'">⠿</span></div>';
	      rcl='waiting-row';
	      // 等待表列: # 姓名 签到 等待 倒计时 次数 地点 操作
	      var hi='';if(id)hi='<span style="font-size:1.3rem;margin-right:0.2rem;vertical-align:middle;">💪</span><span style="display:inline-block;background:rgba(16,185,129,0.12);color:#10b981;border-radius:10px;padding:0.1rem 0.4rem;font-size:0.65rem;font-weight:700;vertical-align:middle;">已检</span>';else if(ip)hi='<span style="font-size:1.3rem;margin-right:0.2rem;vertical-align:middle;">⏭</span><span style="display:inline-block;background:rgba(255,170,0,0.12);color:#ffaa00;border-radius:10px;padding:0.1rem 0.4rem;font-size:0.65rem;font-weight:700;vertical-align:middle;">过号</span>';
	      return '<tr class="'+rcl+'" style="'+rs+'" '+ch+'><td>'+(i+1)+'</td><td>'+hi+'<strong>'+eh(nm)+'</strong></td><td class="q-col-time" title="'+r.sign_time+'">'+r.sign_time.slice(11,19)+'</td><td>'+fw(m)+'</td><td>'+(CE?cdH:'')+'</td><td>'+rct+'</td><td>'+eh(r.location)+'</td><td>'+ah+'</td></tr>';
	    }
	  }).join('');
	}
	
	// ===== 恢复至等待队列 =====
	window.restoreToWait=async function(seq,loc,isCompleted){
	  if(isCompleted){
	    if(!(await cfConfirm('确定将该已完成人员恢复到等待队列？'))) return;
	  }
	  let now=new Date().toISOString().replace('T',' ').slice(0,19);
	  var rn='';
	  for(let r of recs){if(String(r.seq)===String(seq)&&(r.location||'')===(loc||'')){rn=r.name;break;}}
	  let vt=rn?tpl(vTpl.restore||'{name}已恢复到等待队列',{name:rn}):'';
	  try{
	    await fetch('/api/restore_record',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({seq:seq,location:loc||'',_peer_voice:vt})});
	  }catch(e){}
	  // 本地同步：重置状态+时间，等钟从0开始
	  for(let r of recs){if(String(r.seq)===String(seq)&&(r.location||'')===(loc||'')){r.status='等待中';r.sign_time=now;break;}}
	  rd(recs);
	  if(vt)spk(vt);
	  var wt=$('table-waiting'); if(wt)wt.scrollIntoView({behavior:'smooth',block:'start'});
	};

function mk(n){if(!n||n==='未知')return n;return n[0]+'*'.repeat(n.length-1);}
function eh(s){let d=document.createElement('div');d.textContent=s||'';return d.innerHTML;}
function ea(s){return String(s||'').replace(/'/g,"\\'").replace(/"/g,'&quot;');}
function wm(t){return Math.floor((new Date()-new Date(t.replace(' ','T')))/60000);}
function fw(m){return m<0?'--':m<60?m+'分钟':Math.floor(m/60)+'h'+m%60+'m';}

window.showSigninDialog=function(){$('signin-dialog').style.display='flex';$('signin-name').focus();$('signin-msg').style.display='none';};
window.doSignin=async function(){
  let nm=$('signin-name').value.trim(),id=$('signin-id').value.trim()||'手动录入',msg=$('signin-msg');
  if(!nm){msg.textContent='请输入姓名';msg.style.color='#ef4444';msg.style.display='block';return;}
  try{let r=await fetch('/api/manual_signin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:nm,id_number:id})});
    let d=await r.json();
    if(d.ok){msg.textContent='✓ '+nm+' 签到成功！请稍候等待叫号';msg.style.color='#22c55e';msg.style.display='block';
      $('signin-name').value='';$('signin-id').value='';spk(tpl(vTpl.welcome||'{name}，欢迎签到！',{name:nm}));fd();
      setTimeout(()=>{$('signin-dialog').style.display='none';},1500);
    }else{msg.textContent='✗ '+(d.error||'失败');msg.style.color='#ef4444';msg.style.display='block';}
  }catch(e){msg.textContent='网络错误';msg.style.color='#ef4444';msg.style.display='block';}
};
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&$('signin-dialog').style.display==='flex')window.doSignin();});

window.delQ=async function(seq,loc){
  if(!(await cfConfirm('确定移出等待队列？')))return;
  try{await fetch('/api/delete_records',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({targets:[{seq:seq,location:loc||''}]})});fd();}catch(e){alert('删除失败');}
};

// ===== 编辑人员 =====
window.openQuickEdit=function(seq,loc,name,id){
  $('#edit-seq').value=seq; $('#edit-loc').value=loc||'';
  $('#edit-name').value=name||''; $('#edit-idnum').value=id||'';
  $('#edit-dialog').style.display='flex'; $('#edit-name').focus();
};
window.doEditSave=async function(){
  let seq=parseInt($('#edit-seq').value), loc=$('#edit-loc').value;
  let nm=$('#edit-name').value.trim(), idnum=$('#edit-idnum').value.trim();
  if(!nm){alert('请输入姓名');return;}
  try{await fetch('/api/update_record',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({seq,location:loc,name:nm,id_number:idnum,_set_status:'',name:nm})});}catch(e){}
  for(let r of recs){if(r.seq===seq&&(r.location||'')===loc){r.name=nm;r.id_number=idnum;break;}}
  $('#edit-dialog').style.display='none'; rd(recs);
};
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&$('#edit-dialog').style.display==='flex')doEditSave();});

// ===== 拖拽排序 =====
let dragSrc=null;
function dtAttach(tbodyId){
  let tb=document.getElementById(tbodyId); if(!tb) return;
  tb.addEventListener('dragstart',e=>{
    let h=e.target.closest('.drag-handle'); if(!h) return;
    dragSrc={seq:parseInt(h.dataset.seq),loc:h.dataset.loc||''};
    e.target.closest('tr').style.opacity='0.4';
    e.dataTransfer.effectAllowed='move';
  });
  tb.addEventListener('dragend',e=>{
    let h=e.target.closest('.drag-handle'); if(h) e.target.closest('tr').style.opacity='';
  });
  tb.addEventListener('dragover',e=>{e.preventDefault(); e.dataTransfer.dropEffect='move';});
  tb.addEventListener('drop',e=>{
    e.preventDefault();
    let tr=e.target.closest('tr'); if(!tr||!dragSrc) return;
    let tgtH=tr.querySelector('.drag-handle');
    if(!tgtH) return;
    let tgtSeq=parseInt(tgtH.dataset.seq), tgtLoc=tgtH.dataset.loc||'';
    if(tgtSeq===dragSrc.seq&&tgtLoc===dragSrc.loc) return;
    // 交换两个记录的签到时间来实现排序调整
    let srcR=recs.find(r=>r.seq===dragSrc.seq&&(r.location||'')===dragSrc.loc);
    let tgtR=recs.find(r=>r.seq===tgtSeq&&(r.location||'')===tgtLoc);
    if(srcR&&tgtR){let tmp=srcR.sign_time; srcR.sign_time=tgtR.sign_time; tgtR.sign_time=tmp;}
    // 同步到服务端（交换 sign_time）
    fetch('/api/swap_records',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({a:{seq:dragSrc.seq,loc:dragSrc.loc},b:{seq:tgtSeq,loc:tgtLoc}})}).catch(()=>{});
    rd(recs); dragSrc=null;
  });
}

function lp(){fd();cd=R;}
setInterval(()=>{cd--;if(cd<0)cd=R;$('countdown').textContent=cd;},1000);

	// ===== 管理员密码验证弹窗 =====
window._pwResolve=null;
window.pwDlg=function(ok){$('pw-dialog').style.display='none';if(window._pwResolve)window._pwResolve(ok ? $('pw-input').value : null);$('pw-input').value='';};
window.verifyAdmin=function(msg){return new Promise(function(resolve){window._pwResolve=resolve;$('pw-msg').textContent=msg||'请输入管理员密码';$('pw-dialog').style.display='flex';$('pw-input').focus();});};
document.addEventListener('keydown',function(e){if(e.key==='Enter'&&$('pw-dialog').style.display==='flex')pwDlg(true);});

// ===== 系统监控面板 =====
	var monitorExpanded = false;
	window.toggleMonitor = function(){
		monitorExpanded = !monitorExpanded;
		var p = document.getElementById('monitor-panel'); if(p) p.classList.toggle('expanded', monitorExpanded);
		var a = document.getElementById('mon-arrow'); if(a) a.textContent = monitorExpanded ? '▼' : '▶';
		var b = document.getElementById('monitor-body'); if(b) b.style.display = monitorExpanded ? 'block' : 'none';
	};
	async function fetchMonitor(){
		try{
			var r = await fetch('/api/monitor');
			if(!r.ok) return;
			var d = await r.json();
				var ve = document.getElementById('version-text');
				if(ve && d.version) ve.textContent = d.version;
			var cr = d.card_reader || {};
			// 读卡器状态
			var dot = document.getElementById('mon-card-dot');
			var st = document.getElementById('mon-card-status');
			if(dot && st){
				if(!cr.enabled){
					dot.className = 'monitor-dot sync-local';
					st.textContent = '未启用（同步终端）';
				}else if(cr.online){
					dot.className = 'monitor-dot online';
					st.textContent = cr.total_reads+'次'+(cr.last_name?' · '+cr.last_name:'');
				}else{
					dot.className = 'monitor-dot offline';
					st.textContent = '读卡器离线';
				}
			}
			if(st) st.textContent = cr.online ? (cr.total_reads+'次'+(cr.last_name?' · '+cr.last_name:'')) : '离线';
			// 同步状态
			var sd = d.sync || {};
			var sdot = document.getElementById('mon-sync-dot');
			var sst = document.getElementById('mon-sync-status');
			var sic = document.getElementById('mon-sync-icon');
			if(sdot && sst){
				if(sd.enabled){
					sdot.className = 'monitor-dot online';
					if(sic) sic.textContent = '☁️';
					sst.textContent = sd.provider + ' · 多机同步';
				}else{
					sdot.className = 'monitor-dot sync-local';
					if(sic) sic.textContent = '💻';
					sst.textContent = '仅本机存储';
				}
			}
			// 文件
			var xl = d.excel_dir || {};
			var cnt = document.getElementById('mon-excel-count');
			if(cnt) cnt.textContent = (xl.files||[]).length + ' 个文件';
			var ul = document.getElementById('mon-file-list');
			if(ul){
				if(xl.files && xl.files.length){
					ul.innerHTML = xl.files.map(function(f){
						return '<li><a href="/api/excel/view/'+encodeURIComponent(f.name)+'" target="_blank" class="mon-file-link">'+eh2(f.name)+'</a><span>'+f.size_kb+'KB · '+f.modified+'</span></li>';
					}).join('');
				}else{
					ul.innerHTML = '<li class="mon-file-empty">暂无数据文件</li>';
				}
			}
		}catch(e){}
	}
	function eh2(s){let d=document.createElement('div');d.textContent=s||'';return d.innerHTML;}

// ===== 自定义确认弹窗（不退出全屏） =====
window._cfResolve=null;
window.cfDlg=function(ok){$('confirm-dialog').style.display='none';if(window._cfResolve)window._cfResolve(ok);};
window.cfConfirm=function(msg){return new Promise(function(resolve){window._cfResolve=resolve;$('confirm-msg').textContent=msg;$('confirm-dialog').style.display='flex';});};

	async function pv(){try{let r=await fetch('/api/pending-voice');let d=await r.json();if(d.ok&&d.text){spk(d.text);if(d.card&&d.card.name){cur=d.card;ucd(cur);justCleared=false;}}}catch(e){}}
	(async()=>{await ls();fd();fetchMonitor();dtAttach('table-waiting');setInterval(lp,R*1000);setInterval(pv,2000);setInterval(async()=>{await ls();},30000);setInterval(fetchMonitor,15000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)lp();});})();
})();
