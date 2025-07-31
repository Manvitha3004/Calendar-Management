import { useState, useEffect } from 'react';
import create from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  token: null,
  setUser: (user) => set({ user }),
  setToken: (token) => {
    set({ token });
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  },
  clearAuth: () => {
    set({ user: null, token: null });
    localStorage.removeItem('token');
  },
}));

export function useAuth() {
  const { user, token, setUser, setToken, clearAuth } = useAuthStore();

  useEffect(() => {
    /* global google */
    if (window.google) {
      google.accounts.id.initialize({
        client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
      });
      google.accounts.id.prompt();
    }
  }, []);

  function handleCredentialResponse(response) {
    // Decode JWT token to get user info
    const base64Url = response.credential.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );
    const userObject = JSON.parse(jsonPayload);
    setUser(userObject);
    setToken(response.credential);
  }

  function signOut() {
    clearAuth();
    if (window.google) {
      google.accounts.id.disableAutoSelect();
    }
  }

  return { user, token, signOut };
}
