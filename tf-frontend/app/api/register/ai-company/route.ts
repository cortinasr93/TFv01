// app/api/register/ai-company/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Log the incoming request data
    console.log('Registration request received:', body);

    const response = await fetch('http://localhost:8000/api/onboarding/ai-company', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || ''
      },
      body: JSON.stringify({
        company_name: body.companyName,
        email: body.email,
        password: body.password,
        website: body.website,
        billing_email: body.billingEmail || body.email
      })
    });

    if (!response.ok) {
        const text = await response.text();
        let errorMessage;
        try {
            const errorData = JSON.parse(text);
            errorMessage = errorData.detail;
        } catch {
            errorMessage = text;
        }
        throw new Error(errorMessage);
    }

    return NextResponse.json(await response.json());
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Registration failed' },
      { status: 500 }
    );
  }
}