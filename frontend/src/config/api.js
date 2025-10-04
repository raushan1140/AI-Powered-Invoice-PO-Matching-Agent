const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const API = {
  INVOICES: `${BASE_URL}/api/invoices`,
  QUERIES: `${BASE_URL}/api/queries`,
  LEADERBOARD: `${BASE_URL}/api/leaderboard`,
};
