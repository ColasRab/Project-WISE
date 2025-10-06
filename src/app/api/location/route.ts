import { NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get("q")

  if (!query) {
    return NextResponse.json({ error: "Missing query" }, { status: 400 })
  }

  try {
    const url = `https://nominatim.openstreetmap.org/search?` +
      new URLSearchParams({
        q: query,
        format: "json",
        countrycodes: "ph",
        limit: "10",
        addressdetails: "1",
      })

    const response = await fetch(url, {
      headers: {
        "User-Agent": "WeatherRiskDashboard/1.0",
      },
    })

    if (!response.ok) {
      return NextResponse.json({ error: "Nominatim request failed" }, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching from Nominatim:", error)
    return NextResponse.json({ error: "Failed to fetch location" }, { status: 500 })
  }
}
