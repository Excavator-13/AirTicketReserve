import request from "./index";

export function fetchCities(keyword) {
  return request.get("/flights/cities/", { params: { keyword } });
}

export function searchFlights(params) {
  return request.get("/flights/search/", { params });
}

export function fetchFlightDetail(id) {
  return request.get(`/flights/${id}/`);
}
