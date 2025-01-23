// tf-frontend/app/api/register/ai-company/route.ts

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
        name: body.name,
        company_name: body.companyName,
        email: body.email,
        // password: body.password,
        website: body.website,
        use_cases: body.useCases,
        message: body.message,
        onboarding_status: 'waitlist'
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

    const data = await response.json();

    // Create response with the session cookie
    const nextResponse = NextResponse.json(data);

    // Set session cookie
    nextResponse.cookies.set({
        name: 'session_id',
        value: data.session_id,
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/'
    });

    return nextResponse;

  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Registration failed' },
      { status: 500 }
    );
  }
}