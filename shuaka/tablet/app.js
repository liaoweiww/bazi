(function(){
'use strict';
let R=5,W=35,O=40,CE=true,CM=40,recs=[],cd=5,cur=null,cfg={display:{},timer:{}};
const $=id=>document.getElementById(id);

async function ls(){
  try{let r=await fetch('/api/settings');cfg=await r.json();let d=cfg.display||{},t=cfg.timer||{};
  R=d.refresh_interval||5;W=t.warning_minutes||35;O=t.remind_minutes||40;CE=t.countdown_enabled!==false;CM=t.countdown_minutes||40;
  $('header-title').textContent=d.title||'叫号系统';$('page-title').textContent=(d.title||'叫号')+' · 叫号';
  $('header-subtitle').textContent=d.subtitle||d.location||'';
  if(d.logo_url){let l=$('header-logo');l.src=d.logo_url;l.style.display='block';}
  let t2=cfg.themes||{},th=t2[d.theme]||{};
  let s=(k,v)=>document.documentElement.style.setProperty(k,v);
  s('--bg',d.bg_primary||th.bg_primary||'#0a0e14');s('--bg2',th.bg_secondary||'#131820');s('--bg3',th.bg_row||'#1a1f2b');
  s('--card',th.bg_row_alt||'#161c26');s('--text',th.text_primary||'#e2e6ec');s('--text2',th.text_secondary||'#8b95a5');
  s('--accent',d.accent||th.accent||'#4f8fff');s('--border',th.border||'#1e2633');
  // marquees
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

async function fd(){try{let r=await fetch('/api/signins');if(!r.ok)throw new Error();rd(await r.json());ss(true);}catch(e){ss(false);}}
function ss(ok){$('status-dot').className='bottombar-dot '+(ok?'online':'offline');$('status-text').textContent=ok?'实时连接':'连接断开';}

async function us(seq,loc,status,recalled){
  let b={seq,loc,_set_status:status,name:''};if(recalled!==undefined)b._recalled=recalled;
  try{await fetch('/api/update_record',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});}catch(e){}
  for(let r of recs){if(r.seq===seq&&r.location===loc){r.status=status;if(recalled!==undefined)r._recalled=recalled;break;}}
}

window.callNext=async function(){
  let w=[...recs].filter(r=>!['已叫号','已过号','已完成'].includes(r.status||'')).sort((a,b)=>a.sign_time.localeCompare(b.sign_time));
  if(!w.length){alert('没有等待中的人员');return;}
  let p=w[0],rc=(p._recalled||0)+1;
  await us(p.seq,p.location,'已叫号',rc);
  cur=p;p._recalled=rc;p.status='已叫号';ucd(p);
  spk((rc>1?'第'+rc+'次叫号，':'')+'请'+p.name+'到窗口办理');
  rd(recs);
};

window.markDone=async function(){
  if(!cur){alert('没有正在叫号的人员');return;}
  cur.status='已完成';await us(cur.seq,cur.location,'已完成');spk(cur.name+'办理完成');cur=null;rcd();rd(recs);
};

window.markPass=async function(){
  if(!cur){alert('没有正在叫号的人员');return;}
  cur.status='已过号';await us(cur.seq,cur.location,'已过号');spk('过号，请'+cur.name+'稍后重叫');cur=null;rcd();rd(recs);
};

window.reCall=async function(){
  if(!cur){
    let cs=recs.filter(r=>['已过号','已叫号'].includes(r.status||''));
    if(!cs.length){alert('没有可重叫的人员');return;}
    let p=cs.sort((a,b)=>b.sign_time.localeCompare(a.sign_time))[0],rc=(p._recalled||0)+1;
    await us(p.seq,p.location,'已叫号',rc);cur=p;p.status='已叫号';p._recalled=rc;ucd(p);spk('请'+p.name+'到窗口办理');rd(recs);return;
  }
  let rc=(cur._recalled||0)+1;await us(cur.seq,cur.location,'已叫号',rc);cur._recalled=rc;spk('再次叫号，请'+cur.name+'到窗口办理');ucd(cur);rd(recs);
};

window.callSpecific=async function(seq,loc){
  let p=recs.find(r=>r.seq===seq&&r.location===loc);if(!p)return;
  let rc=(p._recalled||0)+1;await us(seq,loc,'已叫号',rc);cur=p;p.status='已叫号';p._recalled=rc;ucd(p);
  spk((rc>1?'第'+rc+'次叫号，':'')+'请'+p.name+'到窗口办理');rd(recs);
};

function ucd(p){$('calling-num').textContent=String(p.seq).padStart(2,'0');$('calling-name').textContent=p.name;
  $('calling-window').textContent='请到窗口办理'+(p._recalled&&p._recalled>1?' (第'+p._recalled+'次叫号)':'');$('calling-card').classList.add('active');}
function rcd(){$('calling-num').textContent='--';$('calling-name').textContent='等待叫号';$('calling-window').textContent='请到窗口办理';$('calling-card').classList.remove('active');}

function rd(data){
  recs=data;let dd=cfg.display||{},srt=[...data].sort((a,b)=>a.sign_time.localeCompare(b.sign_time));
  let wt=srt.filter(r=>!['已叫号','已过号','已完成'].includes(r.status||'')&&wm(r.sign_time)<O);
  let hy=srt.filter(r=>['已叫号','已过号','已完成'].includes(r.status||'')||wm(r.sign_time)>=O);
  if(!cur&&hy.length){let lt=hy.filter(r=>r.status==='已叫号').sort((a,b)=>b.sign_time.localeCompare(a.sign_time))[0];if(lt)cur=lt;}
  let td=new Date().toISOString().slice(0,10);
  $('stat-today').textContent=data.filter(r=>r.sign_time.startsWith(td)).length;
  $('stat-waiting').textContent=wt.length;$('stat-done').textContent=data.filter(r=>r.status==='已完成').length;
  $('stat-overdue').textContent=data.filter(r=>!['已叫号','已过号','已完成'].includes(r.status||'')&&wm(r.sign_time)>=O).length;
  $('queue-wait-count').textContent=wt.length+'人';$('queue-done-count').textContent=hy.length+'人';
  rr('table-waiting',wt,dd,false);rr('table-history',hy,dd,true);
}

function rr(tid,rows,dd,sb){
  let tb=document.getElementById(tid);if(!tb)return;
  if(!rows.length){tb.innerHTML='<tr><td colspan="8" style="text-align:center;padding:1.5rem;color:var(--text3);">—</td></tr>';return;}
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
    let ah=sb?'<button class="btn-call-row" onclick="event.stopPropagation();callSpecific('+r.seq+',\''+ea(r.location)+'\')">📢 叫号</button>':
      '<div class="row-actions"><span class="tag tag-'+cls+'">'+txt+'</span><button class="btn-row-icon" onclick="event.stopPropagation();openQuickEdit('+r.seq+',\''+ea(r.location)+'\',\''+ea(r.name)+'\',\''+ea(r.id_number||'')+'\')">✎</button><button class="btn-row-icon btn-row-del" onclick="event.stopPropagation();delQ('+r.seq+',\''+ea(r.location)+'\')">✕</button><span class="drag-handle" draggable="true" data-seq="'+r.seq+'" data-loc="'+ea(r.location)+'">⠿</span></div>';
    let ch=sb?'onclick="callSpecific('+r.seq+',\''+ea(r.location)+'\')"':'',rcl=sb?'can-call':'waiting-row';
    return '<tr class="'+rcl+'" style="'+rs+'" '+ch+'><td>'+(i+1)+'</td><td><strong>'+eh(nm)+'</strong></td><td class="q-col-time" title="'+r.sign_time+'">'+r.sign_time.slice(11,19)+'</td><td>'+(ie?'--':fw(m))+'</td><td>'+(CE?cdH:'')+'</td><td>'+rct+'</td><td>'+eh(r.location)+'</td><td>'+ah+'</td></tr>';
  }).join('');
}

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
      $('signin-name').value='';$('signin-id').value='';spk('欢迎'+nm+'，请稍候等待叫号');fd();
      setTimeout(()=>{$('signin-dialog').style.display='none';},1500);
    }else{msg.textContent='✗ '+(d.error||'失败');msg.style.color='#ef4444';msg.style.display='block';}
  }catch(e){msg.textContent='网络错误';msg.style.color='#ef4444';msg.style.display='block';}
};
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&$('signin-dialog').style.display==='flex')window.doSignin();});

window.delQ=async function(seq,loc){
  if(!confirm('确定移出等待队列？'))return;
  try{await fetch('/api/delete_records',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({targets:[{seq,location:loc}]})});fd();}catch(e){alert('删除失败');}
};

window.openQuickEdit=function(seq,loc,name,id){alert('编辑: '+name);};

function lp(){fd();cd=R;}
setInterval(()=>{cd--;if(cd<0)cd=R;$('countdown').textContent=cd;},1000);

(async()=>{await ls();fd();setInterval(lp,R*1000);setInterval(async()=>{await ls();},30000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)lp();});})();
})();
