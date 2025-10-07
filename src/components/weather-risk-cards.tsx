"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle } from "lucide-react"
import { motion } from "framer-motion"
import { AnimatedWeatherIcon } from "./animated-weather-icon"

const getSeverityColor = (severity: number) => {
  if (severity < 0.3) return { label: "Low Risk", color: "bg-green-500/20 text-green-400 border-green-500/30" }
  if (severity < 0.7) return { label: "Medium Risk", color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" }
  return { label: "High Risk", color: "bg-red-500/20 text-red-400 border-red-500/30" }
}

const getRainSeverity = (chanceOfRain: number) => {
  if (chanceOfRain < 30) return 0.0  // Low chance
  if (chanceOfRain < 60) return 0.3  // Medium chance
  if (chanceOfRain < 80) return 0.6  // High chance
  return 0.9  // Very high chance
}

const getRainCategory = (chanceOfRain: number) => {
  if (chanceOfRain < 30) return "Low Chance"
  if (chanceOfRain < 60) return "Possible"
  if (chanceOfRain < 80) return "Likely"
  return "Very Likely"
}

const cardBackgrounds = {
  wind: "bg-gradient-to-br from-cyan-500/5 via-cyan-400/5 to-blue-500/5 relative overflow-hidden before:absolute before:inset-0 before:bg-[radial-gradient(circle_at_50%_120%,rgba(6,182,212,0.1),transparent)] before:animate-pulse",
  rain: "bg-gradient-to-br from-indigo-500/5 via-blue-400/5 to-indigo-600/5 relative overflow-hidden before:absolute before:inset-0 before:bg-[linear-gradient(45deg,transparent_25%,rgba(99,102,241,0.05)_25%,rgba(99,102,241,0.05)_50%,transparent_50%,transparent_75%,rgba(99,102,241,0.05)_75%)] before:bg-[length:20px_20px]",
  temperature:
    "bg-gradient-to-br from-amber-500/5 via-orange-400/5 to-red-500/5 relative overflow-hidden before:absolute before:inset-0 before:bg-[radial-gradient(circle_at_80%_20%,rgba(251,191,36,0.1),transparent)]",
  humidity:
    "bg-gradient-to-br from-emerald-500/5 via-teal-400/5 to-cyan-500/5 relative overflow-hidden before:absolute before:inset-0 before:bg-[radial-gradient(ellipse_at_bottom,rgba(16,185,129,0.1),transparent)]",
}

export default function WeatherRiskCards({ data }: { data: any }) {
  // Safely access nested properties with fallbacks
  const assessment = data?.assessment || {}
  const predictions = data?.predictions || {}
  
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  }

  // Check if we have required data
  if (!assessment || !predictions) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        No weather data available
      </div>
    )
  }

  // Calculate rain severity from chance_of_rain
  const chanceOfRain = predictions.chance_of_rain || 0
  const rainSeverity = getRainSeverity(chanceOfRain)
  const rainCategory = getRainCategory(chanceOfRain)

  return (
    <motion.div className="space-y-6" variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={cardVariants}>
        <Card
          className={`border-2 transition-all duration-300 hover:shadow-lg ${
            assessment.safe_for_outdoors
              ? "border-green-500/30 bg-green-500/5 hover:border-green-500/50"
              : "border-amber-500/30 bg-amber-500/5 hover:border-amber-500/50"
          }`}
        >
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Number.POSITIVE_INFINITY,
                    ease: "easeInOut",
                  }}
                >
                  {assessment.safe_for_outdoors ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-amber-500" />
                  )}
                </motion.div>
                Overall Assessment
              </CardTitle>
              <Badge variant="outline" className={getSeverityColor(assessment.overall_risk || 0).color}>
                Risk: {Math.round((assessment.overall_risk || 0) * 100)}%
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-lg font-medium">{assessment.recommendation || "No recommendation available"}</p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-4" variants={containerVariants}>
        {/* Wind */}
        <motion.div variants={cardVariants}>
          <Card
            className={`border-cyan-500/20 hover:border-cyan-500/40 hover:shadow-lg transition-all duration-300 group ${cardBackgrounds.wind}`}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Wind Conditions</CardTitle>
              <AnimatedWeatherIcon
                type="wind"
                className="h-5 w-5 text-cyan-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4 relative z-10">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                >
                  {assessment.wind?.category || "Unknown"}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">
                  {(predictions.wind_speed_ms || 0).toFixed(2)} m/s
                </p>
              </div>
              <Badge variant="outline" className={getSeverityColor(assessment.wind?.severity || 0).color}>
                {getSeverityColor(assessment.wind?.severity || 0).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>

        {/* Chance of Rain */}
        <motion.div variants={cardVariants}>
          <Card
            className={`border-indigo-500/20 hover:border-indigo-500/40 hover:shadow-lg transition-all duration-300 group ${cardBackgrounds.rain}`}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Chance of Rain</CardTitle>
              <AnimatedWeatherIcon
                type="rain"
                className="h-5 w-5 text-indigo-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4 relative z-10">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.3 }}
                >
                  {rainCategory}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">
                  {chanceOfRain.toFixed(0)}% probability
                </p>
              </div>
              <Badge variant="outline" className={getSeverityColor(rainSeverity).color}>
                {getSeverityColor(rainSeverity).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>

        {/* Temperature */}
        <motion.div variants={cardVariants}>
          <Card
            className={`border-amber-500/20 hover:border-amber-500/40 hover:shadow-lg transition-all duration-300 group ${cardBackgrounds.temperature}`}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Temperature</CardTitle>
              <AnimatedWeatherIcon
                type="temperature"
                className="h-5 w-5 text-amber-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4 relative z-10">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.4 }}
                >
                  {assessment.temperature?.category || "Unknown"}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">
                  {(predictions.temperature_c || 0).toFixed(2)} °C
                </p>
              </div>
              <Badge variant="outline" className={getSeverityColor(assessment.temperature?.severity || 0).color}>
                {getSeverityColor(assessment.temperature?.severity || 0).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>

        {/* Humidity */}
        <motion.div variants={cardVariants}>
          <Card
            className={`border-emerald-500/20 hover:border-emerald-500/40 hover:shadow-lg transition-all duration-300 group ${cardBackgrounds.humidity}`}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Humidity</CardTitle>
              <AnimatedWeatherIcon
                type="humidity"
                className="h-5 w-5 text-emerald-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4 relative z-10">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.5 }}
                >
                  {assessment.humidity?.category || "Unknown"}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">
                  {(predictions.humidity_percent || 0).toFixed(2)}%
                </p>
              </div>
              <Badge variant="outline" className={getSeverityColor(assessment.humidity?.severity || 0).color}>
                {getSeverityColor(assessment.humidity?.severity || 0).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}