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

    if (time === "all") {
      const promises = Array.from({ length: 24 }, (_, hour) =>
        fetch(`https://project-wise.onrender.com/api/weather?lat=${lat}&lon=${lon}&hour=${hour}`, {
          cache: "no-store",
        }).then((res) => res.json()),
      )

      const allData = await Promise.all(promises)
      return NextResponse.json(allData)
    }

    const url = time
      ? `https://project-wise.onrender.com/api/weather?lat=${lat}&lon=${lon}&hour=${time}`
      : `https://project-wise.onrender.com/api/weather?lat=${lat}&lon=${lon}`

    const apiRes = await fetch(url, {
      cache: "no-store",
    })

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
