// tf-frontend/app/api/register/ai-company/route.ts

import { NextResponse } from 'next/server';
import { fetchApi } from '@/utils/api';
import { ApiError } from '@/utils/api';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Log the incoming request data
    console.log('Registration request received:', body);

    const registrationData = {
      name: body.name,
      company_name: body.companyName,
      email: body.email,
      // password: body.password,
      website: body.website,
      use_cases: body.useCases,
      message: body.message,
      onboarding_status: 'waitlist'
    };
    
    const response = await fetchApi('/api/onboarding/ai-company', {
      method: 'POST',
      body: JSON.stringify(registrationData)
    });

    const data = await response.json();

    // Create response with the session cookie
    const nextResponse = NextResponse.json(data);

    // Set session cookie
    if (data.session_id) {
      nextResponse.cookies.set({
          name: 'session_id',
          value: data.session_id,
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          path: '/'
      });
    }

    return nextResponse;

  } catch (error) {
    console.error('AI Company registration error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Registration failed' },
      { status: error instanceof ApiError ? error.status : 500 }
    );
  }
}