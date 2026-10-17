import { computed, ref } from "vue";
import { defineStore } from "pinia";

const ACCESS_TOKEN_KEY = "heladeria_access_token";
const REFRESH_TOKEN_KEY = "heladeria_refresh_token";
const TOKEN_EXPIRY_KEY = "heladeria_token_expiry";

function getStorage(): Storage | null {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function readStorage(key: string): string | null {
  const storage = getStorage();
  if (!storage) return null;

  try {
    return storage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string | null) {
  const storage = getStorage();
  if (!storage) return;

  try {
    if (value === null) {
      storage.removeItem(key);
      return;
    }

    storage.setItem(key, value);
  } catch {
    // ignore storage write errors in non-browser/test contexts
  }
}

function getTokenExpiryMilliseconds(tokenValue: string | null): number | null {
  if (!tokenValue) return null;

  try {
    const payloadSegment = tokenValue.split(".")[1];
    if (!payloadSegment) return null;

    const normalized = payloadSegment
      .replace(/-/g, "+")
      .replace(/_/g, "/")
      .padEnd(Math.ceil(payloadSegment.length / 4) * 4, "=");

    const decoded = JSON.parse(
      typeof window !== "undefined"
        ? window.atob(normalized)
        : globalThis.atob(normalized),
    );

    const expiryEpoch = Number(decoded?.exp);
    return Number.isFinite(expiryEpoch) ? expiryEpoch * 1000 : null;
  } catch {
    return null;
  }
}

function isExpired(tokenValue: string | null): boolean {
  const expiry = getTokenExpiryMilliseconds(tokenValue);
  if (!expiry) return false;
  return Date.now() >= expiry;
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(readStorage(ACCESS_TOKEN_KEY));
  const refreshToken = ref<string | null>(readStorage(REFRESH_TOKEN_KEY));

  const isAuthenticated = computed(
    () => Boolean(token.value) && !isExpired(token.value),
  );

  function setTokens(
    nextAccessToken: string | null,
    nextRefreshToken: string | null,
  ) {
    const nextExpiry = getTokenExpiryMilliseconds(nextAccessToken);
    token.value = nextAccessToken;
    refreshToken.value = nextRefreshToken;

    if (nextAccessToken) {
      writeStorage(ACCESS_TOKEN_KEY, nextAccessToken);
      if (nextExpiry) {
        writeStorage(TOKEN_EXPIRY_KEY, String(nextExpiry));
      }
    } else {
      writeStorage(ACCESS_TOKEN_KEY, null);
      writeStorage(TOKEN_EXPIRY_KEY, null);
    }

    if (nextRefreshToken) {
      writeStorage(REFRESH_TOKEN_KEY, nextRefreshToken);
    } else {
      writeStorage(REFRESH_TOKEN_KEY, null);
    }
  }

  function setToken(nextToken: string | null) {
    setTokens(nextToken, refreshToken.value);
  }

  function logout() {
    setTokens(null, null);
  }

  return {
    token,
    refreshToken,
    isAuthenticated,
    setToken,
    setTokens,
    logout,
  };
});
