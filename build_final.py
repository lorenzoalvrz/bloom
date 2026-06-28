import json
d=json.load(open("embed_portal.json"))
SPL=json.dumps(d["petalsSplit"]);POS=json.dumps(d["petalPos"]);COLS=json.dumps(d["petalCols"]);GLOW=d["glow"]
EY=json.dumps(d["eyes"]);PO=json.dumps(d["portal"]);RM=d["room"];HEAD=d["head"];ROOMBG=d["roomBg"];SFR=json.dumps(d["screenFrames"]);SBOX=json.dumps(d["screenBox"]);SMASK=d["screenMask"];GLAREPOS=json.dumps(d["glarePos"]);GLARE=d["glare"];NGA=json.dumps(d["noteGifA"]);NGB=json.dumps(d["noteGifB"]);NC=d["noteCol"];WMPFRAME=d["wmpFrame"];XBOX=d["xboxPanel"];FONTVT=d["fontVT"];FONTSE=d["fontSE"];BGFLOWER=d["bgFlower"];BGVIDEO=d["bgVideo"];BGFRAMES=json.dumps(d["bgFrames"]);MP=d["mp"];BACKBTN=d["backbtn"];BOOT=d["boot"];DS=d["ds"]
THREE=open("three.min.js").read()

CORE=r"""
const PETS=__SPL__,POS=__POS__,COLS=__COLS__,GLOW="__GLOW__",EYES=__EY__,PORTAL=__PO__,RM="__RM__";
const HEAD="__HEAD__",ROOMBG="__ROOMBG__",SFR=__SFR__,SBOX=__SBOX__,SMASK="__SMASK__",GLAREPOS=__GLAREPOS__,GLARE="__GLARE__",NGA=__NGA__,NGB=__NGB__,NC="__NC__";
const ROOM_W=2.25,ROOM_Z=-2.0,MASK_R=0.30;
const Z_REST=3.5,Z_WAKE=2.2,Z_END=-0.05,DROP_Z=0.41;
const scene=new THREE.Scene();
const cam=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,0.1,100);cam.position.set(0,0,Z_REST);
const rnd=new THREE.WebGLRenderer({canvas:document.getElementById('c'),antialias:true,alpha:true,stencil:true});
rnd.setPixelRatio(Math.min(devicePixelRatio,2));rnd.setSize(innerWidth,innerHeight);
const loader=new THREE.TextureLoader();
function tex(u){const t=loader.load(u);t.minFilter=THREE.LinearFilter;t.magFilter=THREE.LinearFilter;return t;}
function preload(a){return a.map(u=>tex(u));}

// shared single-light uniforms: the SELECTED petal's glow lights the whole flat scene per-pixel
const lightU={uLightPos:{value:new THREE.Vector2(0,0.57)},uLightColor:{value:new THREE.Color(COLS[0])},
  uWake:{value:0},uAmbient:{value:0.12},uIntensity:{value:1.0},uRadius:{value:0.6},uTint:{value:0.34},
  uWhitePos:{value:new THREE.Vector2(0,0.57)},uWhiteI:{value:0},uWhiteR:{value:0.35},
  uMouthPos:{value:new THREE.Vector2(0,-0.02)},uMouthI:{value:0},uMouthR:{value:0.72}};
const VS="varying vec2 vUv;varying vec2 vW;void main(){vUv=uv;vec4 wp=modelMatrix*vec4(position,1.0);vW=wp.xy;gl_Position=projectionMatrix*viewMatrix*wp;}";
const FS="uniform sampler2D uMap;uniform vec2 uLightPos,uWhitePos,uMouthPos;uniform vec3 uLightColor;uniform float uWake,uAmbient,uIntensity,uRadius,uTint,uWhiteI,uWhiteR,uMouthI,uMouthR;varying vec2 vUv;varying vec2 vW;void main(){vec4 tx=texture2D(uMap,vUv);float d1=distance(vW,uLightPos);float r1=d1/uRadius;float a1=uIntensity/(1.0+r1*r1);float d2=distance(vW,uWhitePos);float r2=d2/uWhiteR;float a2=uWhiteI/(1.0+r2*r2);float d3=distance(vW,uMouthPos);float r3=d3/uMouthR;float a3=uMouthI/(1.0+r3*r3);vec3 f=vec3(uAmbient)+mix(vec3(1.0),uLightColor,uTint)*a1+vec3(1.0)*a2+vec3(1.0)*a3;f=min(f,vec3(2.4));vec3 lit=tx.rgb*f;vec3 col=mix(tx.rgb,lit,uWake);gl_FragColor=vec4(col,tx.a);}";
function litMat(map){return new THREE.ShaderMaterial({uniforms:Object.assign({uMap:{value:map}},lightU),vertexShader:VS,fragmentShader:FS,transparent:true,depthTest:false,depthWrite:false});}

const wheel=new THREE.Group();scene.add(wheel);
const glowTex=tex(GLOW),petalM=[],glowM=[],st=[];
for(let i=0;i<6;i++){
  const pm=new THREE.Mesh(new THREE.PlaneGeometry(2.4,2.4),litMat(tex(PETS[i])));pm.renderOrder=1;wheel.add(pm);petalM.push(pm);
  const gm=new THREE.Mesh(new THREE.PlaneGeometry(1.55,1.55),new THREE.MeshBasicMaterial({map:glowTex,transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,color:new THREE.Color(COLS[i]),opacity:0}));
  gm.position.set(POS[i][0],POS[i][1],0.0);gm.renderOrder=0;pm.add(gm);glowM.push(gm);
  const a=Math.atan2(POS[i][1],POS[i][0]);
  st.push({dir:[Math.cos(a),Math.sin(a)],b1:0.5+Math.random()*0.5,p1:Math.random()*6.28,b2:0.8+Math.random()*0.7,p2:Math.random()*6.28,gf:0.4+Math.random()*0.5,gp:Math.random()*6.28,sc:1,on:1});
}
const pick=new THREE.Mesh(new THREE.PlaneGeometry(2.4,2.4),new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthWrite:false}));pick.renderOrder=-1;wheel.add(pick);

const eyesTex=preload(EYES),portalTex=preload(PORTAL);
const faceMat=litMat(eyesTex[0]);
const face=new THREE.Mesh(new THREE.PlaneGeometry(0.62,0.62),faceMat);face.position.z=0.02;face.renderOrder=4;scene.add(face);
function setFace(tx){faceMat.uniforms.uMap.value=tx;}
const mouthGlow=new THREE.Mesh(new THREE.PlaneGeometry(1.5,1.5),new THREE.MeshBasicMaterial({map:glowTex,transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,color:new THREE.Color(0xffffff),opacity:0}));
mouthGlow.position.set(0,-0.02,0.03);mouthGlow.renderOrder=5;scene.add(mouthGlow);

const maskMat=new THREE.MeshBasicMaterial({depthTest:false,depthWrite:false,colorWrite:false});
maskMat.stencilWrite=true;maskMat.stencilRef=1;maskMat.stencilFunc=THREE.AlwaysStencilFunc;
maskMat.stencilZPass=THREE.ReplaceStencilOp;maskMat.stencilFail=THREE.ReplaceStencilOp;maskMat.stencilZFail=THREE.ReplaceStencilOp;
const maskCircle=new THREE.Mesh(new THREE.CircleGeometry(MASK_R,72),maskMat);maskCircle.position.set(0,0,0.001);maskCircle.renderOrder=2;face.add(maskCircle);
// every layer of the room reads the SAME stencil the flower uses, so the whole live scene reveals through the mouth
function stencilRead(mat){mat.stencilWrite=true;mat.stencilRef=1;mat.stencilFunc=THREE.EqualStencilFunc;mat.stencilFail=THREE.KeepStencilOp;mat.stencilZFail=THREE.KeepStencilOp;mat.stencilZPass=THREE.KeepStencilOp;return mat;}
const insGroup=new THREE.Group();scene.add(insGroup);
const BVS="varying vec2 vUv;varying vec2 vW;void main(){vUv=uv;vec4 wp=modelMatrix*vec4(position,1.0);vW=wp.xy;gl_Position=projectionMatrix*viewMatrix*wp;}";
const BFS="uniform sampler2D uMap;uniform vec2 uGP;uniform float uAmb,uGI,uGR;varying vec2 vUv;varying vec2 vW;void main(){vec4 t=texture2D(uMap,vUv);float lum=dot(t.rgb,vec3(0.299,0.587,0.114));vec3 c=mix(t.rgb,t.rgb*0.68,smoothstep(0.80,0.99,lum));float d=distance(vW,uGP);float r=d/uGR;float at=uGI/(1.0+r*r);gl_FragColor=vec4(c*min(uAmb+at,1.3),t.a);}";
const bgU={uGP:{value:new THREE.Vector2(GLAREPOS[0],GLAREPOS[1])},uAmb:{value:0.64},uGI:{value:0.5},uGR:{value:1.4}};
const bgMat=stencilRead(new THREE.ShaderMaterial({uniforms:Object.assign({uMap:{value:tex(ROOMBG)}},bgU),vertexShader:BVS,fragmentShader:BFS,transparent:true,depthTest:false,depthWrite:false}));
const bgMesh=new THREE.Mesh(new THREE.PlaneGeometry(2.25,2.25),bgMat);bgMesh.position.set(0,0,ROOM_Z);bgMesh.renderOrder=3.0;insGroup.add(bgMesh);
const glareTex=tex(GLARE);const glareMat=stencilRead(new THREE.MeshBasicMaterial({map:glareTex,transparent:true,opacity:0,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,color:new THREE.Color(0xffffff)}));
const glareSpr=new THREE.Mesh(new THREE.PlaneGeometry(2.8,1.563),glareMat);glareSpr.position.set(-0.262,-0.646,ROOM_Z+0.01);glareSpr.renderOrder=3.02;insGroup.add(glareSpr);
let glareLit=1;
const smaskTex=tex(SMASK);
const HVS="varying vec2 vUv;varying vec2 vW;void main(){vUv=uv;vec4 wp=modelMatrix*vec4(position,1.0);vW=wp.xy;gl_Position=projectionMatrix*viewMatrix*wp;}";
const HFS="uniform sampler2D uMap;uniform vec2 uGlarePos;uniform vec3 uGlareColor;uniform float uGlareI,uAmbient,uGlareR;uniform vec2 uTermUV;uniform vec3 uTermColor;uniform float uTermI,uTermR;varying vec2 vUv;varying vec2 vW;void main(){vec4 t=texture2D(uMap,vUv);float d=distance(vW,uGlarePos);float r=d/uGlareR;float at=uGlareI/(1.0+r*r);vec3 col=t.rgb*(uAmbient+at*0.8)+uGlareColor*at*0.16;float dT=distance(vUv,uTermUV);float atT=uTermI/(1.0+pow(dT/uTermR,2.0));col+=uTermColor*atT*(0.28+0.5*t.rgb);gl_FragColor=vec4(min(col,vec3(1.4)),t.a);}";
const headU={uGlarePos:{value:new THREE.Vector2(GLAREPOS[0],GLAREPOS[1])},uGlareColor:{value:new THREE.Color(0xdfeaff)},uGlareI:{value:1.0},uAmbient:{value:0.18},uGlareR:{value:0.70},uTermUV:{value:new THREE.Vector2(0.509,0.659)},uTermColor:{value:new THREE.Color(0x5cff9e)},uTermI:{value:0.0},uTermR:{value:0.30}};
const headMat=stencilRead(new THREE.ShaderMaterial({uniforms:Object.assign({uMap:{value:tex(HEAD)}},headU),vertexShader:HVS,fragmentShader:HFS,transparent:true,depthTest:false,depthWrite:false}));
const headMesh=new THREE.Mesh(new THREE.PlaneGeometry(0.675,0.718),headMat);headMesh.position.set(0,0.025,-1.99);headMesh.renderOrder=3.2;insGroup.add(headMesh);
const sFrames=SFR.map(u=>tex(u));
const scrMat=stencilRead(new THREE.MeshBasicMaterial({map:sFrames[0],alphaMap:smaskTex,transparent:true,depthTest:false,depthWrite:false}));
const scrBackMat=stencilRead(new THREE.MeshBasicMaterial({color:0x000000,alphaMap:smaskTex,transparent:true,depthTest:false,depthWrite:false}));
const scrBack=new THREE.Mesh(new THREE.PlaneGeometry(SBOX[2]*1.05,SBOX[3]*1.05),scrBackMat);scrBack.position.set(SBOX[0],SBOX[1],-0.012);scrBack.renderOrder=3.08;headMesh.add(scrBack);
const screen=new THREE.Mesh(new THREE.PlaneGeometry(SBOX[2]*1.05,SBOX[3]*1.05),scrMat);screen.position.set(SBOX[0],SBOX[1],-0.01);screen.renderOrder=3.1;headMesh.add(screen);
const tvMat=stencilRead(new THREE.MeshBasicMaterial({color:0xffffff,alphaMap:smaskTex,transparent:true,opacity:0,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending}));
const tvLine=new THREE.Mesh(new THREE.PlaneGeometry(SBOX[2]*1.05,SBOX[3]*1.05),tvMat);tvLine.position.set(SBOX[0],SBOX[1],-0.008);tvLine.renderOrder=3.15;headMesh.add(tvLine);
let sfi=0,sft=0;
const ngA=NGA.map(u=>tex(u)),ngB=NGB.map(u=>tex(u));   // A=glossy/grey, B=rainbow clef
const noteGeo=new THREE.PlaneGeometry(1,1);
const R=Math.random;
const NOTEDEF=[
  {fr:ngB,x:-0.26,y: 0.17,s:0.125,iv:0.10},  // L upper  rainbow
  {fr:ngA,x:-0.33,y: 0.01,s:0.115,iv:0.13},  // L mid    grey/glossy
  {fr:ngA,x:-0.23,y:-0.04,s:0.100,iv:0.13},  // L lower  grey/glossy
  {fr:ngB,x: 0.26,y: 0.17,s:0.125,iv:0.10},  // R upper  rainbow  (the one added to this side)
  {fr:ngA,x: 0.33,y: 0.01,s:0.115,iv:0.13},  // R mid    grey/glossy
  {fr:ngA,x: 0.29,y:-0.04,s:0.105,iv:0.13}   // R lower  grey/glossy
];
const notes=[];
for(const D of NOTEDEF){
  const nm=new THREE.Mesh(noteGeo,new THREE.MeshBasicMaterial({map:D.fr[0],transparent:true,opacity:0,depthTest:false,depthWrite:false}));
  nm.position.set(D.x,D.y,0.03);nm.scale.set(D.s,D.s,1);nm.renderOrder=3.3;headMesh.add(nm);
  notes.push({m:nm,fr:D.fr,iv:D.iv,fi:0,ft:R()*0.13,ax:D.x,ay:D.y,sz:D.s,
    bf:1.0+R()*1.6,bp:R()*6.28,ba:0.03+R()*0.04,
    sf:0.6+R()*1.0,sp:R()*6.28,sa:0.02+R()*0.03,
    rf:0.5+R()*1.2,rp:R()*6.28,ra:0.10+R()*0.22,
    pf:0.8+R()*1.3,pp:R()*6.28,
    df:0.2+R()*0.35,dp:R()*6.28,da:0.04+R()*0.06});
}
let notesVis=0,termGlowI=0;
const maskedMats=[bgMat,headMat,scrMat,tvMat,glareMat,scrBackMat];
let masked=true;function setMasked(m){if(m===masked)return;masked=m;const f=m?THREE.EqualStencilFunc:THREE.AlwaysStencilFunc;maskedMats.forEach(mt=>{mt.stencilFunc=f;mt.needsUpdate=true;});}
let inph="play",tIn=0;const NEL_IDLE_Y=0.22,NEL_IDLE_S=1.1;
const termDiv=document.getElementById('term'),termin=document.getElementById('termin'),termlog=document.getElementById('termlog');
const wmpf=document.getElementById('wmpf');
termin.addEventListener('keydown',ev=>{if(ev.key==='Enter'&&termin.value.trim()){const m=document.createElement('div');m.textContent='\u203a '+termin.value;termlog.appendChild(m);termin.value='';termlog.scrollTop=termlog.scrollHeight;}});
function placeTerm(){const ctr=new THREE.Vector3(SBOX[0],SBOX[1],0.01);headMesh.localToWorld(ctr);ctr.project(cam);const c0=new THREE.Vector3(SBOX[0]-SBOX[2]*0.5,SBOX[1]-SBOX[3]*0.5,0.01),c1=new THREE.Vector3(SBOX[0]+SBOX[2]*0.5,SBOX[1]+SBOX[3]*0.5,0.01);headMesh.localToWorld(c0);c0.project(cam);headMesh.localToWorld(c1);c1.project(cam);termDiv.style.left=((ctr.x*0.5+0.5)*innerWidth)+'px';termDiv.style.top=((-ctr.y*0.5+0.5)*innerHeight)+'px';termDiv.style.width=(Math.abs(c1.x-c0.x)*0.5*innerWidth*0.96)+'px';termDiv.style.height=(Math.abs(c1.y-c0.y)*0.5*innerHeight*0.96)+'px';}
function resetInside(){inph="play";headMesh.rotation.z=0;headMesh.scale.set(1,1,1);screen.scale.set(1,1,1);tvMat.opacity=0;termDiv.classList.remove('on','off');termDiv.style.opacity=0;scrMat.map=sFrames[0];scrMat.color.set(0xffffff);scrMat.needsUpdate=true;}

let rot=0,vel=0,dragging=false,lastX=0,moved=0,phase="rest",tA=null,target=null,dbg=null;
const back=document.getElementById('back');const rc=new THREE.Raycaster();
const sceneEl=document.getElementById('scene'),dsEl=document.getElementById('ds'),dsImg=dsEl.querySelector('img'),dswT=document.getElementById('dswT'),dswB=document.getElementById('dswB');let clickIdx=0;const DS_HUE=[305,-25,46,170,217,274];
const CATS=[
{cat:'PSYCHO',
 top:{name:'AM STACK',tap:1,rows:[['Dextroamphetamine','1/day'],['Tropisetron','AM'],['Nefiracetam','AM'],['Bromantane','50mg']]},
 bot:{name:'PM STACK',tap:1,rows:[['Guanfacine','0.5 tab'],['Agmatine','500mg'],['Daridorexant','PM'],['Dihexa','15mg T/Th/Su']]}},
{cat:'INJECT',
 top:{name:'SCHEDULE',rows:[['HCG','Tu/Fr 100u 35d'],['GHK-Cu','daily 94u 23d'],['Test Cyp','MWF 775u 72d']]},
 bot:{name:'LOG TODAY',tap:1,btn:'+ LOG INJECTION',act:'log',rows:[['GHK-Cu','-4u'],['Test Cyp','-25u']]}},
{cat:'PACKING',
 top:{name:'CALCULATOR',calc:[['HCG',2,'u',10],['Test Cyp',3,'u',25],['GHK-Cu',7,'u',4],['AM orals',7,'ct',4],['PM orals',7,'ct',5]]},
 bot:{name:'CHECKLIST',checks:['HCG vial','Test Cyp','GHK-Cu','Pill organizer','Topicals kit']}},
{cat:'ANCILLARY',
 top:{name:'AM SUPPORT',tap:1,rows:[['Fish Oil','1800mg'],['Multi 50+','1/day'],['Creatine','5g']]},
 bot:{name:'PM SUPPORT',tap:1,rows:[['TUDCA','1/day'],['Magnesium','x2'],['Tadalafil','2.5mg'],['Anastrozole','PRN']]}},
{cat:'PENDING',
 top:{name:'INCOMING',rows:[['Daridorexant','access pending'],['Tropisetron','now active']]},
 bot:{name:'STANDBY',btn:'PROMOTE TO ACTIVE',act:'promote',rows:[['Anastrozole','0.125 3/wk'],['Status','not started',1]]}},
{cat:'TOPICAL',
 top:{name:'HAIR',rows:[['Routine','TBD',1]]},
 bot:{name:'SKIN PM',tap:1,streak:1,rows:[['1 BP Wash','4%'],['2 Clindamycin',''],['3 CB-03-01',''],['4 Tretinoin','pea']]}}];
const dsState={};
function dsSt(i){return dsState[i]||(dsState[i]={done:{},checked:{},trip:7,streak:0,logged:false,promoted:false});}
function dsSeg(s,side,i){var st=dsSt(i);
 var o='<div class="dswh"><span class="ttl"><i class="dswdot"></i>'+s.name+'</span><span class="dswchip">'+CATS[i].cat+'</span></div>';
 if(s.calc){o+='<div class="dswfield"><span class="lbl">DURATION</span><span class="stp"><b class="sbtn" data-act="dec">&minus;</b><span class="val">'+st.trip+'</span><span class="u">days</span><b class="sbtn" data-act="inc">+</b></span></div>';
   s.calc.forEach(function(c){var units=Math.ceil(st.trip/7*c[1])*c[3];o+='<div class="dswr"><i class="mk">&#9656;</i><span class="nm">'+c[0]+'</span><span class="ld"></span><b>'+units+' '+c[2]+'</b></div>';});}
 if(s.rows)s.rows.forEach(function(r,ri){var k=side+ri,done=s.tap&&st.done[k];
   o+='<div class="dswr'+(r[2]?' mut':'')+(s.tap?' tap':'')+(done?' done':'')+'" data-k="'+k+'"><i class="mk">'+(done?'&#10003;':'&#9656;')+'</i><span class="nm">'+r[0]+'</span><span class="ld"></span><b>'+(r[1]||'')+'</b></div>';});
 if(s.checks)s.checks.forEach(function(c,ci){o+='<div class="dswck'+(st.checked[ci]?' on':'')+'" data-c="'+ci+'"><i></i>'+c+'</div>';});
 if(s.btn){var done=(s.act==='log'&&st.logged)||(s.act==='promote'&&st.promoted),bl=done?'&#10003; '+(s.act==='log'?'LOGGED':'PROMOTED'):s.btn;
   o+='<div class="dswbtn'+(done?' done':'')+'" data-act="'+s.act+'">'+bl+'</div>';}
 if(s.streak)o+='<div class="dswfoot">STREAK <b>'+st.streak+'d</b><span class="sgo" data-act="streak">+ LOG NIGHT</span></div>';
 return o;}
function dsFill(i){var c=CATS[i]||CATS[0];dswT.querySelector('.dswbody').innerHTML=dsSeg(c.top,'t',i);dswB.querySelector('.dswbody').innerHTML=dsSeg(c.bot,'b',i);}
document.getElementById('dsstage').addEventListener('click',function(e){
 if(dsEl.style.display==='none')return;var i=clickIdx,st=dsSt(i);
 var a=e.target.closest('[data-act]');
 if(a){var k=a.getAttribute('data-act');
   if(k==='dec')st.trip=Math.max(1,st.trip-1);
   else if(k==='inc')st.trip=Math.min(90,st.trip+1);
   else if(k==='log'){st.logged=!st.logged;(CATS[i].bot.rows||[]).forEach(function(_,ri){st.done['b'+ri]=st.logged;});}
   else if(k==='promote')st.promoted=!st.promoted;
   else if(k==='streak')st.streak++;
   dsFill(i);return;}
 var ck=e.target.closest('.dswck'); if(ck){var ci=ck.getAttribute('data-c');st.checked[ci]=!st.checked[ci];dsFill(i);return;}
 var row=e.target.closest('.dswr.tap'); if(row){var rk=row.getAttribute('data-k');st.done[rk]=!st.done[rk];dsFill(i);return;}
});
function norm(a){a%=Math.PI*2;return a<0?a+Math.PI*2:a;}
function topIndex(){return ((Math.round(rot/(Math.PI/3))%6)+6)%6;}
addEventListener('pointerdown',e=>{if(phase==="opening"||phase==="flying"||phase==="returning"||phase==="pclick"||phase==="pscene_off"||phase==="ds"||phase==="dsexit")return;dragging=true;moved=0;lastX=e.clientX;vel=0;target=null;});
addEventListener('pointermove',e=>{if(!dragging||phase!=="awake")return;const dx=e.clientX-lastX;lastX=e.clientX;moved+=Math.abs(dx);rot-=dx*0.01;vel=-dx*0.01;});
addEventListener('pointerup',e=>{if(!dragging)return;dragging=false;if(moved<5)onTap(e);});
function onTap(e){if(phase==="rest"){wmpf.classList.add('go');wake();return;}
  if(phase==="inside"){if(inph==="play"){const n=new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);rc.setFromCamera(n,cam);if(rc.intersectObject(headMesh).length){inph="off";tIn=performance.now();}}return;}
  if(phase!=="awake")return;
  const ndc=new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);rc.setFromCamera(ndc,cam);
  const hit=rc.intersectObject(pick)[0];if(!hit)return;
  const lp=pick.worldToLocal(hit.point.clone());const r=Math.hypot(lp.x,lp.y);
  if(r<0.34){enter();return;}
  if(r<1.3){const deg=Math.atan2(lp.y,lp.x)*180/Math.PI;const idx=(((Math.round((90-deg)/60))%6)+6)%6;
    if(idx===topIndex()){clickIdx=idx;phase="pclick";tA=performance.now();}
    else{const des=idx*Math.PI/3;target=rot+Math.atan2(Math.sin(des-rot),Math.cos(des-rot));vel=0;}}
}
function ease(t){return t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;}
function wake(){phase="waking";tA=performance.now();}
function enter(){phase="opening";tA=performance.now();}
back.onclick=()=>{
  if(phase==="ds"){phase="dsexit";tA=performance.now();back.classList.remove('show');dswT.classList.remove('on');dswB.classList.remove('on');void dswT.offsetWidth;dswT.classList.add('off');dswB.classList.add('off');return;}
  if(phase!=="inside")return;
  if(inph==="term"){inph="termexit";tIn=performance.now();termDiv.classList.remove('on','off');void termDiv.offsetWidth;termDiv.classList.add('off');return;}
  if(inph==="play"){phase="returning";tA=performance.now();back.classList.remove('show');resetInside();}};
function fmap(arr,k){return arr[Math.max(0,Math.min(arr.length-1,Math.round(k*(arr.length-1))))];}
const L=(a,b,k)=>a+(b-a)*k;
const trkw=document.getElementById('trkw'),trk=document.getElementById('trk'),trkRows=[...trk.querySelectorAll('.row')],trkHl=trk.querySelector('.hl');
const mpw=document.getElementById('mpw'),mp=document.getElementById('mp'),mpbtn=document.getElementById('mpbtn');let mpState='hidden';
mpbtn.onclick=(e)=>{e.stopPropagation();if(phase==="inside"&&inph==="play"){inph="off";tIn=performance.now();}};
const PETAL_NAMES=["ORALS","INJECTABLES","PEPTIDES","SARMS","ANCILLARIES","OTHER"];
const ROW_C=[33.4,41.4,49.5,57.5,65.5,73.5];
trkRows.forEach((r,i)=>{r.textContent=PETAL_NAMES[i]||("PETAL "+(i+1));r.style.top=ROW_C[i]+"%";});
trkHl.style.top=(ROW_C[0]-3.48)+"%";let trkState='hidden';
const TERMHUE_DEG=0;termDiv.style.setProperty('--thr',TERMHUE_DEG+'deg');{const c=new THREE.Color(0x3dff6e),h={};c.getHSL(h);c.setHSL((h.h+TERMHUE_DEG/360)%1,h.s,h.l);headU.uTermColor.value.copy(c);}

function crtFrame(p){ // p in [0,1]: 0 = screen fully ON, 1 = fully OFF (CRT power-off look)
  if(p<0.55){const q=p/0.55;screen.scale.set(1,1-q*0.96,1);scrMat.opacity=1;tvLine.scale.set(1,0.05,1);tvMat.opacity=q*0.9;}
  else if(p<0.8){const q=(p-0.55)/0.25;screen.scale.set(1,0.04,1);scrMat.opacity=1-q;tvLine.scale.set(1-q*0.97,0.05,1);tvMat.opacity=0.95;}
  else{const q=(p-0.8)/0.2;screen.scale.set(1,0.04,1);scrMat.opacity=0;tvLine.scale.set(0.03,0.05*(1-q),1);tvMat.opacity=0.95*(1-q);}
}
function animate(ms){requestAnimationFrame(animate);const t=ms*0.001;
  const top=topIndex();
  {const aw=phase==="awake";if(aw&&trkState!=='on'){trkw.classList.add('show');trk.classList.remove('off');void trk.offsetWidth;trk.classList.add('on');trkState='on';}else if(!aw&&trkState==='on'){trk.classList.remove('on');void trk.offsetWidth;trk.classList.add('off');trkState='off';}else if(trkState==='off'&&(phase==='inside'||phase==='rest')){trkw.classList.remove('show');trk.classList.remove('off');trkState='hidden';}}
  {const mpShow=(phase==="inside"&&inph==="play");if(mpShow&&mpState!=='on'){mpw.classList.add('show');mp.classList.remove('off');void mp.offsetWidth;mp.classList.add('on');mpState='on';}else if(!mpShow&&mpState==='on'){mp.classList.remove('on');void mp.offsetWidth;mp.classList.add('off');mpState='off';}else if(!mpShow&&mpState==='off'&&phase!=="inside"){mpw.classList.remove('show');mp.classList.remove('off');mpState='hidden';}}
  {const lc=lightU.uLightColor.value;trkw.style.setProperty('--lc','rgb('+(lc.r*255|0)+','+(lc.g*255|0)+','+(lc.b*255|0)+')');}
  trkHl.style.top=(ROW_C[top]-3.48)+"%";
  for(let i=0;i<6;i++)trkRows[i].classList.toggle("sel",i===top);
  lightU.uLightColor.value.lerp(new THREE.Color(COLS[top]),0.1);
  lightU.uWake.value=L(lightU.uWake.value,(phase==="rest")?0:1,0.1);
  lightU.uWhiteI.value=L(lightU.uWhiteI.value,(phase==="rest")?0:0.8,0.1);
  const clk=(phase==="pclick")?Math.min((performance.now()-tA)/250,1):((phase==="pscene_off")?1:0);const clkE=ease(clk);
  if(clk>0)lightU.uWhiteI.value=Math.max(lightU.uWhiteI.value,0.8+0.95*clkE);
  let mi=0;
  for(let i=0;i<6;i++){
    let tS,tOn,pulseB,pulseA,pf,bobAmt;
    if(phase==="rest"){tS=1;tOn=1;pulseB=0.5;pulseA=0.22;pf=st[i].gf;bobAmt=1;}
    else{const awake=(phase==="waking"||phase==="awake"||phase==="pclick"||phase==="pscene_off");
      if(i===top){tS=1.05;tOn=awake?1:0;pulseB=0.9;pulseA=0.12;pf=0.5;bobAmt=(phase==="awake")?0.3:0;
        if(clk>0){tS=1.05+0.26*clkE;pulseB=0.9+1.1*clkE;pulseA=0.12*(1-clkE);}}
      else{tS=1;tOn=0;pulseB=0;pulseA=0;pf=0;bobAmt=0;}}
    st[i].sc=L(st[i].sc,tS,(clk>0&&i===top)?0.35:0.1);st[i].on=L(st[i].on,tOn,0.1);
    const bob=bobAmt*0.016*(0.6*Math.sin(t*st[i].b1*2.1+st[i].p1)+0.4*Math.sin(t*st[i].b2*2.1+st[i].p2));
    petalM[i].scale.set(st[i].sc,st[i].sc,1);
    petalM[i].position.set(st[i].dir[0]*bob,st[i].dir[1]*bob,0);
    glowM[i].material.opacity=st[i].on*(pulseB+pulseA*Math.sin(t*pf*3.14+st[i].gp));
  }
  wheel.rotation.z=rot;
  if(phase==="rest"){setFace(eyesTex[0]);setMasked(true);}
  else if(phase==="waking"){const k=Math.min((performance.now()-tA)/900,1),e=ease(k);cam.position.z=Z_REST-(Z_REST-Z_WAKE)*e;setFace(fmap(eyesTex,e));if(k>=1){phase="awake";rot=norm(rot);}}
  else if(phase==="awake"){if(target!==null){rot=L(rot,target,0.16);if(Math.abs(target-rot)<0.004){rot=target;target=null;}}else if(!dragging){vel*=0.96;rot+=vel;if(Math.abs(vel)<0.002)vel=0;}}
  else if(phase==="opening"){const k=Math.min((performance.now()-tA)/850,1),e=ease(k);setFace(fmap(portalTex,e));mi=e;if(k>=1){phase="flying";tA=performance.now();}}
  else if(phase==="flying"){const k=Math.min((performance.now()-tA)/1450,1),e=ease(k);setFace(portalTex[portalTex.length-1]);cam.position.z=Z_WAKE-(Z_WAKE-Z_END)*e;setMasked(cam.position.z>DROP_Z);mi=1-e;if(k>=1){phase="inside";back.classList.add('show');resetInside();}}
  else if(phase==="inside"){setMasked(false);}
  // the room is ALWAYS live (stencil-hidden until the mouth opens) so flying in is seamless
  glareLit=L(glareLit,(inph==="zoom"||inph==="term"||inph==="termexit")?0:1,0.1);
  headU.uGlareI.value=glareLit;
  glareMat.opacity=glareLit*(0.42+0.05*Math.sin(t*3.0));
  notesVis=L(notesVis,(phase==="inside"&&inph==="play")?1:0,0.08);
  {const dep=notesVis<0?0:(notesVis>1?1:notesVis);const ed=dep*dep*(3-2*dep);
  for(const n of notes){const by=(n.ba*Math.sin(t*n.bf+n.bp)+n.da*Math.sin(t*n.df+n.dp))*dep, bx=(n.sa*Math.sin(t*n.sf+n.sp))*dep;
    n.m.position.set(L(n.ax*0.3,n.ax,ed)+bx,L(n.ay*0.3,n.ay,ed)+by,0.03);n.m.rotation.z=(n.ra*Math.sin(t*n.rf+n.rp))*dep;
    const sc=n.sz*(0.95+0.08*Math.sin(t*n.pf+n.pp)*dep);n.m.scale.set(sc,sc,1);n.m.material.opacity=dep;
    if(dep>0.55){n.ft+=0.016;if(n.ft>=n.iv){n.ft=0;n.fi=(n.fi+1)%n.fr.length;n.m.material.map=n.fr[n.fi];n.m.material.needsUpdate=true;}}}}
  termGlowI=L(termGlowI,(inph==="zoom"||inph==="term")?1:0,0.12);
  headU.uTermI.value=termGlowI*1.4;
  tvLine.visible=(inph==="off"||inph==="poweron");
  if(inph==="play"){
    scrMat.opacity=1;screen.scale.set(1,1,1);
    const sway=0.05*Math.sin(t*2.4), bobY=0.018*Math.sin(t*4.8+0.6);
    headMesh.position.set(sway,NEL_IDLE_Y+bobY,-1.99);
    headMesh.rotation.z=0.075*Math.sin(t*2.4);                         // lean into the bob, in place
    headMesh.scale.set(NEL_IDLE_S*(1+0.02*Math.sin(t*4.8)),NEL_IDLE_S*(1-0.02*Math.sin(t*4.8)),1);
    sft+=0.016;if(sft>0.2){sft=0;sfi=(sfi+1)%sFrames.length;scrMat.map=sFrames[sfi];scrMat.needsUpdate=true;}
  } else if(inph==="off"){              // CRT power-off + settle to centre
    headMesh.position.x=L(headMesh.position.x,0,0.12);headMesh.position.y=L(headMesh.position.y,NEL_IDLE_Y,0.12);headMesh.position.z=-1.99;
    headMesh.rotation.z=L(headMesh.rotation.z,0,0.15);{const os=L(headMesh.scale.x,1,0.15);headMesh.scale.set(os,os,1);}
    const p=Math.min((performance.now()-tIn)/650,1);
    crtFrame(p);
    if(p>=1){inph="zoom";tIn=performance.now();scrMat.opacity=0;screen.scale.set(1,1,1);}
  } else if(inph==="zoom"){             // terminal comes toward the camera
    headMesh.position.x=L(headMesh.position.x,0,0.12);headMesh.position.y=L(headMesh.position.y,0.06,0.12);
    headMesh.position.z=L(headMesh.position.z,-1.02,0.1);
    scrMat.opacity=0;tvMat.opacity=0;
    if((performance.now()-tIn)/800>=1){inph="term";placeTerm();termDiv.classList.remove('on','off');void termDiv.offsetWidth;termDiv.classList.add('on');try{termin.focus();}catch(e){}}
  } else if(inph==="term"){
    scrMat.opacity=0;tvMat.opacity=0;headMesh.position.set(0,0.06,-1.02);placeTerm();
  } else if(inph==="termexit"){          // reverse step 1: DOM terminal shuts off (tv-off), head holds at zoom pos
    scrMat.opacity=0;tvMat.opacity=0;headMesh.position.set(0,0.06,-1.02);
    if((performance.now()-tIn)/520>=1){inph="unzoom";tIn=performance.now();}
  } else if(inph==="unzoom"){            // reverse of zoom: head backs away from camera
    headMesh.position.x=L(headMesh.position.x,0,0.12);headMesh.position.y=L(headMesh.position.y,NEL_IDLE_Y,0.12);
    headMesh.position.z=L(headMesh.position.z,-1.99,0.1);{const us=L(headMesh.scale.x,NEL_IDLE_S,0.1);headMesh.scale.set(us,us,1);}
    scrMat.opacity=0;tvMat.opacity=0;
    if((performance.now()-tIn)/800>=1){inph="poweron";tIn=performance.now();scrMat.map=sFrames[sfi];scrMat.needsUpdate=true;}
  } else if(inph==="poweron"){           // reverse of off: CRT power-ON, then resume idle
    headMesh.position.set(0,NEL_IDLE_Y,-1.99);headMesh.rotation.z=0;headMesh.scale.set(NEL_IDLE_S,NEL_IDLE_S,1);
    const pr=1-Math.min((performance.now()-tIn)/650,1);
    crtFrame(pr);
    if((performance.now()-tIn)/650>=1){inph="play";scrMat.opacity=1;screen.scale.set(1,1,1);tvMat.opacity=0;tvLine.scale.set(1,0.05,1);}
  }
  if(phase==="returning"){const k=Math.min((performance.now()-tA)/1300,1),e=ease(k);cam.position.z=Z_END+((Z_WAKE)-Z_END)*e;setMasked(cam.position.z>DROP_Z);setFace(fmap(portalTex,1-e));mi=(1-e)*0.6;if(k>=1){phase="awake";rot=norm(rot);}}
  if(phase==="pclick"&&(performance.now()-tA)>=250){phase="pscene_off";tA=performance.now();dsEl.style.setProperty('--dc',COLS[clickIdx]);dsFill(clickIdx);dsEl.style.display='flex';dsEl.classList.remove('show');sceneEl.classList.remove('tvon');void sceneEl.offsetWidth;sceneEl.classList.add('tvoff');}
  if(phase==="pscene_off"){const ep=performance.now()-tA;if(ep>=640)dsEl.classList.add('show');if(ep>=1750){phase="ds";back.classList.add('show');dswT.classList.remove('off');dswB.classList.remove('off');void dswT.offsetWidth;dswT.classList.add('on');dswB.classList.add('on');}}
  if(phase==="dsexit"){const ed=performance.now()-tA;
    if(ed>=400&&dsEl.classList.contains('show'))dsEl.classList.remove('show');
    if(ed>=1150&&!sceneEl.classList.contains('tvon')){sceneEl.classList.remove('tvoff');void sceneEl.offsetWidth;sceneEl.classList.add('tvon');}
    if(ed>=1780){phase="awake";sceneEl.classList.remove('tvon');dsEl.style.display='none';dswT.classList.remove('on','off');dswB.classList.remove('on','off');}}
  if(dbg!==null){setFace(fmap(portalTex,dbg));cam.position.z=Z_WAKE;setMasked(true);mi=dbg;}
  lightU.uMouthI.value=L(lightU.uMouthI.value,mi*1.25,0.22);
  mouthGlow.material.opacity=Math.min(0.55,lightU.uMouthI.value*0.42);
  rnd.render(scene,cam);}
animate(0);
addEventListener('resize',()=>{cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();rnd.setSize(innerWidth,innerHeight);});
window.__wake=()=>wake();window.__rest=()=>{phase="rest";rot=0;cam.position.z=Z_REST;};window.__setRot=v=>{rot=v;};window.__enter=()=>enter();
window.__phase=()=>phase;window.__top=()=>topIndex();
window.__dbgOpen=(k)=>{dbg=k;phase="awake";};
window.__inside=()=>{dbg=null;phase="inside";cam.position.z=Z_END;setMasked(false);back.classList.add('show');resetInside();};
window.__tapHead=()=>{if(inph==="play"){inph="off";tIn=performance.now();}};
window.__state=()=>JSON.stringify({phase:phase,inph:inph,mpState:mpState,scrOp:scrMat.opacity,backOp:scrBackMat.opacity,hz:headMesh.position.z.toFixed(2)});
window.__setInph=(v)=>{inph=v;tIn=performance.now();};window.__back=()=>back.onclick();
"""
SHELL=r"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<style>@font-face{font-family:'vt';src:url(__FONTVT__) format('woff2');font-display:swap;}@font-face{font-family:'tw';src:url(__FONTSE__) format('woff2');font-display:swap;}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
html,body{height:100%;overflow:hidden;background:#000;font-family:sans-serif;color:#fff;user-select:none;}
#c{position:fixed;inset:0;display:block;touch-action:none;z-index:1;}
#bgf{position:fixed;inset:0;z-index:0;background:#000;object-fit:cover;width:100%;height:100%;transform:scale(1.06);animation:bgbreathe 7.5s ease-in-out infinite;will-change:filter;}
#bgvig{position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(80% 68% at 50% 43%,rgba(0,0,0,0) 36%,rgba(0,0,0,.625) 74%,rgba(0,0,0,1) 100%);}
#bgglow{position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(52% 40% at 50% 43%,rgba(255,248,232,.30),rgba(255,248,232,0) 72%);mix-blend-mode:screen;animation:bgglow 7.5s ease-in-out infinite;will-change:opacity;}
@keyframes bgbreathe{0%,100%{filter:brightness(.32) saturate(.9) blur(1.5px);}50%{filter:brightness(.44) saturate(1.04) blur(1.5px);}}
@keyframes bgglow{0%,100%{opacity:.55;}50%{opacity:.95;}}
#back{position:fixed;left:14px;top:max(18px,env(safe-area-inset-top));z-index:6;width:60px;height:60px;border:none;background:url(__BACKBTN__) center/contain no-repeat;cursor:pointer;opacity:0;transform:scale(0);transform-origin:50% 50%;pointer-events:none;font-size:0;color:transparent;filter:drop-shadow(0 3px 7px rgba(0,0,0,.45));transition:transform .3s cubic-bezier(.5,-0.3,.75,.4),opacity .26s ease;will-change:transform,opacity;}
#back.show{animation:backpop .5s cubic-bezier(.34,1.56,.64,1) forwards;pointer-events:auto;}
@keyframes backpop{0%{opacity:0;transform:scale(.2);}55%{opacity:1;transform:scale(1.18);}100%{opacity:1;transform:scale(1);}}
#back:active{transform:scale(.9);}
#term{position:fixed;transform:translate(-50%,-50%);opacity:0;z-index:4;display:flex;flex-direction:column;background:linear-gradient(160deg,#04250f,#010d05);border:1.5px solid rgba(80,255,130,.95);border-radius:7px;box-shadow:0 0 48px rgba(57,255,110,.95),0 0 96px rgba(57,255,90,.55),inset 0 0 28px rgba(50,225,95,.6);overflow:hidden;transform-origin:50% 50%;filter:hue-rotate(var(--thr,0deg));}
#term.on{animation:termon .58s cubic-bezier(.4,.08,.2,1) forwards;}
@keyframes termon{0%{opacity:1;transform:translate(-50%,-50%) scale(1.25,.004);filter:brightness(6.5) contrast(1.5) hue-rotate(var(--thr,0deg));}10%{opacity:1;transform:translate(-50%,-50%) scale(1.25,.004);filter:brightness(6.5) contrast(1.5) hue-rotate(var(--thr,0deg));}50%{transform:translate(-50%,-50%) scale(1.22,.02);filter:brightness(4.5) contrast(1.3) hue-rotate(var(--thr,0deg));}70%{transform:translate(-50%,-50%) scale(1,1.06);filter:brightness(2.2) hue-rotate(var(--thr,0deg));}100%{opacity:1;transform:translate(-50%,-50%) scale(1,1);filter:brightness(1) hue-rotate(var(--thr,0deg));}}
#term.off{animation:termoff .5s cubic-bezier(.55,0,.7,.25) forwards;}
@keyframes termoff{0%{opacity:1;transform:translate(-50%,-50%) scale(1,1);filter:brightness(1) hue-rotate(var(--thr,0deg));}28%{transform:translate(-50%,-50%) scale(1,1.04);filter:brightness(2.4) contrast(1.2) hue-rotate(var(--thr,0deg));}62%{transform:translate(-50%,-50%) scale(1.03,.02);filter:brightness(6) contrast(1.5) hue-rotate(var(--thr,0deg));}100%{opacity:0;transform:translate(-50%,-50%) scale(.18,.004);filter:brightness(9) hue-rotate(var(--thr,0deg));}}
#termlog{flex:1;padding:6px 11px;font:17px/1.18 'vt',ui-monospace,monospace;color:#6dff97;overflow-y:auto;text-shadow:0 0 10px rgba(80,255,130,.95),0 0 3px rgba(160,255,190,.8);letter-spacing:.5px;}
#terminp{display:flex;align-items:center;gap:6px;padding:5px 11px;border-top:1px solid rgba(110,255,160,.35);}
#terminp span{color:#7dffae;font:18px 'vt',ui-monospace,monospace;text-shadow:0 0 6px rgba(110,255,165,.6);}
#termin{flex:1;min-width:0;background:transparent;border:none;outline:none;color:#d8ffe6;font:17px 'vt',ui-monospace,monospace;letter-spacing:.5px;}#termin::placeholder{color:#5ca87a;}
#wmpf{position:fixed;inset:0;background:url(__WMPFRAME__) center/cover no-repeat;opacity:1;pointer-events:none;z-index:6;transform-origin:50% 43%;will-change:transform,opacity;}
@keyframes wmpz{0%{opacity:1;transform:scale(1);}45%{opacity:1;}100%{opacity:0;transform:scale(5.2);}}
#wmpf.go{animation:wmpz 0.68s cubic-bezier(.5,0,.9,.4) forwards;}
#trkw{position:fixed;left:50%;bottom:4.5vh;transform:translateX(-50%);width:min(83.3vw,381px);aspect-ratio:528/374;z-index:3;pointer-events:none;opacity:0;--lc:#5cff9e;filter:drop-shadow(0 0 3px var(--lc)) drop-shadow(0 0 9px var(--lc)) drop-shadow(0 0 18px var(--lc));}
#trkw.show{opacity:1;}
#trk{position:absolute;inset:0;background:url(__XBOX__) center/contain no-repeat;container-type:size;transform-origin:50% 50%;}
#trk.on{animation:trkon .62s cubic-bezier(.4,.08,.2,1) forwards;}
#trk.off{animation:trkoff .5s cubic-bezier(.55,0,.7,.25) forwards;}
@keyframes trkon{0%{transform:scale(1.3,.004);filter:brightness(7) contrast(1.5) saturate(.4);}9%{transform:scale(1.3,.004);filter:brightness(7) contrast(1.5) saturate(.4);}48%{transform:scale(1.28,.02);filter:brightness(5) contrast(1.3) saturate(.7);}68%{transform:scale(1,1.06);filter:brightness(2.4) contrast(1.1) saturate(1);}100%{transform:scale(1,1);filter:brightness(1) contrast(1) saturate(1);}}
@keyframes trkoff{0%{transform:scale(1,1);filter:brightness(1) contrast(1);opacity:1;}26%{transform:scale(1,1.03);filter:brightness(2.6) contrast(1.2);opacity:1;}56%{transform:scale(1.03,.014);filter:brightness(6) contrast(1.6);opacity:1;}80%{transform:scale(1,.005);filter:brightness(8) contrast(1.6);opacity:1;}100%{transform:scale(.2,.0025);filter:brightness(10);opacity:0;}}
#trk .tint{position:absolute;inset:0;background:var(--lc,#5cff9e);mix-blend-mode:soft-light;opacity:.6;-webkit-mask:url(__XBOX__) center/contain no-repeat;mask:url(__XBOX__) center/contain no-repeat;pointer-events:none;z-index:0;}
#trk .ttl{position:absolute;left:8.5%;top:16.8%;transform:translateY(-50%);font:8.6cqh/1 'vt',monospace;letter-spacing:.1em;color:#b6e85a;text-shadow:0 0 7px rgba(160,225,80,.7);}
#trk .row{position:absolute;left:10.5%;transform:translateY(-50%);font:5.7cqh/1 'vt',monospace;letter-spacing:.03em;color:#d6f0a4;white-space:nowrap;z-index:2;text-shadow:0 1px 1px rgba(0,0,0,.5);}
#trk .row.sel{color:#241a00;text-shadow:none;}
#trk .hl{position:absolute;left:7%;width:59%;height:6.95%;border-radius:3px;background:linear-gradient(180deg,#ffe27a,#f2b22e 55%,#c98a16);box-shadow:0 0 6px rgba(255,200,60,.55),inset 0 1px 0 rgba(255,255,255,.4);z-index:1;transition:top .18s cubic-bezier(.3,.8,.3,1);}#mpw{position:fixed;left:50%;bottom:4.5vh;transform:translateX(-50%);width:min(96vw,470px);aspect-ratio:733/264;z-index:3;pointer-events:none;opacity:0;}
#mpw.show{opacity:1;}
#mp{position:absolute;inset:0;background:url(__MP__) center/contain no-repeat;container-type:size;transform-origin:50% 50%;}
#mpglare{position:absolute;inset:0;background:url(__GLARE__) 72% 30%/135% no-repeat;mix-blend-mode:screen;opacity:.6;pointer-events:none;-webkit-mask:url(__MP__) center/contain no-repeat;mask:url(__MP__) center/contain no-repeat;-webkit-mask-size:contain;mask-size:contain;}
#mp.on{animation:trkon .62s cubic-bezier(.4,.08,.2,1) forwards;}
#mp.off{animation:trkoff .5s cubic-bezier(.55,0,.7,.25) forwards;}
.mpbtn{position:absolute;left:26%;top:46%;width:60%;height:13%;display:flex;align-items:center;justify-content:flex-start;gap:.45em;background:transparent;border:none;cursor:pointer;pointer-events:none;font:700 9cqh/1 Tahoma,Arial,sans-serif;color:#eef4ff;text-shadow:0 1px 2px rgba(0,28,68,.7),0 0 1px rgba(0,0,0,.55);letter-spacing:.2px;white-space:nowrap;}
#mp.on .mpbtn{pointer-events:auto;}
.mpbtn .pt{font-size:.82em;opacity:.92;}
.mpbtn:hover,.mpbtn:active{color:#ffffff;text-shadow:0 1px 2px rgba(0,28,68,.85),0 0 6px rgba(150,210,255,.55);}
#scene{position:fixed;inset:0;z-index:3;overflow:hidden;transform-origin:50% 50%;}
#scene.tvoff{animation:sceneoff .62s cubic-bezier(.55,0,.7,.25) forwards;}
#scene.tvon{animation:scenein .6s cubic-bezier(.2,.7,.3,1) forwards;}
@keyframes sceneoff{0%{transform:scale(1,1);filter:brightness(1) contrast(1);opacity:1;}16%{transform:scale(1,1.035);filter:brightness(2.3) contrast(1.2);}52%{transform:scale(1,.012);filter:brightness(7) contrast(1.5);}80%{transform:scale(1,.004);filter:brightness(9);opacity:1;}100%{transform:scale(0,.002);filter:brightness(12);opacity:0;}}
@keyframes scenein{0%{transform:scale(0,.002);filter:brightness(12);opacity:0;}20%{transform:scale(1,.004);filter:brightness(9);opacity:1;}48%{transform:scale(1,.012);filter:brightness(7) contrast(1.5);}84%{transform:scale(1,1.035);filter:brightness(2.3) contrast(1.2);}100%{transform:scale(1,1);filter:brightness(1) contrast(1);opacity:1;}}
#bgkeep{position:fixed;inset:0;z-index:1;pointer-events:none;}
#ds{position:fixed;inset:0;z-index:2;background:transparent;display:none;align-items:center;justify-content:center;isolation:isolate;opacity:1;transform-origin:50% 66%;transform:translateY(8%) scale(3.3);transition:transform 1s cubic-bezier(.25,.46,.45,.94);}
#ds.show{transform:translateY(0) scale(1);}
#dsstage{position:relative;aspect-ratio:736/1308;height:100%;max-width:100%;}
#dsbody{position:absolute;inset:0;isolation:isolate;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 736 1308'%3E%3Cpath fill='%23fff' fill-rule='evenodd' d='M0 0H736V1308H0Z M79 37H657V450H79Z M78 571H656V988H78Z'/%3E%3C/svg%3E") center/100% 100% no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 736 1308'%3E%3Cpath fill='%23fff' fill-rule='evenodd' d='M0 0H736V1308H0Z M79 37H657V450H79Z M78 571H656V988H78Z'/%3E%3C/svg%3E") center/100% 100% no-repeat;}
#dsbody img{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;filter:saturate(1.5) brightness(.95);}
#dstint{position:absolute;inset:0;background:var(--dc,#888);mix-blend-mode:multiply;opacity:.9;pointer-events:none;}
#dsdark{position:absolute;inset:0;background:#000;opacity:.40;pointer-events:none;}
.dswin{position:absolute;border-radius:5px;overflow:hidden;transform-origin:50% 50%;opacity:0;transform:scaleY(.004);color:#eef0f6;border:1.5px solid var(--dc,#888);background:transparent;box-shadow:0 0 8px 1px var(--dc,#888),0 0 27px 7px var(--dc,#888),0 0 60px 18px var(--dc,#888),inset 0 0 22px -3px var(--dc,#888);}
#dswT{left:9.38%;top:2.06%;width:81.24%;height:33.11%;}
#dswB{left:9.24%;top:42.89%;width:81.25%;height:33.41%;}
.dswscan{position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,.22) 0 1px,transparent 1px 3px);}
.dswbody{position:absolute;inset:0;padding:7px 10px;display:flex;flex-direction:column;overflow:hidden;text-shadow:0 1px 3px rgba(0,0,0,.95),0 0 6px rgba(0,0,0,.7);}
.dswh{font:700 13px/1 'vt',monospace;letter-spacing:.05em;text-transform:uppercase;color:var(--dc,#fff);text-shadow:0 0 8px var(--dc,#fff),0 1px 3px rgba(0,0,0,.95);padding-bottom:4px;margin-bottom:5px;border-bottom:1px solid rgba(255,255,255,.18);display:flex;justify-content:space-between;align-items:center;}
.dswh .ttl{display:flex;align-items:center;gap:6px;}
.dswdot{width:7px;height:7px;border-radius:50%;background:var(--dc,#fff);box-shadow:0 0 6px var(--dc,#fff);animation:dswpulse 1.7s ease-in-out infinite;flex:none;}
@keyframes dswpulse{0%,100%{opacity:.35;}50%{opacity:1;}}
.dswchip{font-size:9px;letter-spacing:.14em;border:1px solid var(--dc,#fff);border-radius:3px;padding:1px 6px;color:var(--dc,#fff);opacity:.92;text-shadow:0 0 5px var(--dc,#fff);}
.dswr{display:flex;align-items:center;gap:6px;font:500 12.5px/1.2 ui-monospace,Menlo,monospace;padding:3px 0;}
.dswr .mk{color:var(--dc,#fff);font-size:9px;opacity:.85;flex:none;}
.dswr .nm{color:#fff;white-space:nowrap;}
.dswr .ld{flex:1;min-width:8px;height:0;border-bottom:1px dotted rgba(255,255,255,.22);margin-bottom:2px;}
.dswr b{color:var(--dc,#fff);font-weight:600;flex:none;font-size:11px;opacity:.95;}
.dswr.mut .nm{color:rgba(238,240,246,.55);}
.dswr.mut .mk{opacity:.45;}
.dswframe{position:absolute;inset:6px;pointer-events:none;opacity:.9;filter:drop-shadow(0 0 3px var(--dc,#fff));background:linear-gradient(var(--dc,#fff),var(--dc,#fff)) 0 0/13px 2px no-repeat,linear-gradient(var(--dc,#fff),var(--dc,#fff)) 0 0/2px 13px no-repeat,linear-gradient(var(--dc,#fff),var(--dc,#fff)) 100% 0/13px 2px no-repeat,linear-gradient(var(--dc,#fff),var(--dc,#fff)) 100% 0/2px 13px no-repeat,linear-gradient(var(--dc,#fff),var(--dc,#fff)) 0 100%/13px 2px no-repeat,linear-gradient(var(--dc,#fff),var(--dc,#fff)) 0 100%/2px 13px no-repeat,linear-gradient(var(--dc,#fff),var(--dc,#fff)) 100% 100%/13px 2px no-repeat,linear-gradient(var(--dc,#fff),var(--dc,#fff)) 100% 100%/2px 13px no-repeat;}
.dswr.tap{cursor:pointer;-webkit-tap-highlight-color:transparent;}
.dswr.done .nm{text-decoration:line-through;opacity:.45;}
.dswr.done .mk{opacity:1;}
.dswbtn{margin-top:auto;cursor:pointer;border:1px solid var(--dc,#888);border-radius:5px;color:var(--dc,#fff);text-align:center;padding:6px 4px;font:700 11px 'vt',monospace;letter-spacing:.08em;text-shadow:0 0 6px var(--dc,#fff);box-shadow:inset 0 0 14px -6px var(--dc,#888);-webkit-tap-highlight-color:transparent;}
.dswbtn.done{background:var(--dc,#fff);color:#08080c;text-shadow:none;box-shadow:0 0 10px -1px var(--dc,#fff);}
.dswck{display:flex;align-items:center;gap:8px;font:500 12.5px ui-monospace,Menlo,monospace;padding:3px 0;color:#fff;cursor:pointer;-webkit-tap-highlight-color:transparent;}
.dswck i{width:13px;height:13px;border:1.5px solid var(--dc,#888);border-radius:3px;flex:none;box-shadow:inset 0 0 8px -3px var(--dc,#888);}
.dswck.on i{background:var(--dc,#fff);box-shadow:0 0 8px var(--dc,#fff);}
.dswck.on{color:rgba(255,255,255,.55);text-decoration:line-through;}
.dswfield{margin:1px 0 6px;border:1px solid var(--dc,#888);border-radius:5px;padding:4px 9px;font:600 13px 'vt',monospace;color:#fff;display:flex;justify-content:space-between;align-items:center;}
.dswfield .lbl{letter-spacing:.06em;}
.dswfield .stp{display:flex;align-items:center;gap:7px;}
.dswfield .val{min-width:18px;text-align:center;color:var(--dc,#fff);font-size:15px;}
.dswfield .u{font-size:10px;opacity:.65;letter-spacing:.05em;}
.sbtn{cursor:pointer;width:19px;height:19px;line-height:17px;text-align:center;border:1px solid var(--dc,#fff);border-radius:4px;color:var(--dc,#fff);font-size:13px;-webkit-tap-highlight-color:transparent;}
.dswfoot{margin-top:auto;font:700 11px 'vt',monospace;letter-spacing:.12em;color:var(--dc,#fff);text-shadow:0 0 6px var(--dc,#fff);display:flex;align-items:center;gap:8px;}
.dswfoot .sgo{cursor:pointer;border:1px solid var(--dc,#fff);border-radius:3px;padding:2px 7px;font-size:9px;letter-spacing:.06em;-webkit-tap-highlight-color:transparent;}
.dswin.on{animation:dswon .58s cubic-bezier(.2,.7,.3,1) forwards;}
.dswin.off{animation:dswoff .42s cubic-bezier(.5,0,.7,.3) forwards;}
@keyframes dswon{0%{transform:scaleY(.004);filter:brightness(3.2);opacity:0;}9%{opacity:1;}38%{transform:scaleY(.03);filter:brightness(2.6);}58%{transform:scaleY(1);filter:brightness(1.6);}80%{filter:brightness(1.12);}100%{transform:scaleY(1);filter:brightness(1);opacity:1;}}
@keyframes dswoff{0%{transform:scaleY(1);filter:brightness(1);opacity:1;}34%{transform:scaleY(1);filter:brightness(2.3);}62%{transform:scaleY(.03);filter:brightness(3.2);}100%{transform:scaleY(.003) scaleX(.5);filter:brightness(4);opacity:0;}}
#boot{position:fixed;inset:0;z-index:30;background:#000;display:flex;align-items:center;justify-content:center;transition:opacity .6s ease;}
#boot.hide{opacity:0;pointer-events:none;}
#boot img{width:min(66vw,300px);height:auto;image-rendering:auto;}
</style></head><body>
<div id="boot"><img src="__BOOT__" alt=""></div>
<div id="bgkeep"><img id="bgf"><div id="bgvig"></div><div id="bgglow"></div></div>
<div id="ds"><div id="dsstage"><div id="dsbody"><img src="__DS__" alt=""><div id="dstint"></div><div id="dsdark"></div></div><div class="dswin" id="dswT"><div class="dswbody"></div><div class="dswscan"></div><div class="dswframe"></div></div><div class="dswin" id="dswB"><div class="dswbody"></div><div class="dswscan"></div><div class="dswframe"></div></div></div></div>
<div id="scene">
<canvas id="c"></canvas>
<div id="wmpf"></div>
<div id="trkw"><div id="trk"><div class="tint"></div><div class="ttl">TRACKER</div><div class="hl"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div></div></div>
</div>
<button id="back" aria-label="back"></button>
<div id="term"><div id="termlog">nelson@bloom:~$ ready</div><div id="terminp"><span>$</span><input id="termin" placeholder="type a command…" autocomplete="off"/></div></div>
<div id="mpw"><div id="mp"><button class="mpbtn" id="mpbtn"><span class="pt">&#9654;</span>OPEN TERMINAL</button><div id="mpglare"></div></div></div>
<script>(function(){var F=__BGFRAMES__;var el=document.getElementById('bgf');F.forEach(function(u){var im=new Image();im.src=u;});el.src=F[0];var i=0,d=1;setInterval(function(){i+=d;if(i>=F.length-1){i=F.length-1;d=-1;}else if(i<=0){i=0;d=1;}el.src=F[i];},125);})();
setTimeout(function(){var bt=document.getElementById('boot');if(bt){bt.classList.add('hide');setTimeout(function(){bt.style.display='none';},700);}},2100);</script><script>__THREE__</script><script>__CORE__</script></body></html>"""
core=CORE.replace("__SPL__",SPL).replace("__POS__",POS).replace("__COLS__",COLS).replace("__GLOW__",GLOW).replace("__EY__",EY).replace("__PO__",PO).replace("__RM__",RM).replace("__HEAD__",HEAD).replace("__ROOMBG__",ROOMBG).replace("__SFR__",SFR).replace("__SBOX__",SBOX).replace("__SMASK__",SMASK).replace("__GLAREPOS__",GLAREPOS).replace("__GLARE__",GLARE).replace("__NGA__",NGA).replace("__NGB__",NGB).replace("__NC__",NC).replace("__WMPFRAME__",WMPFRAME)
open("bloom-3d-local.html","w").write(SHELL.replace("__THREE__",THREE).replace("__CORE__",core).replace("__WMPFRAME__",WMPFRAME).replace("__XBOX__",XBOX).replace("__FONTVT__",FONTVT).replace("__FONTSE__",FONTSE).replace("__BGFLOWER__",BGFLOWER).replace("__BGFRAMES__",BGFRAMES).replace("__MP__",MP).replace("__GLARE__",GLARE).replace("__BACKBTN__",BACKBTN).replace("__BOOT__",BOOT).replace("__DS__",DS))
open("/mnt/user-data/outputs/bloom-3d.html","w").write(SHELL.replace("<script>__THREE__</script>",'<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>').replace("__CORE__",core).replace("__WMPFRAME__",WMPFRAME).replace("__XBOX__",XBOX).replace("__FONTVT__",FONTVT).replace("__FONTSE__",FONTSE).replace("__BGFLOWER__",BGFLOWER).replace("__BGFRAMES__",BGFRAMES).replace("__MP__",MP).replace("__GLARE__",GLARE).replace("__BACKBTN__",BACKBTN).replace("__BOOT__",BOOT).replace("__DS__",DS))
print("lit-shader build written")
