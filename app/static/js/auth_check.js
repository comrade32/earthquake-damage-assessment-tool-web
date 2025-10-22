function checkAuth() {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = '/';  // Redirect to login if no token
  }
}

async function verifyToken() {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = '/';
  } else {
    const response = await fetch('/api/auth-check', {
      method: 'GET',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    if (!response.ok) {
      localStorage.removeItem('token');
      window.location.href = '/';  // Redirect to login if token invalid
    }
  }
}

window.onload = function() {
  checkAuth();
  verifyToken();
};
