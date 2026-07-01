import json,os
# Deliverable dir: the Linux sandbox default when present, else a local ./dist (macOS/dev).
OUT_DIR="/mnt/user-data/outputs" if os.path.isdir("/mnt/user-data/outputs") else "dist"
os.makedirs(OUT_DIR,exist_ok=True)
d=json.load(open("embed_portal.json"))
SPL=json.dumps(d["petalsSplit"]);POS=json.dumps(d["petalPos"]);COLS=json.dumps(d["petalCols"]);GLOW=d["glow"]
EY=json.dumps(d["eyes"]);PO=json.dumps(d["portal"]);RM=d["room"];HEAD=d["head"];ROOMBG=d["roomBg"];SFR=json.dumps(d["screenFrames"]);SBOX=json.dumps(d["screenBox"]);SMASK=d["screenMask"];GLAREPOS=json.dumps(d["glarePos"]);GLARE=d["glare"];NGA=json.dumps(d["noteGifA"]);NGB=json.dumps(d["noteGifB"]);NC=d["noteCol"];WMPFRAME=d["wmpFrame"];XBOX=d["xboxPanel"];FONTVT=d["fontVT"];FONTSE=d["fontSE"];BGFLOWER=d["bgFlower"];BGVIDEO=d["bgVideo"];BGFRAMES=json.dumps(d["bgFrames"]);MP=d["mp"];BACKBTN=d["backbtn"];BOOT=d["boot"];DS=d["ds"];DSPIC=d["dsbg"]
THREE=open("three.min.js").read()
# stack_v5 seed baked as the offline default (gitignored; falls back to empty skeleton when absent)
try:
    STACK_SEED=json.dumps(json.load(open("backend/stack_v5.seed.json")),separators=(',',':'))
except Exception:
    STACK_SEED='{"version":5,"updated":null,"compounds":[],"inventory":{},"packing":{"items":[],"checklist":[]},"state":{"trip":7,"done":{},"checked":{},"streaks":{},"promoted":{},"logs":[]}}'

CORE=r"""
const PETS=__SPL__,POS=__POS__,COLS=__COLS__,GLOW="__GLOW__",EYES=__EY__,PORTAL=__PO__,RM="__RM__";
const HEAD="__HEAD__",ROOMBG="__ROOMBG__",SFR=__SFR__,SBOX=__SBOX__,SMASK="__SMASK__",GLAREPOS=__GLAREPOS__,GLARE="__GLARE__",NGA=__NGA__,NGB=__NGB__,NC="__NC__";
/* ===== stack_v5 backend config (set after deploying backend/worker.js; empty = offline-only) ===== */
const STORE_URL="";          /* e.g. "https://bloom-stack.you.workers.dev" */
const STORE_TOKEN="";        /* BLOOM_TOKEN */
const NELSON_URL="";         /* e.g. "http://localhost:8787/nelson" (local dev only) */
const LS_KEY="bloom_stack_v5";
const today=()=>{const d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);};  /* LOCAL date — checks reset at your midnight */
const STACK_DEFAULT=__STACK_SEED__;
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
const HFS="uniform sampler2D uMap;uniform vec2 uGlarePos;uniform vec3 uGlareColor;uniform float uGlareI,uAmbient,uGlareR;uniform vec2 uTermUV;uniform vec3 uTermColor;uniform float uTermI,uTermR;varying vec2 vUv;varying vec2 vW;void main(){vec4 t=texture2D(uMap,vUv);float d=distance(vW,uGlarePos);float r=d/uGlareR;float at=uGlareI/(1.0+r*r);vec3 col=t.rgb*1.3*(uAmbient+at*0.8)+uGlareColor*at*0.16;float dT=distance(vUv,uTermUV);float atT=uTermI/(1.0+pow(dT/uTermR,2.0));col+=uTermColor*atT*(0.28+0.5*t.rgb);gl_FragColor=vec4(min(col,vec3(1.4)),t.a);}";
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
/* ===== Nelson \u2014 Claude (Opus 4.8) agent that edits the stack via tool use ===== */
const NEL_KEY_LS='bloom_anthropic_key',NEL_MODEL='claude-opus-4-8';
let nelMsgs=[];
function nelGetKey(){try{return localStorage.getItem(NEL_KEY_LS)||'';}catch(e){return '';}}
function nelLog(txt,cls){const m=document.createElement('div');if(cls)m.className=cls;m.textContent=txt;termlog.appendChild(m);termlog.scrollTop=termlog.scrollHeight;return m;}
function nelDownloadSave(){try{var data=JSON.stringify(Store.data,null,2),blob=new Blob([data],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='bloom-stack-'+today()+'.json';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(url);},1000);return true;}catch(e){nelLog('save failed: '+(e&&e.message?e.message:e),'nelerr');return false;}}
function nelLoadSave(){var inp=document.createElement('input');inp.type='file';inp.accept='application/json,.json';inp.onchange=function(){var f=inp.files&&inp.files[0];if(!f)return;var r=new FileReader();r.onload=function(){try{var d=JSON.parse(r.result);if(!d||!d.compounds)throw 'not a bloom save file';Store.data=d;Store._save();Store._render();nelLog('loaded save ('+d.compounds.length+' items).','nelmsg');}catch(e){nelLog('load failed: '+(e&&e.message?e.message:e),'nelerr');}};r.readAsText(f);};inp.click();}
function nelSnapshot(){var d=Store.data,dl={},du={};d.compounds.forEach(function(c){if(c.route==='inject'){var x=Store.invDaysLeft(c.id);if(x!=null)dl[c.id]=x;}du[c.id]=dueToday(c.sched);});
 return JSON.stringify({compounds:d.compounds,inventory:d.inventory,packing:d.packing,trip:d.state.trip,checkedToday:d.state.done[today()]||{},packingChecked:Object.keys(d.state.checked||{}).filter(function(k){return k.indexOf('2:')===0;}),streaks:d.state.streaks,derived:{daysLeft:dl,dueToday:du}});}
function nelResolve(a){var cs=Store.data.compounds,c;if(a.id){c=cs.find(function(x){return x.id===a.id;});if(c)return c;}
 if(a.name){var nm=(''+a.name).toLowerCase(),ms=cs.filter(function(x){return x.name.toLowerCase()===nm;});if(!ms.length)ms=cs.filter(function(x){return x.name.toLowerCase().indexOf(nm)>=0;});
  if(a.petal!=null){var f=ms.filter(function(x){return x.petal===a.petal;});if(f.length)ms=f;}
  if(ms.length===1)return ms[0];if(ms.length>1)throw 'ambiguous name "'+a.name+'" ('+ms.length+' matches) - give id or petal';}
 throw 'no item matching '+(a.id||a.name);}
const NEL_PETALS='0=PSYCH oral AM(top)/PM(bot); 1=INJECT injectables (inventory+schedule); 2=PACKING; 3=ANCILLARY oral support AM/PM; 4=PENDING incoming(top)/standby(bot); 5=TOPICAL hair(top)/skin(bot)';
const NEL_TOOLS=[
 {name:'add_item',description:'Add a new item to a petal. petal 0/3/5 are orals/topicals, 1 is injectables (also creates inventory), 4 is pending. seg is top or bot.',input_schema:{type:'object',properties:{petal:{type:'integer'},seg:{type:'string',enum:['top','bot']},name:{type:'string'},dose:{type:'string'},sched:{type:'string',description:'daily, AM, PM, or weekday set like MWF / Tu/Fr / T/Th/Su'}},required:['petal','seg','name']}},
 {name:'edit_item',description:'Change a field of an existing item, identified by id or name. field is name, dose, sched, petal, or seg.',input_schema:{type:'object',properties:{id:{type:'string'},name:{type:'string'},field:{type:'string',enum:['name','dose','sched','petal','seg']},value:{type:'string'}},required:['field','value']}},
 {name:'delete_item',description:'Remove an item, by id or name.',input_schema:{type:'object',properties:{id:{type:'string'},name:{type:'string'}}}},
 {name:'set_inventory',description:'Set injectable inventory numbers (units, perDose, freqPerWeek), by id or name.',input_schema:{type:'object',properties:{id:{type:'string'},name:{type:'string'},units:{type:'number'},perDose:{type:'number'},freqPerWeek:{type:'number'}}}},
 {name:'log_injection',description:'Log an injection for today (decrements inventory). Toggles off if already logged. By id or name.',input_schema:{type:'object',properties:{id:{type:'string'},name:{type:'string'}}}},
 {name:'check_item',description:'Toggle the taken state for today for an oral or topical item. By id or name.',input_schema:{type:'object',properties:{id:{type:'string'},name:{type:'string'}}}},
 {name:'set_trip',description:'Set the PACKING trip duration in days (1-90).',input_schema:{type:'object',properties:{days:{type:'integer'}},required:['days']}},
 {name:'promote_item',description:'Move a PENDING item into an active petal as a live item. Identify the pending item by id or name; give destination petal and seg, and optionally dose and sched.',input_schema:{type:'object',properties:{id:{type:'string'},name:{type:'string'},petal:{type:'integer'},seg:{type:'string',enum:['top','bot']},dose:{type:'string'},sched:{type:'string'}},required:['petal']}},
 {name:'add_packing_item',description:'Add an item to the PACKING checklist.',input_schema:{type:'object',properties:{name:{type:'string'}},required:['name']}},
 {name:'remove_packing_item',description:'Remove a PACKING checklist item by name.',input_schema:{type:'object',properties:{name:{type:'string'}},required:['name']}},
 {name:'check_packing',description:'Check or uncheck a PACKING checklist item by name. Set checked false to uncheck.',input_schema:{type:'object',properties:{name:{type:'string'},checked:{type:'boolean'}},required:['name']}},
 {name:'reset_packing',description:'Uncheck every PACKING checklist item.',input_schema:{type:'object',properties:{}}},
 {name:'download_save',description:'Export the entire current stack as a JSON backup file that downloads to the device.',input_schema:{type:'object',properties:{}}},
 {name:'get_stack',description:'Return the current full stack as JSON, including derived days-left and due-today.',input_schema:{type:'object',properties:{}}}];
function nelRun(name,inp){inp=inp||{};
 if(name==='get_stack')return nelSnapshot();
 if(name==='add_item'){var seg=inp.seg||'top',c=newCompound(inp.petal,seg);c.name=inp.name;if(inp.dose!=null)c.dose=inp.dose;if(inp.sched!=null)c.sched=inp.sched;Store.action({type:'item.add',compound:c});return 'added '+c.name+' (id '+c.id+') to petal '+inp.petal+' '+seg;}
 if(name==='edit_item'){var c=nelResolve(inp),v=(inp.field==='petal')?parseInt(inp.value,10):inp.value;Store.action({type:'item.edit',id:c.id,field:inp.field,value:v});return 'set '+c.name+'.'+inp.field+' = '+inp.value;}
 if(name==='delete_item'){var c=nelResolve(inp);Store.action({type:'item.delete',id:c.id});return 'deleted '+c.name;}
 if(name==='set_inventory'){var c=nelResolve(inp);['units','perDose','freqPerWeek'].forEach(function(f){if(inp[f]!=null)Store.action({type:'inv.edit',id:c.id,field:f,value:inp[f]});});return 'updated inventory for '+c.name;}
 if(name==='log_injection'){var c=nelResolve(inp);Store.action({type:'inject.log',id:c.id});return 'toggled injection log for '+c.name;}
 if(name==='check_item'){var c=nelResolve(inp);Store.action({type:'tap',id:c.id});return 'toggled check for '+c.name;}
 if(name==='set_trip'){Store.action({type:'trip',value:inp.days});return 'trip set to '+inp.days+' days';}
 if(name==='promote_item'){var pend=Store.data.compounds.filter(function(x){return x.route==='pending';}),c;if(inp.id)c=pend.find(function(x){return x.id===inp.id;})||nelResolve(inp);else{var nm=(''+(inp.name||'')).toLowerCase(),ms=pend.filter(function(x){return x.name.toLowerCase().indexOf(nm)>=0;});c=(ms.length===1)?ms[0]:nelResolve(inp);}Store.action({type:'item.promote',id:c.id,petal:inp.petal,seg:inp.seg,dose:inp.dose,sched:inp.sched});return 'promoted '+c.name+' to petal '+inp.petal+(inp.seg?' '+inp.seg:'');}
 if(name==='add_packing_item'){Store.action({type:'packing.add',name:inp.name});return 'added '+inp.name+' to packing checklist';}
 if(name==='remove_packing_item'){Store.action({type:'packing.del',name:inp.name});return 'removed '+inp.name+' from packing checklist';}
 if(name==='check_packing'){var arr=Store.data.packing.checklist||[],nm=(''+inp.name).toLowerCase(),ix=arr.findIndex(function(x){return x.toLowerCase().indexOf(nm)>=0;});if(ix<0)throw 'no packing item matching '+inp.name;Store.action({type:'packing.checkSet',idx:ix,on:inp.checked!==false});return (inp.checked!==false?'checked ':'unchecked ')+arr[ix];}
 if(name==='reset_packing'){Store.action({type:'checklist.reset'});return 'packing checklist reset';}
 if(name==='download_save'){nelDownloadSave();return 'started download of bloom-stack-'+today()+'.json';}
 throw 'unknown tool '+name;}
async function nelSend(userText){var key=nelGetKey();if(!key){nelLog('no API key set. type:  /key sk-ant-...','nelerr');return;}
 nelMsgs.push({role:'user',content:userText});
 var sys='You are Nelson, the assistant inside the Bloom stack-tracker app. You edit the supplement/peptide stack by calling tools. Petals: '+NEL_PETALS+'. Schedules use daily/AM/PM or weekday sets (MWF, Tu/Fr, T/Th/Su). When asked to change the stack, call the right tools - you may call several in one turn to edit multiple petals at once. After acting, reply in one or two short sentences. You can also answer questions about the stack - days of inventory left (derived.daysLeft, keyed by id), what is due today (derived.dueToday), streaks, packing - using the snapshot or get_stack; just answer, do not call edit tools for a question. You can promote pending items and manage the packing checklist. Current stack:\n'+nelSnapshot();
 var pending=nelLog('nelson: ...','nelpending');
 try{for(var step=0;step<8;step++){
   var res=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'content-type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01','anthropic-dangerous-direct-browser-access':'true'},body:JSON.stringify({model:NEL_MODEL,max_tokens:1024,system:sys,tools:NEL_TOOLS,messages:nelMsgs})});
   if(!res.ok){var et=await res.text();if(pending)pending.remove();nelLog('nelson: API error '+res.status+' '+et.slice(0,160),'nelerr');nelMsgs.pop();return;}
   var data=await res.json();nelMsgs.push({role:'assistant',content:data.content});
   var texts=data.content.filter(function(b){return b.type==='text';}).map(function(b){return b.text;}).join(' ').trim();
   if(texts){if(pending){pending.remove();pending=null;}nelLog('nelson: '+texts,'nelmsg');}
   var tus=data.content.filter(function(b){return b.type==='tool_use';});
   if(data.stop_reason!=='tool_use'||!tus.length){if(pending)pending.remove();return;}
   var results=tus.map(function(tu){var out,err=false;try{out=''+nelRun(tu.name,tu.input);}catch(e){out='ERROR: '+(e&&e.message?e.message:e);err=true;}nelLog('  '+(err?'x ':'> ')+tu.name+': '+(out.length>80?out.slice(0,80)+'\u2026':out),err?'nelerr':'neltool');return {type:'tool_result',tool_use_id:tu.id,content:out,is_error:err};});
   nelMsgs.push({role:'user',content:results});if(!pending)pending=nelLog('nelson: ...','nelpending');
  }
  if(pending)pending.remove();nelLog('nelson: (stopped after 8 steps)','nelerr');
 }catch(e){if(pending)pending.remove();nelLog('nelson: network error - '+(e&&e.message?e.message:e),'nelerr');}}
termin.addEventListener('keydown',function(ev){if(ev.key!=='Enter')return;var txt=termin.value.trim();if(!txt)return;termin.value='';nelLog('\u203a '+txt);
 if(txt.indexOf('/key')===0){var k=txt.slice(4).trim();if(k){try{localStorage.setItem(NEL_KEY_LS,k);}catch(e){}nelLog('key saved (stored locally in this browser only - dev use).','nelmsg');}else{nelLog(nelGetKey()?'key is set. /key <new> to replace, /forget to remove.':'no key. /key sk-ant-... to add one.','nelmsg');}return;}
 if(txt==='/forget'){try{localStorage.removeItem(NEL_KEY_LS);}catch(e){}nelLog('key removed.','nelmsg');return;}
 if(txt==='/reset'){nelMsgs=[];nelLog('conversation reset.','nelmsg');return;}
 if(txt==='/save'){nelLog('exporting bloom-stack-'+today()+'.json','nelmsg');nelDownloadSave();return;}
 if(txt==='/load'){nelLog('choose a save file to restore...','nelmsg');nelLoadSave();return;}
 nelSend(txt);});
function placeTerm(){const ctr=new THREE.Vector3(SBOX[0],SBOX[1],0.01);headMesh.localToWorld(ctr);ctr.project(cam);const c0=new THREE.Vector3(SBOX[0]-SBOX[2]*0.5,SBOX[1]-SBOX[3]*0.5,0.01),c1=new THREE.Vector3(SBOX[0]+SBOX[2]*0.5,SBOX[1]+SBOX[3]*0.5,0.01);headMesh.localToWorld(c0);c0.project(cam);headMesh.localToWorld(c1);c1.project(cam);termDiv.style.left=((ctr.x*0.5+0.5)*innerWidth)+'px';termDiv.style.top=((-ctr.y*0.5+0.5)*innerHeight - 10)+'px';termDiv.style.width=(Math.abs(c1.x-c0.x)*0.5*innerWidth*0.96)+'px';termDiv.style.height=(Math.abs(c1.y-c0.y)*0.5*innerHeight*0.96)+'px';}
function resetInside(){inph="play";headMesh.rotation.z=0;headMesh.scale.set(1,1,1);screen.scale.set(1,1,1);tvMat.opacity=0;termDiv.classList.remove('on','off');termDiv.style.opacity=0;scrMat.map=sFrames[0];scrMat.color.set(0xffffff);scrMat.needsUpdate=true;}

let rot=0,vel=0,dragging=false,lastX=0,moved=0,phase="rest",tA=null,target=null,dbg=null;
const back=document.getElementById('back'),info=document.getElementById('info'),infobub=document.getElementById('infobub');let infoState='off';const rc=new THREE.Raycaster();
const sceneEl=document.getElementById('scene'),dsEl=document.getElementById('ds'),bgEl=document.getElementById('bgkeep'),dsImg=dsEl.querySelector('img'),dswT=document.getElementById('dswT'),dswB=document.getElementById('dswB'),dsvigEl=document.getElementById('dsvig');let clickIdx=0;const _tcol=new THREE.Color();let _lr=-1,_lg=-1,_lb=-1;let _lf=0;
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
/* ===== stack_v5 store (offline-first; syncs to backend/worker.js when STORE_URL set) ===== */
const STREAK_ID={5:'topical-pm'},PROMOTE_ID={4:'anastrozole-pend'};
const LOG_ITEMS={1:[{id:'ghk-cu',units:4},{id:'test-cyp',units:25}]};   /* INJECT bot rows, in order */
const INJ_DAYS={1:[{id:'hcg',ri:0},{id:'ghk-cu',ri:1},{id:'test-cyp',ri:2}]};  /* live days-left → schedule rows */
function applyAction(s,a){var st=s.state;
 if(a.type==='tap'){var day=(st.done[today()]||(st.done[today()]={}));if(a.id){if(day[a.id])delete day[a.id];else day[a.id]=true;}else{var k='p'+a.petal+':'+a.key;if(day[k])delete day[k];else day[k]=true;}}
 else if(a.type==='check'){var k=a.petal+':'+a.idx;if(st.checked[k])delete st.checked[k];else st.checked[k]=true;}
 else if(a.type==='streak'){var c=(st.streaks[a.id]||(st.streaks[a.id]={count:0,lastDate:null}));if(c.lastDate!==today()){c.count++;c.lastDate=today();}}
 else if(a.type==='promote'){if(st.promoted[a.id])delete st.promoted[a.id];else st.promoted[a.id]=true;}
 else if(a.type==='trip'){st.trip=Math.max(1,Math.min(90,a.value|0));}
 else if(a.type==='log'){var dd=(st.loggedDays||(st.loggedDays={})),key=today()+':'+a.petal,day=(st.done[today()]||(st.done[today()]={})),items=a.items||[];
   if(dd[key]){items.forEach(function(it,ix){var inv=s.inventory[it.id];if(inv)inv.units+=it.units;delete day['p'+a.petal+':b'+ix];for(var j=st.logs.length-1;j>=0;j--){if(st.logs[j].id===it.id){st.logs.splice(j,1);break;}}});delete dd[key];}
   else{items.forEach(function(it,ix){var inv=s.inventory[it.id];if(inv)inv.units=Math.max(0,inv.units-it.units);st.logs.push({id:it.id,units:it.units,ts:new Date().toISOString()});day['p'+a.petal+':b'+ix]=true;});dd[key]=true;}}
 else if(a.type==='item.add'){s.compounds.push(a.compound);if(a.compound.route==='inject'&&!s.inventory[a.compound.id])s.inventory[a.compound.id]={units:0,perDose:0,freqPerWeek:7,unit:'u'};}
 else if(a.type==='item.edit'){var c=s.compounds.find(function(x){return x.id===a.id;});if(c){c[a.field]=a.value;if(a.field==='qty')c.qtyDate=today();}}
 else if(a.type==='item.delete'){s.compounds=s.compounds.filter(function(x){return x.id!==a.id;});if(st.done[today()])delete st.done[today()][a.id];delete s.inventory[a.id];}
 else if(a.type==='inv.edit'){var v=s.inventory[a.id]||(s.inventory[a.id]={units:0,perDose:0,freqPerWeek:7,unit:'u'});var n=parseFloat(a.value);v[a.field]=isNaN(n)?0:n;}
 else if(a.type==='inject.log'){var day=(st.done[today()]||(st.done[today()]={})),inv=s.inventory[a.id],u=(inv?inv.perDose:0);
   if(day[a.id]){if(inv)inv.units+=u;delete day[a.id];for(var j=st.logs.length-1;j>=0;j--){if(st.logs[j].id===a.id){st.logs.splice(j,1);break;}}}
   else{if(inv)inv.units=Math.max(0,inv.units-u);day[a.id]=true;st.logs.push({id:a.id,units:u,ts:new Date().toISOString()});}}
 else if(a.type==='item.promote'){var c=s.compounds.find(function(x){return x.id===a.id;});if(c){c.petal=a.petal;if(a.seg)c.seg=a.seg;c.route=ROUTE_BY_PETAL[a.petal]||c.route;if(a.dose!=null)c.dose=a.dose;if(a.sched!=null)c.sched=a.sched;if(c.route==='inject'&&!s.inventory[c.id])s.inventory[c.id]={units:0,perDose:0,freqPerWeek:7,unit:'u'};}}
 else if(a.type==='packing.add'){(s.packing.checklist||(s.packing.checklist=[])).push(a.name);}
 else if(a.type==='packing.del'){var arr=s.packing.checklist||[],ix=(a.idx!=null)?a.idx:arr.findIndex(function(x){return x.toLowerCase().indexOf((''+a.name).toLowerCase())>=0;});if(ix>=0)arr.splice(ix,1);}
 else if(a.type==='packing.checkSet'){var k='2:'+a.idx;if(a.on)st.checked[k]=true;else delete st.checked[k];}
 else if(a.type==='checklist.reset'){Object.keys(st.checked).forEach(function(k){if(k.indexOf('2:')===0)delete st.checked[k];});}
 return s;}
function syncCATS(){
 (INJ_DAYS[1]||[]).forEach(function(m){var d=Store.invDaysLeft(m.id);if(d!=null){var row=CATS[1].top.rows[m.ri];if(row)row[1]=row[1].replace(/\d+d$/,d+'d');}});
 var pk=Store.data.packing;if(pk&&pk.items&&pk.items.length){CATS[2].top.calc=pk.items.map(function(p){return [p.name,p.perWeek,p.unit,p.perUnit];});if(pk.checklist)CATS[2].bot.checks=pk.checklist.slice();}}
const Store={
 data:JSON.parse(JSON.stringify(STACK_DEFAULT)),
 invDaysLeft:function(id){var v=this.data.inventory[id];if(!v)return null;var b=v.perDose*v.freqPerWeek/7;return b>0?Math.floor(v.units/b):null;},
 _local:function(){try{var r=localStorage.getItem(LS_KEY);if(r)this.data=JSON.parse(r);}catch(e){}},
 _save:function(){try{localStorage.setItem(LS_KEY,JSON.stringify(this.data));}catch(e){}},
 _migrate:function(){var ch=false;(this.data.compounds||[]).forEach(function(c){if(isOral(c)&&bubVal(c.qty)!==''&&!c.qtyDate){c.qtyDate=today();ch=true;}});if(ch)this._save();},  // existing oral counts begin auto-decrementing from today
 _render:function(){syncCATS();if(dsEl.style.display!=='none')dsFill(clickIdx);},
 load:async function(){this._local();this._migrate();this._render();
  if(STORE_URL){try{var r=await fetch(STORE_URL+'/state');if(r.ok){this.data=await r.json();this._save();this._render();}}catch(e){}}},
 action:async function(a){applyAction(this.data,a);this._save();this._render();
  if(STORE_URL){try{var r=await fetch(STORE_URL+'/action',{method:'POST',headers:{'content-type':'application/json','x-bloom-token':STORE_TOKEN},body:JSON.stringify(a)});if(r.ok){this.data=await r.json();this._save();this._render();}}catch(e){}}}};
function dsSt(i){var S=Store.data.state,day=S.done[today()]||{},done={},checked={},pre='p'+i+':',cpre=i+':';
 for(var k in day){if(k.indexOf(pre)===0)done[k.slice(pre.length)]=day[k];}
 for(var c in S.checked){if(c.indexOf(cpre)===0)checked[c.slice(cpre.length)]=S.checked[c];}
 var strk=STREAK_ID[i],pro=PROMOTE_ID[i];
 return {done:done,checked:checked,trip:S.trip,streak:(strk&&S.streaks[strk])?S.streaks[strk].count:0,logged:!!(S.loggedDays&&S.loggedDays[today()+':'+i]),promoted:!!(pro&&S.promoted[pro])};}
Store.load();
function dsSegLegacy(s,side,i){var st=dsSt(i);
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
/* ===== store-driven DS tiles ===== */
const CATNAME=['PSYCHO','INJECT','PACKING','ANCILLARY','PENDING','TOPICAL'];
const SEG=[
 {top:{name:'AM STACK',kind:'check'},bot:{name:'PM STACK',kind:'check'}},
 {top:{name:'SCHEDULE',kind:'inject',mode:'sched'},bot:{name:'LOG TODAY',kind:'inject',mode:'log'}},
 {top:{name:'CALCULATOR',kind:'legacy'},bot:{name:'CHECKLIST',kind:'legacy'}},
 {top:{name:'AM SUPPORT',kind:'check'},bot:{name:'PM SUPPORT',kind:'check'}},
 {top:{name:'INCOMING',kind:'pending'},bot:{name:'STANDBY',kind:'pending'}},
 {top:{name:'HAIR',kind:'check'},bot:{name:'SKIN PM',kind:'check',streak:'topical-pm',order:'soft'}}];
const DAYMAP={su:0,sun:0,u:0,m:1,mon:1,tu:2,tue:2,t:2,w:3,wed:3,th:4,thu:4,f:5,fr:5,fri:5,sa:6,sat:6,s:6};
function dueDays(sched){if(!sched)return null;var s=(''+sched).trim();if(/^(daily|am|pm|qd|ed|prn)$/i.test(s))return null;var set={};s.split('/').forEach(function(p){p=p.trim();if(!p)return;var key=p.toLowerCase();if(DAYMAP.hasOwnProperty(key)){set[DAYMAP[key]]=1;return;}for(var j=0;j<p.length;){var two=p.substr(j,2).toLowerCase(),one=p.substr(j,1).toLowerCase();if((two==='th'||two==='tu'||two==='su'||two==='sa')&&DAYMAP.hasOwnProperty(two)){set[DAYMAP[two]]=1;j+=2;}else if(DAYMAP.hasOwnProperty(one)){set[DAYMAP[one]]=1;j+=1;}else j+=1;}});return Object.keys(set).length?set:null;}
function dueToday(sched){var d=dueDays(sched);if(!d)return true;return !!d[new Date().getDay()];}
function compoundsFor(i,seg){return Store.data.compounds.filter(function(c){return c.petal===i&&(!seg||c.seg===seg);});}
let dsEdit={top:false,bot:false};
const ROUTE_BY_PETAL={0:'oral',1:'inject',3:'support',4:'pending',5:'topical'};const LOW_STOCK_D=10;
function esc(s){return (''+(s==null?'':s)).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');}
function newCompound(petal,seg){return {id:'c'+Date.now().toString(36)+Math.floor(Math.random()*1e4),name:'New item',petal:petal,seg:seg,route:ROUTE_BY_PETAL[petal]||'oral',dose:'',sched:'daily'};}
function dsHdr(name,chip,eside){var ed=eside?dsEdit[eside]:false;
 return '<div class="dswh"><span class="ttl"><i class="dswdot"></i>'+name+'</span><span class="dswhr">'+(eside?'<span class="dsedit'+(ed?' on':'')+'" data-edit="'+eside+'">'+(ed?'done':'✎ edit')+'</span>':'')+'<span class="dswchip">'+chip+'</span></span></div>';}
function isOral(c){return !!(c&&(c.route==='oral'||c.route==='support'));}
function oralDaily(c){var s=(''+(c.sched||'')).toLowerCase();return (/am/.test(s)&&/pm/.test(s))?2:1;}  // twice-daily if both AM & PM, else once
function schedDays(c){return dueDays((''+(c.sched||'')).toLowerCase().replace(/am|pm|daily|qd|ed|prn|once/g,' ').trim());}  // weekday set the item is taken on (null = every day), AM/PM stripped
function oralUsed(c){if(!c.qtyDate)return 0;var per=oralDaily(c),days=schedDays(c);var start=new Date(c.qtyDate+'T00:00:00'),end=new Date(today()+'T00:00:00');if(isNaN(start.getTime())||!(end>start))return 0;var n=0,d=start,g=0;while(d<end&&g<4000){var wd=d.getDay();if(!days||days[wd])n+=per;d.setDate(d.getDate()+1);g++;}return n;}
function bubQtyN(c){var b=parseFloat(c.qty);if(isNaN(b))return NaN;return isOral(c)?Math.max(0,b-oralUsed(c)):b;}  // orals auto-count-down from qtyDate baseline; no log needed
function bubQtyStr(c){var n=bubQtyN(c);return isNaN(n)?'':(''+n);}
function fmtMD(d){return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()]+' '+d.getDate();}
function runOut(c){var q=bubQtyN(c);if(isNaN(q)||q<=0)return null;var per=oralDaily(c)||1,days=schedDays(c),d=new Date(today()+'T00:00:00'),rem=q,g=0;while(g<4000){var wd=d.getDay();if(!days||days[wd]){rem-=per;if(rem<=0)return d;}d.setDate(d.getDate()+1);g++;}return null;}  // project forward at the scheduled consumption rate to the exhaustion date
function bubLow(c){var q=bubQtyN(c),r=parseFloat(c.reorderAt);return(!isNaN(q)&&!isNaN(r)&&q<=r);}
function bubVal(v){return (v==null?'':(''+v).trim());}
function bubbleCard(c,o){o=o||{};var hasQ=bubVal(c.qty)!=='',low=bubLow(c),cls='dbub';if(o.tap){cls+=' tap';if(o.done)cls+=' done';if(o.due===false)cls+=' off';}if(low)cls+=' low';
 var ro=(isOral(c)||c.route==='inject')?runOut(c):null,roStr=ro?'<span class="dbout">out <b>'+fmtMD(ro)+'</b></span>':'';
 var mid=hasQ?('<span class="dbq">'+esc(bubQtyStr(c))+'</span><span class="dbqu">left</span>'+roStr+(low?'<span class="dbro">REORDER</span>':(bubVal(c.reorderAt)!==''?'<span class="dbthr">reorder @ '+esc(c.reorderAt)+'</span>':''))):'<span class="dbqm">— set count —</span>';
 var src=esc(c.source||'');
 return '<div class="'+cls+'" data-id="'+c.id+'"'+(o.tap==='inject'?' data-log="1"':'')+'>'
  +'<div class="dbnm">'+(o.tap?'<i class="dbck">'+(o.done?'&#10003;':'&#9656;')+'</i>':'')+'<span class="dbnt">'+esc(c.name)+'</span></div>'
  +'<div class="dbmid">'+mid+'</div>'
  +'<div class="dbbot"><span class="dbdose">'+(esc(c.dose||'')||'—')+'</span>'+(src?'<span class="dbsrc">'+src+'</span>':'')+'</div>'
  +'</div>';}
function bubbleEdit(c){return '<div class="dbube" data-id="'+c.id+'">'
  +'<input class="ein enm" data-field="name" value="'+esc(c.name)+'" placeholder="name"/>'
  +'<div class="dbrow2"><input class="ein" data-field="qty" value="'+esc(bubQtyStr(c))+'" placeholder="qty left" inputmode="decimal"/><input class="ein" data-field="reorderAt" value="'+esc(c.reorderAt)+'" placeholder="reorder @" inputmode="decimal"/></div>'
  +'<div class="dbrow2"><input class="ein" data-field="dose" value="'+esc(c.dose)+'" placeholder="dose"/><input class="ein" data-field="sched" value="'+esc(c.sched)+'" placeholder="sched"/></div>'
  +'<input class="ein" data-field="source" value="'+esc(c.source)+'" placeholder="pharmacy / source"/>'
  +'<b class="del" data-del="'+c.id+'">&times; remove</b></div>';}
function isBub(d){return !!(d&&(d.kind==='check'||d.kind==='inject'||d.kind==='pending'));}
function clearSlant(winEl){var k=winEl.querySelectorAll('.dswbody>*');for(var j=0;j<k.length;j++){k[j].style.marginLeft='';k[j].style.marginRight='';}}
function checkSeg(i,seg,def){var eside=(seg==='top')?'top':'bot',editing=dsEdit[eside],o=dsHdr(def.name,CATNAME[i],eside),list=compoundsFor(i,seg);
 if(editing){list.forEach(function(c){o+=bubbleEdit(c);});o+='<div class="dswadd" data-add="'+eside+'">+ add item</div>';return o;}
 var dm=Store.data.state.done[today()]||{};
 if(!list.length)o+='<div class="dbmt">no items yet — tap edit to add</div>';
 list.forEach(function(c){o+=bubbleCard(c,{tap:'check',due:dueToday(c.sched),done:!!dm[c.id]});});
 if(def.streak){var sk=Store.data.state.streaks[def.streak]||{count:0};o+='<div class="dswfoot">STREAK <b>'+sk.count+'d</b><span class="sgo" data-act="streak" data-sid="'+def.streak+'">+ LOG NIGHT</span></div>';}
 return o;}
function injCompounds(i){return Store.data.compounds.filter(function(c){return c.petal===i&&c.route==='inject';});}
function injSeg(i,mode,def){var list=injCompounds(i),editing=(mode==='sched')&&dsEdit['top'],o=dsHdr(def.name,CATNAME[i],mode==='sched'?'top':null);
 if(editing){list.forEach(function(c){o+=bubbleEdit(c);});o+='<div class="dswadd" data-add="top">+ add injectable</div>';return o;}
 var dm=Store.data.state.done[today()]||{};
 if(!list.length)o+='<div class="dbmt">none — tap edit to add</div>';
 list.forEach(function(c){var due=dueToday(c.sched),done=!!dm[c.id];if(mode==='log')o+=bubbleCard(c,{tap:'inject',due:due,done:done});else o+=bubbleCard(c,{due:due});});
 return o;}
function pendSeg(i,seg,def){var eside=(seg==='top')?'top':'bot',editing=dsEdit[eside],o=dsHdr(def.name,CATNAME[i],eside),list=compoundsFor(i,seg);
 if(editing){list.forEach(function(c){o+=bubbleEdit(c);});o+='<div class="dswadd" data-add="'+eside+'">+ add item</div>';return o;}
 if(!list.length)o+='<div class="dbmt">none — tap edit to add</div>';
 list.forEach(function(c){o+=bubbleCard(c,{});});
 return o;}
/* ===== PACKING calendar — scroll current month + 6 ahead; pick trip end-date; tracks today ===== */
const CAL_MON=['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER'],CAL_MS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function calY_M_D(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}
function calMonth(yy,mm,tt,te){var start=new Date(yy,mm,1).getDay(),dim=new Date(yy,mm+1,0).getDate(),cells='';
 for(var b=0;b<start;b++)cells+='<span class="calc emp"></span>';
 for(var dn=1;dn<=dim;dn++){var cd=new Date(yy,mm,dn);cd.setHours(0,0,0,0);var v=+cd,cls='calc';
   if(v<tt)cls+=' cd-past';if(v===tt)cls+=' cd-today';if(v===te)cls+=' cd-end';if(v>tt&&v<te)cls+=' cd-range';
   cells+='<span class="'+cls+'" data-cal="d" data-d="'+calY_M_D(cd)+'">'+dn+'</span>';}
 return '<div class="calmo"><div class="calmy">'+CAL_MON[mm]+' '+yy+'</div><div class="calgrid calhead"><span>S</span><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span></div><div class="calgrid calbody">'+cells+'</div></div>';}
function calSeg(i,def){var t0=new Date();t0.setHours(0,0,0,0);var trip=Store.data.state.trip,end=new Date(t0);end.setDate(end.getDate()+trip);var tt=+t0,te=+end,cy=t0.getFullYear(),cm=t0.getMonth();
 var o=dsHdr('CALENDAR',CATNAME[i],null);
 o+='<div class="calsum">TRIP <b>'+trip+'d</b> &middot; ends <b>'+CAL_MS[end.getMonth()]+' '+end.getDate()+'</b></div>';
 for(var mo=0;mo<7;mo++){var d0=new Date(cy,cm+mo,1);o+=calMonth(d0.getFullYear(),d0.getMonth(),tt,te);}
 return o;}
/* ===== PACKING checklist — auto-derived from the live stack, subdivided by category ===== */
const PACK_GROUPS=[{label:'PSYCH · ORAL',petal:0},{label:'ANCILLARY · ORAL',petal:3},{label:'INJECTABLES',petal:1},{label:'TOPICALS',petal:5}];
function packHasAmt(c){if(c.route==='inject'){var v=Store.data.inventory[c.id];return !!(v&&v.units>0);}return bubVal(c.qty)!=='';}
function packAmount(c){if(c.route==='inject'){var v=Store.data.inventory[c.id];return (v&&v.units)?(v.units+(v.unit||'u')):'';}var q=bubQtyStr(c);return q!==''?(q+' left'):'';}
function packShort(c){var trip=Store.data.state.trip;   // insufficient = on-hand won't cover the trip duration (per the calculator's date horizon)
 if(c.route==='inject'){var dl=Store.invDaysLeft(c.id);return dl!=null&&dl<trip;}
 if(isOral(c)){var ro=runOut(c);if(!ro)return false;var te=new Date(today()+'T00:00:00');te.setDate(te.getDate()+trip);return ro<te;}
 return false;}
function packRow(c,CK){var hasDose=bubVal(c.dose)!=='',hasAmt=packHasAmt(c),grey=!hasDose&&!hasAmt,bad=!grey&&hasAmt&&packShort(c),on=!!CK['2:'+c.id];
 var dose=esc(c.dose||''),amt=packAmount(c);
 return '<div class="dswck pk'+(on?' on':'')+(grey?' pgrey':'')+(bad?' pbad':'')+'" data-c="'+esc(c.id)+'"><i></i><span class="cknm">'+esc(c.name)+'</span>'+(dose?'<span class="ckdose">'+dose+'</span>':'')+(amt?'<span class="ckamt">'+esc(amt)+'</span>':'')+(bad?'<span class="ckwarn">&#9888;</span>':'')+'</div>';}
function packSeg(i,def){var CK=Store.data.state.checked||{},o=dsHdr(def.name,CATNAME[i],null);
 PACK_GROUPS.forEach(function(g){var list=Store.data.compounds.filter(function(c){return c.petal===g.petal;});if(!list.length)return;o+='<div class="cksub">'+g.label+'</div>';list.forEach(function(c){o+=packRow(c,CK);});});
 var extra=(Store.data.packing&&Store.data.packing.checklist)||[];
 if(extra.length){o+='<div class="cksub">EXTRAS</div>';extra.forEach(function(nm,ix){var key='x'+ix;o+='<div class="dswck pk'+(CK['2:'+key]?' on':'')+'" data-c="'+key+'"><i></i><span class="cknm">'+esc(nm)+'</span></div>';});}
 return o;}
function segHTML(i,seg,def,side){if(i===2&&seg==='top')return calSeg(i,def);if(i===2&&seg==='bot')return packSeg(i,def);if(def.kind==='check')return checkSeg(i,seg,def);if(def.kind==='inject')return injSeg(i,def.mode,def);if(def.kind==='pending')return pendSeg(i,seg,def);return dsSegLegacy(CATS[i][seg==='top'?'top':'bot'],side,i);}
function slantRows(winEl,maxIns,grow){var b=winEl.querySelector('.dswbody');var H=b.scrollHeight||b.clientHeight||1;var k=b.children;for(var j=0;j<k.length;j++){var el=k[j];if(el.classList&&el.classList.contains('dbub'))continue;var cy=(el.offsetTop+el.offsetHeight/2)/H;var f=grow?cy:(1-cy);if(f<0)f=0;if(f>1)f=1;var ins=(maxIns*f).toFixed(2);el.style.marginLeft=ins+'%';el.style.marginRight=ins+'%';}}
function slantBubbles(winEl,maxIns,grow){var b=winEl.querySelector('.dswbody');if(!b)return;var H=b.clientHeight||1,st=b.scrollTop,k=b.children;for(var j=0;j<k.length;j++){var el=k[j];var vc=(el.offsetTop-st+el.offsetHeight/2)/H;var f=grow?vc:(1-vc);if(f<0)f=0;if(f>1)f=1;el.style.marginLeft=el.style.marginRight=(maxIns*f).toFixed(2)+'%';}}
function dsFill(i){var def=SEG[i]||SEG[0];var tB=dswT.querySelector('.dswbody'),bB=dswB.querySelector('.dswbody');tB.innerHTML=segHTML(i,'top',def.top,'t');bB.innerHTML=segHTML(i,'bot',def.bot,'b');var pk=(i===2),tb=isBub(def.top)||pk,bb=isBub(def.bot)||pk;tB.classList.toggle('scl',tb);bB.classList.toggle('scl',bb);if(tb)slantBubbles(dswT,8.33,true);else slantRows(dswT,8.33,true);if(bb)slantBubbles(dswB,4.55,false);else slantRows(dswB,4.55,false);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){if(dsEl.style.display!=='none'){if(isBub(def.top)||pk)slantBubbles(dswT,8.33,true);else slantRows(dswT,8.33,true);if(isBub(def.bot)||pk)slantBubbles(dswB,4.55,false);else slantRows(dswB,4.55,false);}});}  // re-measure once the 'vt' webfont swaps in (font-display:swap changes row metrics)
document.getElementById('dsstage').addEventListener('click',function(e){
 if(dsEl.style.display==='none')return;var i=clickIdx;
 var a=e.target.closest('[data-act]');
 if(a){var k=a.getAttribute('data-act'),tr=Store.data.state.trip;
   if(k==='dec')Store.action({type:'trip',value:tr-1});
   else if(k==='inc')Store.action({type:'trip',value:tr+1});
   else if(k==='log')Store.action({type:'log',petal:i,items:LOG_ITEMS[i]||[]});
   else if(k==='promote')Store.action({type:'promote',id:PROMOTE_ID[i]});
   else if(k==='streak')Store.action({type:'streak',id:a.getAttribute('data-sid')||STREAK_ID[i]});
   return;}
 var cal=e.target.closest('[data-cal="d"]'); if(cal){var t0=new Date();t0.setHours(0,0,0,0);var sel=new Date(cal.getAttribute('data-d')+'T00:00:00');var diff=Math.round((sel-t0)/86400000);if(diff>=1)Store.action({type:'trip',value:diff});return;}
 var ed=e.target.closest('[data-edit]'); if(ed){var sd=ed.getAttribute('data-edit');dsEdit[sd]=!dsEdit[sd];dsFill(i);return;}
 var dl=e.target.closest('[data-del]'); if(dl){Store.action({type:'item.delete',id:dl.getAttribute('data-del')});return;}
 var ad=e.target.closest('[data-add]'); if(ad){Store.action({type:'item.add',compound:newCompound(i,ad.getAttribute('data-add'))});return;}
 var bub=e.target.closest('.dbub.tap[data-id]'); if(bub){if(bub.classList.contains('off'))return;if(bub.hasAttribute('data-log'))Store.action({type:'inject.log',id:bub.getAttribute('data-id')});else Store.action({type:'tap',id:bub.getAttribute('data-id')});return;}
 var ck=e.target.closest('.dswck'); if(ck){Store.action({type:'check',petal:i,idx:ck.getAttribute('data-c')});return;}
 var idrow=e.target.closest('.dswr.tap[data-id]'); if(idrow){if(idrow.classList.contains('off'))return;if(idrow.hasAttribute('data-log'))Store.action({type:'inject.log',id:idrow.getAttribute('data-id')});else Store.action({type:'tap',id:idrow.getAttribute('data-id')});return;}
 var row=e.target.closest('.dswr.tap'); if(row){Store.action({type:'tap',petal:i,key:row.getAttribute('data-k')});return;}
});
document.getElementById('dsstage').addEventListener('change',function(e){var inp=e.target.closest('input[data-field],input[data-inv]');if(!inp)return;var row=inp.closest('[data-id]');if(!row)return;var id=row.getAttribute('data-id');if(inp.hasAttribute('data-inv'))Store.action({type:'inv.edit',id:id,field:inp.getAttribute('data-inv'),value:inp.value});else Store.action({type:'item.edit',id:id,field:inp.getAttribute('data-field'),value:inp.value});});
dswT.querySelector('.dswbody').addEventListener('scroll',function(){if(this.classList.contains('scl'))slantBubbles(dswT,8.33,true);},{passive:true});
dswB.querySelector('.dswbody').addEventListener('scroll',function(){if(this.classList.contains('scl'))slantBubbles(dswB,4.55,false);},{passive:true});
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
  if(phase==="ds"){phase="dsexit";tA=performance.now();back.classList.remove('show');infobub.classList.remove('show');dswT.classList.remove('on');dswB.classList.remove('on');void dswT.offsetWidth;dswT.classList.add('off');dswB.classList.add('off');return;}
  if(phase!=="inside")return;
  if(inph==="term"){inph="termexit";tIn=performance.now();termDiv.classList.remove('on','off');void termDiv.offsetWidth;termDiv.classList.add('off');return;}
  if(inph==="play"){phase="returning";tA=performance.now();back.classList.remove('show');resetInside();}};
const INFO_TXT={
 awake:'<h4>FLOWER</h4><ul><li><b>spin the petals</b> to cycle through them</li><li><b>tap a petal</b> to select it</li><li><b>tap the face</b> to open the terminal</li></ul>',
 inside:'<h4>NELSON</h4><ul><li><b>open terminal</b> for app-wide control</li><li>type <b>/key</b> then your Claude API key to begin</li><li>then just tell Nelson what to change</li></ul>',
 ds:'<h4>TERMINAL</h4><ul><li><b>&#9998; edit</b> (panel top-right) &mdash; add, edit or remove items</li><li><b>tap a row</b> &mdash; check it off or log a dose</li><li><b>PACKING</b> &mdash; tap a calendar date to set trip length; scroll for months</li><li><b>&#9664; back</b> (top-left) &mdash; step back out</li></ul>'};
info.onclick=()=>{if(infobub.classList.contains('show')){infobub.classList.remove('show');return;}infobub.innerHTML=INFO_TXT[phase]||INFO_TXT.awake;infobub.classList.add('show');};
info.addEventListener('pointerdown',e=>e.stopPropagation());
infobub.addEventListener('pointerdown',e=>e.stopPropagation());
function fmap(arr,k){return arr[Math.max(0,Math.min(arr.length-1,Math.round(k*(arr.length-1))))];}
const L=(a,b,k)=>a+(b-a)*k;
const trkw=document.getElementById('trkw'),trk=document.getElementById('trk'),trkRows=[...trk.querySelectorAll('.row')],trkHl=trk.querySelector('.hl');
const mpw=document.getElementById('mpw'),mp=document.getElementById('mp'),mpbtn=document.getElementById('mpbtn');let mpState='hidden';
mpbtn.onclick=(e)=>{e.stopPropagation();if(phase==="inside"&&inph==="play"){inph="off";tIn=performance.now();}};
const PETAL_NAMES=["PSYCH","INJECT","PACKING","ANCILLARY","PENDING","TOPICALS"];  /* tracker rows = petals 0-5 */
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
  {const _n=performance.now();if(_lf){const _d=_n-_lf;if(_d>40)console.warn('[bloom] SLOW FRAME '+_d.toFixed(0)+'ms  phase='+phase+'  inph='+inph+((phase==='dsexit'||phase==='pscene_off')?'  ed='+(_n-tA).toFixed(0):''));}_lf=_n;}
  const top=topIndex();
  {const aw=phase==="awake";if(aw&&trkState!=='on'){trkw.classList.add('show');trk.classList.remove('off');void trk.offsetWidth;trk.classList.add('on');trkState='on';}else if(!aw&&trkState==='on'){trk.classList.remove('on');void trk.offsetWidth;trk.classList.add('off');trkState='off';}else if(trkState==='off'&&(phase==='inside'||phase==='rest')){trkw.classList.remove('show');trk.classList.remove('off');trkState='hidden';}}
  {const mpShow=(phase==="inside"&&inph==="play");if(mpShow&&mpState!=='on'){mpw.classList.add('show');mp.classList.remove('off');void mp.offsetWidth;mp.classList.add('on');mpState='on';}else if(!mpShow&&mpState==='on'){mp.classList.remove('on');void mp.offsetWidth;mp.classList.add('off');mpState='off';}else if(!mpShow&&mpState==='off'&&phase!=="inside"){mpw.classList.remove('show');mp.classList.remove('off');mpState='hidden';}}
  {const infoShow=(phase==="awake"||phase==="inside"||phase==="ds");if(infoShow&&infoState!=='on'){info.classList.add('show');infoState='on';}else if(!infoShow&&infoState!=='off'){info.classList.remove('show');infobub.classList.remove('show');infoState='off';}}
  {const lc=lightU.uLightColor.value,r=lc.r*255|0,g=lc.g*255|0,b=lc.b*255|0;if(r!==_lr||g!==_lg||b!==_lb){_lr=r;_lg=g;_lb=b;trkw.style.setProperty('--lc','rgb('+r+','+g+','+b+')');}}  // only write when the color actually changes — no per-frame string alloc / style recalc
  trkHl.style.top=(ROW_C[top]-3.48)+"%";
  for(let i=0;i<6;i++)trkRows[i].classList.toggle("sel",i===top);
  lightU.uLightColor.value.lerp(_tcol.set(COLS[top]),0.1);
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
  if(phase==="pclick"&&(performance.now()-tA)>=250){phase="pscene_off";tA=performance.now();dsEl.style.setProperty('--dc',COLS[clickIdx]);dsEdit={top:false,bot:false};dsFill(clickIdx);dsEl.style.display='flex';dsvigEl.classList.add('on');dsEl.style.opacity='';dsEl.classList.remove('show');dsEl.classList.remove('dsout');bgEl.classList.remove('dsfit');sceneEl.classList.remove('tvon');void sceneEl.offsetWidth;sceneEl.classList.add('tvoff');}
  if(phase==="pscene_off"){const ep=performance.now()-tA;if(ep>=640){dsEl.classList.add('show');(function(s,w,h){s.left='50%';s.top='50%';s.right='auto';s.bottom='auto';s.marginLeft=(-w/2)+'px';s.marginTop=(-h/2)+'px';s.width=w+'px';s.height=h+'px';})(bgEl.style,innerWidth,innerHeight);bgEl.classList.add('dsfit');}if(ep>=1750){phase="ds";back.classList.add('show');dswT.classList.remove('off');dswB.classList.remove('off');void dswT.offsetWidth;dswT.classList.add('on');dswB.classList.add('on');}}
  if(phase==="dsexit"){const ed=performance.now()-tA;
    if(ed>=150&&dsEl.classList.contains('show')){dsEl.classList.remove('show');dsEl.classList.add('dsout');bgEl.classList.remove('dsfit');}  // dsout = decoupled return-end (more zoomed than the entry start)  // DS + bg grow back together on the way out
    if(ed>=1550&&!sceneEl.classList.contains('tvon')){sceneEl.classList.remove('tvoff');void sceneEl.offsetWidth;sceneEl.classList.add('tvon');}  // flower sweeps back in AFTER the slowed DS zoom-out is visible
    if(ed>=2060&&dsEl.style.opacity!=='0')dsEl.style.opacity='0';  // hide DS the CHEAP way (compositor-only opacity) as the scene finishes covering — no layout/paint, can't jank the reveal
    if(ed>=2210&&dswT.style.filter!=='none'){dswT.classList.remove('on','off');dswB.classList.remove('on','off');dswT.style.filter='none';dswB.style.filter='none';}  // terminal cleanup only — bg relayout removed from the hot path entirely (snapshot stays viewport-sized; cleared on resize instead)
    if(ed>=150)dsvigEl.classList.remove('on');if(ed>=2290&&dsEl.style.display!=='none')dsEl.style.display='none';  // HEAVY: hide DS subtree — own frame
    if(ed>=2370){phase="awake";sceneEl.classList.remove('tvon');dswT.style.filter='';dswB.style.filter='';dsEl.style.opacity='';}}  // filter teardown + restore opacity for next open
  if(dbg!==null){setFace(fmap(portalTex,dbg));cam.position.z=Z_WAKE;setMasked(true);mi=dbg;}
  lightU.uMouthI.value=L(lightU.uMouthI.value,mi*1.25,0.22);
  mouthGlow.material.opacity=Math.min(0.55,lightU.uMouthI.value*0.42);
  rnd.render(scene,cam);}
animate(0);
addEventListener('resize',()=>{cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();rnd.setSize(innerWidth,innerHeight);(function(s){s.left=s.top=s.right=s.bottom=s.width=s.height=s.marginLeft=s.marginTop='';})(bgEl.style);});  // bg snapshot reverts to responsive viewport only on actual resize (re-snapshotted on next DS entry)
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
#bgvig{position:fixed;inset:0;z-index:0;pointer-events:none;transform:scale(1.06);background:radial-gradient(80% 68% at 50% 43%,rgba(0,0,0,0) 36%,rgba(0,0,0,.625) 74%,rgba(0,0,0,1) 100%);}
#bgglow{position:fixed;inset:0;z-index:0;pointer-events:none;transform:scale(1.06);background:radial-gradient(52% 40% at 50% 43%,rgba(255,248,232,.30),rgba(255,248,232,0) 72%);mix-blend-mode:screen;animation:bgglow 7.5s ease-in-out infinite;will-change:opacity;}
@keyframes bgbreathe{0%,100%{filter:brightness(.32) saturate(.9) blur(1.5px);}50%{filter:brightness(.44) saturate(1.04) blur(1.5px);}}
@keyframes bgglow{0%,100%{opacity:.55;}50%{opacity:.95;}}
#back{position:fixed;left:14px;top:max(18px,env(safe-area-inset-top));z-index:6;width:79px;height:79px;border:none;background:url(__BACKBTN__) center/contain no-repeat;cursor:pointer;opacity:0;transform:scale(0);transform-origin:50% 50%;pointer-events:none;font-size:0;color:transparent;filter:drop-shadow(0 3px 7px rgba(0,0,0,.45));transition:transform .3s cubic-bezier(.5,-0.3,.75,.4),opacity .26s ease;will-change:transform,opacity;}
#back.show{animation:backpop .5s cubic-bezier(.34,1.56,.64,1) forwards;pointer-events:auto;}
@keyframes backpop{0%{opacity:0;transform:scale(.2);}55%{opacity:1;transform:scale(1.18);}100%{opacity:1;transform:scale(1);}}
#back:active{transform:scale(.9);}
#info{position:fixed;right:14px;top:calc(max(18px,env(safe-area-inset-top)) + 12.5px);z-index:6;width:54px;height:54px;border:2px solid rgba(222,232,247,.9);border-radius:50%;background:radial-gradient(circle at 38% 30%,#8fc0ff,#2170e2 46%,#0a3d99);cursor:pointer;opacity:0;transform:scale(0);transform-origin:50% 50%;pointer-events:none;font:700 31px/1 Georgia,'Times New Roman',serif;color:#fff;box-shadow:0 3px 7px rgba(0,0,0,.45),inset 0 2px 6px rgba(255,255,255,.55),inset 0 -3px 9px rgba(0,20,70,.4);transition:transform .3s cubic-bezier(.5,-0.3,.75,.4),opacity .26s ease;will-change:transform,opacity;}
#info.show{animation:backpop .5s cubic-bezier(.34,1.56,.64,1) forwards;pointer-events:auto;}
#info:active{transform:scale(.9);}
#infobub{position:fixed;right:14px;top:calc(max(18px,env(safe-area-inset-top)) + 80px);z-index:6;width:min(80vw,330px);background:rgba(32,112,236,.16);border:1.5px solid rgba(130,185,255,.5);border-radius:34px;-webkit-backdrop-filter:blur(7px);backdrop-filter:blur(7px);box-shadow:0 8px 26px rgba(8,44,130,.4),inset 0 0 26px rgba(130,185,255,.14);color:#eaf2ff;font:500 13px/1.55 'vt',ui-monospace,monospace;letter-spacing:.02em;padding:17px 24px 19px;opacity:0;transform:translateY(-8px) scale(.96);transform-origin:100% 0;pointer-events:none;transition:opacity .24s ease,transform .24s cubic-bezier(.34,1.4,.64,1);text-shadow:0 1px 3px rgba(0,0,0,.5);}
#infobub.show{opacity:1;transform:translateY(0) scale(1);pointer-events:auto;}
#infobub h4{margin:0 0 8px;font:700 13px 'vt',monospace;letter-spacing:.12em;color:#bcd7ff;text-shadow:0 0 9px rgba(130,185,255,.6);}
#infobub ul{margin:0;padding:0;list-style:none;}
#infobub li{margin:5px 0;padding-left:15px;position:relative;}
#infobub li::before{content:"\203A";position:absolute;left:2px;color:#8fbaff;}
#infobub b{color:#fff;font-weight:700;}
#term{position:fixed;transform:translate(-50%,-50%);opacity:0;z-index:4;display:flex;flex-direction:column;background:linear-gradient(160deg,#04250f,#010d05);border:1.5px solid rgba(80,255,130,.95);border-radius:7px;box-shadow:0 0 48px rgba(57,255,110,.95),0 0 96px rgba(57,255,90,.55),inset 0 0 28px rgba(50,225,95,.6);overflow:hidden;transform-origin:50% 50%;filter:hue-rotate(var(--thr,0deg)) brightness(1.3);}
#term.on{animation:termon .58s cubic-bezier(.4,.08,.2,1) forwards;}
@keyframes termon{0%{opacity:1;transform:translate(-50%,-50%) scale(1.25,.004);filter:brightness(6.5) contrast(1.5) hue-rotate(var(--thr,0deg));}10%{opacity:1;transform:translate(-50%,-50%) scale(1.25,.004);filter:brightness(6.5) contrast(1.5) hue-rotate(var(--thr,0deg));}50%{transform:translate(-50%,-50%) scale(1.22,.02);filter:brightness(4.5) contrast(1.3) hue-rotate(var(--thr,0deg));}70%{transform:translate(-50%,-50%) scale(1,1.06);filter:brightness(2.2) hue-rotate(var(--thr,0deg));}100%{opacity:1;transform:translate(-50%,-50%) scale(1,1);filter:brightness(1) hue-rotate(var(--thr,0deg));}}
#term.off{animation:termoff .5s cubic-bezier(.55,0,.7,.25) forwards;}
@keyframes termoff{0%{opacity:1;transform:translate(-50%,-50%) scale(1,1);filter:brightness(1) hue-rotate(var(--thr,0deg));}28%{transform:translate(-50%,-50%) scale(1,1.04);filter:brightness(2.4) contrast(1.2) hue-rotate(var(--thr,0deg));}62%{transform:translate(-50%,-50%) scale(1.03,.02);filter:brightness(6) contrast(1.5) hue-rotate(var(--thr,0deg));}100%{opacity:0;transform:translate(-50%,-50%) scale(.18,.004);filter:brightness(9) hue-rotate(var(--thr,0deg));}}
#termlog{flex:1;padding:6px 11px;font:17px/1.18 'vt',ui-monospace,monospace;color:#6dff97;overflow-y:auto;text-shadow:0 0 10px rgba(80,255,130,.95),0 0 3px rgba(160,255,190,.8);letter-spacing:.5px;}
#termlog .nelmsg{color:#9dffc0;}
#termlog .neltool{opacity:.72;font-size:14px;}
#termlog .nelerr{color:#ff8f8f;text-shadow:none;}
#termlog .nelpending{opacity:.6;font-style:italic;}
#terminp{display:flex;align-items:center;gap:6px;padding:5px 11px;border-top:1px solid rgba(110,255,160,.35);}
#terminp span{color:#7dffae;font:18px 'vt',ui-monospace,monospace;text-shadow:0 0 6px rgba(110,255,165,.6);}
#termin{flex:1;min-width:0;background:transparent;border:none;outline:none;color:#d8ffe6;font:17px 'vt',ui-monospace,monospace;letter-spacing:.5px;}#termin::placeholder{color:#5ca87a;}
#wmpf{position:fixed;inset:0;background:url(__WMPFRAME__) center/cover no-repeat;opacity:1;pointer-events:none;z-index:6;transform-origin:50% 43%;will-change:transform,opacity;}
@keyframes wmpz{0%{opacity:1;transform:scale(1);}45%{opacity:1;}100%{opacity:0;transform:scale(5.2);}}
#wmpf.go{animation:wmpz 0.68s cubic-bezier(.5,0,.9,.4) forwards;}
#trkw{position:fixed;left:50%;bottom:calc(4.5vh + 10px);transform:translateX(-50%);width:min(83.3vw,381px);aspect-ratio:528/374;z-index:3;pointer-events:none;opacity:0;--lc:#5cff9e;filter:drop-shadow(0 0 3px var(--lc)) drop-shadow(0 0 9px var(--lc)) drop-shadow(0 0 18px var(--lc));}
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
#scene{position:fixed;inset:0;z-index:3;overflow:hidden;transform-origin:50% 50%;will-change:transform;}
#scene.tvoff{animation:sceneoff .62s cubic-bezier(.55,0,.7,.25) forwards;}
#scene.tvon{animation:scenein .6s cubic-bezier(.2,.7,.3,1) forwards;}
@keyframes sceneoff{0%{transform:scale(1,1);opacity:1;}16%{transform:scale(1,1.035);}52%{transform:scale(1,.012);}80%{transform:scale(1,.004);opacity:1;}100%{transform:scale(0,.002);opacity:0;}}
@keyframes scenein{0%{transform:scale(0,.002);opacity:0;}20%{transform:scale(1,.004);opacity:1;}48%{transform:scale(1,.012);}84%{transform:scale(1,1.035);}100%{transform:scale(1,1);opacity:1;}}
#bgkeep{position:fixed;inset:0;z-index:1;pointer-events:none;transform-origin:50% 66%;transition:transform 0.574s cubic-bezier(.4,.5,.6,1);}
#bgkeep.dsfit{transform:scale(.9704);transition:transform 1s cubic-bezier(.5,0,.75,.4);}
#dsblur{position:fixed;inset:0;z-index:5;pointer-events:none;-webkit-backdrop-filter:blur(0.34px);backdrop-filter:blur(0.34px);-webkit-mask:radial-gradient(circle at 50% 50%,transparent 58.5%,#000 61.5%,#000 83.5%,transparent 86.5%);mask:radial-gradient(circle at 50% 50%,transparent 58.5%,#000 61.5%,#000 83.5%,transparent 86.5%);}
#dsblur2{position:fixed;inset:0;z-index:5;pointer-events:none;-webkit-backdrop-filter:blur(2.7px);backdrop-filter:blur(2.7px);-webkit-mask:radial-gradient(circle at 50% 50%,transparent 83.5%,#000 86.5%);mask:radial-gradient(circle at 50% 50%,transparent 83.5%,#000 86.5%);}
#dsvig{position:fixed;inset:0;z-index:4;pointer-events:none;opacity:0;transition:opacity .45s ease;background:radial-gradient(ellipse at 50% 50%,transparent 58%,rgba(0,0,0,.225) 100%);}
#dsvig.on{opacity:1;}
#ds{position:fixed;inset:0;z-index:2;background:transparent;display:none;align-items:center;justify-content:center;isolation:isolate;opacity:1;transform-origin:50% 66%;transform:translateY(-6.28%) scale(5.19);transition:transform 2.201s linear;will-change:transform;}
#ds.show{transform:translateY(6%) scale(1.1);transition:transform 1s cubic-bezier(.25,.46,.45,.94);}
#ds.dsout{transform:translateY(-6.91%) scale(7);transition:transform 2.311s linear(0,0.526 62.5%,1);}
#dsstage{position:relative;width:736px;height:660px;flex:none;--dspic:url("__DSPIC__");--iz:1.667;--panx:0px;--pany:0px;--iox:calc(368px * (1 - var(--iz)) + var(--panx));--ioy:calc(330px * (1 - var(--iz)) + var(--pany));}
#dsocc{position:absolute;inset:0;background:#000;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 736 660'%3E%3Cpath fill='%23fff' fill-rule='evenodd' d='M0 0H736V660H0Z M200 79H533V294H200Z M224 372H513V591H224Z'/%3E%3C/svg%3E") center/100% 100% no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 736 660'%3E%3Cpath fill='%23fff' fill-rule='evenodd' d='M0 0H736V660H0Z M200 79H533V294H200Z M224 372H513V591H224Z'/%3E%3C/svg%3E") center/100% 100% no-repeat;}
#dsbody{position:absolute;inset:0;isolation:isolate;-webkit-mask:url("__DS__") center/100% 100% no-repeat;mask:url("__DS__") center/100% 100% no-repeat;}
#dsbody img{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;filter:grayscale(1) brightness(1.12) contrast(.96);}
#dstint{position:absolute;inset:0;background:var(--dc,#888);mix-blend-mode:multiply;opacity:.9;pointer-events:none;}
#dsdark{position:absolute;inset:0;background:#000;opacity:.52;pointer-events:none;}
.dswin{position:absolute;border-radius:5px;transform-origin:50% 50%;opacity:0;transform:scaleY(.004);color:#eef0f6;background:transparent;}
.dswglow{position:absolute;inset:0;pointer-events:none;filter:drop-shadow(0 0 7px var(--dc,#888)) drop-shadow(0 0 16px var(--dc,#888)) drop-shadow(0 0 32px var(--dc,#888));}
.dswglowf{position:absolute;inset:0;background:var(--dc,#888);opacity:.8;-webkit-mask:radial-gradient(closest-side,transparent 58%,#000 90%);mask:radial-gradient(closest-side,transparent 58%,#000 90%);}
.dswclip{position:absolute;inset:0;overflow:hidden;border-radius:5px;border:1.5px solid var(--dc,#888);}
#dswT{left:27.31%;top:12.88%;width:43.61%;height:34.33%;}
#dswB{left:29.42%;top:56.04%;width:39.43%;height:33.50%;}
.dswx{position:absolute;background-repeat:no-repeat;background-size:calc(736px * var(--iz)) calc(660px * var(--iz));border-radius:5px;overflow:hidden;}
@keyframes dshue{from{filter:hue-rotate(0deg);}to{filter:hue-rotate(360deg);}}
#dsxT{left:-250%;top:-250%;width:600%;height:258.79%;background-position:calc(var(--iox) + 1840px) calc(var(--ioy) + 1650px);}
#dsxB{left:-250%;top:93.64%;width:600%;height:258.79%;background-position:calc(var(--iox) + 1840px) calc(var(--ioy) - 618px);}
#dsxL{left:-250%;top:6.52%;width:260.80%;height:89.40%;transform:skewX(1.75deg);transform-origin:50% 100%;background-position:calc(var(--iox) + 1860px) calc(var(--ioy) - 43px);}
#dsxR{left:88.52%;top:6.52%;width:260.80%;height:89.40%;transform:skewX(-1.75deg);transform-origin:50% 100%;background-position:calc(var(--iox) - 671.5px) calc(var(--ioy) - 43px);}
.dscnr{position:absolute;width:14px;height:14px;background-repeat:no-repeat;background-size:calc(736px * var(--iz)) calc(660px * var(--iz));pointer-events:none;}
#dscTL{left:8.21%;top:8.79%;background-position:calc(var(--iox) - 60.4px) calc(var(--ioy) - 58px);-webkit-mask:radial-gradient(circle 14px at 100% 100%,#0000 99%,#000);mask:radial-gradient(circle 14px at 100% 100%,#0000 99%,#000);}
#dscTR{left:calc(91.11% - 14px);top:8.79%;background-position:calc(var(--iox) - 656.6px) calc(var(--ioy) - 58px);-webkit-mask:radial-gradient(circle 14px at 0 100%,#0000 99%,#000);mask:radial-gradient(circle 14px at 0 100%,#0000 99%,#000);}
#dscBL{left:10.53%;top:calc(93.64% - 14px);background-position:calc(var(--iox) - 77.5px) calc(var(--ioy) - 604px);-webkit-mask:radial-gradient(circle 14px at 100% 0,#0000 99%,#000);mask:radial-gradient(circle 14px at 100% 0,#0000 99%,#000);}
#dscBR{left:calc(88.79% - 14px);top:calc(93.64% - 14px);background-position:calc(var(--iox) - 639.5px) calc(var(--ioy) - 604px);-webkit-mask:radial-gradient(circle 14px at 0 0,#0000 99%,#000);mask:radial-gradient(circle 14px at 0 0,#0000 99%,#000);}
.dstri{position:absolute;inset:0;background-repeat:no-repeat;background-size:calc(736px * var(--iz)) calc(660px * var(--iz));background-position:var(--iox) var(--ioy);pointer-events:none;}
.dswx::before,.dscnr::before,.dstri::before{content:"";position:absolute;inset:0;background-image:var(--dspic);background-repeat:no-repeat;background-size:inherit;background-position:inherit;animation:dshue 2s linear infinite;}
.dswx::after,.dscnr::after,.dstri::after{content:"";position:absolute;inset:0;background-image:radial-gradient(circle at 50% 50%,#000,rgba(0,0,0,0) 77%);background-repeat:no-repeat;background-size:inherit;background-position:inherit;pointer-events:none;}
#dstL{background-position:calc(var(--iox) + 5px) var(--ioy);-webkit-clip-path:polygon(8.21% 8.79%,10.53% 93.64%,13.46% 51.63%);clip-path:polygon(8.21% 8.79%,10.53% 93.64%,13.46% 51.63%);}
#dstR{background-position:calc(var(--iox) - 5px) var(--ioy);-webkit-clip-path:polygon(91.11% 8.79%,88.79% 93.64%,84.51% 51.63%);clip-path:polygon(91.11% 8.79%,88.79% 93.64%,84.51% 51.63%);}
#dswT>.dswclip,#dswT>.dswglow>.dswglowf{-webkit-clip-path:polygon(0% 0%,100% 0%,91.67% 100%,8.33% 100%);clip-path:polygon(0% 0%,100% 0%,91.67% 100%,8.33% 100%);}
#dswB>.dswclip,#dswB>.dswglow>.dswglowf{-webkit-clip-path:polygon(4.55% 0%,95.45% 0%,100% 100%,0% 100%);clip-path:polygon(4.55% 0%,95.45% 0%,100% 100%,0% 100%);}
.dswscan{display:none;}
.dswbody{position:absolute;inset:0;width:142.86%;height:142.86%;transform:scale(.7);transform-origin:0 0;padding:7px 10px;display:flex;flex-direction:column;overflow:hidden;background:rgba(0,0,0,.54);text-shadow:0 1px 3px rgba(0,0,0,.95),0 0 6px rgba(0,0,0,.7);}
.dswbody.scl{overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;padding:8px 6px;}
.dswbody.scl::-webkit-scrollbar{width:3px;}
.dswbody.scl::-webkit-scrollbar-thumb{background:var(--dc,#888);border-radius:3px;}
.dbub{position:relative;margin:8px 0;padding:10px 14px;border-radius:16px;background:rgba(0,0,0,.54);border:1px solid var(--dc,#888);box-shadow:inset 0 0 16px -7px var(--dc,#888),0 0 7px -3px var(--dc,#888);}
.dbub.tap{cursor:pointer;-webkit-tap-highlight-color:transparent;}
.dbub.off{opacity:.42;}
.dbub.done{opacity:.66;}
.dbub.low{border-color:#ff5a6a;box-shadow:inset 0 0 16px -7px #ff5a6a,0 0 9px -2px #ff5a6a;}
.dbnm{display:flex;align-items:baseline;gap:7px;font:700 17px/1.25 'vt',monospace;letter-spacing:.04em;text-transform:uppercase;color:var(--dc,#fff);text-shadow:0 0 7px var(--dc,#fff),0 1px 2px rgba(0,0,0,.92);}
.dbck{flex:none;font-size:15px;opacity:.9;}
.dbnt{flex:1;min-width:0;word-break:break-word;}
.dbmid{margin:7px 0 6px;display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 9px;}
.dbq{font:800 27px/1 'vt',monospace;color:#fff;text-shadow:0 0 9px var(--dc,#fff);}
.dbqu{font:600 15px 'vt',monospace;color:rgba(255,255,255,.62);text-transform:uppercase;letter-spacing:.09em;}
.dbout{font:600 14px 'vt',monospace;color:rgba(255,255,255,.5);letter-spacing:.04em;white-space:nowrap;}
.dbout b{color:var(--dc,#fff);font-weight:800;text-shadow:0 0 6px var(--dc,#888);}
.dbthr{margin-left:auto;font:600 14px 'vt',monospace;color:rgba(255,255,255,.46);}
.dbro{margin-left:auto;font:800 14px 'vt',monospace;letter-spacing:.1em;color:#fff;background:#ff3b50;border-radius:7px;padding:3px 9px;text-shadow:0 0 4px #ff8a96;animation:dbrop 1.4s ease-in-out infinite;}
@keyframes dbrop{0%,100%{opacity:1;}50%{opacity:.5;}}
.dbqm{font:600 14px 'vt',monospace;color:rgba(255,255,255,.42);font-style:italic;}
.dbbot{display:flex;flex-wrap:wrap;align-items:baseline;gap:3px 11px;font:600 14px 'vt',monospace;}
.dbdose{color:var(--dc,#fff);opacity:.92;}
.dbsrc{margin-left:auto;color:rgba(255,255,255,.55);font-size:15px;word-break:break-word;}
.dbmt{font:600 14px 'vt',monospace;color:rgba(255,255,255,.42);padding:12px 4px;text-align:center;}
.dbube{position:relative;margin:7px 0;padding:9px 11px;border-radius:13px;background:rgba(255,255,255,.05);border:1px dashed var(--dc,#888);display:flex;flex-direction:column;gap:5px;}
.dbube .ein{width:100%;box-sizing:border-box;font-size:14px;}
.dbube .dbrow2{display:flex;gap:5px;}
.dbube .dbrow2 .ein{flex:1;min-width:0;}
.dbube .del{align-self:flex-end;cursor:pointer;color:#ff6a78;font:700 12px 'vt',monospace;letter-spacing:.05em;}
.dswh{font:700 15px/1 'vt',monospace;letter-spacing:.05em;text-transform:uppercase;color:var(--dc,#fff);text-shadow:0 0 8px var(--dc,#fff),0 1px 3px rgba(0,0,0,.95);padding-bottom:4px;margin-bottom:5px;border-bottom:1px solid rgba(255,255,255,.18);display:flex;justify-content:space-between;align-items:center;}
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
.dswr.off{opacity:.45;cursor:default;}.dswr.off .nm{color:rgba(238,240,246,.5);}.dswr.off b{color:rgba(238,240,246,.45);font-style:italic;font-size:10px;}
.dswr.seqpend{opacity:.6;}
.dswhr{display:flex;align-items:center;gap:6px;}
.dsedit{cursor:pointer;font:700 9px 'vt',monospace;letter-spacing:.06em;color:var(--dc,#fff);border:1px solid var(--dc,#888);border-radius:3px;padding:2px 6px;-webkit-tap-highlight-color:transparent;text-shadow:0 0 5px var(--dc,#fff);}
.dsedit.on{background:var(--dc,#fff);color:#08080c;text-shadow:none;}
.dswre{display:flex;align-items:center;gap:4px;padding:2px 0;}
.dswre .ein{background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.25);border-radius:3px;color:#fff;font:500 11px ui-monospace,Menlo,monospace;padding:3px 5px;min-width:0;outline:none;}
.dswre .ein:focus{border-color:var(--dc,#fff);box-shadow:0 0 6px -1px var(--dc,#fff);}
.dswre .enm{flex:2;}.dswre .edz{flex:1;}.dswre .esh{flex:1;}
.dswre .del{cursor:pointer;color:var(--dc,#fff);font-size:16px;line-height:1;padding:0 4px;flex:none;text-shadow:0 0 5px var(--dc,#fff);}
.dswadd{margin-top:5px;cursor:pointer;text-align:center;border:1px dashed var(--dc,#888);border-radius:4px;color:var(--dc,#fff);font:700 10px 'vt',monospace;letter-spacing:.08em;padding:5px;opacity:.85;-webkit-tap-highlight-color:transparent;}
.dswadd:active{opacity:1;}
.dswr .sch{font:600 10px 'vt',monospace;color:rgba(255,255,255,.62);letter-spacing:.04em;padding-right:6px;flex:none;}
.dswr.low b{color:#ff5a5a;text-shadow:0 0 7px rgba(255,80,80,.65);}
.dswr.duenow .mk{color:var(--dc,#fff);text-shadow:0 0 7px var(--dc,#fff);}
.dswr.dim{opacity:.5;}
.dswre.inje{flex-wrap:wrap;gap:3px;}
.dswre.inje .enm{flex:1 1 46%;}.dswre.inje .esh{flex:1 1 30%;}.dswre.inje .enum{flex:1 1 18%;min-width:36px;text-align:center;}
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
.calsum{font:700 10px 'vt',monospace;letter-spacing:.05em;color:var(--dc,#fff);opacity:.9;text-shadow:0 0 6px var(--dc,#fff);text-align:center;margin-bottom:7px;}
.calsum b{color:#fff;}
.calmo{margin-bottom:9px;}
.calmy{font:700 11px 'vt',monospace;letter-spacing:.08em;color:var(--dc,#fff);text-shadow:0 0 7px var(--dc,#fff);text-align:center;margin-bottom:3px;padding-bottom:2px;border-bottom:1px solid rgba(255,255,255,.15);}
.calgrid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;}
.calhead{font:700 9px 'vt',monospace;color:var(--dc,#fff);opacity:.55;text-align:center;margin-bottom:2px;}
.calbody .calc{text-align:center;font:600 11px ui-monospace,Menlo,monospace;color:#fff;padding:3px 0;border-radius:4px;cursor:pointer;-webkit-tap-highlight-color:transparent;border:1px solid transparent;}
.calc.emp{cursor:default;}
.calc.cd-past{opacity:.28;cursor:default;}
.calc.cd-range{background:rgba(255,255,255,.09);color:var(--dc,#fff);}
.calc.cd-today{border-color:var(--dc,#fff);color:var(--dc,#fff);text-shadow:0 0 7px var(--dc,#fff);}
.calc.cd-end{background:var(--dc,#fff);color:#08080c;font-weight:700;box-shadow:0 0 9px -1px var(--dc,#fff);}
.cksub{font:700 10px 'vt',monospace;letter-spacing:.11em;color:var(--dc,#fff);opacity:.9;text-shadow:0 0 6px var(--dc,#fff);margin:9px 0 2px;padding-bottom:2px;border-bottom:1px solid rgba(255,255,255,.15);}
.cksub:first-of-type{margin-top:0;}
.dswck.pk{gap:7px;align-items:center;}
.dswck .cknm{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.dswck .ckdose{flex:none;font-size:10px;opacity:.58;}
.dswck .ckamt{flex:none;font-size:11px;font-weight:600;color:var(--dc,#fff);opacity:.92;}
.dswck.pgrey{opacity:.4;}
.dswck.pbad .cknm{color:#ff6b78;}
.dswck.pbad .ckamt{color:#ff5a6a;}
.dswck .ckwarn{flex:none;color:#ff5a6a;font-size:12px;line-height:1;text-shadow:0 0 7px rgba(255,80,90,.75);}
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
<div id="ds"><div id="dsstage"><div id="dsocc"></div><div id="dsbody"><img src="__DS__" alt=""><div id="dstint"></div><div id="dsdark"></div></div><div class="dswin" id="dswT"><div class="dswglow"><div class="dswglowf"></div></div><div class="dswclip"><div class="dswbody"></div><div class="dswscan"></div><div class="dswframe"></div></div></div><div class="dswin" id="dswB"><div class="dswglow"><div class="dswglowf"></div></div><div class="dswclip"><div class="dswbody"></div><div class="dswscan"></div><div class="dswframe"></div></div></div><div class="dswx" id="dsxT"></div><div class="dswx" id="dsxB"></div><div class="dswx" id="dsxL"></div><div class="dswx" id="dsxR"></div><div class="dstri" id="dstL"></div><div class="dstri" id="dstR"></div><div class="dscnr" id="dscTL"></div><div class="dscnr" id="dscTR"></div><div class="dscnr" id="dscBL"></div><div class="dscnr" id="dscBR"></div></div></div><div id="dsblur"></div><div id="dsblur2"></div><div id="dsvig"></div>
<div id="scene">
<canvas id="c"></canvas>
<div id="wmpf"></div>
<div id="trkw"><div id="trk"><div class="tint"></div><div class="ttl">TRACKER</div><div class="hl"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div><div class="row"></div></div></div>
</div>
<button id="back" aria-label="back"></button><button id="info" aria-label="how to use this screen">i</button><div id="infobub"></div>
<div id="term"><div id="termlog">nelson@bloom:~$ ready</div><div id="terminp"><span>$</span><input id="termin" placeholder="type a command…" autocomplete="off"/></div></div>
<div id="mpw"><div id="mp"><button class="mpbtn" id="mpbtn"><span class="pt">&#9654;</span>OPEN TERMINAL</button><div id="mpglare"></div></div></div>
<script>(function(){var F=__BGFRAMES__;var el=document.getElementById('bgf');F.forEach(function(u){var im=new Image();im.src=u;});el.src=F[0];var i=0,d=1;setInterval(function(){i+=d;if(i>=F.length-1){i=F.length-1;d=-1;}else if(i<=0){i=0;d=1;}el.src=F[i];},125);})();
setTimeout(function(){var bt=document.getElementById('boot');if(bt){bt.classList.add('hide');setTimeout(function(){bt.style.display='none';},700);}},2100);</script><script>__THREE__</script><script>__CORE__</script></body></html>"""
core=CORE.replace("__SPL__",SPL).replace("__POS__",POS).replace("__COLS__",COLS).replace("__GLOW__",GLOW).replace("__EY__",EY).replace("__PO__",PO).replace("__RM__",RM).replace("__HEAD__",HEAD).replace("__ROOMBG__",ROOMBG).replace("__SFR__",SFR).replace("__SBOX__",SBOX).replace("__SMASK__",SMASK).replace("__GLAREPOS__",GLAREPOS).replace("__GLARE__",GLARE).replace("__NGA__",NGA).replace("__NGB__",NGB).replace("__NC__",NC).replace("__WMPFRAME__",WMPFRAME).replace("__STACK_SEED__",STACK_SEED)
def _shell(s):
    return (s.replace("__CORE__",core).replace("__WMPFRAME__",WMPFRAME).replace("__XBOX__",XBOX)
             .replace("__FONTVT__",FONTVT).replace("__FONTSE__",FONTSE).replace("__BGFLOWER__",BGFLOWER)
             .replace("__BGFRAMES__",BGFRAMES).replace("__MP__",MP).replace("__GLARE__",GLARE)
             .replace("__BACKBTN__",BACKBTN).replace("__BOOT__",BOOT).replace("__DSPIC__",DSPIC).replace("__DS__",DS))
local_html=_shell(SHELL.replace("__THREE__",THREE))                       # three.js inlined (offline-capable)
open("bloom-3d-local.html","w").write(local_html)
cdn_html=_shell(SHELL.replace("<script>__THREE__</script>",'<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'))
open(os.path.join(OUT_DIR,"bloom-3d.html"),"w").write(cdn_html)

# --- PWA: installable, fully offline, self-contained (uses the inlined build) ---
ICON=BOOT if BOOT.startswith("data:") else "data:image/png;base64,"+BOOT
ICON_MIME=ICON.split(";")[0][5:] if ICON.startswith("data:") else "image/png"
PWA_HEAD=('<link rel="manifest" href="manifest.webmanifest">'
          '<meta name="theme-color" content="#000000">'
          '<meta name="mobile-web-app-capable" content="yes">'
          '<meta name="apple-mobile-web-app-capable" content="yes">'
          '<meta name="apple-mobile-web-app-status-bar-style" content="black">'
          '<meta name="apple-mobile-web-app-title" content="Bloom">'
          '<link rel="apple-touch-icon" href="'+ICON+'">')
PWA_SW="<script>if('serviceWorker' in navigator){addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>"
pwa_html=local_html.replace("</head>",PWA_HEAD+"</head>",1).replace("</body>",PWA_SW+"</body>",1)
open(os.path.join(OUT_DIR,"index.html"),"w").write(pwa_html)
open(os.path.join(OUT_DIR,"manifest.webmanifest"),"w").write(json.dumps({
  "name":"Bloom","short_name":"Bloom","start_url":"./","scope":"./","display":"standalone",
  "orientation":"portrait-primary","background_color":"#000000","theme_color":"#000000",
  "icons":[{"src":ICON,"sizes":"512x512","type":ICON_MIME,"purpose":"any"},
           {"src":ICON,"sizes":"192x192","type":ICON_MIME,"purpose":"maskable"}]}))
open(os.path.join(OUT_DIR,"sw.js"),"w").write(r"""const C='bloom-v1';
self.addEventListener('install',function(e){
  self.skipWaiting();
  e.waitUntil(caches.open(C).then(function(c){return c.addAll(['./index.html','./manifest.webmanifest']);}));
});
self.addEventListener('activate',function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.map(function(k){return k!==C?caches.delete(k):Promise.resolve();}));
  }).then(function(){return self.clients.claim();}));
});
self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET')return;
  e.respondWith(caches.match(e.request).then(function(cached){
    if(cached)return cached;
    return fetch(e.request).then(function(resp){
      var copy=resp.clone();
      caches.open(C).then(function(c){c.put(e.request,copy);});
      return resp;
    }).catch(function(){return caches.match('./index.html');});
  }));
});
""")
print("lit-shader build + PWA written ->",OUT_DIR)
