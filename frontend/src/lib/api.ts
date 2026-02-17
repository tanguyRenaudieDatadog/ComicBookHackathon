// API utility for handling different environments
const getApiUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side rendering
    return '';
  }
  
  // In production, use the same domain
  if (process.env.NODE_ENV === 'production') {
    return '';
  }
  
  // In development, proxy to Flask backend
  return '';
};

export const apiCall = async (endpoint: string, options?: RequestInit) => {
  const baseUrl = getApiUrl();
  const url = `${baseUrl}${endpoint}`;
  
  return fetch(url, {
    ...options,
    headers: {
      ...options?.headers,
    },
  });
};

export default apiCall; 