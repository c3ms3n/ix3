import numpy as np, json, math
from PIL import Image
from scipy import ndimage as ndi
im=np.asarray(Image.open('reference/3.jpg').convert('RGB')).astype(float)
R,G,B=im[...,0],im[...,1],im[...,2]
lum=(R+G+B)/3
sm=ndi.gaussian_filter(lum,1.2)
def bil(a,x,y):
    return ndi.map_coordinates(a,[[y],[x]],order=1)[0]
def trace(start,direction,steps,step=5,search=9,smooth=0.35,minv=0):
    x,y=start; dx,dy=direction; n=math.hypot(dx,dy); dx/=n; dy/=n
    pts=[(x,y)]
    for i in range(steps):
        # advance
        px,py=x+dx*step,y+dy*step
        nx,ny=-dy,dx
        best=-1;bo=0
        for o in np.arange(-search,search+0.1,0.5):
            v=bil(sm,px+nx*o,py+ny*o)
            if v>best: best=v;bo=o
        if best<minv: break
        px+=nx*bo*0.8; py+=ny*bo*0.8
        ndx,ndy=px-x,py-y; nn=math.hypot(ndx,ndy); ndx/=nn; ndy/=nn
        dx=dx*(1-smooth)+ndx*smooth; dy=dy*(1-smooth)+ndy*smooth; nn=math.hypot(dx,dy); dx/=nn; dy/=nn
        x,y=px,py; pts.append((round(x,1),round(y,1)))
    return pts
def dp(pts,eps):
    if len(pts)<3: return pts
    a=np.array(pts[0]);b=np.array(pts[-1]);d=b-a;L=np.hypot(*d)
    dist=[abs(np.cross(d,np.array(p)-a))/L if L>0 else np.hypot(*(np.array(p)-a)) for p in pts[1:-1]]
    i=int(np.argmax(dist)); 
    if dist[i]>eps:
        l=dp(pts[:i+2],eps); r=dp(pts[i+1:],eps); return l[:-1]+r
    return [pts[0],pts[-1]]
if __name__=='__main__':
    # outer line, left: from the top end heading left along the line
    p=trace((650,374),(-1,0.12),200,step=4,search=7,minv=90)
    print(len(p),p[0],p[-1])
    json.dump(p,open('outer_left_raw.json','w'))
    s=dp(p,1.2); print(len(s),s)
