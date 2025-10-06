"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon, Download, Loader2, Sparkles } from "lucide-react"
import { format } from "date-fns"
import WeatherRiskCards from "@/components/weather-risk-cards"
import WeatherChart from "@/components/weather-chart"
import { LocationAutocomplete, PhilippineLocation } from "@/components/location-autocomplete"
import { AnimatedWeatherIcon } from "@/components/animated-weather-icon"
import { TimePicker } from "@/components/time-picker"
import { motion, AnimatePresence } from "framer-motion"

interface LocationForecast {
  location: {
    latitude: number
    longitude: number
    name: string
  }
  datetime?: string
  hour?: number
  predictions: {
    wind_speed_ms: number
    precipitation_mm: number
    temperature_c: number
    humidity_percent: number
  }
  fuzzy_probabilities?: {
    wind: {
      most_likely: string
    }
    precipitation: {
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
    temperature: {
      category: string
      severity: number
      safe: boolean
    }
    humidity: {
      category: string
      severity: number
      safe: boolean
    }
    overall_risk: number
    safe_for_outdoors: boolean
    recommendation: string
  }
}

interface MultipleForecast {
  location: {
    latitude: number
    longitude: number
    name: string
  }
  forecasts: Array<{
    datetime: string
    hour: number
    predictions: {
      wind_speed_ms: number
      precipitation_mm: number
      temperature_c: number
      humidity_percent: number
    }
    assessment: any
  }>
}

export default function WeatherDashboard() {
  const [selectedLocation, setSelectedLocation] = useState<PhilippineLocation | null>(null)
  const [date, setDate] = useState<Date>()
  const [time, setTime] = useState<string>("all")
  const [loading, setLoading] = useState(false)
  const [weatherData, setWeatherData] = useState<LocationForecast | MultipleForecast | null>(null)

  const handleSearch = async () => {
    if (!selectedLocation || !date) return

    setLoading(true)
    try {
      const dateStr = format(date, "yyyy-MM-dd")
      const response = await fetch(`/api/weather`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          lat: selectedLocation.lat,
          lon: selectedLocation.lon,
          target_date: dateStr,
          target_hour: time,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to fetch weather data")
      }

      const data = await response.json()

      if (data.forecast && Array.isArray(data.forecast)) {
        data.forecast = data.forecast.map((item: any) => transformForecastData(item))
      }

      if (data.error) {
        throw new Error(data.error)
      }

      // Enrich with location name
      if (data.forecasts) {
        // Multiple forecasts (all day)
        setWeatherData({
          ...data,
          location: {
            ...data.location,
            name: `${selectedLocation.name}, ${selectedLocation.province}`,
          },
        })
      } else {
        // Single forecast
        setWeatherData({
          ...data,
          location: {
            ...data.location,
            name: `${selectedLocation.name}, ${selectedLocation.province}`,
          },
        })
      }
    } catch (error) {
      console.error("Error fetching weather data:", error)
      alert(error instanceof Error ? error.message : "Failed to fetch weather data")
    } finally {
      setLoading(false)
    }
  }

  const transformForecastData = (backendData: any) => {
    return {
      ...backendData,
      predicted_temp_c: backendData.predicted_temp_c - 273.15 // Convert Kelvin to Celsius
    }
  }

  const handleExport = () => {
    if (!weatherData || !selectedLocation) return

    const dataStr = JSON.stringify(weatherData, null, 2)
    const dataBlob = new Blob([dataStr], { type: "application/json" })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement("a")
    link.href = url
    link.download = `weather-insights-${selectedLocation.name}-${format(date!, "yyyy-MM-dd")}-${time === "all" ? "all-day" : `${time}h`}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const isMultipleForecast = (data: any): data is MultipleForecast => {
    return data && 'forecasts' in data
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-accent/5 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        <motion.div
          className="space-y-2"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-3">
            <AnimatedWeatherIcon type="cloud" className="h-10 w-10 text-primary" />
            <h1 className="text-4xl font-bold tracking-tight text-balance bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              Weather Risk Dashboard
            </h1>
            <Sparkles className="h-6 w-6 text-amber-500 animate-pulse" />
          </div>
          <p className="text-muted-foreground text-lg">
            Plan your outdoor activities in the Philippines with confidence using NASA Earth observation data
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="border-border/50 shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AnimatedWeatherIcon type="sun" className="h-5 w-5 text-amber-500" />
                Search Weather Conditions
              </CardTitle>
              <CardDescription>
                Select a location in the Philippines and date to view weather risk insights
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 space-y-2">
                  <Label htmlFor="location">Location (Philippines)</Label>
                  <LocationAutocomplete value={selectedLocation} onChange={setSelectedLocation} />
                </div>

                <div className="space-y-2">
                  <Label>Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full md:w-[240px] justify-start text-left font-normal bg-transparent hover:bg-accent/50 transition-colors"
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {date ? format(date, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar 
                        mode="single" 
                        selected={date} 
                        onSelect={setDate} 
                        initialFocus
                        disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <TimePicker value={time} onChange={setTime} />

                <div className="flex items-end">
                  <Button
                    onClick={handleSearch}
                    disabled={!selectedLocation || !date || loading}
                    className="w-full md:w-auto bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 transition-all duration-300 shadow-md hover:shadow-lg"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Get Insights
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <AnimatePresence mode="wait">
          {weatherData && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-semibold flex items-center gap-2">
                    <AnimatedWeatherIcon type="cloud" className="h-6 w-6 text-primary" />
                    Weather Insights
                  </h2>
                  <p className="text-muted-foreground">
                    {weatherData.location.name} •{" "}
                    {date ? format(date, "MMMM d, yyyy") : ""} •{" "}
                    {time === "all" ? "All Day (Every 3 hours)" : `${time.padStart(2, "0")}:00`}
                  </p>
                </div>
                <Button
                  onClick={handleExport}
                  variant="outline"
                  className="hover:bg-accent/50 transition-colors bg-transparent"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Export Data
                </Button>
              </div>

              {isMultipleForecast(weatherData) ? (
                <div className="space-y-8">
                  {weatherData.forecasts.map((hourData, index) => (
                    <div key={index} className="space-y-4">
                      <h3 className="text-xl font-semibold flex items-center gap-2">
                        <span className="text-primary">{hourData.hour.toString().padStart(2, "0")}:00</span>
                      </h3>
                      <WeatherRiskCards data={hourData} />
                    </div>
                  ))}
                </div>
              ) : (
                <WeatherRiskCards data={weatherData} />
              )}
            </motion.div>
          )}

          {!weatherData && !loading && (
            <motion.div
              key="empty"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-dashed hover:border-solid transition-all duration-300">
                <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                  <motion.div
                    className="rounded-full bg-gradient-to-br from-primary/20 to-accent/20 p-6 mb-4"
                    animate={{
                      scale: [1, 1.05, 1],
                      rotate: [0, 5, -5, 0],
                    }}
                    transition={{
                      duration: 4,
                      repeat: Number.POSITIVE_INFINITY,
                      ease: "easeInOut",
                    }}
                  >
                    <AnimatedWeatherIcon type="cloud" className="h-12 w-12 text-primary" />
                  </motion.div>
                  <h3 className="text-lg font-semibold mb-2">No data yet</h3>
                  <p className="text-muted-foreground max-w-sm">
                    Select a location in the Philippines, date, and time above to view weather risk insights
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}