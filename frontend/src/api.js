// Set VITE_API_URL in Vercel's project env vars to your deployed backend,
// e.g. https://ai-notes-backend.onrender.com/api
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(username, password) {
  const res = await fetch(`${BASE_URL}/auth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Login failed");
  const data = await res.json();
  localStorage.setItem("access_token", data.access);
  return data;
}

export async function fetchNotes() {
  const res = await fetch(`${BASE_URL}/notes/notes/`, {
    headers: authHeaders(),
  });

  if (!res.ok) {
    throw new Error("Failed to fetch notes");
  }

  const data = await res.json();

  console.log("NOTES API RESPONSE:", data);
  console.log("IS ARRAY:", Array.isArray(data));

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.results)) {
    return data.results;
  }

  console.error("Unexpected notes response:", data);
  return [];
}

export async function createNote(title, content) {
  const res = await fetch(`${BASE_URL}/notes/notes/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ title, content }),
  });
  if (!res.ok) throw new Error("Failed to create note");
  return res.json();
}
