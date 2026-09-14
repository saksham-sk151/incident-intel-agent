import { useEffect, useState } from "react";

const STORAGE_KEY = "incident-intel-theme";

function getInitialTheme() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
  } catch {
    // localStorage can throw in some contexts (private browsing, etc.) --
    // fall through to the system-preference default rather than crash.
  }
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  return prefersDark ? "dark" : "light";
}

// Applies the theme to <html data-theme="..."> (CSS in App.css keys off
// this attribute) and persists the user's explicit choice so it survives a
// reload -- once they've toggled manually, we stop following the OS
// setting for this page, which is the behavior people expect from an
// explicit toggle.
export function useTheme() {
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // ignore -- theme still applies for this session even if it can't persist
    }
  }, [theme]);

  function toggleTheme() {
    setTheme((t) => (t === "dark" ? "light" : "dark"));
  }

  return { theme, toggleTheme };
}
