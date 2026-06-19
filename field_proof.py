"""
Geometry proof for the two new layers, before building in Three.js:
  (1) Flamm paraboloid gravity-well funnel + a sample inspiral trajectory.
  (2) Dipole poloidal field lines r = r_eq*sin^2(theta) threading the equator + jet axis.
Units: Rs = 1.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Rs = 1.0
fig = plt.figure(figsize=(12,5.2), facecolor="black")

# ---------- (1) Flamm funnel cross-section + inspiral ----------
ax = fig.add_subplot(1,2,1, facecolor="black")
r = np.linspace(Rs, 14*Rs, 400)
z = 2.0*np.sqrt(Rs*(r-Rs))          # Flamm paraboloid embedding height
zmax = z.max()
y = (z - zmax)                       # orient as downward funnel: throat deep, rim flat
# both sides of the cross-section
ax.plot(r, y, color="#7ccfff", lw=1.5)
ax.plot(-r, y, color="#7ccfff", lw=1.5)
# concentric "rings" shown as horizontal ticks at sampled radii (depth markers)
for rr in np.linspace(1.3, 14, 9):
    zz = 2.0*np.sqrt(Rs*(rr-Rs)) - zmax
    ax.plot([-rr, rr],[zz,zz], color="#2a4a66", lw=0.6)
# sample inspiral: integrate 2D orbit with light drag, plot radius->funnel depth
def inspiral():
    GM=1.0; p=np.array([11.0,0.0]); v=np.array([0.0,0.30])  # sub-circular -> decays in
    pts=[]
    for _ in range(6000):
        rr=np.hypot(*p)
        if rr<1.2: break
        a=-GM*p/rr**3
        v=v+a*0.01 - v*0.0006        # tiny drag => inspiral
        p=p+v*0.01
        zz=2.0*np.sqrt(max(Rs*(rr-Rs),0))-zmax
        pts.append((p[0],zz))
    return np.array(pts)
tr=inspiral()
ax.plot(tr[:,0], tr[:,1], color="#ffd27c", lw=1.0, alpha=0.9)
ax.scatter([tr[-1,0]],[tr[-1,1]], color="#fff", s=18, zorder=5)
ax.axhline(0, color="#444", lw=0.5)
ax.set_title("Flamm gravity well + inspiral (equatorial cross-section)", color="#cfe8ff", fontsize=10)
ax.set_xlim(-15,15); ax.set_ylim(zmax*-1.05, 1.5)
ax.tick_params(colors="#555"); [s.set_color("#333") for s in ax.spines.values()]

# ---------- (2) Dipole field lines (poloidal plane) ----------
ax2 = fig.add_subplot(1,2,2, facecolor="black")
# axis = vertical (spin axis). field line: r = r_eq * sin^2(theta), theta from axis.
th = np.linspace(0.001, np.pi-0.001, 400)
for r_eq in [3,5,7,9,11]:
    rr = r_eq*np.sin(th)**2
    # only draw outside the horizon
    m = rr>=Rs
    x = rr*np.sin(th)        # cylindrical radius (equatorial direction)
    yv = rr*np.cos(th)       # along spin axis
    ax2.plot(x[m], yv[m], color="#ff7adc", lw=1.0, alpha=0.8)
    ax2.plot(-x[m], yv[m], color="#ff7adc", lw=1.0, alpha=0.8)
# horizon + disk + jet axis
circ=np.linspace(0,2*np.pi,100)
ax2.fill(np.cos(circ)*Rs, np.sin(circ)*Rs, color="#000", ec="#ff8a3a")
ax2.plot([3,8],[0,0], color="#ffcc88", lw=4, alpha=0.5)      # disk (one side)
ax2.plot([-8,-3],[0,0], color="#ffcc88", lw=4, alpha=0.5)
ax2.annotate("", xy=(0,12), xytext=(0,2), arrowprops=dict(color="#9cf", width=2, headwidth=8))  # jet
ax2.annotate("", xy=(0,-12), xytext=(0,-2), arrowprops=dict(color="#9cf", width=2, headwidth=8))
ax2.set_title("Dipole field lines (r=r_eq sin²θ) + jets along spin axis", color="#ffd0f0", fontsize=10)
ax2.set_xlim(-13,13); ax2.set_ylim(-13,13); ax2.set_aspect("equal")
ax2.tick_params(colors="#555"); [s.set_color("#333") for s in ax2.spines.values()]

plt.tight_layout()
plt.savefig("field_proof.png", dpi=110, facecolor="black")
print("wrote field_proof.png  | zmax=%.2f  inspiral_pts=%d"%(zmax, len(tr)))
