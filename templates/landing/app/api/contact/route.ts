import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const endpoint = process.env.CONTACT_ENDPOINT
  if (!endpoint) {
    return NextResponse.json(
      { error: 'CONTACT_ENDPOINT is not configured' },
      { status: 500 },
    )
  }

  try {
    const body = await req.json()
    const upstream = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!upstream.ok) {
      return NextResponse.json({ error: 'Upstream service error' }, { status: 502 })
    }
    return NextResponse.json({ ok: true })
  } catch {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
