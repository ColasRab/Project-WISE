"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle } from "lucide-react"
import { motion } from "framer-motion"
import { AnimatedWeatherIcon } from "./animated-weather-icon"

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
      <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
        <motion.div
          className={`h-full ${color} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
        />
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
              <Badge variant="outline" className={getSeverityColor(assessment.overall_risk).color}>
                Risk: {Math.round(assessment.overall_risk * 100)}%
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-lg font-medium">{assessment.recommendation}</p>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div className="grid grid-cols-1 md:grid-cols-2 gap-4" variants={containerVariants}>
        {/* Wind */}
        <motion.div variants={cardVariants}>
          <Card className="border-cyan-500/20 bg-cyan-500/5 hover:border-cyan-500/40 hover:shadow-lg transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Wind Conditions</CardTitle>
              <AnimatedWeatherIcon
                type="wind"
                className="h-5 w-5 text-cyan-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                >
                  {assessment.wind.category}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">{predictions.wind_speed_ms.toFixed(2)} m/s</p>
              </div>
              <Badge variant="outline" className={getSeverityColor(assessment.wind.severity).color}>
                {getSeverityColor(assessment.wind.severity).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>

        {/* Precipitation */}
        <motion.div variants={cardVariants}>
          <Card className="border-indigo-500/20 bg-indigo-500/5 hover:border-indigo-500/40 hover:shadow-lg transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Precipitation</CardTitle>
              <AnimatedWeatherIcon
                type="rain"
                className="h-5 w-5 text-indigo-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.3 }}
                >
                  {assessment.precipitation.category}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">{predictions.precipitation_mm.toFixed(2)} mm</p>
              </div>
              <Badge variant="outline" className={getSeverityColor(assessment.precipitation.severity).color}>
                {getSeverityColor(assessment.precipitation.severity).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>

        {/* Temperature */}
        <motion.div variants={cardVariants}>
          <Card className="border-amber-500/20 bg-amber-500/5 hover:border-amber-500/40 hover:shadow-lg transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Temperature</CardTitle>
              <AnimatedWeatherIcon
                type="temperature"
                className="h-5 w-5 text-amber-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.4 }}
                >
                  {assessment.temperature.category}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">{predictions.temperature_c.toFixed(2)} °C</p>
              </div>
              <Badge variant="outline" className={getSeverityColor(assessment.temperature.severity).color}>
                {getSeverityColor(assessment.temperature.severity).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>

        {/* Humidity */}
        <motion.div variants={cardVariants}>
          <Card className="border-emerald-500/20 bg-emerald-500/5 hover:border-emerald-500/40 hover:shadow-lg transition-all duration-300 group">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Humidity</CardTitle>
              <AnimatedWeatherIcon
                type="humidity"
                className="h-5 w-5 text-emerald-500 group-hover:scale-110 transition-transform"
              />
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <motion.div
                  className="text-3xl font-bold"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.5 }}
                >
                  {assessment.humidity.category}
                </motion.div>
                <p className="text-xs text-muted-foreground mt-1">{predictions.humidity_percent.toFixed(2)}%</p>
              </div>
              <Badge variant="outline" className={getSeverityColor(assessment.humidity.severity).color}>
                {getSeverityColor(assessment.humidity.severity).label}
              </Badge>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
