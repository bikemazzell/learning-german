
// Mnemonic colors map
const MCOLOR={inka:'#ef4444',barrel:'#22c55e',saudi:'#f59e0b',usa:'#3b82f6',
              lasso:'#ec4899',polo:'#06b6d4',mirror:'#6366f1',anaconda:'#f97316'};

// ── STORAGE ──────────────────────────────────────────────────────────────────
const SK='de-quiz-progress';
function loadProgress(){
  try{const s=localStorage.getItem(SK);return s?JSON.parse(s):{articles:{},dative:{},irregular:{}};}
  catch(e){return{articles:{},dative:{},irregular:{}};}
}
function saveProgress(){
  try{localStorage.setItem(SK,JSON.stringify(progress));}catch(e){}
}

// ── SM-2 ──────────────────────────────────────────────────────────────────────
function sm2Def(){return{correct:0,incorrect:0,ease_factor:2.5,interval:1,last_reviewed:null,next_review:null};}
function sm2Update(e,ok){
  if(ok){
    e.interval=e.interval<=1?6:Math.round(e.interval*e.ease_factor);
    e.ease_factor=Math.max(1.3,parseFloat((e.ease_factor+0.1).toFixed(2)));
    e.correct++;
  }else{
    e.interval=1;
    e.ease_factor=Math.max(1.3,parseFloat((e.ease_factor-0.2).toFixed(2)));
    e.incorrect++;
  }
  const n=new Date();n.setDate(n.getDate()+e.interval);
  e.last_reviewed=new Date().toISOString();
  e.next_review=n.toISOString();
}
function sm2Due(e){return!e||!e.next_review||new Date()>=new Date(e.next_review);}

// ── UTILS ────────────────────────────────────────────────────────────────────
function shuffle(arr){
  const a=[...arr];
  for(let i=a.length-1;i>0;i--){const j=0|Math.random()*(i+1);[a[i],a[j]]=[a[j],a[i]];}
  return a;
}
function norm(s){return(s||'').trim().toLowerCase().replace(/ß/g,'ss').replace(/\s+/g,' ');}
function match(user,correct){
  const u=norm(user);
  return correct.split('/').some(c=>{const n=norm(c);return n===u||n.replace(/^to /,'')===u.replace(/^to /,'');});
}
function pct(c,t){return t>0?Math.round(100*c/t):0;}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function buildChoices(correct,pool,key,n=4){
  // Deduplicate: exclude items whose display value matches the correct one
  const others=[...new Set(shuffle(pool.filter(x=>x[key]!==correct)).map(x=>x[key]))].slice(0,n-1);
  return shuffle([correct,...others]);
}

// ── STATE ────────────────────────────────────────────────────────────────────
let progress=loadProgress();
let activeTab='articles';
let session=null;

// ── APP ───────────────────────────────────────────────────────────────────────
function setTab(t){
  activeTab=t;session=null;
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===t));
  renderMain();
}

function renderMain(){
  const el=document.getElementById('main');
  if(!session){el.innerHTML=renderHome();}
  else if(session.phase==='end'){el.innerHTML=renderEnd();}
  else if(session.phase==='stats'){el.innerHTML=renderStats();}
  else{el.innerHTML=renderQuiz();attachQuizHandlers();}
  el.scrollTop=0;
}

// ── HOME SCREENS ─────────────────────────────────────────────────────────────
function renderHome(){
  if(activeTab==='articles')return renderArticleHome();
  if(activeTab==='dative')return renderDativeHome();
  return renderIrregularHome();
}

function renderArticleHome(){
  const suffixes=['-ant','-chen','-e','-ei','-er','-heit','-ie','-ig','-ik','-ion','-ismus',
    '-keit','-lein','-ling','-ma','-ment','-nis','-or','-schaft','-tum','-tät','-um','-ung','-ur'];
  const semantics=['European rivers','Ge-','alcoholic drinks','car brands','days/months/seasons',
    'fruits','languages','metals','numbers and numerals','trees and flowers','venues',
    'verbal nouns','weather','young people and animals'];
  const suffixOpts=suffixes.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join('');
  const semOpts=semantics.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join('');
  return`<div class="card">
  <h2>Article Endings</h2>
  <div class="subtitle">652 nouns — identify der / die / das by suffix and semantic rules</div>
  <div class="fg"><label class="fl">Gender</label>
    <select id="a-gender"><option value="all">All genders</option>
    <option value="der">der (masculine)</option><option value="die">die (feminine)</option>
    <option value="das">das (neuter)</option></select></div>
  <div class="fg"><label class="fl">Category</label>
    <select id="a-cat"><option value="all">All categories</option>
    <optgroup label="Suffix rules">${suffixOpts}</optgroup>
    <optgroup label="Semantic rules">${semOpts}</optgroup></select></div>
  <div class="fg"><label class="fl">Questions per session</label>
    <select id="a-size"><option value="10">10</option><option value="20">20</option>
    <option value="50">50</option><option value="all">All</option></select></div>
  <button class="btn btn-primary" onclick="startArticle()">Start Quiz</button>
  <button class="btn btn-secondary" onclick="showStats()">Statistics</button>
</div>`;
}

function renderDativeHome(){
  return`<div class="card">
  <h2>Dative Verbs</h2>
  <div class="subtitle">36 verbs that require dative — danken, helfen, gefallen…</div>
  <div class="fg"><label class="fl">Mode</label>
    <select id="d-mode">
      <option value="de">German → English</option>
      <option value="en">English → German</option>
      <option value="dative">Dative article (dem/der/den)</option>
    </select></div>
  <div class="fg"><label class="fl">Questions per session</label>
    <select id="d-size"><option value="10">10</option><option value="20">20</option>
    <option value="36">All 36</option></select></div>
  <button class="btn btn-primary" onclick="startDative()">Start Quiz</button>
  <button class="btn btn-secondary" onclick="showStats()">Statistics</button>
</div>`;
}

function renderIrregularHome(){
  return`<div class="card">
  <h2>Irregular Verbs</h2>
  <div class="subtitle">97 verbs in 8 mnemonic groups — INKA, BARREL, SAUDI…</div>
  <div class="fg"><label class="fl">Mode</label>
    <select id="i-mode">
      <option value="praeteritum">Infinitive → Präteritum</option>
      <option value="perfect">Infinitive → Perfekt</option>
      <option value="both">Infinitive → Both forms</option>
      <option value="en-de">English → German infinitive</option>
    </select></div>
  <div class="fg"><label class="fl">Filter</label>
    <select id="i-filter">
      <option value="all">All verbs</option>
      <option value="due">Due for review (SM-2)</option>
      <optgroup label="Phase">
        <option value="phase1">Phase 1 (INKA, BARREL, SAUDI)</option>
        <option value="phase2">Phase 2 (USA, LASSO)</option>
        <option value="phase3">Phase 3 (POLO)</option>
        <option value="phase4">Phase 4 (MIRROR, ANACONDA)</option>
      </optgroup>
      <optgroup label="Mnemonic group">
        <option value="inka">INKA</option><option value="barrel">BARREL</option>
        <option value="saudi">SAUDI</option><option value="usa">USA</option>
        <option value="lasso">LASSO</option><option value="polo">POLO</option>
        <option value="mirror">MIRROR</option><option value="anaconda">ANACONDA</option>
      </optgroup>
    </select></div>
  <div class="fg"><label class="fl">Questions per session</label>
    <select id="i-size"><option value="10">10</option><option value="20">20</option>
    <option value="all">All</option></select></div>
  <button class="btn btn-primary" onclick="startIrregular()">Start Quiz</button>
  <button class="btn btn-secondary" onclick="showStats()">Statistics</button>
</div>`;
}

// ── START QUIZ ─────────────────────────────────────────────────────────────────
function startArticle(){
  const gender=document.getElementById('a-gender').value;
  const cat=document.getElementById('a-cat').value;
  const sz=document.getElementById('a-size').value;
  let pool=ARTICLE_WORDS.filter(w=>
    (gender==='all'||w.gender===gender)&&
    (cat==='all'||w.category===cat)
  );
  if(!pool.length){alert('No words match the selected filters.');return;}
  pool=shuffle(pool);
  if(sz!=='all'&&+sz>0)pool=pool.slice(0,+sz);
  session={module:'articles',mode:'articles',pool,index:0,correct:0,total:0,phase:'asking'};
  renderMain();
}

function startDative(){
  const mode=document.getElementById('d-mode').value;
  const sz=document.getElementById('d-size').value;
  let pool=shuffle([...DATIVE_VERBS]);
  if(sz!=='all'&&+sz>0)pool=pool.slice(0,+sz);
  session={module:'dative',mode,pool,index:0,correct:0,total:0,phase:'asking'};
  renderMain();
}

function startIrregular(){
  const mode=document.getElementById('i-mode').value;
  const filter=document.getElementById('i-filter').value;
  const sz=document.getElementById('i-size').value;
  let pool=IRREGULAR_VERBS.filter(v=>{
    if(filter==='all')return true;
    if(filter==='due')return sm2Due(progress.irregular[v.infinitive]);
    if(filter.startsWith('phase'))return v.phase===+filter.slice(5);
    return v.mnemonic===filter;
  });
  if(!pool.length){alert('No verbs match the selected filter.');return;}
  if(filter==='due'&&sz!=='all'){
    const due=pool.filter(v=>sm2Due(progress.irregular[v.infinitive]));
    const rest=pool.filter(v=>!sm2Due(progress.irregular[v.infinitive]));
    pool=[...shuffle(due),...shuffle(rest)];
  }else{
    pool=shuffle(pool);
  }
  if(sz!=='all'&&+sz>0)pool=pool.slice(0,+sz);
  session={module:'irregular',mode,pool,index:0,correct:0,total:0,phase:'asking'};
  renderMain();
}

// ── QUIZ RENDER ───────────────────────────────────────────────────────────────
function renderQuiz(){
  const item=session.pool[session.index];
  const prog=pct(session.index,session.pool.length);
  const pbar=`<div class="pbar"><div class="pfill" style="width:${prog}%"></div></div>`;
  const ctr=`<div class="counter"><span>${session.index+1} / ${session.pool.length}</span><span>✓ ${session.correct}</span></div>`;
  const q=renderQuestion(item);
  const ans=session.phase==='asking'?renderAnswerInput(item):renderFeedbackSection(item);
  return pbar+ctr+q+ans;
}

function renderQuestion(item){
  if(session.module==='articles'){
    const weak=item.weak?`<span class="weak-badge">⚠ exceptions</span>`:'';
    return`<div class="card"><div class="q-word">${esc(item.german)}</div>
    <div class="q-hint">${esc(item.english)}</div>
    <div class="q-hint"><span class="tag">${esc(item.category)}</span>${weak}</div></div>`;
  }
  if(session.module==='dative'){
    if(session.mode==='dative'){
      const sent=item.example.replace('___',`<span class="ex-blank">___</span>`);
      return`<div class="card"><div class="ex-sent">${sent}</div>
      <button class="hint-btn" id="hint-btn" onclick="toggleHint()">Show noun hint</button>
      <div class="hint-txt" id="hint-txt" style="display:none">${esc(item.noun_base)}</div></div>`;
    }
    if(session.mode==='de'){
      return`<div class="card"><div class="q-word">${esc(item.german)}</div>
      <button class="hint-btn" id="hint-btn" onclick="toggleHint()">Memory hint</button>
      <div class="hint-txt" id="hint-txt" style="display:none">${esc(item.memory)}</div></div>`;
    }
    // en→de
    return`<div class="card"><div class="q-word">${esc(item.english)}</div>
    <button class="hint-btn" id="hint-btn" onclick="toggleHint()">Memory hint</button>
    <div class="hint-txt" id="hint-txt" style="display:none">${esc(item.memory)}</div></div>`;
  }
  if(session.module==='irregular'){
    const c=MCOLOR[item.mnemonic]||'#64748b';
    const mnTag=`<span class="tag tag-mnemonic" style="background:${c}">${item.mnemonic.toUpperCase()} · ${esc(item.pattern)}</span>`;
    if(session.mode==='en-de'){
      return`<div class="card"><div class="q-word">${esc(item.english)}</div>
      <div class="q-hint">${mnTag}</div></div>`;
    }
    return`<div class="card"><div class="q-word">${esc(item.infinitive)}</div>
    <div class="q-hint">${esc(item.english)}</div><div class="q-hint">${mnTag}</div></div>`;
  }
  return '';
}

function renderAnswerInput(item){
  if(session.module==='articles'){
    return`<button class="btn btn-der" onclick="answer('der')">DER</button>
    <button class="btn btn-die" onclick="answer('die')">DIE</button>
    <button class="btn btn-das" onclick="answer('das')">DAS</button>`;
  }
  if(session.module==='dative'){
    if(session.mode==='dative'){
      return`<button class="btn btn-dem" onclick="answer('dem')">DEM</button>
      <button class="btn btn-der2" onclick="answer('der')">DER</button>
      <button class="btn btn-den" onclick="answer('den')">DEN</button>`;
    }
    const key=session.mode==='de'?'english':'german';
    const choices=buildChoices(item[key],DATIVE_VERBS,key);
    return choices.map(c=>`<button class="btn btn-choice" data-val="${esc(c)}">${esc(c)}</button>`).join('');
  }
  if(session.module==='irregular'){
    if(session.mode==='en-de'){
      const sameGroup=IRREGULAR_VERBS.filter(v=>v.mnemonic===item.mnemonic&&v.infinitive!==item.infinitive);
      const others=IRREGULAR_VERBS.filter(v=>v.mnemonic!==item.mnemonic);
      const dist=[...shuffle(sameGroup),...shuffle(others)];
      const chosen=[...new Set(dist.map(v=>v.infinitive))].slice(0,3);
      const choices=shuffle([item.infinitive,...chosen]);
      return choices.map(c=>`<button class="btn btn-choice" data-val="${esc(c)}">${esc(c)}</button>`).join('');
    }
    if(session.mode==='praeteritum'){
      return`<div class="in-label">Präteritum:</div>
      <input class="text-in" id="ans1" autocomplete="off" autocorrect="off" spellcheck="false" autocapitalize="none" placeholder="Präteritum…">
      <button class="btn btn-submit" onclick="answerTyped()">Check</button>
      <button class="btn btn-reveal" onclick="reveal()">Reveal answer</button>`;
    }
    if(session.mode==='perfect'){
      return`<div class="in-label">Partizip II (Perfekt):</div>
      <input class="text-in" id="ans1" autocomplete="off" autocorrect="off" spellcheck="false" autocapitalize="none" placeholder="Perfekt…">
      <button class="btn btn-submit" onclick="answerTyped()">Check</button>
      <button class="btn btn-reveal" onclick="reveal()">Reveal answer</button>`;
    }
    // both
    return`<div class="in-label">Präteritum:</div>
    <input class="text-in" id="ans1" autocomplete="off" autocorrect="off" spellcheck="false" autocapitalize="none" placeholder="Präteritum…">
    <div class="in-label">Partizip II:</div>
    <input class="text-in" id="ans2" autocomplete="off" autocorrect="off" spellcheck="false" autocapitalize="none" placeholder="Partizip II…">
    <button class="btn btn-submit" onclick="answerTyped()">Check</button>
    <button class="btn btn-reveal" onclick="reveal()">Reveal answer</button>`;
  }
  return '';
}

function renderFeedbackSection(item){
  const ok=session.lastCorrect;
  const cls=ok?'fb fb-ok':'fb fb-err';
  const icon=ok?'✓':'✗';
  let ans='',exp='';
  if(session.module==='articles'){
    ans=`${item.gender.toUpperCase()} ${esc(item.german)}`;
    exp=esc(item.rule);
  }else if(session.module==='dative'){
    if(session.mode==='dative'){
      const filled=item.example.replace('___',`<strong>${esc(item.article).toUpperCase()}</strong>`);
      const genderMap={'der Arzt':'masc','die Frau':'fem','das Kind':'neut'};
      const rule=item.article==='den'?'plural → den':item.article==='der'?'die → der (feminine)':item.noun_base.startsWith('der')?'der → dem (masculine)':'das → dem (neuter)';
      ans=filled;
      exp=`${esc(item.noun_base)} → <strong>${esc(item.article)}</strong> &nbsp; (${rule})`;
    }else{
      ans=`${esc(item.german)} = ${esc(item.english)}`;
      exp=esc(item.memory);
    }
  }else if(session.module==='irregular'){
    const c=MCOLOR[item.mnemonic]||'#64748b';
    ans=`${esc(item.infinitive)} → <strong>${esc(item.praeteritum)}</strong> / ist/hat <strong>${esc(item.perfect)}</strong>`;
    exp=`<span style="color:${c};font-weight:700">${item.mnemonic.toUpperCase()}</span> · ${esc(item.pattern)}`;
  }
  return`<div class="${cls}"><div class="fb-ans">${icon} ${ans}</div><div class="fb-exp">${exp}</div></div>
  <button class="btn btn-primary" onclick="cont()">Continue →</button>`;
}

// ── ANSWER HANDLERS ──────────────────────────────────────────────────────────
function answer(val){
  if(session.phase!=='asking')return;
  const item=session.pool[session.index];
  let ok=false;
  if(session.module==='articles'){
    ok=val===item.gender;
    const e=progress.articles[item.german]||(progress.articles[item.german]={correct:0,incorrect:0});
    ok?e.correct++:e.incorrect++;
  }else if(session.module==='dative'){
    if(session.mode==='dative'){
      ok=val===item.article;
      const e=progress.dative[item.german]||(progress.dative[item.german]={correct:0,incorrect:0,dative_correct:0,dative_incorrect:0});
      ok?e.dative_correct++:e.dative_incorrect++;
    }else{
      const key=session.mode==='de'?'english':'german';
      ok=val===item[key];
      const e=progress.dative[item.german]||(progress.dative[item.german]={correct:0,incorrect:0,dative_correct:0,dative_incorrect:0});
      ok?e.correct++:e.incorrect++;
    }
  }else if(session.module==='irregular'&&session.mode==='en-de'){
    ok=val===item.infinitive;
    const e=progress.irregular[item.infinitive]||(progress.irregular[item.infinitive]=sm2Def());
    sm2Update(e,ok);
  }
  if(ok)session.correct++;
  session.total++;
  session.lastCorrect=ok;
  session.phase='feedback';
  saveProgress();
  renderMain();
}

function answerTyped(){
  if(session.phase!=='asking')return;
  const item=session.pool[session.index];
  const a1=document.getElementById('ans1')?.value||'';
  const a2=document.getElementById('ans2')?.value||'';
  let ok=false;
  if(session.mode==='praeteritum'){
    ok=match(a1,item.praeteritum);
  }else if(session.mode==='perfect'){
    ok=match(a1,item.perfect);
  }else{
    // both
    const ok1=match(a1,item.praeteritum);
    const ok2=match(a2,item.perfect);
    ok=ok1&&ok2;
  }
  const e=progress.irregular[item.infinitive]||(progress.irregular[item.infinitive]=sm2Def());
  sm2Update(e,ok);
  if(ok)session.correct++;
  session.total++;
  session.lastCorrect=ok;
  session.phase='feedback';
  saveProgress();
  renderMain();
}

function reveal(){
  const item=session.pool[session.index];
  const e=progress.irregular[item.infinitive]||(progress.irregular[item.infinitive]=sm2Def());
  sm2Update(e,false);
  session.total++;
  session.lastCorrect=false;
  session.phase='feedback';
  saveProgress();
  renderMain();
}

function cont(){
  session.index++;
  if(session.index>=session.pool.length){
    session.phase='end';
  }else{
    session.phase='asking';
  }
  renderMain();
}

function toggleHint(){
  const btn=document.getElementById('hint-btn');
  const txt=document.getElementById('hint-txt');
  if(btn&&txt){btn.style.display='none';txt.style.display='block';}
}

function attachQuizHandlers(){
  // Multiple choice buttons (data-val avoids onclick quoting issues)
  document.querySelectorAll('button[data-val]').forEach(btn=>{
    btn.addEventListener('click',()=>answer(btn.dataset.val));
  });
  // Enter key submits typed answers
  document.querySelectorAll('.text-in').forEach(inp=>{
    inp.addEventListener('keydown',e=>{if(e.key==='Enter')answerTyped();});
  });
}

// ── END SCREEN ────────────────────────────────────────────────────────────────
function renderEnd(){
  const p=pct(session.correct,session.total);
  const msg=p>=90?'Ausgezeichnet! 🎉':p>=70?'Good progress! Keep practicing.':'Keep studying! Focus on the patterns.';
  return`<div class="card" style="text-align:center">
  <div class="score-big" style="color:${p>=70?'var(--green)':'var(--red)'}">${p}%</div>
  <div style="font-size:20px;font-weight:700;margin-bottom:8px">${session.correct} / ${session.total} correct</div>
  <div class="score-msg">${esc(msg)}</div>
  </div>
  <button class="btn btn-primary" onclick="quizAgain()">Quiz Again</button>
  <button class="btn btn-secondary" onclick="showStats()">See Statistics</button>
  <button class="btn btn-secondary" onclick="goHome()">Change Settings</button>`;
}

function quizAgain(){
  const s=session;
  session={...s,index:0,correct:0,total:0,phase:'asking',
           pool:shuffle([...s.pool])};
  renderMain();
}
function goHome(){session=null;renderMain();}
function showStats(){if(session)session.phase='stats';else session={phase:'stats'};renderMain();}

// ── STATS SCREENS ─────────────────────────────────────────────────────────────
function renderStats(){
  if(activeTab==='articles')return renderArticleStats();
  if(activeTab==='dative')return renderDativeStats();
  return renderIrregularStats();
}

function renderArticleStats(){
  const p=progress.articles;
  let tc=0,ti=0;
  const byGender={der:{c:0,i:0},die:{c:0,i:0},das:{c:0,i:0}};
  const byCat={};
  const hard=[];
  for(const w of ARTICLE_WORDS){
    const e=p[w.german];if(!e)continue;
    tc+=e.correct;ti+=e.incorrect;
    byGender[w.gender].c+=e.correct;byGender[w.gender].i+=e.incorrect;
    if(!byCat[w.category])byCat[w.category]={c:0,i:0};
    byCat[w.category].c+=e.correct;byCat[w.category].i+=e.incorrect;
    const t=e.correct+e.incorrect;
    if(t>=2)hard.push({w:w.german,g:w.gender,c:e.correct,t});
  }
  hard.sort((a,b)=>a.c/a.t-b.c/b.t);
  const tot=tc+ti;
  const gRows=['der','die','das'].map(g=>{
    const e=byGender[g];const t=e.c+e.i;
    const col=g==='der'?'var(--blue)':g==='die'?'var(--magenta)':'var(--green)';
    return`<div class="stat-row"><span style="color:${col};font-weight:700">${g}</span>
    <span class="stat-acc">${e.c}/${t} (${pct(e.c,t)}%)</span></div>`;
  }).join('');
  const catRows=Object.entries(byCat).sort((a,b)=>pct(a[1].c,a[1].c+a[1].i)-pct(b[1].c,b[1].c+b[1].i))
    .slice(0,10).map(([cat,e])=>{const t=e.c+e.i;
    return`<div class="stat-row"><span>${esc(cat)}</span><span class="stat-acc">${pct(e.c,t)}%</span></div>`;}).join('');
  const hardRows=hard.slice(0,8).map(h=>{
    const col=h.g==='der'?'var(--blue)':h.g==='die'?'var(--magenta)':'var(--green)';
    return`<div class="stat-row"><span style="color:${col}">${esc(h.w)}</span>
    <span class="stat-acc">${pct(h.c,h.t)}%</span></div>`;}).join('');
  return`<div class="card"><h2>Articles Statistics</h2>
  <div class="subtitle">Overall: ${tc}/${tot} (${pct(tc,tot)}%) — ${Object.keys(p).length} words practiced</div>
  <h3>By Gender</h3>${gRows}
  ${catRows?`<h3>Weakest Categories</h3>${catRows}`:''}
  ${hardRows?`<h3>Hardest Words</h3>${hardRows}`:''}
  </div>
  <button class="btn btn-secondary" onclick="goHome()">← Back</button>
  <button class="btn btn-secondary" style="color:var(--red)" onclick="resetModule('articles')">Reset Progress</button>`;
}

function renderDativeStats(){
  const p=progress.dative;
  let tc=0,ti=0,dc=0,di=0;
  const hard=[];
  for(const v of DATIVE_VERBS){
    const e=p[v.german];if(!e)continue;
    tc+=e.correct;ti+=e.incorrect;
    dc+=e.dative_correct||0;di+=e.dative_incorrect||0;
    const t=(e.correct+e.incorrect)+(e.dative_correct||0)+(e.dative_incorrect||0);
    const c=e.correct+(e.dative_correct||0);
    if(t>=2)hard.push({v:v.german,c,t});
  }
  hard.sort((a,b)=>a.c/a.t-b.c/b.t);
  const totTrans=tc+ti,totDat=dc+di;
  const hardRows=hard.slice(0,8).map(h=>
    `<div class="stat-row"><span>${esc(h.v)}</span><span class="stat-acc">${pct(h.c,h.t)}%</span></div>`).join('');
  return`<div class="card"><h2>Dative Statistics</h2>
  <div class="subtitle">${Object.keys(p).length} / 36 verbs practiced</div>
  <h3>Translation</h3>
  <div class="stat-row"><span>Correct answers</span><span class="stat-acc">${tc}/${totTrans} (${pct(tc,totTrans)}%)</span></div>
  <h3>Dative Article</h3>
  <div class="stat-row"><span>Correct answers</span><span class="stat-acc">${dc}/${totDat} (${pct(dc,totDat)}%)</span></div>
  ${hardRows?`<h3>Hardest Verbs</h3>${hardRows}`:''}
  </div>
  <button class="btn btn-secondary" onclick="goHome()">← Back</button>
  <button class="btn btn-secondary" style="color:var(--red)" onclick="resetModule('dative')">Reset Progress</button>`;
}

function renderIrregularStats(){
  const p=progress.irregular;
  let tc=0,ti=0;
  const byMnem={};
  const due=[];
  const hard=[];
  for(const v of IRREGULAR_VERBS){
    const e=p[v.infinitive];
    if(sm2Due(e))due.push(v.infinitive);
    if(!e)continue;
    tc+=e.correct;ti+=e.incorrect;
    if(!byMnem[v.mnemonic])byMnem[v.mnemonic]={c:0,i:0};
    byMnem[v.mnemonic].c+=e.correct;byMnem[v.mnemonic].i+=e.incorrect;
    const t=e.correct+e.incorrect;
    if(t>=2)hard.push({v:v.infinitive,m:v.mnemonic,c:e.correct,t});
  }
  hard.sort((a,b)=>a.c/a.t-b.c/b.t);
  const tot=tc+ti;
  const mRows=Object.entries(byMnem).map(([m,e])=>{
    const t=e.c+e.i;const col=MCOLOR[m]||'#64748b';
    return`<div class="stat-row"><span style="color:${col};font-weight:700">${m.toUpperCase()}</span>
    <span class="stat-acc">${e.c}/${t} (${pct(e.c,t)}%)</span></div>`;}).join('');
  const hardRows=hard.slice(0,8).map(h=>{
    const col=MCOLOR[h.m]||'#64748b';
    return`<div class="stat-row"><span style="color:${col}">${esc(h.v)}</span>
    <span class="stat-acc">${pct(h.c,h.t)}%</span></div>`;}).join('');
  return`<div class="card"><h2>Irregular Verbs Statistics</h2>
  <div class="subtitle">Overall: ${tc}/${tot} (${pct(tc,tot)}%) — ${Object.keys(p).length}/81 practiced</div>
  <div class="stat-row"><span>Due for review today</span><span class="stat-acc" style="color:${due.length>0?'var(--orange)':'var(--green)'}">${due.length}</span></div>
  ${mRows?`<h3>By Mnemonic Group</h3>${mRows}`:''}
  ${hardRows?`<h3>Hardest Verbs</h3>${hardRows}`:''}
  </div>
  <button class="btn btn-secondary" onclick="goHome()">← Back</button>
  <button class="btn btn-secondary" style="color:var(--red)" onclick="resetModule('irregular')">Reset Progress</button>`;
}

function resetModule(mod){
  if(!confirm(`Reset all ${mod} progress?`))return;
  progress[mod]={};saveProgress();renderMain();
}

// ── DATIVE RULE HELPER ────────────────────────────────────────────────────────
// determine the dative rule from noun_base
function datRule(noun_base){
  if(noun_base.startsWith('der'))return'der → dem (masc./neut.)';
  if(noun_base.startsWith('die'))return'die → der (fem.)';
  if(noun_base.startsWith('das'))return'das → dem (neut.)';
  return'plural → den';
}

// ── INIT ──────────────────────────────────────────────────────────────────────
renderMain();
