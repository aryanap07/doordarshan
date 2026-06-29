"use strict";

const TOKEN_KEY = "dd_token";
const USER_KEY = "dd_user";

function saveToken(token, remember = false) {
  sessionStorage.setItem(TOKEN_KEY, token);
  if (remember) localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
  localStorage.removeItem(USER_KEY);
}

function _decodePayload(token) {
  try {
    const b64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(b64));
  } catch {
    return null;
  }
}

function isAuthenticated() {
  const token = getToken();
  if (!token) return false;
  const payload = _decodePayload(token);
  if (!payload) return false;
  if (payload.exp && Date.now() / 1000 > payload.exp) {
    clearToken();
    return false;
  }
  return true;
}

function saveUser(user) {
  const json = JSON.stringify(user);
  sessionStorage.setItem(USER_KEY, json);
  if (localStorage.getItem(TOKEN_KEY)) localStorage.setItem(USER_KEY, json);
}

function getUser() {
  const raw =
    sessionStorage.getItem(USER_KEY) || localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function getInitials(username = "") {
  return (
    username
      .split(/\s+/)
      .slice(0, 2)
      .map((w) => w[0]?.toUpperCase() ?? "")
      .join("") || "?"
  );
}

function avatarColor(seed = "") {
  const COLORS = [
    "#2188ff",
    "#3fb950",
    "#d29922",
    "#f85149",
    "#bc8cff",
    "#79c0ff",
    "#56d364",
    "#ffa657",
  ];
  let hash = 0;
  for (const ch of seed) hash = (hash * 31 + ch.charCodeAt(0)) | 0;
  return COLORS[Math.abs(hash) % COLORS.length];
}

function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = "/";
  }
}

function redirectIfAuthed() {
  if (isAuthenticated()) {
    window.location.href = "dashboard";
  }
}

function logout() {
  clearToken();
  window.location.href = "/";
}

window.DoordarshAuth = {
  saveToken,
  getToken,
  clearToken,
  isAuthenticated,
  saveUser,
  getUser,
  getInitials,
  avatarColor,
  requireAuth,
  redirectIfAuthed,
  logout,
};
