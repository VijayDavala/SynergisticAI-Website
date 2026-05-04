// api/send-otp.js — Twilio Verify: send OTP to phone
// Required Vercel env vars:
//   TWILIO_ACCOUNT_SID  — from twilio.com/console
//   TWILIO_AUTH_TOKEN   — from twilio.com/console
//   TWILIO_VERIFY_SID   — from Verify > Services in Twilio console

const twilio = require('twilio');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', 'https://synergisticaisolns.com');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')    return res.status(405).json({ error: 'Method not allowed' });

  const { phone } = req.body || {};
  if (!phone || phone.replace(/\D/g, '').length < 7) {
    return res.status(400).json({ error: 'Valid phone number required (E.164 format: +15551234567)' });
  }

  const { TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SID } = process.env;
  if (!TWILIO_ACCOUNT_SID || !TWILIO_AUTH_TOKEN || !TWILIO_VERIFY_SID) {
    return res.status(500).json({ error: 'OTP service not configured. Contact admin.' });
  }

  try {
    const client = twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);
    await client.verify.v2
      .services(TWILIO_VERIFY_SID)
      .verifications.create({ to: phone, channel: 'sms' });

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('Twilio send-otp error:', err.message);
    return res.status(500).json({ error: err.message });
  }
};
