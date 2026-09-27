#!/usr/bin/env python3
import html,json,os,re
from datetime import datetime
BASE=os.path.dirname(os.path.abspath(__file__)); DATA=os.path.join(BASE,"videos.json"); TEMPLATES=os.path.join(BASE,"templates"); OUT=os.path.join(BASE,"videos")
CONFIG=os.path.join(BASE,"config.json")
def load_config():
    with open(CONFIG,encoding="utf-8") as f:c=json.load(f)
    return c
CONFIG_DATA=load_config()
def resolve_site_url(config):
    explicit=str(config.get("site_url","")).strip().rstrip("/")
    if explicit:return explicit
    gh=config.get("github",{}) if isinstance(config.get("github",{}),dict) else {}
    owner=str(gh.get("owner","")).strip()
    repo=str(gh.get("repository","")).strip()
    if not owner or not repo:
        env_repo=os.environ.get("GITHUB_REPOSITORY","").strip()
        if "/" in env_repo:
            owner,repo=env_repo.split("/",1)
    if owner and repo:
        if repo.lower()==f"{owner}.github.io".lower():
            return f"https://{repo}"
        return f"https://{owner}.github.io/{repo}"
    return ""
SITE_URL=resolve_site_url(CONFIG_DATA)
LEGACY=str(CONFIG_DATA.get("legacy_site_url","")).rstrip("/")
DEFAULT="assets/img/no-cover.svg"
CATS=tuple(CONFIG_DATA.get("categories",["indonesia","papua","barat"]))
ADS=CONFIG_DATA.get("ads",{}) if isinstance(CONFIG_DATA.get("ads",{}),dict) else {}
AD_ENABLED=bool(ADS.get("enabled",False))
def ad(name):
    if not AD_ENABLED:return ""
    return str(ADS.get(name,"") or "").strip()

def native_ad(slot_id):
    raw=ad("native")
    if not raw:return ""
    # Keep the native slot position fixed in the template. Only make the
    # provider container unique per slot, regardless of which native code
    # the admin enters later.
    ids=re.findall(r'container-([A-Za-z0-9_-]+)', raw)
    if ids:
        base=ids[0]
        raw=raw.replace("container-"+base, f"container-{base}-{slot_id}")
    return raw
def load():
    with open(DATA,encoding="utf-8") as f:v=json.load(f)
    if not isinstance(v,list): raise ValueError("videos.json harus array")
    for i,x in enumerate(v):
        for k in ("slug","judul","driveId","tanggal","deskripsi","kategori"):
            if not x.get(k): raise ValueError(f"Video {i}: field {k} kosong")
        if x["kategori"] not in CATS: raise ValueError("Kategori tidak valid: "+str(x["kategori"]))
        x.setdefault("jam","00:00")
    return v
def dt(v):
    try:return datetime.strptime(f'{v.get("tanggal","")}T{v.get("jam","00:00")}','%Y-%m-%dT%H:%M')
    except ValueError:
        try:return datetime.strptime(v.get("tanggal",""),'%Y-%m-%d')
        except ValueError:return datetime.min
def dtext(v): return dt(v).strftime("%d-%m-%Y %H:%M") if dt(v)!=datetime.min else f'{v.get("tanggal","-")} {v.get("jam","00:00")}'
def esc(s):return html.escape(str(s),quote=True)
def cover(v,detail=False):
    c=str(v.get("cover") or "").strip() or DEFAULT
    if c.startswith(("http://","https://")):return c
    local=os.path.join(BASE,c.lstrip("/"))
    if os.path.exists(local):return ("../" if detail else "")+c.lstrip("/")
    return LEGACY+"/"+c.lstrip("/")
def og(v):
    c=str(v.get("cover") or "").strip() or DEFAULT
    if c.startswith(("http://","https://")):return c
    c=c.lstrip("/")
    local=os.path.join(BASE,c)
    if os.path.exists(local):
        return (SITE_URL+"/"+c) if SITE_URL else c
    return (LEGACY+"/"+c) if LEGACY else c
def card(v):
    return f'<a href="videos/{esc(v["slug"])}.html" class="video-card" data-category="{esc(v["kategori"])}"><img src="{esc(cover(v))}" alt="{esc(v["judul"])}" loading="lazy"><div class="card-body"><h3>{esc(v["judul"])}</h3><p class="meta-date">{esc(dtext(v))}</p><span class="badge">{esc(v["kategori"])}</span></div></a>'
def rel(v):
    return f'<a href="{esc(v["slug"])}.html" class="related-card"><div class="related-thumb"><img src="{esc(cover(v,True))}" alt="{esc(v["judul"])}" loading="lazy"><span class="related-play">▶</span></div><div class="related-body"><h3>{esc(v["judul"])}</h3><p>{esc(dtext(v))}</p><span class="badge">{esc(v["kategori"])}</span></div></a>'
def main():
    vs=load(); ordered=sorted(vs,key=dt,reverse=True)
    it=open(os.path.join(TEMPLATES,"index.html"),encoding="utf-8").read()
    open(os.path.join(BASE,"index.html"),"w",encoding="utf-8").write(it.replace("{{ VIDEO_CARDS }}","\n".join(card(v) for v in ordered)).replace("{{ AD_POPUNDER }}",ad("popunder")).replace("{{ AD_SOCIAL_BAR }}",ad("social_bar")).replace("{{ AD_BANNER_DESKTOP }}",ad("banner_desktop")).replace("{{ AD_BANNER_MOBILE }}",ad("banner_mobile")).replace("{{ AD_NATIVE }}",ad("native")))
    os.makedirs(OUT,exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".html"):os.remove(os.path.join(OUT,f))
    vt=open(os.path.join(TEMPLATES,"video.html"),encoding="utf-8").read()
    for v in vs:
        out=vt.replace("{{ JUDUL }}",esc(v["judul"])).replace("{{ DESKRIPSI }}",esc(v["deskripsi"])).replace("{{ DRIVE_ID }}",esc(v["driveId"])).replace("{{ KATEGORI }}",esc(v["kategori"])).replace("{{ TANGGAL }}",esc(dtext(v))).replace("{{ COVER }}",esc(cover(v,True))).replace("{{ OG_COVER }}",esc(og(v))).replace("{{ PAGE_URL }}",esc(f'{SITE_URL}/videos/{v["slug"]}.html' if SITE_URL else f'videos/{v["slug"]}.html'))
        related=[x for x in ordered if x["slug"]!=v["slug"]]
        chunks=[]
        for start in range(0,len(related),4):
            chunks.append('\n'.join(rel(x) for x in related[start:start+4]))
            chunks.append(f'<div class="related-native-ad ad-slot" aria-label="Iklan Native">{native_ad(start//4+1)}</div>')
        related_html='\n'.join(chunks) or '<p>Belum ada video lainnya.</p>'
        out=out.replace("{{ RELATED_VIDEOS }}",related_html)
        out=out.replace("{{ AD_POPUNDER }}",ad("popunder")).replace("{{ AD_SOCIAL_BAR }}",ad("social_bar")).replace("{{ AD_BANNER_DESKTOP }}",ad("banner_desktop")).replace("{{ AD_BANNER_MOBILE }}",ad("banner_mobile"))
        open(os.path.join(OUT,v["slug"]+".html"),"w",encoding="utf-8").write(out)
    print("Generated",len(vs),"videos")
if __name__=="__main__":main()
