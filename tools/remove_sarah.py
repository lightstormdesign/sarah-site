"""Removes Sarah from her Giza photo -> source/giza-empty-crop.png (the transition start frame).
Classical, no AI: GrabCut finds her, then the hole is filled from the same rows of the photo
(the pyramid courses and ground run level) and Poisson-blended. Her hair wisps over the stone are
found with a top-hat filter and filled the same way. Run from the repo root.
Step 1 (mask):"""
import cv2,numpy as np
c=cv2.imread('source/giza-original-crop.png')
H,W=c.shape[:2]
mask=np.zeros((H,W),np.uint8)
rect=(540,720,W-540-80,H-720-1)
bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
cv2.grabCut(c,mask,rect,bg,fg,8,cv2.GC_INIT_WITH_RECT)
m=np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
# keep largest component
n,l,s,_=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(s[1:,4]); m=np.where(l==k,255,0).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
cv2.imwrite('source/sarah-mask-raw.png',m)
# Step 2 (fill):
c=cv2.imread('source/giza-original-crop.png'); H,W=c.shape[:2]
m=cv2.imread('source/sarah-mask-raw.png',0)
md=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41)))
md=cv2.dilate(md,np.ones((1,31),np.uint8))
# hair wisps: bright thin lines in the zone left of her head
g=cv2.cvtColor(c,cv2.COLOR_BGR2GRAY)
th=cv2.morphologyEx(g,cv2.MORPH_TOPHAT,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
zone=np.zeros_like(g); cv2.rectangle(zone,(470,780),(720,1000),255,-1)
w=((th>18)&(zone>0)).astype(np.uint8)*255
n,l,s,_=cv2.connectedComponentsWithStats(w)
keep=np.zeros_like(w)
for i in range(1,n):
    if max(s[i,2],s[i,3])>=14: keep[l==i]=255
wisp=cv2.dilate(keep,np.ones((9,9),np.uint8))
print('wisp px',(wisp>0).sum())
allm=cv2.bitwise_or(md,wisp)
P=60
def pad(a): return cv2.copyMakeBorder(a,0,P,0,0,cv2.BORDER_REFLECT)
fill=c.copy()
fill[wisp>0]=np.roll(c,260,axis=1)[wisp>0]
ys,xs=np.where(md>0); D=int(xs.max()-xs.min()+20)
fill[md>0]=np.roll(c,D,axis=1)[md>0]
fp=pad(fill); cp=fp.copy(); cp[:H]=c
mp=pad(allm); mp[H:]=pad(allm)[H:]  # mask continues into pad
mp[-2:]=0; mp[:,:2]=0; mp[:,-2:]=0
br=cv2.boundingRect(mp); center=(br[0]+br[2]//2, br[1]+br[3]//2)
out=cv2.seamlessClone(fp,cp,mp,center,cv2.NORMAL_CLONE)[:H]
cv2.imwrite('source/giza-empty-crop.png',out); cv2.imwrite('source/sarah-mask.png',allm)
