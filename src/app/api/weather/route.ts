import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { lat, lon, target_date, target_hour } = body

    console.log("Received request:", { lat, lon, target_date, target_hour })

    if (!lat || !lon || !target_date) {
      return NextResponse.json(
        { error: "Missing required parameters: lat, lon, and target_date are required" },
        { status: 400 }
      )
    }

    const backendUrl = process.env.BACKEND_URL || "https://project-wise.onrender.com"
    
    const url = new URL("/api/weather", backendUrl)
    url.searchParams.set("lat", lat.toString())
    url.searchParams.set("lon", lon.toString())
    url.searchParams.set("target_date", target_date)
    url.searchParams.set("target_hour", target_hour || "all")

    console.log("Calling backend:", url.toString())

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(30000),
    })

    const responseText = await response.text()
    console.log("Backend response status:", response.status)
    console.log("Backend response body:", responseText)

    if (!response.ok) {
      let errorData
      try {
        errorData = JSON.parse(responseText)
      } catch {
        errorData = { message: responseText }
      }
      return NextResponse.json(
        { error: errorData.message || errorData.error || `Backend returned ${response.status}` },
        { status: response.status }
      )
    }

    const data = JSON.parse(responseText)

    // Handle loading state
    if (data.status === "loading") {
      return NextResponse.json(
        { error: "Models are still loading. Please try again in a moment." },
        { status: 503 }
      )
    }

    // Handle error state
    if (data.status === "error") {
      return NextResponse.json(
        { error: data.message || "Backend error occurred" },
        { status: 500 }
      )
    }

    // Transform backend response to match frontend expectations
    if (data.status === "success" && data.forecast && Array.isArray(data.forecast)) {
      if (data.forecast.length === 1) {
        // Single forecast
        const fc = data.forecast[0]
        // Convert Kelvin to Celsius if needed
        const tempC = fc.predicted_temp_c > 100 
          ? fc.predicted_temp_c - 273.15 
          : fc.predicted_temp_c
        
        return NextResponse.json({
          location: data.location,
          datetime: fc.datetime,
          predictions: {
            wind_speed_ms: fc.predicted_wind_speed || 0,
            precipitation_mm: fc.predicted_precip_mm || 0,
            temperature_c: tempC || 0,
            humidity_percent: fc.predicted_humidity || 0,
          },
          assessment: fc.assessment || {
            wind: { category: "Unknown", severity: 0, safe: true },
            precipitation: { category: "Unknown", severity: 0, safe: true },
            temperature: { category: "Unknown", severity: 0, safe: true },
            humidity: { category: "Unknown", severity: 0, safe: true },
            overall_risk: 0,
            safe_for_outdoors: true,
            recommendation: "No data available"
          }
        })
      } else {
        // Multiple forecasts
        return NextResponse.json({
          location: data.location,
          forecasts: data.forecast.map((fc: any) => {
            // Convert Kelvin to Celsius if needed
            const tempC = fc.predicted_temp_c > 100 
              ? fc.predicted_temp_c - 273.15 
              : fc.predicted_temp_c
            
            return {
              datetime: fc.datetime,
              hour: new Date(fc.datetime).getHours(),
              predictions: {
                wind_speed_ms: fc.predicted_wind_speed || 0,
                precipitation_mm: fc.predicted_precip_mm || 0,
                temperature_c: tempC || 0,
                humidity_percent: fc.predicted_humidity || 0,
              },
              assessment: fc.assessment || {
                wind: { category: "Unknown", severity: 0, safe: true },
                precipitation: { category: "Unknown", severity: 0, safe: true },
                temperature: { category: "Unknown", severity: 0, safe: true },
                humidity: { category: "Unknown", severity: 0, safe: true },
                overall_risk: 0,
                safe_for_outdoors: true,
                recommendation: "No data available"
              }
            }
          }
          )
        })
      }
    }

    // Fallback - return original response
    return NextResponse.json(data)

  } catch (error) {
    console.error("Error in weather API route:", error)

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