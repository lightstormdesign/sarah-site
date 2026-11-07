# Sarah Breskman Cosme · The Hall of Records (LightStorm, private)

A pitch preview for Sarah Breskman Cosme ("The Holistic Hypnotist"). **Private: nothing here goes public
without her permission.** It follows the LightStorm build rules from TREV's site
(lightstormdesign/trevwebsite, CLAUDE.md): Sarah is never AI-generated. Her real photo dissolves out in
code before any AI clip plays, the transition is at most two clips, and every prompt is environment only.

| Path | What |
|---|---|
| `preview/` | The mockup hero page: a static folder that runs with no build step |
| `plates/` | Hero plates: `giza-{mobile,desktop}-sarah.jpg` (her real photo, extended), `-empty.jpg` (the same frame without her = Kling clip 1's start frame), `-cutout.webp` (her real photo, cut out for the in-code dissolve), `cutouts.json` (positions) |
| `source/` | Her Giza photo cropped from the Instagram post, the masks, and the empty version |
| `tools/` | `remove_sarah.py` (classical removal, no AI) and `make_plates.py` (9:16 and 16:9 frames and cutouts). Run from the repo root: `python3 tools/remove_sarah.py && python3 tools/make_plates.py` |
| `docs/` | `01-site-audit.md`, `02-kling-prompts.md`, `03-opening-message.md` |

## Run the preview
```bash
cd preview && python3 -m http.server 8000     # then open http://<your-computer-ip>:8000 on the phone
```
- Tap **Begin the journey**. Sarah dissolves into gold light, the camera glides to the pyramid's base
  as dusk falls, a seam of light opens, and you pass into the chamber with its three doorways.
- `?auto` starts by itself after 3.5 s (for a hands-free recording). **Replay** sits in the footer.
- When `preview/media/hall-transition-mobile.mp4` exists (the two Kling clips joined, see
  `docs/02-kling-prompts.md`), it plays instead of the staged version. Add `?sim` to force the staged one.
- To record on iPhone: open it in Safari, use "Add to Home Screen" for full screen with no toolbars,
  then use Control Center → Screen Recording. Start, wait about 3 s, tap Begin, and stop about 16 s later.

## Re-running with the full-size original
The plates were made from a screenshot of the Instagram post (the photo area is 1179×1587), so they're
sharp on a phone but soft when the camera pushes in. Drop the original into
`source/giza-original-crop.png`, cropped to the same framing, and re-run both tools. The masks'
coordinates assume that framing, so check `source/sarah-mask.png` after re-running.
