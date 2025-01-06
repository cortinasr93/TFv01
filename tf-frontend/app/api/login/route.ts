// app/api/login/route.ts
import { NextResponse } from 'next/server';
import { headers } from 'next/headers';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    console.log('Login attempt:', { email: body.email, userType: body.userType });

    // Log full request being sent
    const requestBody = {
        email: body.email,
        password: body.password,
        user_type: body.userType
    };
    console.log('Sending request to backend:', requestBody); 

    // Send login request to the backend
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: body.email,
        password: body.password,
        user_type: body.userType
      })
    });

    const responseText = await response.text()
    console.log('Login response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers));
    console.log('Login response text:', responseText);

    if (!response.ok) {
        throw new Error(responseText);
    }

    // Parse response data
    const data = JSON.parse(responseText);
    console.log('Session ID received:', data.session_id);
    console.log('User ID received:', data.user_id);

    // Get the host from the headers
    const headersList = await headers();
    const host = headersList.get('host') || 'localhost:3000';
    const protocol = process.env.NODE_ENV === 'production' ? 'https' : 'http';

    // Construct redirect URL based on user type
    const dashboardPath = body.userType === 'publisher'
        ? `/dashboard/publisher/${data.user_id}`
        : `/dashboard/ai-company/${data.user_id}`;
    
    // Construct absolute URL for redirect
    const redirectUrl = `${protocol}://${host}${dashboardPath}`;
    console.log('Redirecting to:', redirectUrl);

    // Create response with redirect
    const nextResponse = NextResponse.redirect(redirectUrl);

    // Set the session ID cookie
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
    console.error('Login error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Login failed' },
      { status: 401 }
    );
  }
}