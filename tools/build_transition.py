"""Builds preview/media/hall-transition-mobile.mp4 from the two Kling clips.

  hold   1.8 s of clip 1's first frame (= the hero loop's first frame). The page starts this video
         inside the tap (so Low Power Mode can't block it) while Sarah's real photo dissolves on top:
         nothing in the AI clip moves until she is gone.
  clip 1 the pyramid opens and the camera dives in: 10 s retimed to ~4 s with a smooth speed ramp
         (eases out of the still, rushes the dash and the passage, eases onto the stairway)
  clip 2 down the stairs into the Hall: 5 s retimed to ~3.8 s, easing to 1x as it settles on the
         Hall's first frame (= the landing loop's first frame)
Every output frame is a real Kling frame (nearest in time), so nothing is invented. Silent, 30 fps,
1080x1920 H.264, fast start, a keyframe every second.
usage: python3 tools/build_transition.py clip1.mp4 clip2.mp4 out.mp4
"""
import subprocess, sys, cv2, numpy as np

FPS, W, H = 30, 1080, 1920
HOLD_S = 1.8

def frames(path):
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS); out = []
    while True:
        ok, f = cap.read()
        if not ok: break
        out.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA))
    return out, fps

def retime(src, fps, speed):
    """speed(s): playback speed at source time s (seconds). Returns output frames at FPS."""
    dur = len(src) / fps
    s_grid = np.linspace(0, dur, 4000)
    dt = np.diff(s_grid) / np.array([speed(s) for s in s_grid[:-1]])
    t_grid = np.concatenate([[0], np.cumsum(dt)])            # output time for each source time
    n = int(round(t_grid[-1] * FPS))
    s_of_t = np.interp(np.arange(n) / FPS, t_grid, s_grid)
    return [src[min(len(src) - 1, int(round(s * fps)))] for s in s_of_t], t_grid[-1]

def ramp(a, b, x0, x1):
    """cosine ease from a to b over source seconds x0..x1"""
    def f(s):
        u = min(1, max(0, (s - x0) / (x1 - x0)))
        return a + (b - a) * (1 - np.cos(np.pi * u)) / 2
    return f

def main(c1, c2, out):
    f1, fps1 = frames(c1); f2, fps2 = frames(c2)
    # clip 1: 1.2x out of the still -> 3.4x through the dash and passage -> 1.6x onto the stairs
    up, down = ramp(1.2, 3.4, 0.0, 1.6), ramp(3.4, 1.6, 7.6, 9.6)
    a, d1 = retime(f1, fps1, lambda s: up(s) if s < 1.6 else (3.4 if s < 7.6 else down(s)))
    # clip 2: 1.6x down the stairs and through the door -> eases to 1x as it settles in the Hall
    b, d2 = retime(f2, fps2, ramp(1.6, 1.0, 2.4, 5.0))
    # a 3-frame blend across the join (clip 2 starts on clip 1's last frame, give or take a few px)
    k = 3
    join = [cv2.addWeighted(a[-k + i], 1 - (i + 1) / (k + 1), b[i], (i + 1) / (k + 1), 0) for i in range(k)]
    seq = [f1[0]] * int(HOLD_S * FPS) + a[:-k] + join + b[k:]
    print(f"hold {HOLD_S}s + clip1 {d1:.2f}s + clip2 {d2:.2f}s = {len(seq) / FPS:.2f}s")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "25", "-preset", "slow",
                           "-g", str(FPS), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for f in seq: ff.stdin.write(f.tobytes())
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    main(*sys.argv[1:4])
