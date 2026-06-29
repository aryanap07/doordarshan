"use strict";

const api = window.DoordarshApi;
const auth = window.DoordarshAuth;

const toastContainer = document.getElementById("toast-container");

function showToast(message, type = "info", duration = 3500) {
  const icons = { success: "✓", error: "✕", info: "ℹ" };
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.innerHTML = `
    <span class="toast-icon">${icons[type]}</span>
    <span>${message}</span>
  `;
  toastContainer.appendChild(el);

  setTimeout(() => {
    el.classList.add("leaving");
    el.addEventListener("animationend", () => el.remove(), { once: true });
  }, duration);
}

function openModal(id) {
  document.getElementById(id)?.classList.add("open");
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove("open");
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast("Room code copied!", "success", 2000);
  } catch {
    showToast("Could not copy — try manually.", "error");
  }
}

const roomsGrid = document.getElementById("rooms-grid");
const roomsSection = document.getElementById("rooms-section");

function renderRooms(rooms) {
  if (!rooms.length) {
    roomsGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📡</div>
        <p>No rooms yet. Create one to start broadcasting.</p>
      </div>
    `;
    return;
  }

  const currentUser = auth.getUser();

  roomsGrid.innerHTML = rooms
    .map((room) => {
      const isHost = currentUser && room.host_id === currentUser.id;
      const created = new Date(room.created_at).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });

      return `
      <div class="room-card" data-code="${room.room_code}">
        <div class="flex items-center justify-between gap-2">
          <span class="room-title">${_esc(room.title)}</span>
          ${
            room.is_active
              ? `<span class="live-dot">LIVE</span>`
              : `<span class="badge badge-info">Inactive</span>`
          }
        </div>

        <div
          class="room-code-badge"
          title="Click to copy room code"
          data-copy="${room.room_code}"
        >
          <span class="code-text">${room.room_code}</span>
          <span class="copy-icon">⧉</span>
        </div>

        <div class="room-card-footer">
          <span class="text-muted" style="font-size:.8rem;">${created}</span>
          <div class="flex gap-1">
            ${
              isHost
                ? `
              <button class="btn btn-sm btn-ghost" data-delete="${room.room_code}" title="Delete room">
                🗑
              </button>
            `
                : ""
            }
            <button
              class="btn btn-sm btn-primary"
              data-join="${room.room_code}"
            >Join</button>
          </div>
        </div>
      </div>
    `;
    })
    .join("");
}

function _esc(str) {
  return str.replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[c],
  );
}

async function loadRooms() {
  try {
    const rooms = await api.listRooms();
    renderRooms(rooms);
  } catch (err) {
    showToast(err.message || "Failed to load rooms.", "error");
    roomsGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚠️</div>
        <p>${err.message || "Could not load rooms."}</p>
      </div>
    `;
  }
}

const createRoomForm = document.getElementById("create-room-form");
const roomTitleInput = document.getElementById("room-title");
const createRoomError = document.getElementById("create-room-error");
const createRoomBtn = document.getElementById("create-room-btn");

createRoomForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = roomTitleInput.value.trim();
  if (!title) return;

  createRoomBtn.disabled = true;
  createRoomBtn.innerHTML = '<span class="spinner"></span> Creating…';
  createRoomError.classList.remove("visible");

  try {
    const room = await api.createRoom({ title });
    closeModal("create-room-modal");
    roomTitleInput.value = "";
    showToast(`Room "${room.title}" created!`, "success");
    await loadRooms();
  } catch (err) {
    createRoomError.textContent = err.message || "Failed to create room.";
    createRoomError.classList.add("visible");
  } finally {
    createRoomBtn.disabled = false;
    createRoomBtn.textContent = "Create Room";
  }
});

roomsGrid?.addEventListener("click", async (e) => {
  const copyBtn = e.target.closest("[data-copy]");
  const joinBtn = e.target.closest("[data-join]");
  const deleteBtn = e.target.closest("[data-delete]");

  if (copyBtn) {
    await copyToClipboard(copyBtn.dataset.copy);
    return;
  }

  if (joinBtn) {
    navigateToRoom(joinBtn.dataset.join);
    return;
  }

  if (deleteBtn) {
    const code = deleteBtn.dataset.delete;
    if (!confirm(`Delete room ${code}? This cannot be undone.`)) return;
    try {
      await api.deleteRoom(code);
      showToast("Room deleted.", "success");
      await loadRooms();
    } catch (err) {
      showToast(err.message || "Could not delete room.", "error");
    }
    return;
  }
});

const joinCodeInput = document.getElementById("join-code-input");
const joinCodeBtn = document.getElementById("join-code-btn");

joinCodeBtn?.addEventListener("click", async () => {
  const code = joinCodeInput.value.trim().toUpperCase();
  if (!code) {
    showToast("Enter a room code first.", "error", 2000);
    return;
  }

  joinCodeBtn.disabled = true;
  joinCodeBtn.innerHTML = '<span class="spinner"></span>';

  try {
    await api.getRoom(code);
    navigateToRoom(code);
  } catch (err) {
    showToast(
      err.status === 404 ? "Room not found." : err.message || "Error.",
      "error",
    );
    joinCodeBtn.disabled = false;
    joinCodeBtn.textContent = "Join";
  }
});

joinCodeInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") joinCodeBtn.click();
});

joinCodeInput?.addEventListener("input", () => {
  const pos = joinCodeInput.selectionStart;
  joinCodeInput.value = joinCodeInput.value.toUpperCase();
  joinCodeInput.setSelectionRange(pos, pos);
});

function navigateToRoom(code) {
  window.location.href = `room?room=${encodeURIComponent(code)}`;
}

const scheduleMeetingForm = document.getElementById("schedule-meeting-form");
const meetingTitleInput = document.getElementById("meeting-title");
const meetingDescInput = document.getElementById("meeting-desc");
const meetingTimeInput = document.getElementById("meeting-time");
const scheduleMeetingError = document.getElementById("schedule-meeting-error");
const scheduleMeetingBtn = document.getElementById("schedule-meeting-btn");

scheduleMeetingForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = meetingTitleInput.value.trim();
  const description = meetingDescInput.value.trim() || undefined;
  const scheduled_at = meetingTimeInput.value || undefined;

  if (!title) return;

  scheduleMeetingBtn.disabled = true;
  scheduleMeetingBtn.innerHTML = '<span class="spinner"></span> Scheduling…';
  scheduleMeetingError.classList.remove("visible");

  try {
    await api.createMeeting({ title, description, scheduled_at });
    closeModal("schedule-meeting-modal");
    scheduleMeetingForm.reset();
    showToast("Meeting scheduled!", "success");
    await loadMeetings();
  } catch (err) {
    scheduleMeetingError.textContent =
      err.message || "Failed to schedule meeting.";
    scheduleMeetingError.classList.add("visible");
  } finally {
    scheduleMeetingBtn.disabled = false;
    scheduleMeetingBtn.textContent = "Schedule";
  }
});

const meetingsList = document.getElementById("meetings-list");

async function loadMeetings() {
  if (!meetingsList) return;
  try {
    const meetings = await api.listMeetings();
    renderMeetings(meetings);
  } catch (err) {
    meetingsList.innerHTML = `<p class="text-muted" style="font-size:.875rem;">Could not load meetings.</p>`;
  }
}

function renderMeetings(meetings) {
  if (!meetings.length) {
    meetingsList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📅</div>
        <p>No meetings scheduled yet.</p>
      </div>
    `;
    return;
  }

  const currentUser = auth.getUser();

  meetingsList.innerHTML = meetings
    .map((m) => {
      const d = m.scheduled_at ? new Date(m.scheduled_at) : null;
      const dateStr = d
        ? d.toLocaleDateString("en-IN", { day: "numeric", month: "short" })
        : "—";
      const timeStr = d
        ? d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })
        : "—";
      const isHost = currentUser && m.host_id === currentUser.id;

      return `
      <div class="meeting-item">
        <div class="meeting-time-block">
          <div class="meeting-date">${dateStr}</div>
          <div class="meeting-time">${timeStr}</div>
        </div>
        <div class="meeting-info">
          <div class="meeting-title">${_esc(m.title)}</div>
          ${
            m.description
              ? `<div class="meeting-desc">${_esc(m.description)}</div>`
              : ""
          }
        </div>
        <div class="meeting-actions">
          <span class="${m.is_active ? "badge badge-success" : "badge badge-info"}">
            ${m.is_active ? "Active" : "Ended"}
          </span>
          ${
            isHost
              ? `
            <button class="btn btn-sm btn-ghost" data-delete-meeting="${m.id}" title="Delete">🗑</button>
          `
              : ""
          }
        </div>
      </div>
    `;
    })
    .join("");
}

meetingsList?.addEventListener("click", async (e) => {
  const deleteBtn = e.target.closest("[data-delete-meeting]");
  if (!deleteBtn) return;
  const id = parseInt(deleteBtn.dataset.deleteMeeting, 10);
  if (!confirm("Delete this meeting?")) return;
  try {
    await api.deleteMeeting(id);
    showToast("Meeting deleted.", "success");
    await loadMeetings();
  } catch (err) {
    showToast(err.message || "Could not delete meeting.", "error");
  }
});

document.getElementById("qa-new-room")?.addEventListener("click", () => {
  openModal("create-room-modal");
});

document.getElementById("qa-join-room")?.addEventListener("click", () => {
  joinCodeInput?.focus();
  joinCodeInput?.scrollIntoView({ behavior: "smooth", block: "center" });
});

document.getElementById("qa-schedule")?.addEventListener("click", () => {
  openModal("schedule-meeting-modal");
});

document.querySelectorAll("[data-close-modal]").forEach((btn) => {
  btn.addEventListener("click", () => closeModal(btn.dataset.closeModal));
});

document.querySelectorAll(".modal-overlay").forEach((overlay) => {
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.classList.remove("open");
  });
});

function renderUserBadge() {
  const user = auth.getUser();
  const initials = auth.getInitials(user?.username ?? "");
  const color = auth.avatarColor(user?.username ?? "");

  const el = document.getElementById("user-badge");
  if (!el) return;

  el.innerHTML = `
    <div class="avatar-circle sm" style="background:${color};">${initials}</div>
    <span style="font-size:.875rem;font-weight:500;">${_esc(user?.username ?? "")}</span>
  `;
}

(async function init() {
  auth.requireAuth();
  renderUserBadge();
  await Promise.all([loadRooms(), loadMeetings()]);
})();
