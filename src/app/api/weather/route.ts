import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { lat, lon, date, time } = body

    console.log("Received body params:", { lat, lon, date, time })

    if (!lat || !lon || !date) {
      return NextResponse.json(
        { error: "Missing required parameters: lat, lon, and date are required" },
        { status: 400 }
      )
    }

    // Get the backend URL from environment variable or use default
    const backendUrl = process.env.BACKEND_URL || "https://project-wise.onrender.com"

    // Construct the URL with proper parameters
    const url = new URL("/api/weather", backendUrl)
    url.searchParams.set("lat", lat.toString())
    url.searchParams.set("lon", lon.toString())
    url.searchParams.set("target_date", date)
    url.searchParams.set("target_hour", time || "all")

    console.log("Fetching weather data from backend:", url.toString())

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(30000), // 30 sec timeout
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { error: errorData.error || `Backend returned ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching weather data:", error)

    if (error instanceof Error && error.name === "AbortError") {
      return NextResponse.json(
        { error: "Request timeout - backend took too long to respond" },
        { status: 504 }
      )
    }

    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch weather data" },
      { status: 500 }
    )
  }
}
