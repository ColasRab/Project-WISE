"use client"

import { Cloud, CloudRain, Sun, Wind, Droplets, Thermometer } from "lucide-react"
import { motion, easeInOut } from "framer-motion"

interface AnimatedWeatherIconProps {
  type: "wind" | "rain" | "sun" | "cloud" | "humidity" | "temperature"
  className?: string
}

export function AnimatedWeatherIcon({ type, className = "h-12 w-12" }: AnimatedWeatherIconProps) {
  const icons = {
    wind: Wind,
    rain: CloudRain,
    sun: Sun,
    cloud: Cloud,
    humidity: Droplets,
    temperature: Thermometer,
  }

  const Icon = icons[type]

  const animations = {
    wind: {
      x: [0, 5, 0],
      transition: { duration: 2, repeat: Number.POSITIVE_INFINITY, ease: easeInOut },
    },
    rain: {
      y: [0, 3, 0],
      transition: { duration: 1.5, repeat: Number.POSITIVE_INFINITY, ease: easeInOut },
    },
    sun: {
      rotate: 360,
      transition: { duration: 20, repeat: Number.POSITIVE_INFINITY, ease: easeInOut },
    },
    cloud: {
      x: [0, 10, 0],
      transition: { duration: 4, repeat: Number.POSITIVE_INFINITY, ease: easeInOut },
    },
    humidity: {
      scale: [1, 1.1, 1],
      transition: { duration: 2, repeat: Number.POSITIVE_INFINITY, ease: easeInOut },
    },
    temperature: {
      y: [0, -3, 0],
      transition: { duration: 2, repeat: Number.POSITIVE_INFINITY, ease: easeInOut },
    },
  }

  return (
    <motion.div animate={animations[type]} className={className}>
      <Icon className="w-full h-full" />
    </motion.div>
  )
}
