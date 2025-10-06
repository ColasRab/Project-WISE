"use client"

import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface TimePickerProps {
  value: string
  onChange: (value: string) => void
}

export function TimePicker({ value, onChange }: TimePickerProps) {
  const hours = Array.from({ length: 24 }, (_, i) => i)

  return (
    <div className="space-y-2">
      <Label>Time</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-full md:w-[180px] bg-transparent hover:bg-accent/50 transition-colors">
          <SelectValue placeholder="Select time" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Day (24 hours)</SelectItem>
          {hours.map((hour) => (
            <SelectItem key={hour} value={hour.toString()}>
              {hour.toString().padStart(2, "0")}:00
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
