import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Wind, CloudRain, Thermometer, Droplets, AlertCircle, CheckCircle } from "lucide-react"

interface FuzzyProbBlockProps {
  label: string
  percent: number
  color: string
}

function FuzzyProbBlock({ label, percent, color }: FuzzyProbBlockProps) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{percent.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-muted rounded-full h-2">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${percent}%` }} />
      </div>
    </div>
  )
}

const getSeverityColor = (severity: number) => {
  if (severity < 0.3) return { label: "Low Risk", color: "bg-green-500/20 text-green-400 border-green-500/30" }
  if (severity < 0.7) return { label: "Medium Risk", color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" }
  return { label: "High Risk", color: "bg-red-500/20 text-red-400 border-red-500/30" }
}

export default function WeatherRiskCards({ data }: { data: any }) {
  const { fuzzy_probabilities, assessment, predictions } = data

  return (
    <div className="space-y-6">
      {/* Overall Assessment */}
      <Card
        className={`border-2 ${
          assessment.safe_for_outdoors ? "border-green-500/30 bg-green-500/5" : "border-amber-500/30 bg-amber-500/5"
        }`}
      >
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {assessment.safe_for_outdoors ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-amber-500" />
              )}
              Overall Assessment
            </CardTitle>
            <Badge variant="outline" className={getSeverityColor(assessment.overall_risk).color}>
              Risk: {Math.round(assessment.overall_risk * 100)}%
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-lg font-medium">{assessment.recommendation}</p>
        </CardContent>
      </Card>

      {/* Risk Category Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Wind */}
        <Card className="border-cyan-500/20 bg-cyan-500/5">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Wind Conditions</CardTitle>
            <Wind className="h-5 w-5 text-cyan-500" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-3xl font-bold">{assessment.wind.category}</div>
              <p className="text-xs text-muted-foreground mt-1">{predictions.wind_speed_ms.toFixed(2)} m/s</p>
            </div>
            <Badge variant="outline" className={getSeverityColor(assessment.wind.severity).color}>
              {getSeverityColor(assessment.wind.severity).label}
            </Badge>
          </CardContent>
        </Card>

        {/* Precipitation */}
        <Card className="border-indigo-500/20 bg-indigo-500/5">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Precipitation</CardTitle>
            <CloudRain className="h-5 w-5 text-indigo-500" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-3xl font-bold">{assessment.precipitation.category}</div>
              <p className="text-xs text-muted-foreground mt-1">{predictions.precipitation_mm.toFixed(2)} mm</p>
            </div>
            <Badge variant="outline" className={getSeverityColor(assessment.precipitation.severity).color}>
              {getSeverityColor(assessment.precipitation.severity).label}
            </Badge>
          </CardContent>
        </Card>

        {/* Temperature */}
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Temperature</CardTitle>
            <Thermometer className="h-5 w-5 text-amber-500" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-3xl font-bold">{assessment.temperature.category}</div>
              <p className="text-xs text-muted-foreground mt-1">{predictions.temperature_c.toFixed(2)} °C</p>
            </div>
            <Badge variant="outline" className={getSeverityColor(assessment.temperature.severity).color}>
              {getSeverityColor(assessment.temperature.severity).label}
            </Badge>
          </CardContent>
        </Card>

        {/* Humidity */}
        <Card className="border-emerald-500/20 bg-emerald-500/5">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Humidity</CardTitle>
            <Droplets className="h-5 w-5 text-emerald-500" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-3xl font-bold">{assessment.humidity.category}</div>
              <p className="text-xs text-muted-foreground mt-1">{predictions.humidity_percent.toFixed(2)}%</p>
            </div>
            <Badge variant="outline" className={getSeverityColor(assessment.humidity.severity).color}>
              {getSeverityColor(assessment.humidity.severity).label}
            </Badge>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
