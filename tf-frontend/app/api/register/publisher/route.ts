import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        console.log('Publisher registration request received:', body);

        const registrationData = {
                name: body.companyName || body.name,
                email: body.email,
                password: body.password,
                website: body.website,
                content_type: body.contentType,
                settings: {
                    description: body.description,
                    content_categories: body.contentCategories,
                    estimated_volume: body.estimatedVolume,
                    update_frequency: body.updateFrequency
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
            const text = await response.text()
            console.error('Backend error response:', text);

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
        return NextResponse.json(data);

    } catch (error) {
        console.error('Registration error:', error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Registration failed'},
            { status : 500 }
        );
    }
}