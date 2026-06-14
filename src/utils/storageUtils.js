// src/utils/storageUtils.js

const VERSION_PREFIX = "devops_quiz_v1_";

export function saveToStorage(key, value) {
  try {
    const serialized = JSON.stringify(value);
    localStorage.setItem(VERSION_PREFIX + key, serialized);
  } catch (err) {
    console.error("Error saving to localStorage", err);
  }
}

export function loadFromStorage(key, defaultValue = null) {
  try {
    const serialized = localStorage.getItem(VERSION_PREFIX + key);
    if (serialized === null) {
      return defaultValue;
    }
    return JSON.parse(serialized);
  } catch (err) {
    console.error("Error loading from localStorage", err);
    return defaultValue;
  }
}

export function clearStoragePrefix(prefix) {
  try {
    const fullPrefix = VERSION_PREFIX + prefix;
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(fullPrefix)) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(k => localStorage.removeItem(k));
  } catch (err) {
    console.error("Error clearing localStorage prefix", err);
  }
}

export function clearAllStorage() {
  try {
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(VERSION_PREFIX)) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(k => localStorage.removeItem(k));
  } catch (err) {
    console.error("Error clearing all localStorage", err);
  }
}
