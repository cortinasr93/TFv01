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

    console.log('Login response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers));

    const text = await response.text();
    console.log('Login response text:', text);

    // Try to parse JSON only if we get a JSON content type
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        try{
            data = JSON.parse(text);
        } catch (e) {
            console.error('JSON parse error:', e);
            throw new Error('Invalid JSON response from server');
        }
    } else {
        console.error('Unexpected content type:', contentType);
        throw new Error(`Server returned unexpected content type: ${contentType}`);
    }

    if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
    }

    // Get the host from the headers
    const headersList = await headers();
    const host = headersList.get('host') || 'localhost:3000';
    const protocol = process.env.NODE_ENV === 'production' ? 'https' : 'http';

    // Construct absolute URL for redirect
    const redirectUrl = `${protocol}://${host}/dashboard/${data.user_id}`;


    // Set the session ID cookie
    const nextResponse = NextResponse.redirect(redirectUrl); // redirect to user-specific dashboard

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