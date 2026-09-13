"use strict";

let _ICE_SERVERS = [];

async function loadIceServers() {
  const response = await fetch("/api/v1/ice/config");

  if (!response.ok) {
    throw new Error("Unable to fetch ICE configuration");
  }

  const data = await response.json();

  _ICE_SERVERS = data.iceServers;
}

class WebRTCManager {
  constructor(sendFn, selfUserId) {
    this._send = sendFn;
    this._selfUserId = selfUserId;
    this._peers = new Map();
    this._localStream = null;
    this._handlers = {};
    this._pendingCandidates = new Map();
    this._makingOffer = new Set();
    this._ignoreOffer = new Set();
  }

  _isPolite(remoteUserId) {
    return this._selfUserId < remoteUserId;
  }

  on(event, handler) {
    if (!this._handlers[event]) this._handlers[event] = [];
    this._handlers[event].push(handler);
    return this;
  }

  _emit(event, ...args) {
    for (const h of this._handlers[event] || []) {
      try {
        h(...args);
      } catch (err) {
        console.error("[WebRTC] handler error:", err);
      }
    }
  }

  setLocalStream(stream) {
    this._localStream = stream;
    for (const [, pc] of this._peers) {
      this._addTracksTo(pc);
    }
  }

  _addTracksTo(pc) {
    if (!this._localStream) return;
    const existingSenders = pc.getSenders();
    for (const track of this._localStream.getTracks()) {
      const alreadySending = existingSenders.some(
        (s) => s.track?.kind === track.kind
      );
      if (alreadySending) {
        const sender = existingSenders.find((s) => s.track?.kind === track.kind);
        if (sender && sender.track?.id !== track.id) {
          sender.replaceTrack(track).catch(() => {});
        }
      } else {
        pc.addTrack(track, this._localStream);
      }
    }
  }

  _createPeer(remoteUserId) {
    if (this._peers.has(remoteUserId)) return this._peers.get(remoteUserId);

    const pc = new RTCPeerConnection({ iceServers: _ICE_SERVERS });
    this._peers.set(remoteUserId, pc);

    if (this._localStream) {
      for (const track of this._localStream.getTracks()) {
        pc.addTrack(track, this._localStream);
      }
    }

    pc.addEventListener("icecandidate", ({ candidate }) => {
      if (candidate) {
        this._send({
          type: "ice_candidate",
          target_user_id: remoteUserId,
          candidate: candidate.toJSON(),
        });
      }
    });

    pc.addEventListener("track", ({ streams }) => {
      const stream = streams?.[0];
      if (stream) this._emit("remoteStream", remoteUserId, stream);
    });

    pc.addEventListener("connectionstatechange", () => {
      this._emit("peerState", remoteUserId, pc.connectionState);
      if (pc.connectionState === "failed") {
        pc.restartIce();
      }
    });

    pc.addEventListener("iceconnectionstatechange", () => {
      if (pc.iceConnectionState === "disconnected") {
        setTimeout(() => {
          if (pc.iceConnectionState === "disconnected") pc.restartIce();
        }, 4000);
      }
    });

    pc.addEventListener("negotiationneeded", async () => {
      if (this._makingOffer.has(remoteUserId)) return;
      this._makingOffer.add(remoteUserId);
      try {
        const offer = await pc.createOffer();
        if (pc.signalingState !== "stable") return;
        await pc.setLocalDescription(offer);
        this._send({
          type: "offer",
          target_user_id: remoteUserId,
          sdp: pc.localDescription.sdp,
        });
      } catch (err) {
        console.error("[WebRTC] createOffer error:", err);
      } finally {
        this._makingOffer.delete(remoteUserId);
      }
    });

    return pc;
  }

  initiateCall(remoteUserId) {
    this._createPeer(remoteUserId);
  }

  async handleOffer(fromUserId, sdp) {
    const pc = this._createPeer(fromUserId);
    const polite = this._isPolite(fromUserId);
    const offerCollision =
      this._makingOffer.has(fromUserId) || pc.signalingState !== "stable";

    this._ignoreOffer.delete(fromUserId);

    if (offerCollision) {
      if (!polite) {
        this._ignoreOffer.add(fromUserId);
        return;
      }
      await pc.setLocalDescription({ type: "rollback" });
    }

    await pc.setRemoteDescription({ type: "offer", sdp });
    await pc.setLocalDescription(await pc.createAnswer());
    this._send({
      type: "answer",
      target_user_id: fromUserId,
      sdp: pc.localDescription.sdp,
    });

    await this._drainPendingCandidates(fromUserId, pc);
  }

  async handleAnswer(fromUserId, sdp) {
    const pc = this._peers.get(fromUserId);
    if (!pc) return;
    if (pc.signalingState !== "have-local-offer") return;
    await pc.setRemoteDescription({ type: "answer", sdp });
    await this._drainPendingCandidates(fromUserId, pc);
  }

  async handleIceCandidate(fromUserId, candidateJson) {
    const pc = this._peers.get(fromUserId);
    const cand = new RTCIceCandidate(candidateJson);

    if (!pc || !pc.remoteDescription) {
      if (this._ignoreOffer.has(fromUserId)) return;
      const queue = this._pendingCandidates.get(fromUserId) || [];
      queue.push(cand);
      this._pendingCandidates.set(fromUserId, queue);
      return;
    }

    await pc.addIceCandidate(cand).catch(() => {});
  }

  async _drainPendingCandidates(userId, pc) {
    const queue = this._pendingCandidates.get(userId) || [];
    this._pendingCandidates.delete(userId);
    for (const c of queue) {
      await pc.addIceCandidate(c).catch(() => {});
    }
  }

  replaceVideoTrack(newTrack) {
    for (const [, pc] of this._peers) {
      const sender = pc.getSenders().find((s) => s.track?.kind === "video");
      if (sender) sender.replaceTrack(newTrack).catch(() => {});
    }
  }

  replaceAudioTrack(newTrack) {
    for (const [, pc] of this._peers) {
      const sender = pc.getSenders().find((s) => s.track?.kind === "audio");
      if (sender) sender.replaceTrack(newTrack).catch(() => {});
    }
  }

  closePeer(userId) {
    const pc = this._peers.get(userId);
    if (pc) {
      pc.close();
      this._peers.delete(userId);
    }
    this._pendingCandidates.delete(userId);
    this._makingOffer.delete(userId);
    this._ignoreOffer.delete(userId);
  }

  closeAll() {
    for (const [, pc] of this._peers) pc.close();
    this._peers.clear();
    this._pendingCandidates.clear();
    this._makingOffer.clear();
    this._ignoreOffer.clear();
  }

  getPeerState(userId) {
    return this._peers.get(userId)?.connectionState ?? null;
  }
}

window.DoordarshRTC = WebRTCManager;
window.loadIceServers = loadIceServers;