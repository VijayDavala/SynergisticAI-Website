import re, os

with open('/sessions/amazing-brave-rubin/mnt/outputs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ================================================================
# FIX A: HAMBURGER — use pointerdown + direct style manipulation
#         (most reliable on iOS Safari — no class toggling)
# ================================================================

old_hamburger_btn = '''    <button class="hamburger" id="hamburger"
      aria-label="Toggle mobile menu" aria-expanded="false"
      type="button">
      <span></span><span></span><span></span>
    </button>'''

# Keep button the same but confirm it has no onclick
if old_hamburger_btn not in html:
    # Try without type="button"
    html = re.sub(
        r'<button class="hamburger" id="hamburger"[^>]*>(\s*<span></span><span></span><span></span>\s*)</button>',
        '<button class="hamburger" id="hamburger" aria-label="Toggle mobile menu" aria-expanded="false" type="button"><span></span><span></span><span></span></button>',
        html
    )
    print("Fix A-btn: regex replaced hamburger button")
else:
    print("Fix A-btn: hamburger button already correct")

old_ham_js = '''    /* ============ HAMBURGER ============ */
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');

    function _toggleNav() {
      const isOpen = navLinks.classList.toggle('open');
      hamburger.classList.toggle('open', isOpen);
      hamburger.setAttribute('aria-expanded', String(isOpen));
    }

    /* iOS-safe: touchstart + preventDefault blocks the 300ms ghost click.
       The click listener handles mouse users and non-iOS touch browsers.
       _syntheticClick flag ensures only one fires per tap. */
    var _hamburgerTouched = false;
    hamburger.addEventListener('touchstart', function(e) {
      e.preventDefault();
      _hamburgerTouched = true;
      _toggleNav();
    }, { passive: false });
    hamburger.addEventListener('click', function(e) {
      if (_hamburgerTouched) { _hamburgerTouched = false; return; }
      _toggleNav();
    });'''

new_ham_js = '''    /* ============ HAMBURGER ============ */
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    var _navOpen = false;

    /* Direct style manipulation — bypasses all CSS cascade/class issues on iOS.
       pointerdown fires before touch/mouse events and e.preventDefault()
       swallows the entire subsequent event chain (no ghost clicks). */
    function _openNav() {
      _navOpen = true;
      navLinks.style.cssText = [
        'display:flex !important',
        'flex-direction:column',
        'position:fixed',
        'top:var(--nav-height, 80px)',
        'left:0', 'right:0',
        'max-height:70vh',
        'overflow-y:auto',
        '-webkit-overflow-scrolling:touch',
        'background:rgb(6,14,28)',
        'border-bottom:2px solid rgba(0,212,212,0.35)',
        'z-index:1001',
        'visibility:visible',
        'opacity:1',
        'pointer-events:auto'
      ].join(';');
      hamburger.classList.add('open');
      hamburger.setAttribute('aria-expanded', 'true');
    }
    function _closeNav() {
      _navOpen = false;
      navLinks.style.cssText = 'display:none !important;visibility:hidden;opacity:0;pointer-events:none';
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
    }
    function _toggleNav() { if (_navOpen) _closeNav(); else _openNav(); }

    /* Init: hide nav-links on mobile via inline style immediately */
    if (window.innerWidth <= 900) { _closeNav(); }
    window.addEventListener('resize', function() {
      if (window.innerWidth > 900) {
        navLinks.style.cssText = ''; /* let CSS take over on desktop */
        _navOpen = false;
        hamburger.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
      } else if (!_navOpen) {
        _closeNav();
      }
    }, { passive: true });

    /* pointerdown: fires first, preventDefault kills touch+click cascade */
    hamburger.addEventListener('pointerdown', function(e) {
      e.preventDefault();
      e.stopPropagation();
      _toggleNav();
    }, { passive: false });
    /* Fallback for browsers without pointer events */
    hamburger.addEventListener('touchstart', function(e) {
      if (window.PointerEvent) return; /* already handled */
      e.preventDefault();
      _toggleNav();
    }, { passive: false });'''

if old_ham_js in html:
    html = html.replace(old_ham_js, new_ham_js)
    print("Fix A-js: Replaced hamburger JS with pointerdown + direct style")
else:
    print("WARNING: old hamburger JS not found exactly — searching...")
    # Find the hamburger JS section and replace it
    idx_start = html.find('/* ============ HAMBURGER ============ */')
    if idx_start != -1:
        # Find end: next function definition or section
        idx_end = html.find('\n    // Dropdown interaction', idx_start)
        if idx_end != -1:
            html = html[:idx_start] + new_ham_js + '\n' + html[idx_end:]
            print("Fix A-js: Replaced via section search")
        else:
            print("ERROR: Could not find hamburger section end")
    else:
        print("ERROR: Could not find hamburger section start")

# ================================================================
# FIX B: DROPDOWN BLEEDING — force-hide dropdowns on mobile via
#         inline styles immediately on load (belt+suspenders with CSS)
# ================================================================

old_dropdown_fix = '''
    /* ============ FORCE-HIDE DROPDOWNS ON MOBILE ============ */'''

new_dropdown_fix = '''
    /* ============ FORCE-HIDE DROPDOWNS ON MOBILE ============ */'''

if old_dropdown_fix not in html:
    # Find the _hideMobileDropdowns block and replace with improved version
    idx = html.find('function _hideMobileDropdowns()')
    if idx != -1:
        # Find surrounding block
        block_start = html.rfind('/* ============ FORCE-HIDE', 0, idx)
        block_end = html.find('});', idx) 
        block_end = html.find('\n', block_end) + 1
        print(f"Found mobile dropdown block at {block_start}")
    else:
        print("Mobile dropdown block not found — will append")

# Replace/update the _hideMobileDropdowns implementation
old_force_hide = '''    function _hideMobileDropdowns() {
      if (window.innerWidth > 900) return;
      document.querySelectorAll('.dropdown').forEach(function(d) {
        // Only hide dropdowns whose parent nav-item does NOT have .open
        var item = d.closest('.nav-item');
        if (!item || !item.classList.contains('open')) {
          d.style.setProperty('display', 'none', 'important');
        }
      });
    }
    _hideMobileDropdowns();
    window.addEventListener('resize', _hideMobileDropdowns, { passive: true });

    /* When a nav-item gets .open, remove the inline style so CSS can show it */
    document.querySelectorAll('.nav-item').forEach(function(item) {
      var dropdown = item.querySelector('.dropdown');
      if (!dropdown) return;
      var observer = new MutationObserver(function() {
        if (window.innerWidth > 900) return;
        if (item.classList.contains('open')) {
          dropdown.style.removeProperty('display');
        } else {
          dropdown.style.setProperty('display', 'none', 'important');
        }
      });
      observer.observe(item, { attributes: true, attributeFilter: ['class'] });
    });'''

new_force_hide = '''    /* Force all dropdowns hidden on mobile via inline style immediately */
    function _hideMobileDropdowns() {
      if (window.innerWidth > 900) return;
      document.querySelectorAll('.dropdown').forEach(function(d) {
        var item = d.closest('.nav-item');
        if (!item || !item.classList.contains('open')) {
          d.style.cssText = 'display:none !important;visibility:hidden;opacity:0;pointer-events:none';
        }
      });
    }
    _hideMobileDropdowns();
    window.addEventListener('resize', _hideMobileDropdowns, { passive: true });

    /* MutationObserver: show/hide dropdown when .open toggled on nav-item */
    document.querySelectorAll('.nav-item').forEach(function(item) {
      var dropdown = item.querySelector('.dropdown');
      if (!dropdown) return;
      var observer = new MutationObserver(function() {
        if (window.innerWidth > 900) { dropdown.style.cssText = ''; return; }
        if (item.classList.contains('open')) {
          dropdown.style.cssText = [
            'display:block !important',
            'visibility:visible',
            'opacity:1',
            'pointer-events:auto',
            'position:static !important',
            'background:transparent !important',
            'border-left:2px solid var(--teal-bright)',
            'margin-left:28px'
          ].join(';');
        } else {
          dropdown.style.cssText = 'display:none !important;visibility:hidden;opacity:0;pointer-events:none';
        }
      });
      observer.observe(item, { attributes: true, attributeFilter: ['class'] });
    });'''

if old_force_hide in html:
    html = html.replace(old_force_hide, new_force_hide)
    print("Fix B: Updated dropdown force-hide with full inline style approach")
else:
    print("WARNING: old force-hide block not found exactly")
    if '_hideMobileDropdowns' in html:
        print("  -> _hideMobileDropdowns exists, likely already updated differently")

# ================================================================
# FIX C: ADD TILE POPUP DATA — add data-tile attribute to each tile
#         and inject popup HTML + CSS + JS
# ================================================================

tile_data = {
    '01': {
        'title': 'Autonomous AI Agents',
        'icon': '🤖',
        'tagline': 'AI that works while you sleep — 24/7, zero supervision.',
        'what': 'Deploy intelligent agents that receive instructions, make multi-step decisions, and execute complex tasks completely autonomously — no human hand-holding required.',
        'features': [
            'Multi-tool orchestration (web search, CRM, email, APIs)',
            'Self-correcting logic with error recovery',
            'Memory & context retention across sessions',
            'Real-time reporting & audit trails'
        ],
        'results': ['10× productivity increase', '90% reduction in manual tasks', 'Scales without hiring'],
        'usecases': 'Lead research, competitor monitoring, data enrichment, automated reporting, client onboarding sequences.',
        'accent': '#00d4d4'
    },
    '02': {
        'title': 'Workflow Automation',
        'icon': '⚡',
        'tagline': 'Set it once. Run forever. Zero inputs needed.',
        'what': 'Build automated workflows triggered by time, events, or data changes — from daily report generation to instant invoice delivery and client onboarding. Quiet, fast, always on.',
        'features': [
            'Time-based & event-driven triggers',
            'Multi-system integrations (CRM, email, Slack, ERP)',
            'Conditional branching & smart routing',
            'Built-in error handling & retry logic'
        ],
        'results': ['Save 40+ hours per week', 'Zero manual errors', 'Runs 24/7 without oversight'],
        'usecases': 'Invoice generation, report distribution, client onboarding, CRM updates, approval workflows.',
        'accent': '#39ff14'
    },
    '03': {
        'title': 'Business Process Automation',
        'icon': '🏭',
        'tagline': 'Eliminate back-office bottlenecks — permanently.',
        'what': 'Automate your most repetitive, error-prone back-office operations — payroll, HR workflows, invoice processing, and data entry — so your team focuses on work that actually grows the business.',
        'features': [
            'End-to-end HR & payroll automation',
            'Intelligent invoice processing & reconciliation',
            'Automated compliance checks & audit logs',
            'ERP & accounting system integration'
        ],
        'results': ['90% error reduction', '60% cost savings on operations', 'Full compliance & audit ready'],
        'usecases': 'Employee onboarding, purchase order processing, inventory management, accounts payable, expense approvals.',
        'accent': '#ff00cc'
    },
    '04': {
        'title': 'AI Voice Agents',
        'icon': '🎙️',
        'tagline': 'Your best sales rep — available 24/7, at infinite scale.',
        'what': 'Deploy AI voice agents that handle inbound calls and outbound outreach — qualifying leads, booking appointments, sending reminders, and following up — all sounding natural and on-brand.',
        'features': [
            'Human-like conversational AI (no robotic voices)',
            'Inbound support + outbound lead qualification',
            'CRM integration for instant data capture',
            'Custom scripts, personas & escalation rules'
        ],
        'results': ['Handle 1,000s of calls simultaneously', '3× faster lead response time', '24/7 coverage, zero agent fatigue'],
        'usecases': 'Lead qualification, appointment booking, payment reminders, customer support, post-sale follow-ups.',
        'accent': '#00d4d4'
    },
    '05': {
        'title': 'Social Media AI Systems',
        'icon': '📱',
        'tagline': 'Full social media presence — on autopilot.',
        'what': 'AI manages your entire social media operation — generating on-brand content, scheduling posts, responding to comments, and proactively reaching out to prospects across LinkedIn, Instagram, X, and more.',
        'features': [
            'AI-generated content tailored to your brand voice',
            'Automated scheduling across all platforms',
            'Engagement automation (comments, DMs, replies)',
            'Analytics-driven content optimisation'
        ],
        'results': ['10× content output', 'Consistent daily presence', 'Warm leads from DM outreach'],
        'usecases': 'LinkedIn B2B outreach, Instagram growth, Twitter/X engagement, YouTube content, community management.',
        'accent': '#39ff14'
    },
    '06': {
        'title': 'Customer Service Automation',
        'icon': '💬',
        'tagline': 'Instant answers. Happy customers. Zero wait time.',
        'what': 'Deploy AI that handles customer inquiries, routes support tickets, resolves common issues instantly, and escalates only the complex cases to your human team — delivering faster service at a fraction of the cost.',
        'features': [
            'AI chatbot across web, email & WhatsApp',
            'Intelligent ticket routing & prioritisation',
            'Knowledge base integration for accurate answers',
            'Sentiment detection & smart escalation'
        ],
        'results': ['80% of queries resolved without human', '<30 second average response time', '4.8★ average CSAT improvement'],
        'usecases': 'FAQ handling, order tracking, refund processing, technical support, appointment rescheduling.',
        'accent': '#ff00cc'
    },
    '07': {
        'title': 'Marketing Automation',
        'icon': '📈',
        'tagline': 'Personalised at scale. Convert more, spend less.',
        'what': 'Automate the full marketing funnel — from lead capture and nurture sequences to audience segmentation, A/B testing, and campaign reporting — with AI that tailors every touchpoint to individual behaviour.',
        'features': [
            'Behaviour-triggered email & SMS sequences',
            'Dynamic audience segmentation & scoring',
            'Multi-channel campaign orchestration',
            'Real-time A/B testing & optimisation'
        ],
        'results': ['3× higher email open rates', '5× ROI on campaigns', '60% reduction in CPL'],
        'usecases': 'Lead nurture sequences, abandoned cart recovery, re-engagement campaigns, event marketing, upsell flows.',
        'accent': '#7b2fff'
    },
    '08': {
        'title': 'Document Processing',
        'icon': '📄',
        'tagline': 'From hours to seconds — documents processed at AI speed.',
        'what': 'Eliminate manual document handling with AI that extracts, classifies, validates, and routes contracts, invoices, and forms automatically — with human-level accuracy at machine speed.',
        'features': [
            'AI-powered OCR & intelligent data extraction',
            'Automated classification & document routing',
            'Contract review & clause extraction',
            'ERP / accounting system sync'
        ],
        'results': ['95% accuracy on data extraction', '10× faster processing', 'Zero manual keying errors'],
        'usecases': 'Invoice processing, contract management, KYC/onboarding forms, purchase orders, compliance documents.',
        'accent': '#00d4d4'
    },
    '09': {
        'title': 'Smart CRM Integration',
        'icon': '🎯',
        'tagline': 'No lead slips. Every deal tracked. Revenue protected.',
        'what': 'Connect AI directly to your CRM to automate lead scoring, follow-up sequencing, pipeline updates, and deal tracking — so your sales team focuses on closing, not data entry.',
        'features': [
            'AI-powered lead scoring & prioritisation',
            'Automated follow-up sequences by behaviour',
            'Real-time pipeline updates & deal alerts',
            'Revenue forecasting & churn prediction'
        ],
        'results': ['40% increase in pipeline velocity', '2× higher close rates', '100% follow-up compliance'],
        'usecases': 'HubSpot, Salesforce, GHL automation; lead routing; deal stage progression; win/loss analysis.',
        'accent': '#39ff14'
    },
    '10': {
        'title': 'Predictive Process Automation',
        'icon': '🔮',
        'tagline': 'Stay ahead of problems before they happen.',
        'what': 'Deploy machine learning models that forecast demand, detect anomalies, and trigger automated actions before issues arise — keeping your operations proactive, not reactive.',
        'features': [
            'Demand forecasting & inventory optimisation',
            'Real-time anomaly detection & alerts',
            'Automated corrective action workflows',
            'Custom ML model development & deployment'
        ],
        'results': ['30% reduction in operational downtime', '25% inventory cost savings', 'Early warning system for risks'],
        'usecases': 'Supply chain optimisation, fraud detection, predictive maintenance, churn prediction, dynamic pricing.',
        'accent': '#ff00cc'
    }
}

# Add data-tile-id to each tile div
for tile_num, data in tile_data.items():
    old_tile_start = f'<div class="aia-tile reveal" data-accent="{data["accent"].replace("#00d4d4","teal").replace("#39ff14","green").replace("#ff00cc","pink").replace("#7b2fff","purple")}">\n            <span class="aia-tile-num">{tile_num}</span>'
    # Find the tile arrow div and add onclick
    old_arrow = f'<span class="aia-tile-num">{tile_num}</span>'
    # Add data-tile attribute to the outer div
    # Find the exact tile
    pattern = f'(<div class="aia-tile reveal"[^>]*>\\s*<span class="aia-tile-num">{tile_num}</span>)'
    replacement = f'<div class="aia-tile reveal" data-tile="{tile_num}" style="cursor:pointer" onclick="_openTilePopup(\'{tile_num}\')">\n            <span class="aia-tile-num">{tile_num}</span>'
    # Remove the wrapper div tag and replace
    html = re.sub(
        f'<div class="aia-tile reveal"([^>]*)>\\s*<span class="aia-tile-num">{tile_num}</span>',
        f'<div class="aia-tile reveal"\\1 data-tile="{tile_num}" style="cursor:pointer" onclick="_openTilePopup(\'{tile_num}\')">\n            <span class="aia-tile-num">{tile_num}</span>',
        html
    )

print("Fix C: Added onclick to all 10 tiles")

# Build popup HTML
popup_html = '''
  <!-- ===== AI TILE POPUP MODAL ===== -->
  <div id="aiTileModal" class="aitm-overlay" role="dialog" aria-modal="true" aria-hidden="true" onclick="_closeTilePopup(event)">
    <div class="aitm-card" onclick="event.stopPropagation()">
      <button class="aitm-close" onclick="_closeTilePopup()" aria-label="Close">&times;</button>
      <div class="aitm-header">
        <div class="aitm-icon" id="aitm-icon"></div>
        <div>
          <div class="aitm-num" id="aitm-num"></div>
          <h3 class="aitm-title" id="aitm-title"></h3>
          <p class="aitm-tagline" id="aitm-tagline"></p>
        </div>
      </div>
      <p class="aitm-what" id="aitm-what"></p>
      <div class="aitm-body">
        <div class="aitm-col">
          <div class="aitm-section-label">⚙️ Key Capabilities</div>
          <ul class="aitm-features" id="aitm-features"></ul>
        </div>
        <div class="aitm-col">
          <div class="aitm-section-label">📊 Results You Can Expect</div>
          <ul class="aitm-results" id="aitm-results"></ul>
          <div class="aitm-section-label" style="margin-top:18px">🎯 Use Cases</div>
          <p class="aitm-usecases" id="aitm-usecases"></p>
        </div>
      </div>
      <div class="aitm-footer">
        <button class="aitm-cta" onclick="showSection('crm-contact');_closeTilePopup()">Get a Free Automation Audit →</button>
      </div>
    </div>
  </div>'''

# Insert before closing body tag
html = html.replace('</body>', popup_html + '\n</body>', 1)
print("Fix C: Inserted popup modal HTML")

# Build popup CSS
popup_css = '''
    /* ===== AI TILE POPUP STYLES ===== */
    .aitm-overlay {
      display: none; position: fixed; inset: 0; z-index: 9999;
      background: rgba(0,0,0,0.82); backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      align-items: center; justify-content: center;
      padding: 16px; box-sizing: border-box;
    }
    .aitm-overlay.open { display: flex; }
    .aitm-card {
      background: linear-gradient(145deg, rgba(6,18,36,0.98) 0%, rgba(8,26,52,0.98) 100%);
      border: 1px solid rgba(0,212,212,0.3);
      border-radius: 16px;
      max-width: 760px; width: 100%;
      max-height: 88vh; overflow-y: auto;
      padding: 36px 40px 32px;
      position: relative;
      box-shadow: 0 0 60px rgba(0,212,212,0.15), 0 24px 80px rgba(0,0,0,0.6);
      animation: aitm-in 0.28s cubic-bezier(0.22,1,0.36,1);
    }
    @keyframes aitm-in {
      from { opacity:0; transform: scale(0.93) translateY(20px); }
      to   { opacity:1; transform: scale(1) translateY(0); }
    }
    .aitm-close {
      position: absolute; top: 16px; right: 20px;
      background: rgba(0,212,212,0.12); border: 1px solid rgba(0,212,212,0.25);
      color: var(--teal-bright); font-size: 1.5rem; line-height: 1;
      width: 36px; height: 36px; border-radius: 50%;
      cursor: pointer; display: flex; align-items: center; justify-content: center;
      transition: background 0.2s;
    }
    .aitm-close:hover { background: rgba(0,212,212,0.25); }
    .aitm-header {
      display: flex; align-items: flex-start; gap: 20px; margin-bottom: 22px;
    }
    .aitm-icon {
      font-size: 2.4rem; line-height: 1;
      background: rgba(0,212,212,0.1); border: 1px solid rgba(0,212,212,0.25);
      border-radius: 14px; width: 64px; height: 64px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
    }
    .aitm-num {
      font-family: 'Orbitron', sans-serif; font-size: 0.65rem;
      letter-spacing: 3px; color: var(--teal-bright); opacity: 0.7;
      margin-bottom: 4px;
    }
    .aitm-title {
      font-family: 'Orbitron', sans-serif; font-size: 1.15rem;
      font-weight: 700; color: var(--white); margin: 0 0 6px; letter-spacing: 1px;
    }
    .aitm-tagline {
      font-family: 'Rajdhani', sans-serif; font-size: 0.95rem;
      color: var(--teal-bright); margin: 0; letter-spacing: 0.5px;
    }
    .aitm-what {
      font-family: 'Rajdhani', sans-serif; font-size: 0.98rem; line-height: 1.65;
      color: rgba(200,230,255,0.85); margin: 0 0 24px;
      padding-bottom: 20px; border-bottom: 1px solid rgba(0,212,212,0.12);
    }
    .aitm-body { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-bottom: 28px; }
    .aitm-section-label {
      font-family: 'Orbitron', sans-serif; font-size: 0.6rem;
      letter-spacing: 2px; color: var(--teal-bright); text-transform: uppercase;
      margin-bottom: 12px; opacity: 0.9;
    }
    .aitm-features, .aitm-results {
      list-style: none; padding: 0; margin: 0;
    }
    .aitm-features li, .aitm-results li {
      font-family: 'Rajdhani', sans-serif; font-size: 0.9rem;
      color: rgba(200,230,255,0.8); padding: 7px 0;
      border-bottom: 1px solid rgba(0,212,212,0.08);
      display: flex; align-items: flex-start; gap: 8px; line-height: 1.4;
    }
    .aitm-features li::before { content: "▸"; color: var(--teal-bright); flex-shrink: 0; }
    .aitm-results li::before { content: "✓"; color: #39ff14; flex-shrink: 0; font-weight: 700; }
    .aitm-usecases {
      font-family: 'Rajdhani', sans-serif; font-size: 0.88rem;
      color: rgba(180,210,240,0.7); line-height: 1.6; margin: 0;
    }
    .aitm-footer { text-align: center; }
    .aitm-cta {
      background: linear-gradient(135deg, var(--teal-bright), var(--neon-green));
      border: none; color: var(--teal-deep); font-family: 'Orbitron', sans-serif;
      font-size: 0.72rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
      padding: 15px 36px; cursor: pointer;
      clip-path: polygon(12px 0%,100% 0%,calc(100% - 12px) 100%,0% 100%);
      transition: opacity 0.2s; touch-action: manipulation;
    }
    .aitm-cta:hover { opacity: 0.88; }
    @media (max-width: 600px) {
      .aitm-card { padding: 24px 20px 24px; }
      .aitm-body { grid-template-columns: 1fr; gap: 20px; }
      .aitm-title { font-size: 0.95rem; }
    }'''

# Insert before closing </style>
html = html.replace('  </style>\n', popup_css + '\n  </style>\n', 1)
print("Fix C: Inserted popup CSS")

# Build popup JS data + logic
import json
tile_data_js = json.dumps({
    k: {
        'title': v['title'], 'icon': v['icon'], 'tagline': v['tagline'],
        'what': v['what'], 'features': v['features'],
        'results': v['results'], 'usecases': v['usecases'], 'accent': v['accent']
    } for k, v in tile_data.items()
}, ensure_ascii=False, indent=2)

popup_js = f'''
    /* ===== AI TILE POPUP ===== */
    var _TILE_DATA = {tile_data_js};
    function _openTilePopup(id) {{
      var d = _TILE_DATA[id];
      if (!d) return;
      document.getElementById('aitm-icon').textContent = d.icon;
      document.getElementById('aitm-num').textContent = 'SERVICE ' + id;
      document.getElementById('aitm-title').textContent = d.title;
      document.getElementById('aitm-tagline').textContent = d.tagline;
      document.getElementById('aitm-what').textContent = d.what;
      var card = document.querySelector('.aitm-card');
      card.style.borderColor = d.accent + '55';
      card.style.boxShadow = '0 0 60px ' + d.accent + '22, 0 24px 80px rgba(0,0,0,0.6)';
      document.getElementById('aitm-icon').style.borderColor = d.accent + '66';
      document.getElementById('aitm-icon').style.background = d.accent + '18';
      document.getElementById('aitm-tagline').style.color = d.accent;
      var fl = document.getElementById('aitm-features');
      fl.innerHTML = d.features.map(function(f){{return '<li>'+f+'</li>';}}).join('');
      var rl = document.getElementById('aitm-results');
      rl.innerHTML = d.results.map(function(r){{return '<li>'+r+'</li>';}}).join('');
      document.getElementById('aitm-usecases').textContent = d.usecases;
      var modal = document.getElementById('aiTileModal');
      modal.classList.add('open');
      modal.setAttribute('aria-hidden','false');
      document.body.style.overflow = 'hidden';
    }}
    function _closeTilePopup(e) {{
      if (e && e.target !== document.getElementById('aiTileModal')) return;
      var modal = document.getElementById('aiTileModal');
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden','true');
      document.body.style.overflow = '';
    }}
    /* Close on Escape */
    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') _closeTilePopup();
    }});'''

# Insert popup JS before closing </script>
script_end = html.rfind('</script>')
html = html[:script_end] + popup_js + '\n  ' + html[script_end:]
print("Fix C: Inserted popup JS")

# ================================================================
# WRITE OUTPUT
# ================================================================
with open('/sessions/amazing-brave-rubin/mnt/outputs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize('/sessions/amazing-brave-rubin/mnt/outputs/index.html') / 1024
print(f"\nDone. Output: {size_kb:.0f} KB")
