import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    // Get query parameters from the URL
    const { searchParams } = new URL(request.url);
    const lat = searchParams.get('lat');
    const lon = searchParams.get('lon');

    // Validate parameters
    if (!lat || !lon) {
      return NextResponse.json(
        { error: 'Missing required parameters: lat and lon' },
        { status: 400 }
      );
    }

    // Validate lat/lon are numbers
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lon);

    if (isNaN(latitude) || isNaN(longitude)) {
      return NextResponse.json(
        { error: 'Invalid coordinates: lat and lon must be numbers' },
        { status: 400 }
      );
    }

    // Validate coordinate ranges
    if (latitude < -90 || latitude > 90) {
      return NextResponse.json(
        { error: 'Invalid latitude: must be between -90 and 90' },
        { status: 400 }
      );
    }

    if (longitude < -180 || longitude > 180) {
      return NextResponse.json(
        { error: 'Invalid longitude: must be between -180 and 180' },
        { status: 400 }
      );
    }

    // Get the backend API URL from environment variable
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://project-wise.onrender.com';
    
    console.log(`Fetching weather data from: ${BACKEND_URL}/api/weather?lat=${latitude}&lon=${longitude}`);

    // Call the Python backend API
    const response = await fetch(
      `${BACKEND_URL}/api/weather?lat=${latitude}&lon=${longitude}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(30000), // 30 second timeout
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend API error:', errorText);
      return NextResponse.json(
        { 
          error: 'Failed to fetch weather data from backend',
          details: errorText,
          status: response.status
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // Return the data from the backend
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error in weather API route:', error);
    
    // Handle different error types
    if (typeof error === 'object' && error !== null && 'name' in error && (error as any).name === 'AbortError') {
      return NextResponse.json(
        { error: 'Request timeout: Backend server took too long to respond' },
        { status: 504 }
      );
    }

    if (
      typeof error === 'object' &&
      error !== null &&
      'cause' in error &&
      (error as any).cause?.code === 'ECONNREFUSED'
    ) {
      return NextResponse.json(
        { error: 'Backend server is not reachable. Please check if the Python service is running.' },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: typeof error === 'object' && error !== null && 'message' in error ? (error as any).message : String(error)
      },
      { status: 500 }
    );
  }
}
