import skia, time, numpy as np, subprocess, random
W,H=3840,2160
surf=skia.Surface(W,H)
c=surf.getCanvas()
tf=skia.Typeface.MakeFromName("Lora", skia.FontStyle())
font=skia.Font(tf,28)
t0=time.time()
for f in range(10):
    c.clear(skia.Color(15,18,22))
    c.save(); c.scale(2,2)
    p=skia.Paint(AntiAlias=True)
    for i in range(400):
        p.setColor(skia.Color(80+i%100,150,200,200))
        c.drawRoundRect(skia.Rect.MakeXYWH(random.random()*1800,random.random()*1000,30,20),4,4,p)
    for i in range(60):
        c.drawString("GPFS token manager %d"%i, random.random()*1700, random.random()*1000, font, p)
    c.restore()
    img=surf.makeImageSnapshot()
    arr=img.toarray(colorType=skia.kBGRA_8888_ColorType) if hasattr(img,'toarray') else None
    b=arr.tobytes()
print("per frame draw+readback", (time.time()-t0)/10, arr.shape, len(b))
