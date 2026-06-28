# Bloom

Single-file Three.js (r128) web app. A six-petal Murakami flower you click to fly
through a Windows-Media-Player frame, wake the flower, then enter a room with
**Nelson** (a green media-player head) whose green coding terminal powers on when
tapped. In the awake stage an Xbox-Live-style **TRACKER** panel shows the selected petal.

---

## ⚡ Restarting in a new chat — DO THIS FIRST

This project is ~5 MB across a few files. **The 4 MB `embed_portal.json` must NOT be
pasted into chat or pulled with `web_fetch`** — that dumps 4 MB of base64 into the
context window and burns the whole token budget (this is the exact problem this repo
solves). Instead, **download it to the container with bash.** `raw.githubusercontent.com`
and `github.com` are reachable from the sandbox, and files land on disk, *not* in context:

```bash
cd /home/claude && rm -rf bloom && git clone https://github.com/USER/REPO bloom && cd bloom
python3 build_final.py && echo "BUILD OK"
```

If `git` isn't available, curl the files individually (still disk, not context):

```bash
cd /home/claude && mkdir -p bloom && cd bloom
B=https://raw.githubusercontent.com/USER/REPO/main
curl -sL -o build_final.py   $B/build_final.py
curl -sL -o embed_portal.json $B/embed_portal.json
curl -sL -o three.min.js     $B/three.min.js
python3 build_final.py && echo "BUILD OK"
```

That's it — fully operational in one message. Deliverable: `/mnt/user-data/outputs/bloom-3d.html`.

> **This repo is public on purpose** — keep real personal/medical data OUT of it.
> ⚠️ **The `CATS` array in `build_final.py` currently contains the real stack** (compound
> names, doses, schedules) because the DS terminals were populated to build the functional
> UI. Before pushing to a public remote, either **make the repo private** or **replace the
> `CATS` values with placeholders** — Claude Code only needs the *structure*; the real data
> lives in `stack_v5`.

---

## Build system

`build_final.py` is the generator. It reads `embed_portal.json` (all assets, base64) and
`three.min.js`, and writes:
- `bloom-3d-local.html` — three.js **inlined**; for local render-verify only.
- `/mnt/user-data/outputs/bloom-3d.html` — CDN three.js link; **the deliverable**.

**Edit JS/CSS/HTML inside `build_final.py`** (via str_replace), never the generated HTML.
`embed_portal.json` is the asset store / source of truth — edit it for asset swaps, then
rebuild.

### ⚠️ Critical gotcha — SHELL placeholders
`build_final.py` has two regions: `CORE = r"""..."""` (the app JS) and a SHELL HTML
skeleton (`<style>`/`<head>`/`<body>`/DOM). The line that does
`core = CORE.replace("__SPL__"...)...` applies asset placeholders to **CORE only**.
Any placeholder that lives in the SHELL's CSS or DOM —
`__WMPFRAME__`, `__XBOX__`, `__FONTVT__`, `__FONTSE__` — **must be added to BOTH SHELL
write lines** (the local write *and* the CDN write at the bottom of the file), not the
CORE chain. Forgetting this leaves a literal `__XBOX__` in the output. After a build, grep
the deliverable for leftover `__...__` to confirm.

---

## Render-verify (mandatory before presenting)

Render `bloom-3d-local.html` with Playwright + chromium-swiftshader, viewport 420×760,
device_scale_factor 2, args `["--use-gl=swiftshader","--ignore-gpu-blocklist","--enable-unsafe-swiftshader"]`,
env `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.

Debug hooks in-page: `window.__inside()` (jump into room — does NOT dismiss the WMP frame;
set `wmpf.style.opacity=0` in renders), `window.__tapHead()` (open terminal), `__wake()`,
`__rest()`, `__top()` (topIndex), `__phase()`.

**Caveat that wastes time if forgotten:** in headless, `requestAnimationFrame` is throttled
and the swiftshader clock is warped (~9× / erratic). So the 3D loop sometimes won't apply
per-frame DOM opacity, and CSS-animation *timing* in-app is unreliable. To verify a DOM
overlay's look/opacity/animation (tracker, terminal), render a **standalone HTML** that
inlines just that element's CSS + the embedded font (base64 fonts DO render in Playwright)
and trigger the animation directly — don't trust the in-app opacity render. Verify static
state, not animation timing.

---

## Current features + tuning knobs

**WMP frame intro** (opening scene): full-screen player framing the dormant flower; click
flies through it. CSS `#wmpf` `center/cover`, `@keyframes wmpz` `0.68s`, scale 5.2,
transform-origin 50% 43%.

**Room terminal (Nelson):**
- Green coding console, **VT323** font, sized to fill Nelson's screen (`placeTerm()` projects
  the SBOX screen corners, 0.96 inset).
- **CRT turn-on** when you tap the face: `@keyframes termon` `.58s` (`#term.on`, fired in the
  inph→"term" transition; reset in `resetInside()`).
- **Hue knob:** `const TERMHUE_DEG` (top of CORE) rotates the hue of the console *and* the
  green light it casts on Nelson's 3D head, together. `0` = original green, `50` = cyan-teal
  (current), `-100` ≈ amber, `90` ≈ blue, `200` ≈ magenta. Drives `#term`'s
  `filter:hue-rotate(var(--thr))` + the head shader uniform `uTermColor`.
- Head glow strength/spread: `headU.uTermI` (`termGlowI*0.95`), `uTermR` 0.30.

**Xbox TRACKER (awake stage):**
- Panel art = `embed['xboxPanel']` (user-keyed transparent PNG, 528×374, rows cleaned of
  original text + yellow). Bars/labels positioned by % derived from that crop.
- **VT323** font; 6 rows from `const PETAL_NAMES` (PLACEHOLDERS — swap for real categories).
- Moving **yellow highlight** behind the selected row: `#trk .hl`; row centres `const ROW_C`
  (% of panel height); tracks `topIndex()` each frame; selected row gets class `sel` (dark text).
- **Neon glow that matches the selected petal:** `#trkw` has layered `drop-shadow(... var(--lc))`;
  `--lc` is set each frame from the scene light color (`lightU.uLightColor`).
- **Scene-light tint:** `#trk .tint` (soft-light, masked to panel, color `var(--lc)`).
- Position: `#trkw { bottom:4.5vh }`. Size: `width:min(98vw,448px)`, `aspect-ratio:528/374`.
- **CRT turn-on** entering awake (`@keyframes trkon` `.62s`) and **CRT turn-off** when you
  click the center to zoom into the room (`@keyframes trkoff` `.5s`). State machine in the
  animate loop via `trkState` (`'hidden'|'on'|'off'`) + `#trk.on` / `#trk.off`.

**Fonts** (embedded base64 in the embed): VT323 → family `'vt'` (terminal + tracker);
Special Elite → family `'tw'` (typewriter alt — swap `'vt'`→`'tw'` in the `#term*`/`#trk`
font rules to try it).

---

## Asset re-processing (only if swapping an asset)

Assets are baked into `embed_portal.json` as base64, so normal iteration needs only
`build_final.py` + `embed_portal.json`. To re-process an asset you also need the source
(commit these to a `src/` folder if you'll iterate on art):
- `src_xbox_keyed.png` — the hand-keyed Xbox panel (before row cleaning).
- `vt323.ttf` — VT323 as TTF (woff2→ttf via fontTools) for baking text into PNGs with PIL.

Image work: PIL + numpy + scipy. Chat uploads flatten PNG alpha→black, so re-snapshot any
uploaded transparent PNG before trusting it; JPEGs upload fine.

---

## DS petal-detail terminals (click a petal)

Clicking the top petal collapses the flower scene (canvas + WMP frame + tracker) while the
rainbow backdrop **persists** (moved to `#bgkeep`, z1, outside `#scene`); a Nintendo-DS skin
then zooms out into view. The two DS screens are **keyed transparent** — an SVG mask on
`#dsbody` punches holes at both screen rects, and `#ds` is transparent, so the rainbow shows
straight through both screens.

- Each screen hosts a glowing petal-color terminal window (`#dswT` top, `#dswB` bottom): neon
  frame + HUD corner brackets (`.dswframe`) + CRT scanlines, glow cast onto the darkened body.
  CRT power-on (`@keyframes dswon`) when the DS settles, power-off (`dswoff`) on back. The back
  transition reverses the forward (windows off → DS zoom out → flower on), with the flower
  onset overlapped so there's no static dead frame.
- Per-petal color = `COLS[clickIdx]` set as `--dc`. Body darkened by `#dsdark` (40% black) over
  the tuned `#dstint` multiply so the glow reads; glow reach = the `var(--dc)` box-shadow layers
  on `.dswin`. Screen rects (as % of the 736×1308 skin) live in `#dswT`/`#dswB` and the mask path.

### ⭐ THE CLAUDE CODE SEAM (data/API wiring)

All terminal content is data-driven from the **`CATS`** array (top of CORE), indexed by petal
(`clickIdx`): `CATS[i] = {cat, top:{name, rows|calc|checks, tap|btn|act|streak…}, bot:{…}}`.
Each screen renders via `dsSeg(seg, side, i)` → `dsFill(i)`.

Interactions are wired **front-end only** today, with in-session state in **`dsState` / `dsSt(i)`**
(`{done, checked, trip, streak, logged, promoted}`), driven by one delegated click handler on
`#dsstage`: tap-to-take rows, packing −/+ day calculator (computes units from weekly frequency),
checklist toggles, injectables LOG, pending PROMOTE, topicals streak.

**The wiring task:** point `CATS` reads and `dsState` reads/writes at the real `stack_v5` store
(oral time-decay, schedule-gated injection logging, inventory, streaks) so logging actually
mutates inventory and the schedule reads real dates. Nothing in the render/interaction layer
needs to change — only the data source behind `CATS` / `dsState`.

---

## Still to do (Claude Code: the data/API wiring)
- Bind `CATS` + `dsState` to the real `stack_v5` store (see **THE CLAUDE CODE SEAM**): live
  counts/days-left, calculated packing quantities, log/check/streak persistence.
- Wire Nelson's terminal to the live Claude API.
- Hair routine content for the Topicals top screen (still `TBD`).
