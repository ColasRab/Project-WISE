"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { motion } from "framer-motion"

interface MetricStats {
  mean: number
  std: number
  min: number
  max: number
  p25: number
  p75: number
  p90: number
}

interface LocationForecast {
  statistics?: {
    wind?: MetricStats
    precipitation?: MetricStats
    temperature?: MetricStats
    humidity?: MetricStats
  }
}

interface WeatherChartProps {
  data: LocationForecast
}

export default function WeatherChart({ data }: WeatherChartProps) {
  const { statistics } = data

  const percentiles = ["min", "p25", "mean", "p75", "p90", "max"] as const

  const chartData = percentiles.map((key) => ({
    name: key.toUpperCase(),
    wind: statistics?.wind?.[key],
    precipitation: statistics?.precipitation?.[key],
    temperature: statistics?.temperature?.[key],
    humidity: statistics?.humidity?.[key],
  }))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 }}
    >
      <Card className="hover:shadow-lg transition-shadow duration-300">
        <CardHeader>
          <CardTitle>Statistical Distribution</CardTitle>
          <CardDescription>Percentiles of weather variables</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
                formatter={(value: number) => (value !== undefined ? value.toFixed(2) : "—")}
              />
              <Legend />
              {statistics?.wind && <Bar dataKey="wind" fill="#06b6d4" name="Wind (m/s)" radius={[8, 8, 0, 0]} />}
              {statistics?.precipitation && (
                <Bar dataKey="precipitation" fill="#6366f1" name="Precipitation (mm)" radius={[8, 8, 0, 0]} />
              )}
              {statistics?.temperature && (
                <Bar dataKey="temperature" fill="#f59e0b" name="Temperature (°C)" radius={[8, 8, 0, 0]} />
              )}
              {statistics?.humidity && (
                <Bar dataKey="humidity" fill="#10b981" name="Humidity (%)" radius={[8, 8, 0, 0]} />
              )}
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  )
}
