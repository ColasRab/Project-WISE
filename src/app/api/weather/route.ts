import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const lat = searchParams.get("lat")
    const lon = searchParams.get("lon")

    if (!lat || !lon) {
      return NextResponse.json({ error: "Missing latitude or longitude" }, { status: 400 })
    }

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "https://weather-api.onrender.com";

    const apiRes = await fetch(`${apiBase}/api/weather?lat=${lat}&lon=${lon}`);


    if (!apiRes.ok) {
      throw new Error(`Backend API returned ${apiRes.status}`)
    }

    const data = await apiRes.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching weather data:", error)
    return NextResponse.json({ error: "Failed to fetch weather data" }, { status: 500 })
  }
}
