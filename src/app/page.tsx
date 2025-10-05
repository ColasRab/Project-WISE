"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon, Download, MapPin, Loader2 } from "lucide-react"
import { format } from "date-fns"
import WeatherRiskCards from "@/components/weather-risk-cards"
import WeatherChart from "@/components/weather-chart"

interface LocationForecast {
  location: {
    latitude: number
    longitude: number
    name: string
  }
  predictions: {
    wind_speed_ms: number
    precipitation_mm: number
  }
  fuzzy_probabilities: {
    wind: {
      calm_percent: number
      breezy_percent: number
      windy_percent: number
      very_windy_percent: number
      most_likely: string
    }
    precipitation: {
      dry_percent: number
      light_rain_percent: number
      moderate_rain_percent: number
      heavy_rain_percent: number
      most_likely: string
    }
  }
  assessment: {
    wind: {
      category: string
      severity: number
      safe: boolean
    }
    precipitation: {
      category: string
      severity: number
      safe: boolean
    }
    overall_risk: number
    safe_for_outdoors: boolean
    recommendation: string
  }
  statistics?: {
    wind: {
      mean: number
      std: number
      min: number
      max: number
      p25: number
      p75: number
      p90: number
    }
    precipitation: {
      mean: number
      std: number
      min: number
      max: number
      p25: number
      p75: number
      p90: number
    }
  }
}

export default function WeatherDashboard() {
  const [location, setLocation] = useState("")
  const [date, setDate] = useState<Date>()
  const [loading, setLoading] = useState(false)
  const [weatherData, setWeatherData] = useState<LocationForecast | null>(null)

  const geocodeLocation = async (locationName: string) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(locationName)}&format=json&limit=1`,
      )
      const data = await response.json()

      if (data && data.length > 0) {
        return {
          lat: Number.parseFloat(data[0].lat),
          lon: Number.parseFloat(data[0].lon),
          name: data[0].display_name,
        }
      }
      throw new Error("Location not found")
    } catch (error) {
      console.error("Geocoding error:", error)
      throw error
    }
  }

  const handleSearch = async () => {
    if (!location || !date) return

    setLoading(true)
    try {
      // First, convert location name to coordinates
      const coords = await geocodeLocation(location)
      console.log('Geocoded location:', coords)

      // Then fetch weather data using coordinates
      const response = await fetch(`/api/weather?lat=${coords.lat}&lon=${coords.lon}`)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to fetch weather data")
      }

      const data = await response.json()
      console.log('Received weather data:', data)

      if (data.error) {
        throw new Error(data.error)
      }

      // Add location name to the data, ensuring it's always a string
      const enrichedData = {
        ...data,
        location: {
          ...data.location,
          name: coords.name ?? ""
        }
      }

      setWeatherData(enrichedData)
    } catch (error) {
      console.error("Error fetching weather data:", error)
      alert(error instanceof Error ? error.message : "Failed to fetch weather data")
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    if (!weatherData) return

    const dataStr = JSON.stringify(weatherData, null, 2)
    const dataBlob = new Blob([dataStr], { type: "application/json" })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement("a")
    link.href = url
    link.download = `weather-insights-${location}-${format(date!, "yyyy-MM-dd")}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <main className="min-h-screen bg-background p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-balance">Weather Risk Dashboard</h1>
          <p className="text-muted-foreground text-lg">
            Plan your outdoor activities with confidence using NASA Earth observation data
          </p>
        </div>

        {/* Search Controls */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle>Search Weather Conditions</CardTitle>
            <CardDescription>Enter a location and date to view weather risk insights</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 space-y-2">
                <Label htmlFor="location">Location</Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="location"
                    placeholder="Manila"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full md:w-[240px] justify-start text-left font-normal bg-transparent"
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {date ? format(date, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={date} onSelect={setDate} initialFocus />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="flex items-end">
                <Button onClick={handleSearch} disabled={!location || !date || loading} className="w-full md:w-auto">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Get Insights"
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {weatherData && (
          <>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold">Weather Insights</h2>
                <p className="text-muted-foreground">
                  {weatherData.location.name || `${weatherData.location.latitude}, ${weatherData.location.longitude}`} • {date ? format(date, "MMMM d, yyyy") : ''}
                </p>
              </div>
              <Button onClick={handleExport} variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Export Data
              </Button>
            </div>

            <div className="space-y-6">
              <WeatherRiskCards data={weatherData} />
              <WeatherChart data={weatherData} />
            </div>
          </>
        )}

        {!weatherData && !loading && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="rounded-full bg-muted p-4 mb-4">
                <MapPin className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No data yet</h3>
              <p className="text-muted-foreground max-w-sm">
                Enter a location and date above to view weather risk insights and plan your outdoor activities
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}