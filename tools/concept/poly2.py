from trace import *
import contourpy
def iso(mask,eps=1.2):
    """Largest closed iso-contour (0.5) of the smoothed mask, simplified."""
    f=ndi.gaussian_filter(mask.astype(float),1.0)
    cg=contourpy.contour_generator(np.arange(f.shape[1]).astype(float),np.arange(f.shape[0]).astype(float),f)
    lines=cg.lines(0.5)
    best=max(lines,key=lambda l:len(l))
    pts=[(float(x),float(y)) for x,y in best]
    if pts[0]==pts[-1]: pts=pts[:-1]
    a=np.array(pts); far=int(np.argmax(np.hypot(*(a-a[0]).T)))
    p1=dp(pts[:far+1],eps); p2=dp(pts[far:]+[pts[0]],eps)
    return p1[:-1]+p2[:-1]
def region(x0,y0,x1,y1):
    m=np.zeros(R.shape,bool); m[y0:y1,x0:x1]=True; return m
if __name__=='__main__':
    base=((R>150)&((R-B)>70)&(G>70))
    base=ndi.binary_opening(base,iterations=1)
    out={}
    for name,box in {'swoosh':(330,630,480,740),'fuel':(235,630,335,745),'rswoosh':(1130,560,1310,740),'cool':(1265,685,1350,745)}.items():
        m=base&region(*box)
        m=ndi.binary_closing(m,iterations=2)
        lab,n=ndi.label(m); sizes=ndi.sum(m,lab,range(1,n+1)); m=(lab==int(np.argmax(sizes))+1)
        m=ndi.binary_fill_holes(m)
        p=iso(m,1.0); out[name]=[(round(x,1),round(y,1)) for x,y in p]; print(name,len(p),'area',int(m.sum()))
    json.dump(out,open('amber_polys.json','w'))
    from PIL import ImageDraw
    img=Image.open('reference/3.jpg').convert('RGB'); d=ImageDraw.Draw(img)
    for n_,p in out.items(): d.line(p+[p[0]],fill=(0,255,0),width=1)
    img.crop((215,540,1400,780)).resize((1185*1,240*1)).save('amber_chk.png')
