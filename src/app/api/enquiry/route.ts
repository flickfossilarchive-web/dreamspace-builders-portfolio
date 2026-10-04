import { NextResponse } from 'next/server';
import { z } from 'zod';

export const runtime = 'nodejs';

const RESEND_REQUEST_TIMEOUT_MS = 10_000;

const enquirySchema = z.object({
  name: z.string().trim().min(2).max(120),
  email: z.string().trim().email().max(254),
  phone: z.string().trim().regex(/^\d{10}$/),
  subject: z.string().trim().min(5).max(160),
  message: z.string().trim().min(10).max(5000),
});

function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  })[char] ?? char);
}

export async function POST(request: Request) {
  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ error: 'Email notifications are not configured.' }, { status: 503 });
  }

  const contentLength = Number(request.headers.get('content-length') ?? 0);
  if (contentLength > 12_000) {
    return NextResponse.json({ error: 'Enquiry is too large.' }, { status: 413 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid request.' }, { status: 400 });
  }

  const parsed = enquirySchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Please check the enquiry details and try again.' }, { status: 400 });
  }

  const { name, email, phone, subject, message } = parsed.data;
  const safeSubject = subject.replace(/[\r\n]+/g, ' ').slice(0, 160);
  const details = [
    ['Name', name],
    ['Email', email],
    ['Phone', phone],
    ['Enquiry', safeSubject],
    ['Project details', message],
  ] as const;

  const html = `<h2>New project enquiry</h2><table cellpadding="8" cellspacing="0" style="border-collapse:collapse">${details.map(([label, value]) => `<tr><th align="left" valign="top">${escapeHtml(label)}</th><td>${escapeHtml(value).replace(/\n/g, '<br>')}</td></tr>`).join('')}</table>`;
  const text = details.map(([label, value]) => `${label}:\n${value}`).join('\n\n');

  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Dreamspace Builders <website@dreamspacebuilders12.com>',
        to: ['Dreamspacebuilders12@gmail.com'],
        reply_to: email,
        subject: `New website enquiry: ${safeSubject}`,
        html,
        text,
      }),
      signal: AbortSignal.timeout(RESEND_REQUEST_TIMEOUT_MS),
    });

    if (!response.ok) {
      const result = await response.json().catch(() => ({}));
      console.error('Resend email failed:', response.status, result?.message ?? 'Unknown provider error');
      return NextResponse.json({ error: 'The enquiry was saved, but its email notification could not be sent.' }, { status: 502 });
    }

    return NextResponse.json({ sent: true });
  } catch (error) {
    console.error('Resend request failed:', error instanceof Error ? error.message : 'Unknown error');
    return NextResponse.json({ error: 'The enquiry was saved, but its email notification could not be sent.' }, { status: 502 });
  }
}

