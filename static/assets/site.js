/* Al-Fatiem Alarabi site script: language switch, menu, lightbox, shared data */

(function(){
var LS=null;try{LS=window.localStorage}catch(e){}
function getLang(){try{var l=LS&&LS.getItem('afl');if(l==='ar'||l==='en')return l}catch(e){}return 'en'}
window.AFL={lang:getLang(),subs:[],t:function(o){return o==null?'':(typeof o==='string'?o:(o[AFL.lang]||o.en))}};
function applyLang(l){AFL.lang=l;var h=document.documentElement;h.lang=l;h.dir=l==='ar'?'rtl':'ltr';
 try{LS&&LS.setItem('afl',l)}catch(e){}
 document.querySelectorAll('option[data-en]').forEach(function(o){o.textContent=o.getAttribute('data-'+l)});
 document.querySelectorAll('[data-ph-en]').forEach(function(e){e.placeholder=e.getAttribute('data-ph-'+l)});
 document.querySelectorAll('.lang').forEach(function(b){b.textContent=l==='ar'?'English':'عربي'});
 AFL.subs.forEach(function(f){f()})}
AFL.apply=applyLang;
document.addEventListener('DOMContentLoaded',function(){
 applyLang(AFL.lang);
 document.querySelectorAll('.lang').forEach(function(b){b.addEventListener('click',function(){applyLang(AFL.lang==='ar'?'en':'ar')})});
 var mb=document.querySelector('.menu-btn'),nv=document.querySelector('.nav');
 if(mb){mb.addEventListener('click',function(){var o=nv.classList.toggle('open');mb.setAttribute('aria-expanded',o)});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nv.classList.contains('open')){nv.classList.remove('open');mb.setAttribute('aria-expanded','false');mb.focus()}});document.addEventListener('click',function(e){if(nv.classList.contains('open')&&!e.target.closest('.nav')&&!e.target.closest('.menu-btn')){nv.classList.remove('open');mb.setAttribute('aria-expanded','false')}})}
 var lb=document.querySelector('.lb');
 if(lb){var li=lb.querySelector('img'),gal=[],gi=0,pv=lb.querySelector('.pv'),nx=lb.querySelector('.nx');
  var lbx=lb.querySelector('.x'),opener=null;function show(){if(!lb.classList.contains('open'))opener=document.activeElement;li.src=gal[gi];li.alt=AFL.lang==='ar'?'صورة مكبّرة':'Enlarged image';pv.hidden=nx.hidden=gal.length<2;lb.classList.add('open');lbx.focus()}
  function hide(){lb.classList.remove('open');if(opener&&opener.focus)opener.focus()}
  document.addEventListener('click',function(e){var g=e.target.closest('[data-gal]');
   if(g){gal=g.getAttribute('data-gal').split(',').map(function(k){return k.indexOf('/')>-1?k:'img/'+k+'.webp'});gi=+(g.getAttribute('data-start')||0);show();return}
   var im=e.target.closest('[data-zoom]');if(im){gal=[im.getAttribute('data-zoom')];gi=0;show();return}
   if(e.target.closest('.lb .pv')){gi=(gi+gal.length-1)%gal.length;show();return}
   if(e.target.closest('.lb .nx')){gi=(gi+1)%gal.length;show();return}
   if(lb.classList.contains('open')&&(e.target.closest('.lb .x')||e.target===lb))hide()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&lb.classList.contains('open'))hide();if(lb.classList.contains('open')&&gal.length>1){if(e.key==='ArrowRight'){gi=(gi+1)%gal.length;show()}if(e.key==='ArrowLeft'){gi=(gi+gal.length-1)%gal.length;show()}}})}
 (window.AFL_INIT||[]).forEach(function(f){f()});
 applyLang(AFL.lang);
});
})();

/* ---------- shared data ---------- */
var LAYERS=[
 {id:'sub',n:1,mm:'200',w:70,c:'--l-sub',en:'Substrate (wall)',ar:'الجدار (الركيزة)',
  de:'The existing concrete or block wall. We inspect it and clean it before any material goes on.',da:'الجدار القائم من الخرسانة أو البلوك. نفحصه وننظّفه قبل تركيب أي مادة.',mat:''},
 {id:'adh',n:2,mm:'5',w:20,c:'--l-adh',en:'Adhesive',ar:'مادة اللصق',
  de:'Bonds the insulation board to the wall.',da:'تثبّت لوح العزل على الجدار.',mat:'Plafixx 910 Adhesive & Base Coat (Plafixx Dry Mix Company W.L.L.)'},
 {id:'eps',n:3,mm:'55+',w:220,c:'--l-eps',en:'Insulation board (EPS)',ar:'لوح العزل (بوليسترين)',
  de:'Expanded polystyrene. The registered system is 55 mm minimum, with a thermal conductivity of 0.0382 W/m·K.',da:'بوليسترين ممدّد. النظام المسجّل بسماكة 55 مم كحد أدنى وموصلية حرارية 0.0382 واط/م·كلفن.',mat:'Bahrain Polystyrene Factory W.L.L. · 18.75 kg/m³'},
 {id:'dow',n:4,mm:'',w:0,c:'--l-line',en:'Mechanical fixing (dowels)',ar:'التثبيت الميكانيكي (مسامير التثبيت)',
  de:'Dowels pass through the board into the wall as a second fixing on top of the adhesive.',da:'مسامير تخترق اللوح إلى الجدار كتثبيت إضافي فوق مادة اللصق.',mat:'Tecfi S.p.A – Klimas sp. z o.o.'},
 {id:'mesh',n:5,mm:'',w:0,c:'--l-fin',en:'Glass-fibre mesh',ar:'شبك الألياف الزجاجية',
  de:'Reinforcing mesh set into the basecoat. It spreads stress and limits cracking.',da:'شبك تسليح يُدفن في طبقة الأساس. يوزّع الإجهاد ويحدّ من التشقق.',mat:'AL FATIEM EIFS PRO: Dakota Group S.a.S · AL FATIEM EIFS: Dr. Gunther Kast GmbH & Co / Valmiera Glass Group'},
 {id:'base',n:6,mm:'4',w:16,c:'--l-base',en:'Basecoat',ar:'طبقة الأساس',
  de:'The reinforced render layer that protects the board and takes the finish.',da:'طبقة اللياسة المسلّحة التي تحمي اللوح وتستقبل التشطيب.',mat:'Plafixx 910 Adhesive & Base Coat (Plafixx Dry Mix Company W.L.L.)'},
 {id:'pri',n:7,mm:'1',w:6,c:'--l-prim',en:'Primer',ar:'طبقة التأسيس',
  de:'Prepares the basecoat so the finish bonds evenly.',da:'تهيّئ طبقة الأساس ليلتصق التشطيب بشكل متجانس.',mat:''},
 {id:'fin',n:8,mm:'2',w:8,c:'--l-fin',en:'Decorative finish',ar:'التشطيب الزخرفي',
  de:'The colour and texture you see. It also weatherproofs the wall.',da:'اللون والملمس الظاهران. كما يحمي الجدار من العوامل الجوية.',mat:''}
];
function layerSVG(host,interactive){
 var X=10,bands=[],ids={};
 var s='<svg class="sec-svg" viewBox="0 0 400 250" role="img" aria-label="Wall section"><defs>'+
 '<pattern id="hat" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" style="fill:var(--l-sub)"/><line x1="0" y1="0" x2="0" y2="8" style="stroke:var(--l-line);stroke-width:1;opacity:.45"/></pattern>'+
 '<pattern id="dot" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" style="fill:var(--l-eps)"/><circle cx="4.5" cy="4.5" r="1.1" style="fill:var(--l-line);opacity:.28"/></pattern></defs>';
 s+='<g id="bands">';
 var delay=0;
 LAYERS.forEach(function(L){if(!L.w)return;
  var fill=L.id==='sub'?'url(#hat)':(L.id==='eps'?'url(#dot)':'var('+L.c+')');
  s+='<rect class="band-r grow" data-id="'+L.id+'" x="'+X+'" y="30" width="'+L.w+'" height="180" style="fill:'+fill+';animation-delay:'+delay+'ms"/>';
  ids[L.id]=X;X+=L.w;delay+=110});
 // mesh line (inside basecoat) and dowels (through adhesive + EPS)
 var bx=ids.base+5;
 s+='<line class="band-r" data-id="mesh" x1="'+bx+'" x2="'+bx+'" y1="30" y2="210" style="stroke:var(--blue);stroke-width:2.5;stroke-dasharray:3 2"/>';
 [60,120,180].forEach(function(y){s+='<g class="band-r" data-id="dow" style="stroke:var(--l-line);fill:var(--l-line)"><line x1="'+(ids.sub+55)+'" x2="'+(ids.eps+196)+'" y1="'+y+'" y2="'+y+'" stroke-width="2.2"/><rect x="'+(ids.eps+196)+'" y="'+(y-5)+'" width="5" height="10"/></g>'});
 s+='</g>';
 // substrate break marks
 s+='<path d="M10 30 l4 6 -4 6 4 6 -4 6" class="dim"/>';
 s+='<text x="12" y="226">INT.</text><text x="'+(X-24)+'" y="226">EXT.</text>';
 s+='<path class="dim" d="M'+ids.adh+' 238 H'+X+' M'+ids.adh+' 233 v10 M'+X+' 233 v10"/><text x="'+(ids.adh+((X-ids.adh)/2)-30)+'" y="248">≈ 67 mm</text>';
 s+='</svg>';host.innerHTML=s;
 var svg=host.querySelector('svg');
 return {highlight:function(id){var g=svg.querySelector('#bands');
   if(!id){g.classList.remove('dim-on');svg.querySelectorAll('.on').forEach(function(e){e.classList.remove('on')});return}
   g.classList.add('dim-on');svg.querySelectorAll('.band-r').forEach(function(e){e.classList.toggle('on',e.getAttribute('data-id')===id)})}};
}
function legendHTML(){return LAYERS.filter(function(L){return L.w}).map(function(L){var f=L.id==='sub'?'var(--l-sub)':(L.id==='eps'?'var(--l-eps)':'var('+L.c+')');return '<span><i style="background:'+f+'"></i>'+AFL.t({en:L.en,ar:L.ar})+'</span>'}).join('')}

var PROJECTS=(function(){var e=document.getElementById('projects-data');try{return e?JSON.parse(e.textContent):[]}catch(x){return []}})();
function fmtA(a){return a==null?'—':Math.round(a).toLocaleString('en-US')+(AFL.lang==='ar'?' م²':' m²')}
function totalArea(list){return list.reduce(function(s,p){return s+(p.a||0)},0)}

function projCard(p){
 var tx=AFL.t(p),ph=p.ph||[];
 var th=ph.length?'<button type="button" class="th" data-gal="'+ph.join(',')+'" aria-label="'+tx.replace(/"/g,'')+'"><img src="'+(ph[0].indexOf('/')>-1?ph[0]:'img/'+ph[0]+'.webp')+'" alt="" loading="lazy">'+(ph.length>1?'<span class="count">'+ph.length+' '+AFL.t({en:'photos',ar:'صور'})+'</span>':'')+'</button>':'<div class="th none">AF</div>';
 var svc=p.sv.map(function(s){return '<span class="'+s+'">'+(s==='eifs'?AFL.t({en:'Insulation',ar:'عزل'}):AFL.t({en:'Scaffolding',ar:'سقالات'}))+'</span>'}).join('');
 var cl=[];if(p.cl)cl.push(AFL.t(p.cl));if(p.cons)cl.push('<span>'+AFL.t({en:'Consultant',ar:'الاستشاري'})+': '+p.cons+'</span>');
 var chain=p.chain?'<p class="note" style="margin-top:8px">'+AFL.t(p.chain)+'</p>':'';
 return '<article class="prow">'+th+'<div><h3>'+tx+'</h3><p class="sub">'+AFL.t(p.loc)+' · '+p.y+'</p><div class="svc">'+svc+'</div>'+chain+'</div><div class="area">'+(p.a?'<bdi dir="ltr">'+fmtA(p.a)+'</bdi><small>'+AFL.t({en:'insulated area',ar:'المساحة المعزولة'})+'</small>':'—')+'</div><div class="cl">'+(cl.join('')||'—')+'</div></article>'}

