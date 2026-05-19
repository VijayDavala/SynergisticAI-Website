# Synergistic AI Solutions — Website Project Memory
*Last updated: May 2026 | Load this file at the start of every website session*

---

## Company
- **Name**: Synergistic AI Solutions
- **Type**: B2B — Agentic AI, automation, and digital marketing services
- **Owner**: Vijay Davala (aiadventureworld@gmail.com)

---

## Active Working File
```
[Workspace Folder]\website-mobile-test\index.html
```
- **Size**: ~537 KB
- **Status**: CONFIRMED WORKING in production (May 2026) — iOS Safari ✅ Desktop ✅
- **Contents**: Full site + all 22 popups + video removed + iOS fixes + Meta Pixel + LinkedIn Tag + favicons + social links + 30s callback popup + Supabase REST API lead capture
- **This is the base for all future work.**
- **GitHub**: https://github.com/VijayDavala/SynergisticAI-Website (branch: `main`)
- **Production URL**: Deployed via Vercel (auto-deploys on push to `main`)

## Original Upload (never modify)
- Path in Linux sandbox: `/sessions/.../uploads/index.html`
- 2.4 MB (includes embedded base64 video)
- Always build FROM the working file above, never from the original upload

---

## What Is Complete ✅

### Popup System — ALL DONE ✅
22 popups wired up via a single modal (`id="uniModal"`) fed by JavaScript data.

| Section | Count | onclick pattern | CSS class |
|---|---|---|---|
| AI Automation | 10 | `_openPop('ai','01')` … `'10'` | `aia-tile reveal` |
| Digital Marketing | 8 | `_openPop('dm','01')` … `'08'` | `dm-service-item reveal` |
| Synergistic Advantage | 4 | `_openPop('adv','b2b/research/partnership/deployment')` | `industry-card reveal` |

**Popup functions**: `_openPop(type, id)` · `_closeModal(e)` · Escape key listener
**Popup CSS classes**: `.uni-overlay` `.uni-card` `.uni-close` `.uni-header` `.uni-icon` `.uni-badge` `.uni-title` `.uni-tag` `.uni-desc` `.uni-body` `.uni-label` `.uni-list` `.uni-green` `.uni-use` `.uni-cta`

### 30-Second Callback Popup ✅ SHIPPED
- Triggers 30 seconds after page load (CSS animation dual-trigger + JS setTimeout)
- `sessionStorage('cbShown')` prevents repeat in same browser session
- Fields: First Name, Last Name, Email, Phone, Service of Interest
- Sends `company: 'Not provided'` as fallback (table requires NOT NULL)
- On submit → saves to Supabase `leads` table → redirects to `/thank-you`
- Overlay click + Escape key closes popup
- CSS classes: `#cb-overlay`, `#cb-card`, `#cb-form`, `#cb-submit`, `#cb-err`

### Supabase Lead Capture ✅ WORKING
- **REST endpoint**: `https://pduemybwotfrtznpvyii.supabase.co/rest/v1/leads`
- **ANON KEY**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBkdWVteWJ3b3RmcnR6bnB2eWlpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyMzIxOTUsImV4cCI6MjA4OTgwODE5NX0.XuBxihlukn9IEes1ty5VTonF-sYJqHfAz3NRx7P6Ecg`
- Headers required: `apikey`, `Authorization: Bearer <ANON_KEY>`, `Content-Type: application/json`, `Prefer: return=minimal`
- **Main form** (`submitLeadForm()`): sends first_name, last_name, business_email, company, phone_country_code, phone_number, service_of_interest, message, source='website_contact_form', status='new'
- **Popup form** (`submitCBForm()`): sends first_name, last_name, business_email, company='Not provided', phone_number, phone_country_code='+1', service_of_interest, source='popup_callback_form', status='new'
- Both forms redirect to `/thank-you` on completion (regardless of Supabase response)

### Supabase `leads` Table Schema
| Column | Type | Nullable | Default |
|---|---|---|---|
| id | bigint | NO | nextval (auto) |
| first_name | text | NO | — |
| last_name | text | NO | — |
| business_email | text | NO | — |
| phone_country_code | text | NO | '+1' |
| phone_number | text | NO | — |
| phone_full | text | YES | — |
| company | text | YES | — (made nullable May 2026) |
| service_of_interest | text | YES | — |
| message | text | YES | — |
| source | text | NO | 'website_contact_form' |
| status | text | YES | 'new' (added May 2026) |
| created_at | timestamptz | YES | now() (added May 2026) |

**RLS Policies on `leads`**: `public_can_insert` (INSERT, {public}), `allow_anon_insert` (INSERT, {anon}), `authenticated_select_leads`, `authenticated_update_leads`, `authenticated_delete_leads`

### Thank You Page ✅ SHIPPED
- File: `thank-you.html` (repo root)
- Route: `/thank-you` → served via `vercel.json` explicit rewrite
- Fires `fbq('track', 'Lead')` + `window.lintrk('track', { conversion_id: 25674076 })`
- Auto-redirects to `/` after 10 seconds
- Dark space theme matching site brand

### vercel.json ✅ FIXED
```json
{
  "rewrites": [
    { "source": "/thank-you", "destination": "/thank-you.html" },
    { "source": "/((?!.*\\.).*)", "destination": "/index.html" }
  ]
}
```
**Critical**: `/thank-you` route MUST be before the catch-all — the catch-all intercepts any path without a dot.

### Meta Pixel ✅ SHIPPED
- Pixel ID: `1472196291369040`
- In `<head>` of `index.html` and `thank-you.html`
- `fbq('track', 'Lead')` fires on: main form success, popup form success, thank-you page load

### LinkedIn Insight Tag ✅ SHIPPED
- Partner ID: `9270068`
- Conversion ID: `25674076`
- In `<head>` + `<body>` of `index.html` and `thank-you.html`
- `window.lintrk('track', { conversion_id: 25674076 })` fires on: main form success, popup form success, thank-you page load

### Favicon ✅ SHIPPED
- `favicon.ico`, `favicon-192.png`, `favicon-512.png` — generated from `logo.jpg` using Pillow
- Linked in `<head>` of `index.html` and `thank-you.html`

### Social Media Links ✅ SHIPPED
Order in footer: LinkedIn → Instagram → Facebook → YouTube → X
- LinkedIn: https://www.linkedin.com/company/synergistic-ai-solutions
- Instagram: https://www.instagram.com/synergistic_ai_solutions/
- Facebook: https://www.facebook.com/profile.php?id=61575870813809
- YouTube: `href="#"` (placeholder — URL not yet provided)
- X: `href="#"` (placeholder — URL not yet provided)

### SEO H1/H2 Fix ✅ SHIPPED
- Site had 4× `<h1>` tags — reduced to 1× `<h1>` + 3× `<h2>` for correct heading hierarchy

### Video Removed ✅
- Original had ~1.9 MB base64 video. Removed (`src=""`). File reduced from 2.4 MB → ~537 KB.

### iOS / Desktop Fixes ✅ SHIPPED
- Touch guard: `window.matchMedia('(pointer: coarse)').matches` at top of `initFX()`
- Hamburger: `touchend` primary + click fallback
- `backdrop-filter: none` at source to prevent iOS touch interception
- Cursor fix: `cursor: auto` override for coarse-pointer devices

### hCaptcha — REMOVED ✅
- Was added then removed. No bot protection currently active on the form.

---

## Pending Work

### ⚠️ YouTube & X Social Links
- Both currently have `href="#"` placeholders
- Provide URLs when ready to update

### ⚠️ Bot Protection (Optional)
- hCaptcha was removed because it required a paid plan
- Consider Cloudflare Turnstile (free forever) as a future replacement

---

## Build Rules (Critical)

### Always use `json.dumps()` for popup data
```python
import json
POP = { "ai": { "01": { "title": "...", "tagline": "Your brand's home" } } }
pop_json = json.dumps(POP, ensure_ascii=False)
POPUP_JS = f"var _POP = {pop_json};"   # Safe — all strings double-quoted
```
**Never** write JS object literals with single-quoted strings containing apostrophes in a Python heredoc.

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
- `present_files` tool returns "not accessible on user's computer" — does not work
- `computer://` links are unreliable for this user
- **Workaround**: Tell user to navigate to file in File Explorer and open in browser manually
- Sandbox cannot reach Supabase or external HTTPS — test API calls must be done from browser devtools

---

## Testing Method — CRITICAL
- **WhatsApp file sharing does NOT work** — WhatsApp in-app viewer doesn't execute JavaScript
- **Only valid iOS test**: Deploy to Vercel → open URL in Safari on iPhone
- Preview branch: `mobile-fix-preview` → Vercel preview URL
- Production branch: `main` → auto-deploys to production

---

## Session History
| Session | Work Done |
|---|---|
| 1–2 | Built full single-page landing page (logo colours, all sections, animations, tabs, Supabase contact form) |
| 3 | Fixed logo (base64 embed), iOS hamburger attempts, added AI Automation popups |
| 4 | Added DM + Advantage popups; iOS touch fix attempt BROKE everything; reverted |
| 5 | Found apostrophe/json.dumps bug; clean rebuild; confirmed working on desktop |
| 6–7 | iOS full fix (touch guard, backdrop-filter, hamburger touchend), footer fix, cursor fix, hCaptcha — shipped |
| 8–9 | Removed hCaptcha, added email OTP (Resend) then removed OTP; H1→H2 SEO fix; Meta Pixel; LinkedIn tag; favicons; social links; vercel.json fix for /thank-you; thank-you page created |
| 10 | 30s callback popup (CSS+JS dual trigger, sessionStorage suppression); Supabase REST API for both forms; fixed payload + auth headers; fixed company NOT NULL constraint; all confirmed working ✅ |

## Start of Next Session
1. Read this file first
2. Working file: `website-mobile-test/index.html`
3. Site is fully production-ready — all forms save to Supabase, analytics firing correctly
4. Only pending items: YouTube/X social links, optional bot protection
