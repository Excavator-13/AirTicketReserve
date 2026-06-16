import { defineStore } from "pinia";
import { fetchCities, searchFlights, fetchFlightDetail } from "@/api/flights";

export const useFlightStore = defineStore("flight", {
  state: () => ({
    searchParams: {
      departure_city: "",
      arrival_city: "",
      departure_airport_code: "",
      arrival_airport_code: "",
      date: "",
      is_round_trip: false,
      return_date: "",
      adults: 1,
      children: 0,
      infants: 0,
    },
    outboundFlights: [],
    returnFlights: [],
    currentFlight: null,
    loading: false,
    searchId: null,
    searchSortBy: "price",
    searchFilters: {
      directOnly: false,
      airlines: [],
      departureAirports: [],
      arrivalAirports: [],
      aircraftSizes: [],
      timeRange: [0, 24],
      arrivalTimeRange: [0, 24],
    },
  }),

  actions: {
    async searchFlights(params) {
      this.loading = true;
      this.searchParams = { ...this.searchParams, ...params };
      this.searchId = Date.now();
      this.searchSortBy = "price";
      this.searchFilters = {
        directOnly: false,
        airlines: [],
        departureAirports: [],
        arrivalAirports: [],
        aircraftSizes: [],
        timeRange: [0, 24],
        arrivalTimeRange: [0, 24],
      };
      try {
        const data = await searchFlights(params);
        this.outboundFlights = data.outbound || [];
        this.returnFlights = data.return || [];
      } finally {
        this.loading = false;
      }
    },

    async fetchFlightDetail(id) {
      this.loading = true;
      try {
        this.currentFlight = await fetchFlightDetail(id);
      } finally {
        this.loading = false;
      }
    },

    async fetchCities(keyword) {
      return await fetchCities(keyword);
    },
  },
});
