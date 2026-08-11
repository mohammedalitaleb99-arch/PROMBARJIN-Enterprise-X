const DOMAINS = {
  finance: ['finance','accounting','investment','valuation','cash flow','npv','irr','forecast'],
  mining: ['mining','antimony','tin','tungsten','copper','lithium','nickel','cobalt','graphite','rare earth','ore'],
  energy: ['oil','gas','lng','lpg','refining','petrochemical','energy','renewable','hydrogen','carbon','ccus','esg'],
  negotiation: ['negotiation','offtake','procurement','joint venture','contract renewal','batna','zopa'],
  research: ['research','sources','evidence','verify','literature','market study'],
  coding: ['code','coding','software','api','python','javascript','bug','repository']
};
const PUBLIC_HOSTS = new Set(['reuters.com','www.reuters.com','bbc.com','www.bbc.com','apnews.com','www.apnews.com','sec.gov','www.sec.gov','eia.gov','www.eia.gov','iea.org','www.iea.org','worldbank.org','www.worldbank.org','imf.org','www.imf.org','fred.stlouisfed.org']);

function classify(text) {
  const t = text.toLowerCase();
  const scored = Object.entries(DOMAINS).map(([d, terms]) => [d, terms.reduce((n, x) => n + (t.includes(x) ? 1 : 0), 0)]).sort((a,b)=>b[1]-a[1]);
  const active = scored.filter(([,s])=>s>0).map(([d])=>d);
  return { primary_domain: active[0] || 'general', secondary_domains: active.slice(1,4), complexity: text.length>1200||active.length>=3?'high':(text.length>500||active.length?'medium':'low'), risk: /legal|investment|contract|regulatory|safety/i.test(text)?'high':'medium', evidence_required:true };
}

function gate(answer) {
  const issues = [];
  if (!answer.trim()) issues.push('empty_output');
  return { status: issues.length ? 'FAIL' : 'PASS', score: Math.max(0,100-20*issues.length), issues };
}

async function dbState(env) {
  const [memories, decisions, messages] = await Promise.all([
    env.DB.prepare('SELECT * FROM memories ORDER BY id DESC LIMIT 100').all(),
    env.DB.prepare('SELECT * FROM decisions ORDER BY id DESC LIMIT 50').all(),
    env.DB.prepare('SELECT * FROM conversations ORDER BY id DESC LIMIT 30').all()
  ]);
  return { memories: memories.results || [], decisions: decisions.results || [], messages: (messages.results || []).reverse() };
}

async function quote(symbol, env) {
  if (!env.TWELVE_DATA_API_KEY) return {status:'not_configured', symbol};
  const u = new URL('https://api.twelvedata.com/price'); u.searchParams.set('symbol',symbol); u.searchParams.set('apikey',env.TWELVE_DATA_API_KEY);
  const r = await fetch(u); const data = await r.json();
  return {status:data.price ? 'ok':'error', provider:'Twelve Data', symbol, price:data.price, timestamp:new Date().toISOString(), raw:data};
}

async function publicSource(rawUrl) {
  const u = new URL(rawUrl); const host=u.hostname.toLowerCase();
  if (!(PUBLIC_HOSTS.has(host) || [...PUBLIC_HOSTS].some(h=>host.endsWith('.'+h)))) throw new Error('Domain is not on the PROMBARJIN public-source allowlist.');
  const r=await fetch(u,{headers:{'User-Agent':'PROMBARJIN/1.0'}});
  const text=await r.text();
  return {url:r.url,status_code:r.status,fetched_at:new Date().toISOString(),content:text.slice(0,30000)};
}

async function aiReply(userText, profile, history, env) {
  if (!env.OPENAI_API_KEY) return `PROMBARJIN is online in no-key mode.\n\nDomain: ${profile.primary_domain}\nComplexity: ${profile.complexity}\nEvidence required: ${profile.evidence_required}\n\nConnect an OpenAI API key as a Cloudflare Worker secret to enable model-backed answers.`;
  const body={model:env.OPENAI_MODEL||'gpt-5-mini', input:[{role:'system',content:'PROMBARJIN OMEGA runtime. Separate fact, inference, estimate, opinion and speculation. Never fabricate live data or citations. Primary domain='+profile.primary_domain+', secondary='+profile.secondary_domains.join(', ')},{role:'user',content:userText}]};
  const r=await fetch('https://api.openai.com/v1/responses',{method:'POST',headers:{'Authorization':'Bearer '+env.OPENAI_API_KEY,'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok) return `OpenAI request failed with status ${r.status}.`;
  const data=await r.json(); return data.output_text || 'No model output.';
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/health') return Response.json({status:'ok',service:'prombarjin-cloudflare',internet_gateway:true,market_gateway:!!env.TWELVE_DATA_API_KEY,d1:true});
    if (url.pathname === '/api/state' && request.method === 'GET') return Response.json(await dbState(env));
    if (url.pathname === '/api/market/quote' && request.method === 'GET') { try { return Response.json(await quote((url.searchParams.get('symbol')||'AAPL').toUpperCase(),env)); } catch(e){ return Response.json({status:'error',message:String(e)},{status:502}); } }
    if (url.pathname === '/api/source' && request.method === 'GET') { try { return Response.json(await publicSource(url.searchParams.get('url')||'')); } catch(e){ return Response.json({error:String(e)},{status:403}); } }
    if (url.pathname === '/api/memory' && request.method === 'POST') { const b=await request.json(); await env.DB.prepare('INSERT INTO memories(key,value) VALUES(?,?)').bind(b.key,b.value).run(); return Response.json({status:'saved'}); }
    if (url.pathname === '/api/decision' && request.method === 'POST') { const b=await request.json(); const c=Math.max(0,Math.min(100,Number(b.confidence??75))); await env.DB.prepare('INSERT INTO decisions(title,rationale,confidence) VALUES(?,?,?)').bind(b.title,b.rationale,c).run(); return Response.json({status:'saved'}); }
    if (url.pathname === '/api/chat' && request.method === 'POST') {
      const b=await request.json(); const message=String(b.message||'').trim(); if(!message) return Response.json({error:'message required'},{status:400});
      await env.DB.prepare('INSERT INTO conversations(role,content) VALUES(?,?)').bind('user',message).run();
      const profile=classify(message); const state=await dbState(env); const reply=await aiReply(message,profile,state.messages,env);
      await env.DB.prepare('INSERT INTO conversations(role,content) VALUES(?,?)').bind('assistant',reply).run();
      return Response.json({reply,profile,quality_gate:gate(reply)});
    }
    return env.ASSETS.fetch(request);
  }
};
