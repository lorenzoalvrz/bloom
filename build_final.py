import json
d=json.load(open("embed_portal.json"))
SPL=json.dumps(d["petalsSplit"]);POS=json.dumps(d["petalPos"]);COLS=json.dumps(d["petalCols"]);GLOW=d["glow"]
EY=json.dumps(d["eyes"]);PO=json.dumps(d["portal"]);RM=d["room"];HEAD=d["head"];ROOMBG=d["roomBg"];SFR=json.dumps(d["screenFrames"]);SBOX=json.dumps(d["screenBox"]);SMASK=d["screenMask"];GLAREPOS=json.dumps(d["glarePos"]);GLARE=d["glare"];NGA=json.dumps(d["noteGifA"]);NGB=json.dumps(d["noteGifB"]);NC=d["noteCol"];WMPFRAME=d["wmpFrame"];XBOX=d["xboxPanel"];FONTVT=d["fontVT"];FONTSE=d["fontSE"]
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
  const gm=new THREE.Mesh(new THREE.PlaneGeometry(1.3,1.3),new THREE.MeshBasicMaterial({map:glowTex,transparent:true,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending,color:new THREE.Color(COLS[i]),opacity:0}));
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
let inph="play",tIn=0;
const termDiv=document.getElementById('term'),termin=document.getElementById('termin'),termlog=document.getElementById('termlog');
const wmpf=document.getElementById('wmpf');
termin.addEventListener('keydown',ev=>{if(ev.key==='Enter'&&termin.value.trim()){const m=document.createElement('div');m.textContent='\u203a '+termin.value;termlog.appendChild(m);termin.value='';termlog.scrollTop=termlog.scrollHeight;}});
function placeTerm(){const ctr=new THREE.Vector3(SBOX[0],SBOX[1],0.01);headMesh.localToWorld(ctr);ctr.project(cam);const c0=new THREE.Vector3(SBOX[0]-SBOX[2]*0.5,SBOX[1]-SBOX[3]*0.5,0.01),c1=new THREE.Vector3(SBOX[0]+SBOX[2]*0.5,SBOX[1]+SBOX[3]*0.5,0.01);headMesh.localToWorld(c0);c0.project(cam);headMesh.localToWorld(c1);c1.project(cam);termDiv.style.left=((ctr.x*0.5+0.5)*innerWidth)+'px';termDiv.style.top=((-ctr.y*0.5+0.5)*innerHeight)+'px';termDiv.style.width=(Math.abs(c1.x-c0.x)*0.5*innerWidth*0.96)+'px';termDiv.style.height=(Math.abs(c1.y-c0.y)*0.5*innerHeight*0.96)+'px';}
function resetInside(){inph="play";headMesh.rotation.z=0;headMesh.scale.set(1,1,1);screen.scale.set(1,1,1);tvMat.opacity=0;termDiv.classList.remove('on');termDiv.style.opacity=0;scrMat.map=sFrames[0];scrMat.color.set(0xffffff);scrMat.needsUpdate=true;}

let rot=0,vel=0,dragging=false,lastX=0,moved=0,phase="rest",tA=null,target=null,dbg=null;
const back=document.getElementById('back');const rc=new THREE.Raycaster();
function norm(a){a%=Math.PI*2;return a<0?a+Math.PI*2:a;}
function topIndex(){return ((Math.round(rot/(Math.PI/3))%6)+6)%6;}
addEventListener('pointerdown',e=>{if(phase==="opening"||phase==="flying"||phase==="returning")return;dragging=true;moved=0;lastX=e.clientX;vel=0;target=null;});
addEventListener('pointermove',e=>{if(!dragging||phase!=="awake")return;const dx=e.clientX-lastX;lastX=e.clientX;moved+=Math.abs(dx);rot+=dx*0.01;vel=dx*0.01;});
addEventListener('pointerup',e=>{if(!dragging)return;dragging=false;if(moved<5)onTap(e);});
function onTap(e){if(phase==="rest"){wmpf.classList.add('go');wake();return;}
  if(phase==="inside"){if(inph==="play"){const n=new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);rc.setFromCamera(n,cam);if(rc.intersectObject(headMesh).length){inph="off";tIn=performance.now();}}return;}
  if(phase!=="awake")return;
  const ndc=new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);rc.setFromCamera(ndc,cam);
  const hit=rc.intersectObject(pick)[0];if(!hit)return;
  const lp=pick.worldToLocal(hit.point.clone());const r=Math.hypot(lp.x,lp.y);
  if(r<0.34){enter();return;}
  if(r<1.3){const deg=Math.atan2(lp.y,lp.x)*180/Math.PI;const idx=(((Math.round((90-deg)/60))%6)+6)%6;
    const des=idx*Math.PI/3;target=rot+Math.atan2(Math.sin(des-rot),Math.cos(des-rot));vel=0;}
}
function ease(t){return t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;}
function wake(){phase="waking";tA=performance.now();}
function enter(){phase="opening";tA=performance.now();}
back.onclick=()=>{if(phase!=="inside")return;phase="returning";tA=performance.now();back.style.opacity=0;resetInside();};
function fmap(arr,k){return arr[Math.max(0,Math.min(arr.length-1,Math.round(k*(arr.length-1))))];}
const L=(a,b,k)=>a+(b-a)*k;
const trkw=document.getElementById('trkw'),trk=document.getElementById('trk'),trkRows=[...trk.querySelectorAll('.row')],trkHl=trk.querySelector('.hl');
const PETAL_NAMES=["ORALS","INJECTABLES","PEPTIDES","SARMS","ANCILLARIES","OTHER"];
const ROW_C=[33.4,41.4,49.5,57.5,65.5,73.5];
trkRows.forEach((r,i)=>{r.textContent=PETAL_NAMES[i]||("PETAL "+(i+1));r.style.top=ROW_C[i]+"%";});
trkHl.style.top=(ROW_C[0]-3.48)+"%";let trkState='hidden';
const TERMHUE_DEG=50;termDiv.style.setProperty('--thr',TERMHUE_DEG+'deg');{const c=new THREE.Color(0x5cff9e),h={};c.getHSL(h);c.setHSL((h.h+TERMHUE_DEG/360)%1,h.s,h.l);headU.uTermColor.value.copy(c);}

function animate(ms){requestAnimationFrame(animate);const t=ms*0.001;
  const top=topIndex();
  {const aw=phase==="awake";if(aw&&trkState!=='on'){trkw.classList.add('show');trk.classList.remove('off');void trk.offsetWidth;trk.classList.add('on');trkState='on';}else if(!aw&&trkState==='on'){trk.classList.remove('on');void trk.offsetWidth;trk.classList.add('off');trkState='off';}else if(trkState==='off'&&(phase==='inside'||phase==='rest')){trkw.classList.remove('show');trk.classList.remove('off');trkState='hidden';}}
  {const lc=lightU.uLightColor.value;trkw.style.setProperty('--lc','rgb('+(lc.r*255|0)+','+(lc.g*255|0)+','+(lc.b*255|0)+')');}
  trkHl.style.top=(ROW_C[top]-3.48)+"%";
  for(let i=0;i<6;i++)trkRows[i].classList.toggle("sel",i===top);
  lightU.uLightColor.value.lerp(new THREE.Color(COLS[top]),0.1);
  lightU.uWake.value=L(lightU.uWake.value,(phase==="rest")?0:1,0.1);
  lightU.uWhiteI.value=L(lightU.uWhiteI.value,(phase==="rest")?0:0.8,0.1);
  let mi=0;
  for(let i=0;i<6;i++){
    let tS,tOn,pulseB,pulseA,pf,bobAmt;
    if(phase==="rest"){tS=1;tOn=1;pulseB=0.5;pulseA=0.22;pf=st[i].gf;bobAmt=1;}
    else{const awake=(phase==="waking"||phase==="awake");
      if(i===top){tS=1.05;tOn=awake?1:0;pulseB=0.9;pulseA=0.12;pf=0.5;bobAmt=awake?0.3:0;}
      else{tS=1;tOn=0;pulseB=0;pulseA=0;pf=0;bobAmt=0;}}
    st[i].sc=L(st[i].sc,tS,0.1);st[i].on=L(st[i].on,tOn,0.1);
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
  else if(phase==="flying"){const k=Math.min((performance.now()-tA)/1450,1),e=ease(k);setFace(portalTex[portalTex.length-1]);cam.position.z=Z_WAKE-(Z_WAKE-Z_END)*e;setMasked(cam.position.z>DROP_Z);mi=1-e;if(k>=1){phase="inside";back.style.opacity=1;resetInside();}}
  else if(phase==="inside"){setMasked(false);}
  // the room is ALWAYS live (stencil-hidden until the mouth opens) so flying in is seamless
  glareLit=L(glareLit,(inph==="zoom"||inph==="term")?0:1,0.1);
  headU.uGlareI.value=glareLit;
  glareMat.opacity=glareLit*(0.42+0.05*Math.sin(t*3.0));
  notesVis=L(notesVis,(inph==="play")?1:0,0.1);
  for(const n of notes){const by=n.ba*Math.sin(t*n.bf+n.bp)+n.da*Math.sin(t*n.df+n.dp), bx=n.sa*Math.sin(t*n.sf+n.sp);
    n.m.position.set(n.ax+bx,n.ay+by,0.03);n.m.rotation.z=n.ra*Math.sin(t*n.rf+n.rp);
    const sc=n.sz*(0.9+0.1*Math.sin(t*n.pf+n.pp));n.m.scale.set(sc,sc,1);n.m.material.opacity=notesVis;
    n.ft+=0.016;if(n.ft>=n.iv){n.ft=0;n.fi=(n.fi+1)%n.fr.length;n.m.material.map=n.fr[n.fi];n.m.material.needsUpdate=true;}}
  termGlowI=L(termGlowI,(inph==="zoom"||inph==="term")?1:0,0.12);
  headU.uTermI.value=termGlowI*0.95;
  tvLine.visible=(inph==="off");
  if(inph==="play"){
    scrMat.opacity=1;screen.scale.set(1,1,1);
    const sway=0.05*Math.sin(t*2.4), bobY=0.018*Math.sin(t*4.8+0.6);
    headMesh.position.set(sway,0.025+bobY,-1.99);
    headMesh.rotation.z=0.075*Math.sin(t*2.4);                         // lean into the bob, in place
    headMesh.scale.set(1+0.02*Math.sin(t*4.8),1-0.02*Math.sin(t*4.8),1);
    sft+=0.016;if(sft>0.1){sft=0;sfi=(sfi+1)%sFrames.length;scrMat.map=sFrames[sfi];scrMat.needsUpdate=true;}
  } else if(inph==="off"){              // CRT power-off + settle to centre
    headMesh.position.x=L(headMesh.position.x,0,0.12);headMesh.position.y=L(headMesh.position.y,0.025,0.12);headMesh.position.z=-1.99;
    headMesh.rotation.z=L(headMesh.rotation.z,0,0.15);headMesh.scale.set(1,1,1);
    const p=Math.min((performance.now()-tIn)/650,1);
    if(p<0.55){const q=p/0.55;screen.scale.set(1,1-q*0.96,1);tvLine.scale.set(1,0.05,1);tvMat.opacity=q*0.9;}
    else if(p<0.8){const q=(p-0.55)/0.25;screen.scale.set(1,0.04,1);scrMat.opacity=1-q;tvLine.scale.set(1-q*0.97,0.05,1);tvMat.opacity=0.95;}
    else{const q=(p-0.8)/0.2;scrMat.opacity=0;tvLine.scale.set(0.03,0.05*(1-q),1);tvMat.opacity=0.95*(1-q);}
    if(p>=1){inph="zoom";tIn=performance.now();scrMat.opacity=0;screen.scale.set(1,1,1);}
  } else if(inph==="zoom"){             // terminal comes toward the camera
    headMesh.position.x=L(headMesh.position.x,0,0.12);headMesh.position.y=L(headMesh.position.y,0.06,0.12);
    headMesh.position.z=L(headMesh.position.z,-1.02,0.1);
    scrMat.opacity=0;tvMat.opacity=0;
    if((performance.now()-tIn)/800>=1){inph="term";placeTerm();termDiv.classList.remove('on');void termDiv.offsetWidth;termDiv.classList.add('on');try{termin.focus();}catch(e){}}
  } else if(inph==="term"){
    scrMat.opacity=0;tvMat.opacity=0;headMesh.position.set(0,0.06,-1.02);placeTerm();
  }
  else if(phase==="returning"){const k=Math.min((performance.now()-tA)/1300,1),e=ease(k);cam.position.z=Z_END+((Z_WAKE)-Z_END)*e;setMasked(cam.position.z>DROP_Z);setFace(fmap(portalTex,1-e));mi=(1-e)*0.6;if(k>=1){phase="awake";rot=norm(rot);}}
  if(dbg!==null){setFace(fmap(portalTex,dbg));cam.position.z=Z_WAKE;setMasked(true);mi=dbg;}
  lightU.uMouthI.value=L(lightU.uMouthI.value,mi*1.25,0.22);
  mouthGlow.material.opacity=Math.min(0.55,lightU.uMouthI.value*0.42);
  rnd.render(scene,cam);}
animate(0);
addEventListener('resize',()=>{cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();rnd.setSize(innerWidth,innerHeight);});
window.__wake=()=>wake();window.__rest=()=>{phase="rest";rot=0;cam.position.z=Z_REST;};window.__setRot=v=>{rot=v;};window.__enter=()=>enter();
window.__phase=()=>phase;window.__top=()=>topIndex();
window.__dbgOpen=(k)=>{dbg=k;phase="awake";};
window.__inside=()=>{dbg=null;phase="inside";cam.position.z=Z_END;setMasked(false);back.style.opacity=1;resetInside();};
window.__tapHead=()=>{if(inph==="play"){inph="off";tIn=performance.now();}};
window.__state=()=>JSON.stringify({inph:inph,scrOp:scrMat.opacity,backOp:scrBackMat.opacity,hz:headMesh.position.z.toFixed(2)});
"""
SHELL=r"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<style>@font-face{font-family:'vt';src:url(__FONTVT__) format('woff2');font-display:swap;}@font-face{font-family:'tw';src:url(__FONTSE__) format('woff2');font-display:swap;}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
html,body{height:100%;overflow:hidden;background:#000;font-family:sans-serif;color:#fff;user-select:none;}
#c{position:fixed;inset:0;display:block;touch-action:none;}
#back{position:fixed;left:14px;top:max(18px,env(safe-area-inset-top));z-index:6;font-weight:700;font-size:.85rem;color:#fff;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:9px 18px;cursor:pointer;opacity:0;transition:opacity .4s;backdrop-filter:blur(10px);}
#term{position:fixed;transform:translate(-50%,-50%);opacity:0;z-index:4;display:flex;flex-direction:column;background:linear-gradient(160deg,#0e3d20,#06220f);border:1px solid rgba(120,255,170,.65);border-radius:7px;box-shadow:0 0 28px rgba(85,255,155,.7),inset 0 0 20px rgba(45,170,90,.5);overflow:hidden;transform-origin:50% 50%;filter:hue-rotate(var(--thr,0deg));}
#term.on{animation:termon .58s cubic-bezier(.4,.08,.2,1) forwards;}
@keyframes termon{0%{opacity:1;transform:translate(-50%,-50%) scale(1.25,.004);filter:brightness(6.5) contrast(1.5) hue-rotate(var(--thr,0deg));}10%{opacity:1;transform:translate(-50%,-50%) scale(1.25,.004);filter:brightness(6.5) contrast(1.5) hue-rotate(var(--thr,0deg));}50%{transform:translate(-50%,-50%) scale(1.22,.02);filter:brightness(4.5) contrast(1.3) hue-rotate(var(--thr,0deg));}70%{transform:translate(-50%,-50%) scale(1,1.06);filter:brightness(2.2) hue-rotate(var(--thr,0deg));}100%{opacity:1;transform:translate(-50%,-50%) scale(1,1);filter:brightness(1) hue-rotate(var(--thr,0deg));}}
#termlog{flex:1;padding:6px 11px;font:17px/1.18 'vt',ui-monospace,monospace;color:#9affc0;overflow-y:auto;text-shadow:0 0 7px rgba(110,255,165,.7);letter-spacing:.5px;}
#terminp{display:flex;align-items:center;gap:6px;padding:5px 11px;border-top:1px solid rgba(110,255,160,.35);}
#terminp span{color:#7dffae;font:18px 'vt',ui-monospace,monospace;text-shadow:0 0 6px rgba(110,255,165,.6);}
#termin{flex:1;min-width:0;background:transparent;border:none;outline:none;color:#d8ffe6;font:17px 'vt',ui-monospace,monospace;letter-spacing:.5px;}#termin::placeholder{color:#5ca87a;}
#wmpf{position:fixed;inset:0;background:url(__WMPFRAME__) center/cover no-repeat;opacity:1;pointer-events:none;z-index:6;transform-origin:50% 43%;will-change:transform,opacity;}
@keyframes wmpz{0%{opacity:1;transform:scale(1);}45%{opacity:1;}100%{opacity:0;transform:scale(5.2);}}
#wmpf.go{animation:wmpz 0.68s cubic-bezier(.5,0,.9,.4) forwards;}
#trkw{position:fixed;left:50%;bottom:4.5vh;transform:translateX(-50%);width:min(98vw,448px);aspect-ratio:528/374;z-index:3;pointer-events:none;opacity:0;--lc:#5cff9e;filter:drop-shadow(0 0 3px var(--lc)) drop-shadow(0 0 9px var(--lc)) drop-shadow(0 0 18px var(--lc));}
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
#trk .hl{position:absolute;left:7%;width:59%;height:6.95%;border-radius:3px;background:linear-gradient(180deg,#ffe27a,#f2b22e 55%,#c98a16);box-shadow:0 0 6px rgba(255,200,60,.55),inset 0 1px 0 rgba(255,255,255,.4);z-index:1;transition:top .18s cubic-bezier(.3,.8,.3,1);}</style></head><body>
<canvas id="c"></canvas><button id="back">‹ back</button>
<div id="term"><div id="termlog">nelson@bloom:~$ ready</div><div id="terminp"><span>$</span><input id="termin" placeholder="type a command…" autocomplete="off"/></div></div>
<div id="wmpf"></div>
<div id="trkw"><div id="trk"><div class="tint"></div><div class="ttl">TRACKER</div><div class="hl"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div></div></div>
<script>__THREE__</script><script>__CORE__</script></body></html>"""
core=CORE.replace("__SPL__",SPL).replace("__POS__",POS).replace("__COLS__",COLS).replace("__GLOW__",GLOW).replace("__EY__",EY).replace("__PO__",PO).replace("__RM__",RM).replace("__HEAD__",HEAD).replace("__ROOMBG__",ROOMBG).replace("__SFR__",SFR).replace("__SBOX__",SBOX).replace("__SMASK__",SMASK).replace("__GLAREPOS__",GLAREPOS).replace("__GLARE__",GLARE).replace("__NGA__",NGA).replace("__NGB__",NGB).replace("__NC__",NC).replace("__WMPFRAME__",WMPFRAME)
open("bloom-3d-local.html","w").write(SHELL.replace("__THREE__",THREE).replace("__CORE__",core).replace("__WMPFRAME__",WMPFRAME).replace("__XBOX__",XBOX).replace("__FONTVT__",FONTVT).replace("__FONTSE__",FONTSE))
open("/mnt/user-data/outputs/bloom-3d.html","w").write(SHELL.replace("<script>__THREE__</script>",'<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>').replace("__CORE__",core).replace("__WMPFRAME__",WMPFRAME).replace("__XBOX__",XBOX).replace("__FONTVT__",FONTVT).replace("__FONTSE__",FONTSE))
print("lit-shader build written")
