# Synergistic AI Solutions — Website Project Memory
*Last updated: April 2026 | Load this file at the start of every website session*

---

## Company
- **Name**: Synergistic AI Solutions
- **Type**: B2B — Agentic AI, automation, and digital marketing services
- **Owner**: Vijay Davala (aiadventureworld@gmail.com)

---

## Active Working File
```
[Workspace Folder]\website-with-popups\index.html
```
- **Size**: ~508 KB  
- **Status**: CONFIRMED WORKING (April 2026)  
- **Contents**: Original site + all 22 service tile popups + video removed  
- **This is the base for all future work.**

## Original Upload (never modify)
- Path in Linux sandbox: `/sessions/.../uploads/index.html`  
- 2.4 MB (includes embedded base64 video)  
- Always build FROM this, never from a previously-built file

---

## What Is Complete

### Popup System — ALL DONE ✅
22 popups wired up via a single modal (`id="uniModal"`) fed by JavaScript data.

| Section | Count | onclick pattern | CSS class |
|---|---|---|---|
| AI Automation | 10 | `_openPop('ai','01')` … `'10'` | `aia-tile reveal` |
| Digital Marketing | 8 | `_openPop('dm','01')` … `'08'` | `dm-service-item reveal` |
| Synergistic Advantage | 4 | `_openPop('adv','b2b/research/partnership/deployment')` | `industry-card reveal` |

**Popup functions**: `_openPop(type, id)` · `_closeModal(e)` · Escape key listener  
**Popup CSS classes**: `.uni-overlay` `.uni-card` `.uni-close` `.uni-header` `.uni-icon` `.uni-badge` `.uni-title` `.uni-tag` `.uni-desc` `.uni-body` `.uni-label` `.uni-list` `.uni-green` `.uni-use` `.uni-cta`

### Video Removed ✅
Original had ~1.9 MB base64 video in logo modal. Removed — `src=""` on the `<video>` element.  
File reduced from 2.4 MB → 508 KB.

---

## Pending Work

### iOS Touch Fix 🔧 (next task)
**Root cause**: `initFX()` magnetic button effect applies `transform: translate()` on touch (iOS fires synthetic mousemove), but `mouseleave` never fires → transform persists → hit area shifts → all subsequent taps miss.

**Symptoms**: Hamburger non-responsive, "Explore Services" button not tappable, entire site broken on iOS touch.

**Safe fix** — add ONE line inside existing `initFX` IIFE, right before the magnetic button `forEach`:
```javascript
// Around line 4600 in original file, before:
// document.querySelectorAll('.btn-primary,.btn-secondary,.nav-cta,...').forEach(...)
if ('ontouchstart' in window) return;  // ← ADD THIS ONE LINE ONLY
```

Also add to CSS globally:
```css
* { touch-action: manipulation; }
```

**NEVER do these** (they broke everything before):
- Wrap the `(function initFX() {` opening in a conditional
- Change the `})()` closing to anything else
- Modify hamburger JS
- Modify dropdown JS

---

## Build Rules (Critical)

### Always use `json.dumps()` for popup data
```python
import json
POP = { "ai": { "01": { "title": "...", "tagline": "Your brand's home" } } }
pop_json = json.dumps(POP, ensure_ascii=False)
POPUP_JS = f"var _POP = {pop_json};"   # Safe — all strings double-quoted
```
**Never** write JS object literals with single-quoted strings containing apostrophes in a Python heredoc — Python strips the backslash, breaking JavaScript.

### Injection points in the original file
| What | How to find | Method |
|---|---|---|
| CSS | Marker: `</style>\n\n  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2">` | `str.replace(..., count=1)` |
| JS | Last `</script>` | `html.rfind('</script>')` |
| HTML | `</body>` | `str.replace('</body>', POPUP_HTML + '\n</body>', 1)` |

### Video removal
```python
import re
html = re.sub(r'src="data:video/mp4;base64,[A-Za-z0-9+/=]+"', 'src=""', html)
```

### DO NOT TOUCH these original JS functions
```javascript
function showSection(id) { ... }   // Tab navigation — breaks everything if modified
(function initFX() { ... })()      // Visual effects — IIFE must stay intact
```
Only APPEND new code. Never restructure existing blocks.

---

## Verification Checklist (run after every build)
```python
checks = {
    'No video base64':       'data:video/mp4;base64,A' not in html,
    'showSection exists':    'function showSection' in html,
    'initFX exists':         'initFX' in html,
    '_POP (x1)':             html.count('var _POP') == 1,
    '_BADGE (x1)':           html.count('var _BADGE') == 1,
    'AI tiles (10)':         html.count("onclick=\"_openPop('ai'") == 10,
    'DM tiles (8)':          html.count("onclick=\"_openPop('dm'") == 8,
    'Adv cards (4)':         html.count("onclick=\"_openPop('adv'") == 4,
    'Modal HTML':            'id="uniModal"' in html,
    'Scripts balanced':      html.count('<script') == html.count('</script>'),
}
```

---

## Known Session Issues
- `present_files` tool returns "not accessible on user's computer" — does not work in this project's sessions
- `computer://` links are unreliable for this user
- **Workaround**: Tell user to navigate to file in File Explorer and open in browser manually
- New deliverables should be saved to a NEW SUBFOLDER (e.g., `website-with-popups/`) so user can find them clearly

---

## Session History
| Session | Work Done |
|---|---|
| 1–2 | Built full single-page landing page (logo colours, all sections, animations, tabs, Supabase contact form) |
| 3 | Fixed logo (base64 embed), iOS hamburger attempts, added AI Automation popups |
| 4 | Added DM + Advantage popups; iOS touch fix attempt BROKE everything (initFX restructure); reverted |
| 5 | Found apostrophe/json.dumps bug; clean rebuild; confirmed working on desktop |

## Start of Next Session
1. Read this file first
2. Working file: `website-with-popups/index.html`
3. Next task: iOS touch fix (safe approach above)
4. Build using Python script pattern from `/tmp/build_v2.py`
