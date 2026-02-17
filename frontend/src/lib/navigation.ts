// Navigation utility for handling demo page redirects
export const goToDemo = () => {
  if (process.env.NODE_ENV === 'production') {
    // In production, navigate to the demo page on the same domain
    window.location.href = '/demo';
  } else {
    // In development, redirect to the Flask backend
    window.location.href = 'http://localhost:8080';
  }
};

export default goToDemo; 