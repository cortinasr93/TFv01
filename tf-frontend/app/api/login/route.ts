// tf-frontend/app/api/login/route.ts

import { NextResponse } from 'next/server';
import { headers } from 'next/headers';
import { fetchApi } from '@/utils/api';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    console.log('Login attempt:', { email: body.email, userType: body.userType });

    // Input validation
    if (!body.email || !body.userType) {
      return NextResponse.json(
        { error: 'Email and user type are required'},
        { status: 400 }
      );
    }
    
    // Log full request being sent
    const requestBody = {
        email: body.email,
        password: body.password,
        user_type: body.userType
    };
    console.log('Sending request to backend:', requestBody); 

    // Send login request to the backend
    const response = await fetchApi('/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
      cache: 'no-store' // Prevent caching of login requests
    });

    if (!response.ok) {
      // Handle specific error cases
      const errorData = await response.json();
      const errorMessage = errorData.detail || 'Login failed';
      throw new Error(errorMessage);
    }

    const data = await response.json();

    console.log('Session ID received:', data.session_id);
    console.log('User ID received:', data.user_id);

    // Get the host from the headers
    const protocol = process.env.NODE_ENV === 'production' ? 'https' : 'http';
    const dashboardPath = body.userType === 'publisher'
      ? `/dashboard/publisher/${data.user_id}`
      : `/dashboard/ai-company/${data.user_id}`;

    
    // Construct absolute URL for redirect
    const redirectUrl = `${protocol}://${request.headers.get('host')}${dashboardPath}`;
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
        path: '/',
        maxAge: 60 * 30 // 30 minutes, matching backend duration
    });

    return nextResponse;

  } catch (error) {
    console.error('Login error:', error);
    
    // Enhanced error handling
    const statusCode = error instanceof Response ? error.status : 401;
    const errorMessage = error instanceof Error 
      ? error.message 
      : 'Authentication failed. Please check your credentials and try again.';

    return NextResponse.json(
      { error: errorMessage },
      { status: statusCode }
    );
  }
}