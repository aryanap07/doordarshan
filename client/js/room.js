"use strict";

const api = window.DoordarshApi;
const auth = window.DoordarshAuth;

auth.requireAuth();

const params = new URLSearchParams(window.location.search);
const ROOM_CODE = params.get("room");

if (!ROOM_CODE) window.location.href = "dashboard";

const videoGrid = document.getElementById("video-grid");
const participantsList = document.getElementById("participants-list");
const chatMessages = document.getElementById("chat-messages");
const chatTextarea = document.getElementById("chat-textarea");
const chatSendBtn = document.getElementById("chat-send-btn");
const wsStatusEl = document.getElementById("ws-status");
const wsStatusTextEl = document.getElementById("ws-status-text");
const roomNameEl = document.getElementById("room-name");
const topbarCodeEl = document.getElementById("topbar-code");
const participantCountEl = document.getElementById("participant-count");
const mediaPermBanner = document.getElementById("media-perm-banner");
const permRetryBtn = document.getElementById("perm-retry-btn");

const btnMute = document.getElementById("ctrl-mute");
const btnCamera = document.getElementById("ctrl-camera");
const btnShare = document.getElementById("ctrl-share");
const btnChat = document.getElementById("ctrl-chat");
const btnLeave = document.getElementById("ctrl-leave");

const selfUser = auth.getUser();

const participants = new Map();
let isChatOpen = true;

const toastContainer = document.getElementById("toast-container");

function showToast(message, type = "info", duration = 3500) {
  const icons = { success: "✓", error: "✕", info: "ℹ" };
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span class="toast-icon">${icons[type] ?? "ℹ"}</span><span>${message}</span>`;
  toastContainer.appendChild(el);
  if (duration > 0) {
    setTimeout(() => {
      el.classList.add("leaving");
      el.addEventListener("animationend", () => el.remove(), { once: true });
    }, duration);
  }
  return el;
}

function _esc(str = "") {
  return String(str).replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[c]
  );
}

const media = new window.DoordarshMedia();
const wsManager = new window.DoordarshWS();
const rtc = new window.DoordarshRTC((payload) => wsManager.send(payload));

media.on("stream", (stream) => {
  rtc.setLocalStream(stream);
  hidePremBanner();
  attachLocalStream(stream);
});

media.on("error", (err) => {
  console.warn("[Media] Error:", err.name, err.message);
  if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
    showPermBanner("Camera and microphone access was denied.");
  } else if (err.name === "NotFoundError") {
    showPermBanner("No camera or microphone found. Joining audio-only.");
    media.startAudioOnly().catch(() => {});
  } else {
    showToast("Could not access media: " + err.message, "error", 5000);
  }
});

media.on("micToggle", (muted) => {
  btnMute.classList.toggle("muted", muted);
  btnMute.querySelector(".ctrl-icon").textContent = muted ? "🔇" : "🎤";
  btnMute.querySelector(".ctrl-label").textContent = muted ? "Unmute" : "Mute";
  const selfTile = videoGrid.querySelector(`[data-uid="${selfUser.id}"]`);
  if (selfTile) {
    const existing = selfTile.querySelector(".tile-mute-icon");
    if (muted && !existing) {
      const icon = document.createElement("div");
      icon.className = "tile-mute-icon";
      icon.textContent = "🔇";
      selfTile.querySelector(".tile-label")?.appendChild(icon);
    } else if (!muted && existing) {
      existing.remove();
    }
  }
});

media.on("cameraToggle", (off) => {
  updateCameraUI(off);
  const selfTile = videoGrid.querySelector(`[data-uid="${selfUser.id}"]`);
  if (selfTile) {
    const avatar = selfTile.querySelector(".tile-avatar");
    const video = selfTile.querySelector("video");
    if (avatar) avatar.style.display = off ? "flex" : "none";
    if (video) video.style.display = off ? "none" : "block";
  }
});

media.on("screenShare", (screenTrack) => {
  rtc.replaceVideoTrack(screenTrack);
  updateScreenShareUI(true);
  const selfTile = videoGrid.querySelector(`[data-uid="${selfUser.id}"]`);
  if (selfTile) {
    const video = selfTile.querySelector("video");
    if (video && media.getStream()) {
      const dummyStream = new MediaStream([screenTrack]);
      video.srcObject = dummyStream;
      video.play().catch(() => {});
      const avatar = selfTile.querySelector(".tile-avatar");
      if (avatar) avatar.style.display = "none";
      video.style.display = "block";
    }
  }
});

media.on("screenShareStop", (camTrack) => {
  if (camTrack) rtc.replaceVideoTrack(camTrack);
  updateScreenShareUI(false);
  const selfTile = videoGrid.querySelector(`[data-uid="${selfUser.id}"]`);
  if (selfTile) {
    const video = selfTile.querySelector("video");
    if (video && media.getStream()) {
      video.srcObject = media.getStream();
      video.play().catch(() => {});
    }
    const off = media.isCamOff();
    const avatar = selfTile.querySelector(".tile-avatar");
    if (avatar) avatar.style.display = off ? "flex" : "none";
    if (video) video.style.display = off ? "none" : "block";
  }
});

media.on("videoTrackChanged", (track) => {
  rtc.replaceVideoTrack(track);
  const selfTile = videoGrid.querySelector(`[data-uid="${selfUser.id}"]`);
  if (selfTile) {
    const video = selfTile.querySelector("video");
    if (video && media.getStream()) {
      video.srcObject = media.getStream();
    }
  }
});

media.on("audioTrackChanged", (track) => {
  rtc.replaceAudioTrack(track);
});

wsManager.on("status", setWsStatus);
wsManager.on("open", onWsOpen);
wsManager.on("close", () => {});
wsManager.on("error", () => console.warn("[WS] connection error"));
wsManager.on("reconnecting", ({ delay }) => {
  showToast(`Connection lost — reconnecting in ${delay / 1000}s…`, "info");
});
wsManager.on("reconnect_failed", () => {
  showToast("Could not reconnect. Refresh the page to retry.", "error", 0);
});
wsManager.on("auth_error", () => {
  showToast("Session expired. Please sign in again.", "error");
  auth.logout();
});

wsManager.on("msg:ping", () => wsManager.send({ type: "pong" }));
wsManager.on("msg:participant_list", handleParticipantList);
wsManager.on("msg:participant_joined", handleParticipantJoined);
wsManager.on("msg:participant_left", handleParticipantLeft);
wsManager.on("msg:offer", (msg) => rtc.handleOffer(msg.from_user_id, msg.sdp));
wsManager.on("msg:answer", (msg) => rtc.handleAnswer(msg.from_user_id, msg.sdp));
wsManager.on("msg:ice_candidate", (msg) =>
  rtc.handleIceCandidate(msg.from_user_id, msg.candidate)
);
wsManager.on("msg:direct_message", handleIncomingDm);
wsManager.on("msg:error", (msg) =>
  showToast(`Server: ${msg.message}`, "error")
);

rtc.on("remoteStream", (userId, stream) => {
  attachStream(userId, stream);
});

rtc.on("peerState", (userId, state) => {
  const tile = videoGrid.querySelector(`[data-uid="${userId}"]`);
  if (!tile) return;
  const indicator = tile.querySelector(".tile-conn-state");
  if (state === "connected" || state === "completed") {
    if (indicator) indicator.remove();
  } else if (state === "connecting" || state === "checking") {
    if (!indicator) {
      const el = document.createElement("div");
      el.className = "tile-conn-state";
      el.textContent = "Connecting…";
      tile.querySelector(".tile-label")?.prepend(el);
    }
  } else if (state === "failed" || state === "disconnected") {
    if (indicator) indicator.textContent = "Reconnecting…";
  }
});

function setWsStatus(state) {
  wsStatusEl.className = `ws-status ${state}`;
  const labels = {
    connecting: "Connecting…",
    connected: "Live",
    disconnected: "Disconnected",
  };
  if (wsStatusTextEl) wsStatusTextEl.textContent = labels[state] ?? state;
}

function onWsOpen() {
  showToast("Connected to room", "success", 2000);
  addSelfTile();
}

function addSelfTile() {
  if (videoGrid.querySelector(`[data-uid="${selfUser.id}"]`)) return;
  const initials = auth.getInitials(selfUser.username);
  const color = auth.avatarColor(String(selfUser.id));
  const tile = document.createElement("div");
  tile.className = "video-tile self-tile";
  tile.dataset.uid = selfUser.id;
  tile.innerHTML = `
    <video autoplay playsinline muted></video>
    <div class="tile-avatar">
      <div class="avatar-circle" style="background:${color};">${initials}</div>
      <span class="tile-username">${_esc(selfUser.username)} (You)</span>
    </div>
    <div class="tile-label">
      <span class="tile-name-pill">${_esc(selfUser.username)} · You</span>
    </div>
  `;
  videoGrid.appendChild(tile);
  participants.set(selfUser.id, { user_id: selfUser.id, username: selfUser.username });
  updateGridClass();
  updateParticipantCount();

  const stream = media.getStream();
  if (stream) attachLocalStream(stream);
}

function attachLocalStream(stream) {
  const tile = videoGrid.querySelector(`[data-uid="${selfUser.id}"]`);
  if (!tile) return;
  const video = tile.querySelector("video");
  const avatar = tile.querySelector(".tile-avatar");
  if (video) {
    video.srcObject = stream;
    video.muted = true;
    video.play().catch(() => {});
  }
  const hasVideo = stream.getVideoTracks().length > 0 && !media.isCamOff();
  if (avatar) avatar.style.display = hasVideo ? "none" : "flex";
  if (video) video.style.display = hasVideo ? "block" : "none";

  addSelfToParticipantList();
}

function addSelfToParticipantList() {
  if (participantsList.querySelector(`[data-uid="${selfUser.id}"]`)) return;
  const initials = auth.getInitials(selfUser.username);
  const color = auth.avatarColor(String(selfUser.id));
  const item = document.createElement("div");
  item.className = "participant-item";
  item.dataset.uid = selfUser.id;
  item.innerHTML = `
    <div class="avatar-circle sm" style="background:${color};">${initials}</div>
    <span class="participant-name">${_esc(selfUser.username)}</span>
    <span class="participant-badge">You</span>
  `;
  participantsList.appendChild(item);
}

function handleParticipantList(msg) {
  for (const [uid] of participants) {
    if (uid !== selfUser.id) {
      removeParticipant(uid);
      rtc.closePeer(uid);
    }
  }
  for (const p of msg.participants) {
    if (p.user_id !== selfUser.id) {
      addParticipant(p, false);
      rtc.initiateCall(p.user_id);
    }
  }
}

function handleParticipantJoined(msg) {
  if (msg.user_id === selfUser.id) return;
  addParticipant({ user_id: msg.user_id, username: msg.username }, false);
  addSystemMsg(`${msg.username} joined`);
  showToast(`${msg.username} joined the room`, "info", 2500);
  rtc.initiateCall(msg.user_id);
}

function handleParticipantLeft(msg) {
  rtc.closePeer(msg.user_id);
  removeParticipant(msg.user_id);
  addSystemMsg(`${msg.username} left`);
  showToast(`${msg.username} left`, "info", 2000);
}

function addParticipant(p, isSelf) {
  if (participants.has(p.user_id)) return;
  participants.set(p.user_id, p);

  const initials = auth.getInitials(p.username);
  const color = auth.avatarColor(String(p.user_id));

  const tile = document.createElement("div");
  tile.className = `video-tile${isSelf ? " self-tile" : ""}`;
  tile.dataset.uid = p.user_id;
  tile.innerHTML = `
    <video autoplay playsinline></video>
    <div class="tile-avatar">
      <div class="avatar-circle" style="background:${color};">${initials}</div>
      <span class="tile-username">${_esc(p.username)}${isSelf ? " (You)" : ""}</span>
    </div>
    <div class="tile-label">
      <span class="tile-name-pill">${_esc(p.username)}${isSelf ? " · You" : ""}</span>
    </div>
  `;
  videoGrid.appendChild(tile);
  updateGridClass();

  const item = document.createElement("div");
  item.className = "participant-item";
  item.dataset.uid = p.user_id;
  item.innerHTML = `
    <div class="avatar-circle sm" style="background:${color};">${initials}</div>
    <span class="participant-name">${_esc(p.username)}</span>
    ${isSelf ? '<span class="participant-badge">You</span>' : ""}
  `;
  participantsList.appendChild(item);

  updateParticipantCount();
}

function removeParticipant(userId) {
  participants.delete(userId);
  videoGrid.querySelector(`[data-uid="${userId}"]`)?.remove();
  participantsList.querySelector(`[data-uid="${userId}"]`)?.remove();
  updateGridClass();
  updateParticipantCount();
}

function attachStream(userId, stream) {
  const tile = videoGrid.querySelector(`[data-uid="${userId}"]`);
  if (!tile) return;
  const video = tile.querySelector("video");
  const avatar = tile.querySelector(".tile-avatar");
  if (video) {
    video.srcObject = stream;
    video.play().catch(() => {});
    stream.addEventListener("active", () => {
      if (avatar && stream.getVideoTracks().some((t) => t.enabled && t.readyState === "live")) {
        avatar.style.display = "none";
        video.style.display = "block";
      }
    });
    const checkVideo = () => {
      const hasLiveVideo = stream
        .getVideoTracks()
        .some((t) => t.enabled && t.readyState === "live");
      if (avatar) avatar.style.display = hasLiveVideo ? "none" : "flex";
      if (video) video.style.display = hasLiveVideo ? "block" : "none";
    };
    stream.getVideoTracks().forEach((t) => {
      t.addEventListener("ended", checkVideo);
      t.addEventListener("mute", checkVideo);
      t.addEventListener("unmute", checkVideo);
    });
    stream.addEventListener("addtrack", checkVideo);
    stream.addEventListener("removetrack", checkVideo);
    checkVideo();
  }
}

function updateGridClass() {
  const n = Math.min(participants.size, 9);
  videoGrid.className = `video-grid count-${Math.max(n, 1)}`;
}

function updateParticipantCount() {
  if (participantCountEl) participantCountEl.textContent = participants.size;
}

function handleIncomingDm(msg) {
  const sender = participants.get(msg.from_user_id);
  const name = sender?.username ?? `User ${msg.from_user_id}`;
  appendChatMsg(name, msg.content, msg.from_user_id === selfUser.id);

  if (!isChatOpen) {
    const badge = document.getElementById("chat-unread-badge");
    if (badge) {
      badge.textContent = (parseInt(badge.textContent || "0", 10) + 1).toString();
      badge.style.display = "inline";
    }
  }
}

function appendChatMsg(name, content, isSelf) {
  const time = new Date().toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
  const el = document.createElement("div");
  el.className = `chat-msg${isSelf ? " self" : ""}`;
  el.innerHTML = `
    <div class="chat-msg-header">
      <span class="chat-msg-name">${_esc(name)}</span>
      <span class="chat-msg-time">${time}</span>
    </div>
    <div class="chat-msg-body">${_esc(content)}</div>
  `;
  chatMessages.appendChild(el);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addSystemMsg(text) {
  const el = document.createElement("div");
  el.className = "chat-system-msg";
  el.textContent = text;
  chatMessages.appendChild(el);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function sendChatMessage(content) {
  if (!content.trim()) return;
  appendChatMsg(selfUser.username, content, true);

  let sent = 0;
  for (const [uid] of participants) {
    if (uid === selfUser.id) continue;
    wsManager.send({ type: "direct_message", target_user_id: uid, content });
    sent++;
  }

  if (sent === 0) addSystemMsg("No one else is in the room yet.");
}

chatSendBtn?.addEventListener("click", () => {
  const content = chatTextarea.value.trim();
  if (!content) return;
  sendChatMessage(content);
  chatTextarea.value = "";
  chatTextarea.style.height = "auto";
});

chatTextarea?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatSendBtn.click();
  }
});

chatTextarea?.addEventListener("input", () => {
  chatTextarea.style.height = "auto";
  chatTextarea.style.height = `${chatTextarea.scrollHeight}px`;
});

btnMute?.addEventListener("click", () => {
  media.toggleMic();
});

btnCamera?.addEventListener("click", () => {
  media.toggleCamera();
});

btnShare?.addEventListener("click", async () => {
  if (media.isScreenSharing()) {
    media.stopScreenShare();
  } else {
    btnShare.disabled = true;
    const track = await media.startScreenShare();
    btnShare.disabled = false;
    if (!track) showToast("Screen sharing cancelled.", "info", 2000);
  }
});

btnChat?.addEventListener("click", () => {
  isChatOpen = !isChatOpen;
  const sidebar = document.getElementById("room-sidebar");
  sidebar?.classList.toggle("collapsed", !isChatOpen);
  btnChat.classList.toggle("active", isChatOpen);

  if (isChatOpen) {
    const badge = document.getElementById("chat-unread-badge");
    if (badge) {
      badge.textContent = "";
      badge.style.display = "none";
    }
  }
});

btnLeave?.addEventListener("click", leaveRoom);

async function leaveRoom() {
  rtc.closeAll();
  media.stop();
  wsManager.disconnect(1000, "User left");

  try {
    await api.leaveRoom(ROOM_CODE);
  } catch {}

  window.location.href = "dashboard";
}

window.addEventListener("beforeunload", () => {
  wsManager.send({ type: "leave" });
  wsManager.disconnect(1000, "Page unload");
  media.stop();
  rtc.closeAll();
});

document.querySelectorAll(".sidebar-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document
      .querySelectorAll(".sidebar-tab")
      .forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");

    const target = tab.dataset.tab;
    document.querySelectorAll(".sidebar-panel").forEach((p) => {
      p.classList.toggle("hidden", p.dataset.panel !== target);
    });
  });
});

function updateCameraUI(off) {
  btnCamera.classList.toggle("muted", off);
  btnCamera.querySelector(".ctrl-icon").textContent = off ? "📷" : "📹";
  btnCamera.querySelector(".ctrl-label").textContent = off ? "Show cam" : "Camera";
}

function updateScreenShareUI(sharing) {
  btnShare.classList.toggle("active", sharing);
  btnShare.querySelector(".ctrl-icon").textContent = sharing ? "🖥️" : "🖥";
  btnShare.querySelector(".ctrl-label").textContent = sharing ? "Stop share" : "Share";
}

function showPermBanner(msg) {
  if (!mediaPermBanner) return;
  const msgEl = mediaPermBanner.querySelector(".perm-msg");
  if (msgEl) msgEl.textContent = msg;
  mediaPermBanner.style.display = "flex";
}

function hidePremBanner() {
  if (mediaPermBanner) mediaPermBanner.style.display = "none";
}

permRetryBtn?.addEventListener("click", async () => {
  hidePremBanner();
  await media.start().catch(() => {});
});

async function initRoomInfo() {
  try {
    const room = await api.getRoom(ROOM_CODE);
    if (roomNameEl) roomNameEl.textContent = room.title;
    document.title = `${room.title} — Doordarshan`;
  } catch {
    if (roomNameEl) roomNameEl.textContent = ROOM_CODE;
  }

  if (topbarCodeEl) {
    topbarCodeEl.querySelector(".code-text").textContent = ROOM_CODE;
    topbarCodeEl.addEventListener("click", async () => {
      await navigator.clipboard.writeText(ROOM_CODE).catch(() => {});
      showToast("Room code copied!", "success", 1800);
    });
  }
}

window.DoordarshRoom = { showToast };

(async function init() {
  await initRoomInfo();

  await media.start().catch(() => {});

  await api.joinRoom(ROOM_CODE);

  wsManager.connect(api.buildWsUrl(ROOM_CODE));
})();
