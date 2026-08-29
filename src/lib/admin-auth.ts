import { createHmac, timingSafeEqual } from 'crypto';

export const ADMIN_COOKIE_NAME = 'dreamspace_admin_session';
const SESSION_TTL_SECONDS = 60 * 60 * 12;

function secret() {
  return process.env.ADMIN_SESSION_SECRET || process.env.ADMIN_PASSWORD || process.env.NEXT_PUBLIC_ADMIN_PASSWORD || 'change-this-secret';
}

export function getAdminCredentials() {
  return {
    username: process.env.ADMIN_USERNAME || process.env.NEXT_PUBLIC_ADMIN_USERNAME || '',
    password: process.env.ADMIN_PASSWORD || process.env.NEXT_PUBLIC_ADMIN_PASSWORD || '',
  };
}

function sign(payload: string) {
  return createHmac('sha256', secret()).update(payload).digest('hex');
}

export function createAdminSession(username: string) {
  const expiresAt = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  const payload = `${username}.${expiresAt}`;
  return `${payload}.${sign(payload)}`;
}

export function verifyAdminSession(token: string | undefined) {
  if (!token) return false;
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  const [username, expiresAtText, providedSignature] = parts;
  const expiresAt = Number(expiresAtText);
  if (!username || !Number.isFinite(expiresAt) || expiresAt < Math.floor(Date.now() / 1000)) return false;

  const expectedSignature = sign(`${username}.${expiresAtText}`);
  const provided = Buffer.from(providedSignature, 'utf8');
  const expected = Buffer.from(expectedSignature, 'utf8');
  return provided.length === expected.length && timingSafeEqual(provided, expected);
}
