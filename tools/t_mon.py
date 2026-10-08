import time, sys, numpy as np
from PIL import Image
from sdf import *
from monsters import *
fn = {'scarecrow':scarecrow,'wraith':wraith,'witch':witch,'pumpking':pumpking,'zombie':zombie}[sys.argv[1]]
W,H = int(sys.argv[2]), int(sys.argv[3])
ss = int(sys.argv[4]) if len(sys.argv)>4 else 2
t=time.time(); ims=[]
for pose in ('walk1','walk2','attack','pain'):
    im=render(fn(pose),W,H,cam_y=H/96/2-0.01,cam_h=H/96,ss=ss)
    a=to_rgba(im); a[im.glow,:3]=np.minimum(255,a[im.glow,:3].astype(int)+40)
    ims.append(a)
print(sys.argv[1], time.time()-t)
sheet=Image.new('RGBA',(W*len(ims),H),(40,30,50,255))
for i,a in enumerate(ims): sheet.alpha_composite(Image.fromarray(a,'RGBA'),(i*W,0))
sheet.resize((sheet.width*3,sheet.height*3),Image.NEAREST).save('out/%s.png'%sys.argv[1])
