// Deal Model V1.1 in JavaScript: line-for-line port of engine/r360/deal_engine.py.
// Parity with Python is checked by tests/test_deal_engine_js.py. Change both together.
(function (root) {
  const PARAMS = ["issuances","activationCC","txCC","atsCC","activationUPI","txUPI","atsUPI","intlPct"];
  const EVEN = Array(12).fill(1 / 12);
  const DEFAULT_CONFIG = {rvp:.0008,rff:2.4,ifp:.015,intlRevShare:.25,iip:.002,imip:.001,mcb:.10,msb:.0001,upf:5e6,bpF:6,bpC:14,milestone_rule:"cif"};
  const DEFAULT_VOLUME_SLABS = [{t:0,fb:1.2,pb:.0002},{t:1e6,fb:1.4,pb:.00025},{t:2e6,fb:1.6,pb:.0003},{t:4e6,fb:1.8,pb:.00035}];
  const DEFAULT_CIF_SLABS = [{t:0,pb:.5},{t:1e6,pb:.6},{t:2e6,pb:.65},{t:3e6,pb:.7}];
  const SCENARIOS = {base:{cif:1,volume:1,activation:1,ats:1,intl:1},conservative:{cif:.85,volume:.85,activation:.9,ats:.95,intl:.9},aggressive:{cif:1.15,volume:1.15,activation:1.1,ats:1.05,intl:1.1}};
  function defaultVariant(name="V1", years=5){const r=[...Array(years).keys()];const s={};PARAMS.forEach(k=>s[k]=[...EVEN]);
    return {name,years,cardFee:100,cif:r.map(i=>(i+1)*60000),issuances:r.map(i=>(i+1)*45000+15000),activationCC:r.map(i=>.3+i*.05),txCC:r.map(i=>4+i),atsCC:r.map(i=>3000+i*400),activationUPI:r.map(i=>.15+i*.06),txUPI:r.map(i=>6+i*2),atsUPI:r.map(i=>800+i*150),intlPct:r.map(i=>.05+i*.01),seasonality:s};}
  function slab(v,slabs){let r=slabs[0];for(const s of slabs){if(v>=s.t)r=s;else break;}return r;}
  function deriveMonthlyAttrition(start,target,iss){let lo=0,hi=.15,best=.008;for(let k=0;k<50;k++){const mid=(lo+hi)/2;let c=start;for(const m of iss)c=Math.max(0,c+m-mid*(c+m));if(c>target)lo=mid;else hi=mid;best=mid;}return Math.max(0,Math.min(.15,best));}
  function derivedAttritionRates(v){const sn=v.seasonality.issuances;const t=sn.reduce((a,b)=>a+b,0)||1;const rates=[];let prev=0;
    for(let y=0;y<v.years;y++){const iss=[...Array(12).keys()].map(m=>v.issuances[y]*(sn[m]/t));const rate=deriveMonthlyAttrition(prev,v.cif[y],iss);rates.push(rate);let c=prev;for(let m=0;m<12;m++)c=Math.max(0,c+iss[m]-rate*(c+iss[m]));prev=c;}return rates;}
  function dist(ann,sn,kind){const t=sn.reduce((a,b)=>a+b,0)||1;const out=[];for(const a of ann)for(let i=0;i<12;i++)out.push(kind==="sum"?a*sn[i]/t:a*sn[i]/(t/12));return out;}
  function calcVariant(v,pm){const n=v.years*12,s=v.seasonality,g=k=>pm[k]===undefined?1:pm[k];
    const iss=dist(v.issuances,s.issuances,"sum").map(x=>x*g("cif"));const rates=derivedAttritionRates(v);const mA=[...Array(n).keys()].map(m=>rates[Math.floor(m/12)]);
    const acC=dist(v.activationCC,s.activationCC,"avg").map(x=>Math.min(x*g("activation"),1)),acU=dist(v.activationUPI,s.activationUPI,"avg").map(x=>Math.min(x*g("activation"),1));
    const tC=dist(v.txCC,s.txCC,"avg").map(x=>x*g("volume")),tU=dist(v.txUPI,s.txUPI,"avg").map(x=>x*g("volume"));
    const aC=dist(v.atsCC,s.atsCC,"avg").map(x=>x*g("ats")),aU=dist(v.atsUPI,s.atsUPI,"avg").map(x=>x*g("ats"));
    const ip=dist(v.intlPct,s.intlPct,"avg").map(x=>Math.min(x*g("intl"),1));
    const k={};["cif","sCC","sUP","xCC","xUP","tS","tX","iS","cF"].forEach(key=>k[key]=Array(n).fill(0));
    for(let m=0;m<n;m++){const prev=m>0?k.cif[m-1]:0;k.cif[m]=Math.max(0,prev+iss[m]-mA[m]*prev-mA[m]*iss[m]);k.xCC[m]=k.cif[m]*acC[m]*tC[m];k.xUP[m]=k.cif[m]*acU[m]*tU[m];
      k.sCC[m]=k.xCC[m]*aC[m];k.sUP[m]=k.xUP[m]*aU[m];k.tS[m]=k.sCC[m]+k.sUP[m];k.tX[m]=k.xCC[m]+k.xUP[m];k.iS[m]=k.tS[m]*ip[m];k.cF[m]=(m+1)%3===0?k.cif[m]*v.cardFee:0;}
    k.derived_attrition=rates;k.n=n;return k;}
  function calcAll(variants,cfg,volumeSlabs,cifSlabs,pm){cfg=Object.assign({},DEFAULT_CONFIG,cfg||{});const slV=volumeSlabs||DEFAULT_VOLUME_SLABS,slC=cifSlabs||DEFAULT_CIF_SLABS;pm=pm||SCENARIOS.base;
    const vR=variants.map(v=>calcVariant(JSON.parse(JSON.stringify(v)),pm));const mxM=Math.max(...variants.map(v=>v.years*12)),mxY=Math.max(...variants.map(v=>v.years));
    const keys=["cif","sCC","sUP","xCC","xUP","tS","tX","iS","cF"];const c={};keys.forEach(key=>c[key]=Array(mxM).fill(0));
    for(const vr of vR)for(const key of keys)for(let m=0;m<vr[key].length;m++)c[key][m]+=vr[key][m];
    const rV=c.tS.map(x=>x*cfg.rvp),rF=c.tX.map(x=>x*cfg.rff),iF=c.iS.map(x=>x*cfg.ifp*cfg.intlRevShare);
    const rev=[...Array(mxM).keys()].map(i=>rV[i]+rF[i]+c.cF[i]+iF[i]);
    const sV=c.tX.map((tx,i)=>{const sl=slab(tx,slV);return sl.fb*tx+sl.pb*c.tS[i];});const icF=c.cF.map((x,i)=>x*slab(c.cif[i],slC).pb);const iIS=c.iS.map(x=>x*cfg.iip);
    const ms=Array(mxM).fill(0);const sum=(a,s,e)=>{let t=0;for(let i=s;i<e;i++)t+=a[i];return t;};
    for(let y=0;y<mxY;y++){const s=y*12,e=Math.min(y*12+12,mxM);if(e<=s)continue;const yc=c.cif[e-1],ys=sum(c.tS,s,e);const tgt=variants.reduce((a,v)=>a+(y<v.cif.length?v.cif[y]:0),0);let hit=yc>=tgt*.95;
      if(cfg.milestone_rule==="cif_spends"){const ts=(cfg.spend_targets||Array(mxY).fill(0))[y];hit=hit&&ys>=ts*.95;}
      if(hit){const bn=sum(c.cF,s,e)*cfg.mcb+ys*cfg.msb+sum(c.iS,s,e)*(cfg.imip||0);for(let m=s;m<e;m++)ms[m]=bn/(e-s);}}
    const inc=[...Array(mxM).keys()].map(i=>sV[i]+icF[i]+iIS[i]+ms[i]);const totS=c.tS.reduce((a,b)=>a+b,0),totR=rev.reduce((a,b)=>a+b,0),totI=inc.reduce((a,b)=>a+b,0)+cfg.upf,netR=totR-totI;
    const bps=x=>totS>0?x/totS*1e4:0;const years=[];
    for(let y=0;y<mxY;y++){const s=y*12,e=Math.min(y*12+12,mxM);years.push({year:"Y"+(y+1),cif:c.cif[e-1],spends:sum(c.tS,s,e),txns:sum(c.tX,s,e),intl_spends:sum(c.iS,s,e),revenue:sum(rev,s,e),incentives:sum(inc,s,e),net:sum(rev,s,e)-sum(inc,s,e),
      rev_value:sum(rV,s,e),rev_flat:sum(rF,s,e),rev_cardfee:sum(c.cF,s,e),rev_intl:sum(iF,s,e),inc_volume:sum(sV,s,e),inc_cif:sum(icF,s,e),inc_intl:sum(iIS,s,e),inc_milestone:sum(ms,s,e),lastTx:c.tX[e-1],lastCif:c.cif[e-1]});}
    return {total_spends:totS,total_revenue:totR,total_incentives:totI,net_revenue:netR,net_bps:bps(netR),gross_bps:bps(totR),incentive_bps:bps(totI),upfront:cfg.upf,
      corridor:{floor:cfg.bpF,ceiling:cfg.bpC},years,monthly:{cif:c.cif,spends:c.tS,txns:c.tX,revenue:rev,incentives:inc},variants:variants.map((v,i)=>({name:v.name,derived_attrition:vR[i].derived_attrition}))};}
  const api={PARAMS,EVEN,DEFAULT_CONFIG,DEFAULT_VOLUME_SLABS,DEFAULT_CIF_SLABS,SCENARIOS,defaultVariant,calcAll};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;else root.DealEngine=api;
})(this);
