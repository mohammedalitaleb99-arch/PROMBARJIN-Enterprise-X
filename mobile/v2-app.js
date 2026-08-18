const chat=document.getElementById('chat'),input=document.getElementById('input'),send=document.getElementById('send'),profile=document.getElementById('profile'),status=document.getElementById('status');

const API_BASES=[
  'https://prombarjin-enterprise-x.onrender.com',
  'http://127.0.0.1:8000',
  ...(window.location.origin && !window.location.origin.startsWith('file:')?[window.location.origin]:[])
].filter((v,i,a)=>v&&!a.slice(0,i).includes(v));

async function apiFetch(path,options={}){
  let lastError=new Error('Backend unavailable');
  for(const base of API_BASES){
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),7000);
    try{
      const r=await fetch(base+path,{...options,cache:'no-store',signal:controller.signal});
      clearTimeout(timer);
      if(!r.ok)throw new Error(`HTTP ${r.status}`);
      return r;
    }catch(e){
      clearTimeout(timer);
      lastError=e instanceof Error?e:new Error(String(e));
    }
  }
  throw lastError;
}

function setBackendState(online,message=''){
  if(!status)return;
  status.textContent=online?'ONLINE':'BACKEND OFFLINE';
  status.title=message||'';
}

function add(role,text){
  const d=document.createElement('div');
  d.className='msg '+role;
  d.textContent=text;
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
}

async function checkBackend(){
  try{
    const r=await apiFetch('/health');
    const j=await r.json();
    setBackendState(true,j.service||'Backend online');
    return true;
  }catch(e){
    setBackendState(false,e.message);
    return false;
  }
}

async function exec(){
  const msg=input.value.trim();
  if(!msg)return;
  add('user',msg);
  input.value='';
  send.disabled=true;
  send.textContent='RUNNING';
  try{
    const r=await apiFetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    const j=await r.json();
    add('assistant',j.reply||'No response returned.');
    profile.textContent=JSON.stringify({profile:j.profile,quality_gate:j.quality_gate},null,2);
    setBackendState(true);
  }catch(e){
    add('assistant','Backend error: '+e.message);
    setBackendState(false,e.message);
  }finally{
    send.disabled=false;
    send.textContent='EXECUTE';
  }
}

send.onclick=exec;
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey))exec()});

const quoteBtn=document.getElementById('quote'),symbol=document.getElementById('symbol'),quoteOut=document.getElementById('quoteOut');

async function getQuote(){
  const s=symbol.value.trim();
  if(!s)return;
  quoteBtn.disabled=true;
  quoteOut.textContent='Loading...';
  try{
    const r=await apiFetch('/api/market/quote?symbol='+encodeURIComponent(s));
    const j=await r.json();
    quoteOut.textContent=JSON.stringify(j,null,2);
    setBackendState(true);
  }catch(e){
    quoteOut.textContent='Market error: '+e.message;
    setBackendState(false,e.message);
  }finally{
    quoteBtn.disabled=false;
  }
}

if(quoteBtn){
  quoteBtn.onclick=getQuote;
  getQuote();
  setInterval(getQuote,15000);
}

checkBackend();
if('serviceWorker' in navigator)navigator.serviceWorker.register('/static/sw.js').catch(()=>{});
