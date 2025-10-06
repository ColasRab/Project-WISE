// app/api/weather/route.ts
import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const lat = searchParams.get("lat")
    const lon = searchParams.get("lon")
    const time = searchParams.get("time")

    if (!lat || !lon) {
      return NextResponse.json({ error: "Missing latitude or longitude" }, { status: 400 })
    }

    // If specific time requested, we still need to fetch multiple hours
    // because Prophet generates forecasts from now onwards
    // We'll fetch 24 hours and filter for the requested time
    const hoursToFetch = 24
    const url = `https://project-wise.onrender.com/api/weather?lat=${lat}&lon=${lon}&hours=${hoursToFetch}`

    console.log("Fetching from backend:", url)

    const apiRes = await fetch(url, {
      cache: "no-store",
    })

    if (!apiRes.ok) {
      const errorText = await apiRes.text()
      console.error("Backend API error:", apiRes.status, errorText)
      throw new Error(`Backend API returned ${apiRes.status}`)
    }

    const data = await apiRes.json()
    
    if (data.status === "error") {
      throw new Error(data.message || "Backend returned error status")
    }

    if (data.status === "loading") {
      return NextResponse.json({
        error: "Models are still loading. Please try again in a moment.",
        status: "loading"
      }, { status: 503 })
    }

    // If specific time requested, filter the forecast data
    if (time && time !== "all" && data.forecast && Array.isArray(data.forecast)) {
      const requestedHour = parseInt(time)
      
      // Find the forecast entry closest to the requested hour
      const filteredForecasts = data.forecast.filter((entry: any) => {
        const forecastDate = new Date(entry.datetime)
        return forecastDate.getHours() === requestedHour
      })

      if (filteredForecasts.length > 0) {
        // Return just the first matching forecast
        const forecast = filteredForecasts[0]
        
        return NextResponse.json({
          status: "success",
          location: data.location,
          predictions: {
            wind_speed_ms: forecast.predicted_wind_u,
            precipitation_mm: forecast.predicted_precip_mm,
            temperature_c: forecast.predicted_temp_c,
            humidity_percent: forecast.predicted_humidity,
          },
          assessment: forecast.assessment,
          fuzzy_probabilities: {
            wind: {
              most_likely: forecast.assessment.wind.category,
            },
            precipitation: {
              most_likely: forecast.assessment.precipitation.category,
            },
          },
        })
      }
    }

    // If "all" time or no specific match, return all forecasts formatted
    if (data.forecast && Array.isArray(data.forecast)) {
      return NextResponse.json({
        status: "success",
        location: data.location,
        forecasts: data.forecast.map((entry: any) => ({
          datetime: entry.datetime,
          predictions: {
            wind_speed_ms: Math.sqrt(
              Math.pow(entry.predicted_wind_u, 2) + Math.pow(entry.predicted_wind_v, 2)
            ),
            precipitation_mm: entry.predicted_precip_mm,
            temperature_c: entry.predicted_temp_c,
            humidity_percent: entry.predicted_humidity,
          },
          assessment: entry.assessment,
        })),
      })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching weather data:", error)
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : "Failed to fetch weather data",
        details: error instanceof Error ? error.stack : undefined
      }, 
      { status: 500 }
    )
  }
}