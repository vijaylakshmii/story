import numpy as np, json, subprocess
SR=48000; DUR=85.7; rng=np.random.default_rng(11)
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def env(n,att,dec):
    t=np.arange(n)/SR; return np.minimum(t/att,1)*np.exp(-np.maximum(t-att,0)/dec)
def key(v):
    n=int(0.07*SR); t=np.arange(n)/SR
    click=bp(rng.standard_normal(n),2200+300*v,7000)*env(n,0.0005,0.006)
    thock=np.sin(2*np.pi*(180+40*v)*t)*env(n,0.001,0.012)*0.9
    body=bp(rng.standard_normal(n),600,1800)*env(n,0.001,0.01)*0.6
    rel=np.zeros(n); k=int((0.035+0.01*v)*SR); m=n-k
    rel[k:]=bp(rng.standard_normal(m),3000,8000)*env(m,0.0004,0.004)*0.35
    x=click+thock+body+rel; return x/np.abs(x).max()
def mouse():
    n=int(0.12*SR); x=np.zeros(n)
    for off,amp,f in [(0,1.0,4200),(int(0.075*SR),0.6,5200)]:
        m=int(0.012*SR); t=np.arange(m)/SR
        s=(bp(rng.standard_normal(m),2500,9000)*0.7+np.sin(2*np.pi*f*t)*0.5)*env(m,0.0003,0.0025)
        x[off:off+m]+=s*amp
    return x/np.abs(x).max()
def ding():
    n=int(0.9*SR); t=np.arange(n)/SR
    x=(np.sin(2*np.pi*1318.5*t)+0.5*np.sin(2*np.pi*1975.5*t)+0.25*np.sin(2*np.pi*2637*t))*env(n,0.002,0.28)
    return x/np.abs(x).max()
def tick():
    n=int(0.03*SR); t=np.arange(n)/SR; x=np.sin(2*np.pi*2600*t)*env(n,0.0003,0.004)+bp(rng.standard_normal(n),3000,9000)*env(n,0.0002,0.002)*0.5
    return x/np.abs(x).max()
def pop():
    n=int(0.09*SR); t=np.arange(n)/SR; f=880*np.exp(-t*9)+520
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*55); x[:24]*=np.linspace(0,1,24); return x/np.abs(x).max()
def whoosh(length=0.55,peak=0.2):
    n=int(length*SR); out=np.zeros(n); fl=1024; hop=512; win=np.hanning(fl)
    for s in range(0,n-fl,hop):
        fc=350*(2600/350)**(s/n); seg=rng.standard_normal(fl)*win; S=np.fft.rfft(seg); f=np.fft.rfftfreq(fl,1/SR)
        S*=np.exp(-0.5*((np.log(f+1)-np.log(fc))/0.45)**2); out[s:s+fl]+=np.fft.irfft(S,fl)
    t=np.arange(n)/SR; out*=np.where(t<peak,(t/peak)**2.2,np.exp(-(t-peak)/0.11)); return out/np.abs(out).max()
bus=np.zeros(int(DUR*SR)); log=[]
def place(x,t,db,lab,peak=0.0):
    i=int((t-peak)*SR); 
    if i<0: x=x[-i:]; i=0
    bus[i:i+len(x)]+=x[:len(bus)-i]*10**(db/20); log.append({"event":lab,"t":round(t,3),"gain_db":db})
T=json.load(open("style/timeline2.json"))
for it in T["type"]:
    last=-1
    for i,ch in enumerate(it["text"]):
        if ch=="\n": continue
        tc=it["t0"]+i/it["cps"]
        if tc-last<0.055: continue
        last=tc; v=rng.uniform(-1,1)
        place(key(v),tc,-27+rng.uniform(-2,1.5)-(4 if ch==" " else 0),f"key:{it['id']}")
for c in T["cursor"]:
    if c.get("click"): place(mouse(),c["t"],-20,"mouse")
for t in T["pops"]: place(pop(),t+0.08,-24,"pop",0.004)
for t,kind in T["whoosh"]: place(whoosh(),t+0.16,{"card":-22,"scene":-20,"soft":-26}[kind],"whoosh:"+kind,0.2)
for t in T["ding"]: place(ding(),t,-25,"ding")
a,b=T["ticks"]
for k in range(10): place(tick(),a+k*(b-a)/9,-28,"tick")
bus=np.clip(bus,-1,1).astype(np.float32)
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","-","-c:a","pcm_s24le","sound/sfx_bus2.wav"],input=bus.tobytes(),check=True)
json.dump(log,open("sound/sfx2.json","w")); 
from collections import Counter; print(Counter(e["event"].split(":")[0] for e in log))
