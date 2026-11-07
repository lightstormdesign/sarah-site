# The transition: two Kling clips, environment only

**The rule:** Sarah is never in an AI frame. On the site, her real photo dissolves into gold light in
code first. Only then does clip 1 start, on the **empty** plate. Every prompt below describes the place
only. Never upload an image of her to Kling or to any image model, including as a "reference".

```
hero (her real photo)  →  code dissolve  →  CLIP 1: empty plate → base of the pyramid at dusk, seam of light
                                             CLIP 2: through the seam → the Atlantean chamber (the landing)
```

## Frames

| Frame | File | Notes |
|---|---|---|
| Clip 1 **start** | `plates/giza-mobile-empty.jpg` (1080×1920) | This is the hero exactly, minus Sarah. The site's dissolve ends on this frame. |
| Clip 1 **end** | `frames/clip1-end.jpg` (generate it, see A) | The pyramid's base, close, at deep dusk, with a thin vertical seam of gold light |
| Clip 2 **start** | Clip 1's own last frame (extract it, see below) | Using the real last frame means no jump at the join |
| Clip 2 **end** | `frames/clip2-end.jpg` (generate it, see B) | The landing. Its layout matches the page: title space at top, crystal in the middle, three arches low |

Desktop: repeat with `plates/giza-desktop-empty.jpg` at 16:9 if you want a native desktop video.
Otherwise the phone video works on desktop, as on TREV's site.

---

### A. Clip 1 end frame: image prompt (img2img or "reference" from the empty plate, 9:16)
Upload `plates/giza-mobile-empty.jpg` as the reference image. Image strength is about 0.35, so the
stone, the camera height and the lens all carry over.

> Photograph, 9:16 vertical. Close view of the base of the Pyramid of Khafre at Giza at deep dusk, a few
> minutes after sunset. The camera is low and centred, looking straight at the bottom courses of
> weathered limestone blocks, which fill most of the frame. A thin strip of indigo-violet sky shows at
> the very top, with the last band of amber at the horizon. Between two massive blocks in the centre of
> the bottom course, a narrow vertical seam has opened, and warm gold light spills out of it onto the
> sand, with a faint cool blue glow deep inside. The light from the seam is soft and real, catching the
> stone texture and dust in the air. Same lens and colour grade as the reference photo, photographic,
> natural grain, no fantasy styling. No people, no figures, no silhouettes, no text.

Negative: `person, people, woman, man, figure, silhouette, face, hands, tourist, camel, text, logo, watermark, CGI, cartoon, painting, oversaturated, lens flare streaks`

### B. Clip 2 end frame: the chamber, the landing (9:16)
> Cinematic still, 9:16 vertical. A vast hidden chamber beneath the Giza plateau, Atlantean, carved from
> pale stone and lit from within. In the centre, a tall clear quartz crystal (a six-sided obelisk)
> floats just above a still, reflecting pool. It glows crystal-blue and white from inside, and soft rays
> fall on it from an opening far above. Gold inlay traces the walls in fine sacred-geometry lines. On
> either side, colonnades of slender columns with gold capitals recede into blue shadow. Across the lower
> third of the frame, three tall arched doorways stand side by side in the back wall. Each is outlined
> in gold and filled with a soft blue-white light. The top quarter of the frame is calm and dark (deep
> navy vault) with room for a title. The palette is crystal blue, deep navy and warm gold. The mood is
> sacred, serene and luminous, with fine dust motes in the light. Photoreal, volumetric light, 35 mm
> lens, symmetrical composition. No people, no figures, no statues of people, no text.

Negative: `person, people, figure, silhouette, face, statue of a person, angel, hands, text, letters, hieroglyph text, logo, watermark, red, purple neon, cartoon, low detail`

Keep this frame calm and symmetrical. The page lays the title over its top and the three doorway
buttons over its lower third, so the arches in the image should sit where the buttons go.

---

## Kling settings
Image-to-video, **start + end frame**, 9:16, **Professional / high quality** mode, **5 s** each (10 s
for clip 1 if the glide feels rushed), creativity/relevance about 0.5, **no** camera-control preset
(the prompt drives the camera). Generate 3–4 takes of each and keep the steadiest.

### Clip 1 prompt (start: empty plate · end: A)
> The camera glides slowly and steadily forward at a low height across the sand toward the base of the
> Pyramid of Khafre, in one continuous smooth dolly move with no cuts. As it moves, the golden-hour light
> deepens to dusk: the pale sky turns amber, then rose, then indigo, and the pyramid's stone cools from
> warm beige to dusky violet-brown. Near the end, a thin vertical seam of warm gold light opens between
> two blocks at the base and grows brighter, lighting the dust in the air. The stone stays solid, still
> and photographic. Environment only. The scene is empty: no people, no animals, no figures.

Negative: `person, people, woman, figure, silhouette, face, hands, tourist, camel, morphing stone, warping pyramid, cuts, shaky camera, text, watermark`

### Clip 2 prompt (start: clip 1's last frame · end: B)
> The camera keeps moving forward without stopping and slips through the narrow seam of gold light
> between the stones. For a moment the frame fills with warm light, then it opens into a vast luminous
> chamber of crystal blue and gold. A tall floating quartz crystal glows above a still pool, gold
> sacred-geometry inlay shimmers on the walls, and three gold-framed arched doorways glow softly ahead.
> The camera slows and settles, centred and symmetrical, as dust motes drift in the light. One
> continuous move, serene and sacred. Environment only. The scene is empty: no people, no figures.

Negative: `person, people, figure, silhouette, face, statue of a person, hands, text, letters, flicker, strobing, fast cuts, warping columns, watermark`

---

## Joining and encoding (for iPhone)
```bash
# clip 2's start frame = clip 1's real last frame
ffmpeg -sseof -0.05 -i clip1.mp4 -frames:v 1 -q:v 1 frames/clip2-start.jpg

# trim each clip's weak frames if needed (-ss/-to), then join and encode as one silent web file
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1,scale=1080:1920,fps=30,format=yuv420p" \
  -an -c:v libx264 -profile:v high -crf 23 -preset slow -movflags +faststart \
  preview/media/hall-transition-mobile.mp4
```
The mobile file should come in under about 6 MB. When `preview/media/hall-transition-mobile.mp4` is
present, the preview plays it automatically after the dissolve. Without it, the preview stages the same
two beats in code. Add `?sim` to the URL to force the staged version.

## Checklist before a clip ships
- [ ] Watch every frame at full screen: no person, face, figure or silhouette appears anywhere.
- [ ] Clip 1's first frame matches `giza-mobile-empty.jpg`, so there's no jump after the dissolve.
- [ ] Clip 2's first frame matches clip 1's last frame.
- [ ] Clip 2's last frame is calm enough to hold under the landing's title and doorways.
