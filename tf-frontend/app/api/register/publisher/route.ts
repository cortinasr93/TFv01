// tf-frontend/app/api/register/publisher/route.ts

import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        console.log('Publisher registration request received:', body);

        const registrationData = {
                name: body.name,
                email: body.email,
                company_name: body.companyName,
                // password: body.password,
                website: body.website,
                content_type: body.contentType,
                message: body.message,
                onboarding_status: 'waitlist',
                settings: {
                    description: body.description,
                    content_categories: body.contentCategories,
                }
            };

        console.log('Sending to backend:', registrationData);

        const response = await fetch('http://localhost:8000/api/onboarding/publisher', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Cookie': request.headers.get('cookie') || ''
            },
            body: JSON.stringify(registrationData)
        })
        
        if (!response.ok) {
            const errorData = await response.json();
            return NextResponse.json(errorData, {status: response.status });
        }

        const data = await response.json();

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
        console.error('Registration error:', error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Registration failed'},
            { status : 500 }
        );
    }
}