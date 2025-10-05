"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts"
import { motion } from "framer-motion"
import { TrendingUp, BarChart3, Activity } from "lucide-react"

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

  const confidenceIntervalData = [
    {
      metric: "Wind",
      lower: statistics?.wind?.p25,
      mean: statistics?.wind?.mean,
      upper: statistics?.wind?.p75,
      ci90Lower: statistics?.wind?.min,
      ci90Upper: statistics?.wind?.p90,
      color: "#06b6d4",
    },
    {
      metric: "Precip",
      lower: statistics?.precipitation?.p25,
      mean: statistics?.precipitation?.mean,
      upper: statistics?.precipitation?.p75,
      ci90Lower: statistics?.precipitation?.min,
      ci90Upper: statistics?.precipitation?.p90,
      color: "#6366f1",
    },
    {
      metric: "Temp",
      lower: statistics?.temperature?.p25,
      mean: statistics?.temperature?.mean,
      upper: statistics?.temperature?.p75,
      ci90Lower: statistics?.temperature?.min,
      ci90Upper: statistics?.temperature?.p90,
      color: "#f59e0b",
    },
    {
      metric: "Humidity",
      lower: statistics?.humidity?.p25,
      mean: statistics?.humidity?.mean,
      upper: statistics?.humidity?.p75,
      ci90Lower: statistics?.humidity?.min,
      ci90Upper: statistics?.humidity?.p90,
      color: "#10b981",
    },
  ]

  const trendData = [
    { point: "Min", ...Object.fromEntries(Object.entries(statistics || {}).map(([k, v]) => [k, v.min])) },
    { point: "P25", ...Object.fromEntries(Object.entries(statistics || {}).map(([k, v]) => [k, v.p25])) },
    { point: "Mean", ...Object.fromEntries(Object.entries(statistics || {}).map(([k, v]) => [k, v.mean])) },
    { point: "P75", ...Object.fromEntries(Object.entries(statistics || {}).map(([k, v]) => [k, v.p75])) },
    { point: "P90", ...Object.fromEntries(Object.entries(statistics || {}).map(([k, v]) => [k, v.p90])) },
    { point: "Max", ...Object.fromEntries(Object.entries(statistics || {}).map(([k, v]) => [k, v.max])) },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 }}
    >
      <Card className="hover:shadow-lg transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Statistical Visualization
          </CardTitle>
          <CardDescription>Percentiles, confidence intervals, and trend analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="percentiles" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-4">
              <TabsTrigger value="percentiles" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Percentiles
              </TabsTrigger>
              <TabsTrigger value="confidence" className="flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Confidence Intervals
              </TabsTrigger>
              <TabsTrigger value="trends" className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Trend Analysis
              </TabsTrigger>
            </TabsList>

            <TabsContent value="percentiles" className="mt-0">
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
            </TabsContent>

            <TabsContent value="confidence" className="mt-0">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart
                  data={confidenceIntervalData}
                  layout="horizontal"
                  barCategoryGap="30%"
                  barGap={2}
                  margin={{ top: 20, right: 40, left: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.2} />
                  <XAxis
                  type="number"
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={13}
                  tickLine={false}
                  axisLine={false}
                  />
                  <YAxis
                  dataKey="metric"
                  type="category"
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={14}
                  tickLine={false}
                  axisLine={false}
                  />
                  <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "10px",
                    boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
                    padding: "14px 18px",
                  }}
                  formatter={(value: number) => (value !== undefined ? value.toFixed(2) : "—")}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="bg-card border border-border rounded-xl p-4 shadow-lg min-w-[180px]">
                      <p className="font-semibold mb-2 text-lg">{data.metric}</p>
                      <div className="space-y-1 text-sm">
                        <p className="text-muted-foreground">
                        <span className="font-medium">90% CI:</span>{" "}
                        <span className="text-blue-600">{data.ci90Lower?.toFixed(2)}</span>
                        {" - "}
                        <span className="text-blue-600">{data.ci90Upper?.toFixed(2)}</span>
                        </p>
                        <p className="text-muted-foreground">
                        <span className="font-medium">50% CI:</span>{" "}
                        <span className="text-cyan-600">{data.lower?.toFixed(2)}</span>
                        {" - "}
                        <span className="text-cyan-600">{data.upper?.toFixed(2)}</span>
                        </p>
                        <p className="font-medium">
                        Mean: <span className="text-primary">{data.mean?.toFixed(2)}</span>
                        </p>
                      </div>
                      </div>
                    )
                    }
                    return null
                  }}
                  />
                  {/* 90% CI band */}
                  <Bar
                  dataKey="ci90Upper"
                  minPointSize={2}
                  fill="#e0f2fe"
                  radius={[0, 8, 8, 0]}
                  background={false}
                  isAnimationActive={false}
                  >
                  {confidenceIntervalData.map((entry, index) => (
                    <rect
                    key={index}
                    x={Math.min(entry.ci90Lower ?? 0, entry.ci90Upper ?? 0)}
                    y={index * 48 + 12}
                    width={Math.abs((entry.ci90Upper ?? 0) - (entry.ci90Lower ?? 0))}
                    height={24}
                    rx={8}
                    fill={entry.color + "22"}
                    />
                  ))}
                  </Bar>
                  {/* 50% CI band */}
                  <Bar
                  dataKey="upper"
                  minPointSize={2}
                  fill="#a5f3fc"
                  radius={[0, 8, 8, 0]}
                  background={false}
                  isAnimationActive={false}
                  >
                  {confidenceIntervalData.map((entry, index) => (
                    <rect
                    key={index}
                    x={Math.min(entry.lower ?? 0, entry.upper ?? 0)}
                    y={index * 48 + 18}
                    width={Math.abs((entry.upper ?? 0) - (entry.lower ?? 0))}
                    height={12}
                    rx={6}
                    fill={entry.color + "66"}
                    />
                  ))}
                  </Bar>
                  {/* Mean marker */}
                  <Bar
                  dataKey="mean"
                  fill="#06b6d4"
                  radius={[8, 8, 8, 8]}
                  barSize={8}
                  isAnimationActive={false}
                  >
                  {confidenceIntervalData.map((entry, index) => (
                    <rect
                    key={index}
                    x={entry.mean ?? 0 - 4}
                    y={index * 48 + 24}
                    width={8}
                    height={8}
                    rx={4}
                    fill={entry.color}
                    />
                  ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 text-sm text-muted-foreground text-center">
                Darker bands show 50% confidence interval (P25-P75), lighter bands show 90% range (Min-P90)
              </div>
            </TabsContent>

            <TabsContent value="trends" className="mt-0">
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="windGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="precipGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="humidityGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                  <XAxis dataKey="point" stroke="hsl(var(--muted-foreground))" fontSize={12} />
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
                  {statistics?.wind && (
                    <>
                      <Area
                        type="monotone"
                        dataKey="wind"
                        stroke="#06b6d4"
                        strokeWidth={2}
                        fill="url(#windGradient)"
                        name="Wind (m/s)"
                      />
                      <ReferenceLine
                        y={statistics.wind.mean}
                        stroke="#06b6d4"
                        strokeDasharray="3 3"
                        label={{ value: "Mean", fill: "#06b6d4", fontSize: 10 }}
                      />
                    </>
                  )}
                  {statistics?.precipitation && (
                    <>
                      <Area
                        type="monotone"
                        dataKey="precipitation"
                        stroke="#6366f1"
                        strokeWidth={2}
                        fill="url(#precipGradient)"
                        name="Precipitation (mm)"
                      />
                    </>
                  )}
                  {statistics?.temperature && (
                    <>
                      <Area
                        type="monotone"
                        dataKey="temperature"
                        stroke="#f59e0b"
                        strokeWidth={2}
                        fill="url(#tempGradient)"
                        name="Temperature (°C)"
                      />
                    </>
                  )}
                  {statistics?.humidity && (
                    <>
                      <Area
                        type="monotone"
                        dataKey="humidity"
                        stroke="#10b981"
                        strokeWidth={2}
                        fill="url(#humidityGradient)"
                        name="Humidity (%)"
                      />
                    </>
                  )}
                </AreaChart>
              </ResponsiveContainer>
              <div className="mt-4 text-sm text-muted-foreground text-center">
                Trend progression from minimum to maximum values with mean reference lines
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </motion.div>
  )
}
