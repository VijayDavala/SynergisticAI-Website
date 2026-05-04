const crypto = require('crypto');
const https  = require('https');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')   return res.status(405).json({ error: 'Method not allowed' });

  const { email } = req.body || {};
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'Valid email is required' });
  }

  /* ── Generate OTP ── */
  const otp       = String(Math.floor(100000 + Math.random() * 900000));
  const timestamp = String(Date.now());
  const secret    = process.env.OTP_SECRET || 'synergistic-ai-otp-fallback';

  /* ── Sign: HMAC-SHA256(email|otp|timestamp) ── */
  const sig   = crypto.createHmac('sha256', secret)
                      .update(`${email}|${otp}|${timestamp}`)
                      .digest('hex');
  const token = `${timestamp}|${sig}`;

  /* ── Send email via Resend ── */
  const RESEND_KEY = process.env.RESEND_API_KEY;
  if (!RESEND_KEY) return res.status(500).json({ error: 'Email service not configured' });

  const emailBody = JSON.stringify({
    from:    'Synergistic AI <onboarding@resend.dev>',
    to:      [email],
    subject: 'Your verification code — Synergistic AI Solutions',
    html: `
      <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#0a0a1a;color:#fff;border-radius:12px;">
        <img src="https://synergisticaisolutions.com/logo.png" alt="Synergistic AI" style="height:48px;margin-bottom:24px;" onerror="this.style.display='none'" />
        <h2 style="color:#00d4d4;margin:0 0 16px;">Email Verification</h2>
        <p style="color:rgba(255,255,255,0.75);margin:0 0 24px;">
          Use the code below to verify your email address on our contact form.
          This code expires in <strong style="color:#fff;">10 minutes</strong>.
        </p>
        <div style="background:rgba(0,212,212,0.1);border:1px solid #00d4d4;border-radius:8px;padding:20px;text-align:center;margin-bottom:24px;">
          <span style="font-size:2.5rem;font-weight:700;letter-spacing:0.4em;color:#00d4d4;">${otp}</span>
        </div>
        <p style="font-size:0.78rem;color:rgba(255,255,255,0.4);margin:0;">
          If you did not request this code, you can safely ignore this email.
        </p>
      </div>
    `
  });

  await new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.resend.com',
      path:     '/emails',
      method:   'POST',
      headers:  {
        'Authorization': `Bearer ${RESEND_KEY}`,
        'Content-Type':  'application/json',
        'Content-Length': Buffer.byteLength(emailBody)
      }
    };
    const reqHttp = https.request(options, (r) => {
      let body = '';
      r.on('data', d => body += d);
      r.on('end', () => {
        if (r.statusCode >= 200 && r.statusCode < 300) resolve(body);
        else reject(new Error(`Resend ${r.statusCode}: ${body}`));
      });
    });
    reqHttp.on('error', reject);
    reqHttp.write(emailBody);
    reqHttp.end();
  });

  return res.status(200).json({ token });
};
