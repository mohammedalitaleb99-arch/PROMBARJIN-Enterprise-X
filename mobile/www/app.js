const OUTBOX_KEY='prombarjin.outbox.v1';
const API_BASE='https://prombarjin-enterprise-x.onrender.com';
const mission=document.getElementById('mission');
const result=document.getElementById('result');
const execute=document.getElementById('execute');
const sync=document.getElementById('sync');
function read(){try{return JSON.parse(localStorage.getItem(OUTBOX_KEY)||'[]')}catch{return[]}}
function write(v){localStorage.setItem(OUTBOX_KEY,JSON.stringify(v))}
function uuid(){return crypto.randomUUID?crypto.randomUUID():Date.now()+'-'+Math.random()}
function render(){const q=read();result.textContent='Pending offline events: '+q.length+'\nLedger mode: local-first\nStatus: '+(navigator.onLine?'ONLINE':'OFFLINE')}
async function executeMission(){const prompt=mission.value.trim();if(!prompt)return;const event={event_id:uuid(),action:'CREATE',payload:{prompt},timestamp:new Date().toISOString(),base_version:0,status:'pending'};const q=read();q.push(event);write(q);render();try{if(navigator.onLine){await syncOutbox();}}catch(e){result.textContent='Queued safely offline: '+e.message}}
async function syncOutbox(){const q=read();if(!q.length){render();return}const remaining=[];for(const event of q){try{const r=await fetch(API_BASE+'/api/v1/sync/reconcile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({events:[event]})});if(!r.ok)throw new Error('HTTP '+r.status);const body=await r.json();result.textContent=JSON.stringify(body,null,2)}catch(e){remaining.push(event)}}write(remaining);render()}
execute.onclick=executeMission;sync.onclick=syncOutbox;window.addEventListener('online',syncOutbox);render();