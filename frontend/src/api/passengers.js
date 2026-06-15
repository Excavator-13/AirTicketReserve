import request from "./index";

export function fetchPassengers() {
  return request.get("/passengers/");
}

export function createPassenger(data) {
  return request.post("/passengers/", data);
}

export function deletePassenger(id) {
  return request.delete(`/passengers/${id}/`);
}
