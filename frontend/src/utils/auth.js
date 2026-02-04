import { jwtDecode } from "jwt-decode";

export function getToken() {
  return localStorage.getItem("access_token");
}

export function getUserFromToken() {
  const token = getToken();
  if (!token) return null;

  try {
    return jwtDecode(token);
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  return !!getUserFromToken();
}
