"use client"

import * as React from "react"
import { MapPin, Loader2, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

export interface PhilippineLocation {
  name: string
  province: string
  lat: number
  lon: number
  display_name: string
}

interface LocationAutocompleteProps {
  value: PhilippineLocation | null
  onChange: (location: PhilippineLocation | null) => void
}

interface NominatimResult {
  place_id: number
  display_name: string
  lat: string
  lon: string
  address: {
    city?: string
    town?: string
    municipality?: string
    province?: string
    state?: string
    country?: string
  }
}

export function LocationAutocomplete({ value, onChange }: LocationAutocompleteProps) {
  const [open, setOpen] = React.useState(false)
  const [searchQuery, setSearchQuery] = React.useState("")
  const [suggestions, setSuggestions] = React.useState<PhilippineLocation[]>([])
  const [loading, setLoading] = React.useState(false)
  const debounceTimeout = React.useRef<NodeJS.Timeout>()

  // Fetch suggestions via proxy API
  const fetchSuggestions = async (query: string) => {
    if (!query || query.length < 2) {
      setSuggestions([])
      return
    }

    setLoading(true)
    try {
      // Call your Next.js API route instead of Nominatim directly
      const response = await fetch(`/api/location?q=${encodeURIComponent(query)}`)
      if (!response.ok) throw new Error("Failed to fetch suggestions")

      const data: NominatimResult[] = await response.json()

      const locations: PhilippineLocation[] = data.map((result) => {
        const cityName =
          result.address.city ||
          result.address.town ||
          result.address.municipality ||
          "Unknown Location"

        const province = result.address.province || result.address.state || "Philippines"

        return {
          name: cityName,
          province: province,
          lat: parseFloat(result.lat),
          lon: parseFloat(result.lon),
          display_name: result.display_name,
        }
      })

      setSuggestions(locations)
    } catch (error) {
      console.error("Error fetching location suggestions:", error)
      setSuggestions([])
    } finally {
      setLoading(false)
    }
  }

  // Debounce search input
  React.useEffect(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current)
    }

    debounceTimeout.current = setTimeout(() => {
      fetchSuggestions(searchQuery)
    }, 500)

    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current)
      }
    }
  }, [searchQuery])

  const handleSelect = (location: PhilippineLocation) => {
    onChange(location)
    setSearchQuery("")
    setSuggestions([])
    setOpen(false)
  }

  const handleClear = () => {
    onChange(null)
    setSearchQuery("")
    setSuggestions([])
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className="relative">
          <div
            className={cn(
              "flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors",
              "hover:bg-accent/50 cursor-pointer",
              "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
              !value && "text-muted-foreground"
            )}
            onClick={() => setOpen(true)}
          >
            <div className="flex items-center gap-2 flex-1 overflow-hidden">
              <MapPin className="h-4 w-4 shrink-0 text-muted-foreground" />
              {value ? (
                <span className="truncate">
                  {value.name}, {value.province}
                </span>
              ) : (
                <span>Search location in Philippines...</span>
              )}
            </div>
            {value && (
              <X
                className="h-4 w-4 shrink-0 opacity-50 hover:opacity-100"
                onClick={(e) => {
                  e.stopPropagation()
                  handleClear()
                }}
              />
            )}
          </div>
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="start">
        <Command shouldFilter={false}>
          <div className="flex items-center border-b px-3">
            <MapPin className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            <Input
              placeholder="Type to search cities in Philippines..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="border-0 shadow-none focus-visible:ring-0 h-10"
            />
            {loading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
          </div>
          <CommandList>
            {!loading && searchQuery && suggestions.length === 0 && (
              <CommandEmpty>No locations found. Try searching for a city name.</CommandEmpty>
            )}
            {!loading && !searchQuery && (
              <div className="py-6 text-center text-sm text-muted-foreground">
                Start typing to search for locations...
              </div>
            )}
            {suggestions.length > 0 && (
              <CommandGroup>
                {suggestions.map((location, index) => (
                  <CommandItem
                    key={`${location.lat}-${location.lon}-${index}`}
                    value={location.display_name}
                    onSelect={() => handleSelect(location)}
                    className="cursor-pointer"
                  >
                    <MapPin className="mr-2 h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-col flex-1 min-w-0">
                      <span className="font-medium truncate">{location.name}</span>
                      <span className="text-xs text-muted-foreground truncate">{location.province}</span>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
