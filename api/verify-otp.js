// api/verify-otp.js — Twilio Verify: check OTP entered by user
// Uses the same TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SID env vars

const twilio = require('twilio');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', 'https://synergisticaisolns.com');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')    return res.status(405).json({ error: 'Method not allowed' });

  const { phone, code } = req.body || {};
  if (!phone || !code || String(code).length !== 6) {
    return res.status(400).json({ error: 'Phone and 6-digit code required' });
  }

  const { TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SID } = process.env;
  if (!TWILIO_ACCOUNT_SID || !TWILIO_AUTH_TOKEN || !TWILIO_VERIFY_SID) {
    return res.status(500).json({ error: 'OTP service not configured. Contact admin.' });
  }

  try {
    const client = twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);
    const result = await client.verify.v2
      .services(TWILIO_VERIFY_SID)
      .verificationChecks.create({ to: phone, code: String(code) });

    return res.status(200).json({ approved: result.status === 'approved' });
  } catch (err) {
    console.error('Twilio verify-otp error:', err.message);
    return res.status(500).json({ error: err.message });
  }
};
