import { defineStore } from "pinia";
import { fetchCities, searchFlights, fetchFlightDetail } from "@/api/flights";

export const useFlightStore = defineStore("flight", {
  state: () => ({
    searchParams: {
      departure_city: "",
      arrival_city: "",
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
  }),

  actions: {
    async searchFlights(params) {
      this.loading = true;
      this.searchParams = { ...this.searchParams, ...params };
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
