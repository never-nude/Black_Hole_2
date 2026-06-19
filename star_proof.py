"""
Volumetric star — NumPy CPU port of the GLSL raymarch, for verification before GPU.
Renders a hero frame + a 3-frame strip to PNG. Mirrors exactly the math that will
ship in blackhole.html: world-space ray/sphere intersect, emission-absorption march,
3D-noise plasma with domain-warped granulation, blackbody color ramp, limb darkening,
and a wispy animated corona.
"""
import numpy as np
from PIL import Image

# ---------- 3D value noise (vectorized), matches GLSL hash/noise ----------
def hash3(p):
    # p: (...,3) float -> (...) in [0,1)
    d = p[...,0]*12.9898 + p[...,1]*78.233 + p[...,2]*37.719
    s = np.sin(d) * 43758.5453
    return s - np.floor(s)

def vnoise(p):
    i = np.floor(p); f = p - i
    f = f*f*(3.0 - 2.0*f)
    def H(ox,oy,oz):
        return hash3(i + np.array([ox,oy,oz], dtype=np.float32))
    c000=H(0,0,0); c100=H(1,0,0); c010=H(0,1,0); c110=H(1,1,0)
    c001=H(0,0,1); c101=H(1,0,1); c011=H(0,1,1); c111=H(1,1,1)
    x00=c000+(c100-c000)*f[...,0]; x10=c010+(c110-c010)*f[...,0]
    x01=c001+(c101-c001)*f[...,0]; x11=c011+(c111-c011)*f[...,0]
    y0=x00+(x10-x00)*f[...,1];     y1=x01+(x11-x01)*f[...,1]
    return y0+(y1-y0)*f[...,2]

def fbm(p, oct=5):
    s=0.0; a=0.5; freq=1.0
    for _ in range(oct):
        s = s + a*vnoise(p*freq)
        freq*=2.02; a*=0.5
    return s

# ---------- blackbody-ish ramp: heat in [0,1] -> rgb ----------
# Deep red/orange (cool granule lanes) -> orange -> yellow-white -> blue-white core.
def heat_color(h):
    h = np.clip(h, 0.0, 1.0)
    # control points
    stops = np.array([
        [0.00, 0.55, 0.12, 0.02],   # cool lane, deep ember
        [0.35, 1.00, 0.42, 0.10],   # orange
        [0.62, 1.00, 0.72, 0.34],   # amber
        [0.82, 1.00, 0.94, 0.78],   # warm white
        [1.00, 1.00, 1.00, 0.98],   # white-hot core
    ])
    r=np.interp(h, stops[:,0], stops[:,1])
    g=np.interp(h, stops[:,0], stops[:,2])
    b=np.interp(h, stops[:,0], stops[:,3])
    return np.stack([r,g,b], axis=-1)

# ---------- the raymarched star (world space, normalized to star radius=1) ----------
def render(W, H, t, cam, target):
    # camera basis
    fwd = target - cam; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0,1,0.0])); right/=np.linalg.norm(right)
    up = np.cross(right, fwd)
    aspect = W/H; fov = 1.0  # tan(half-fov)
    xs = (np.linspace(-1,1,W))*aspect*fov
    ys = (np.linspace(1,-1,H))*fov
    gx, gy = np.meshgrid(xs, ys)
    dir = (fwd[None,None,:] + gx[...,None]*right[None,None,:] + gy[...,None]*up[None,None,:])
    dir /= np.linalg.norm(dir, axis=-1, keepdims=True)
    ro = np.broadcast_to(cam, dir.shape).copy()

    C = np.zeros((H,W,3)); R_surf=1.0; R_cor=1.85

    # ray-sphere intersect with corona radius
    b = np.sum(ro*dir, axis=-1)
    c = np.sum(ro*ro, axis=-1) - R_cor*R_cor
    disc = b*b - c
    hit = disc > 0.0
    sq = np.sqrt(np.maximum(disc,0.0))
    t0 = np.maximum(-b - sq, 0.0)
    t1 = -b + sq

    STEPS = 64
    tcur = t0.copy()
    seg = (t1 - t0)/STEPS
    trans = np.ones((H,W))  # transmittance
    for s in range(STEPS):
        tt = t0 + (s+0.5)*seg
        p = ro + dir*tt[...,None]
        r = np.linalg.norm(p, axis=-1)
        rn = r/R_surf

        # *** sample noise at TRUE 3D position p (not ray direction) -> real volume, no spokes ***
        # domain-warped granulation: warp the sample coords, then sample plasma
        warp = fbm(p*2.2 + np.array([0,0,t*0.05]), oct=3)
        gran = fbm(p*5.5 + warp[...,None]*0.8 + np.array([t*0.04,0,0]), oct=5)  # 0..~1

        # --- photosphere body: filled opaque ball, surface modulated by granulation ---
        surfR = 1.0 + 0.055*(gran-0.5)
        edge = 0.045
        body = np.clip((surfR - rn)/edge + 0.5, 0.0, 1.0)  # 1 inside, 0 outside
        sigma_body = body * 17.0

        # mu = view . surface-normal -> 1 at disk center (faces us), 0 at limb.
        nrm = p/np.maximum(r[...,None],1e-6)
        mu = np.clip(np.sum(-dir*nrm, axis=-1), 0.0, 1.0)
        # white-hot disk center -> orange granule limb; granule hot-spots brighter
        heat = 0.50 + 0.45*mu + 0.30*(gran-0.5)
        # classic limb darkening on brightness: I(mu)=0.35+0.65*mu
        limb = 0.35 + 0.65*mu
        Ebody = heat_color(heat) * (limb*(1.05 + 0.6*np.clip(heat,0,1)))[...,None]

        # --- corona: wispy warm filaments, animated; 3D-sampled so it billows, not spokes ---
        flow = fbm(p*2.6 + np.array([t*0.10, t*0.05, 0]), oct=4)
        cwisp = fbm(p*5.0 + flow[...,None]*1.6 + np.array([0, t*0.16, 0]), oct=4)
        fil = np.clip(cwisp-0.62,0,1)/0.38                       # sparse bright filaments
        cdens = fil*np.exp(-(np.clip(rn-1.0,0,5))/0.22)
        sigma_cor = cdens * 2.6
        Ecor = heat_color(0.42 + 0.22*cwisp) * 2.2               # warm orange wisps

        ds = seg
        # body emission-absorption
        dT = np.exp(-sigma_body*ds)
        C += (trans*( (1-dT) ))[...,None]*Ebody
        trans *= dT
        # corona additive (thin, glowing)
        C += (trans*sigma_cor*ds)[...,None]*Ecor

        tcur = tt
    C *= hit[...,None]
    # limb darkening final polish via accumulated edge already handled; gentle tonemap
    C = C/(1.0+C*0.5)               # reinhard-ish
    C = np.power(np.clip(C,0,1), 1/2.2)
    return (C*255).astype(np.uint8)

if __name__ == "__main__":
    W=H=420
    cam = np.array([0,0.35,3.4]); tgt=np.array([0,0,0.0])
    hero = render(W,H,7.0, cam, tgt)
    Image.fromarray(hero).save("star_hero.png")
    # 3-frame time strip to confirm animation + corona motion
    frames=[render(260,260,tt,cam,tgt) for tt in (0.0, 6.0, 12.0)]
    strip=np.concatenate(frames,axis=1)
    Image.fromarray(strip).save("star_strip.png")
    print("wrote star_hero.png, star_strip.png")
