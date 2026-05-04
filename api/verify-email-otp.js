const crypto = require('crypto');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')   return res.status(405).json({ error: 'Method not allowed' });

  const { email, otp, token } = req.body || {};
  if (!email || !otp || !token) {
    return res.status(400).json({ error: 'email, otp, and token are required' });
  }

  const secret = process.env.OTP_SECRET || 'synergistic-ai-otp-fallback';

  /* ── Parse token ── */
  const parts = token.split('|');
  if (parts.length !== 2) return res.status(400).json({ error: 'Invalid token format' });

  const [timestamp, receivedSig] = parts;

  /* ── Check expiry (10 minutes) ── */
  const age = Date.now() - parseInt(timestamp, 10);
  if (isNaN(age) || age > 10 * 60 * 1000) {
    return res.status(400).json({ error: 'Code has expired. Please request a new one.' });
  }

  /* ── Recompute HMAC and compare ── */
  const expectedSig = crypto.createHmac('sha256', secret)
                            .update(`${email}|${otp}|${timestamp}`)
                            .digest('hex');

  /* Constant-time comparison to prevent timing attacks */
  let match = false;
  try {
    match = crypto.timingSafeEqual(
      Buffer.from(receivedSig, 'hex'),
      Buffer.from(expectedSig, 'hex')
    );
  } catch (e) {
    match = false;
  }

  if (!match) {
    return res.status(400).json({ error: 'Invalid code. Please check and try again.' });
  }

  return res.status(200).json({ success: true });
};
