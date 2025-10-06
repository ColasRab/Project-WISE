import { NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const lat = searchParams.get("lat")
  const lon = searchParams.get("lon")
  const targetDate = searchParams.get("target_date")
  const targetHour = searchParams.get("target_hour") || "all"

  console.log("Received params:", { lat, lon, targetDate, targetHour })

  if (!lat || !lon || !targetDate) {
    return NextResponse.json(
      { error: "Missing required parameters: lat, lon, and target_date are required" },
      { status: 400 }
    )
  }

  try {
    // Get the backend URL from environment variable or use default
    const backendUrl = process.env.BACKEND_URL || "https://project-wise.onrender.com"
    
    // Construct the URL with proper parameters
    const url = new URL("/api/weather", backendUrl)
    url.searchParams.set("lat", lat)
    url.searchParams.set("lon", lon)
    url.searchParams.set("target_date", targetDate)
    url.searchParams.set("target_hour", targetHour)

    console.log("Fetching weather data from:", url.toString())
    console.log("Parameters being sent:", {
      lat,
      lon,
      target_date: targetDate,
      target_hour: targetHour
    })

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      // Add timeout to prevent hanging
      signal: AbortSignal.timeout(30000), // 30 second timeout
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: "Unknown error" }))
      console.error("Backend error:", errorData)
      return NextResponse.json(
        { error: errorData.message || `Backend returned ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()

    // Return the data from the backend
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching weather data:", error)
    
    if (error instanceof Error) {
      if (error.name === "AbortError") {
        return NextResponse.json(
          { error: "Request timeout - backend took too long to respond" },
          { status: 504 }
        )
      }
      return NextResponse.json(
        { error: `Failed to fetch weather data: ${error.message}` },
        { status: 500 }
      )
    }

    return NextResponse.json(
      { error: "Failed to fetch weather data from backend" },
      { status: 500 }
    )
  }
}