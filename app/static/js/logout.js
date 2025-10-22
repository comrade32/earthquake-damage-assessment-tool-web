document.addEventListener('DOMContentLoaded', function () {
  const logoutLink = document.querySelector('.logout-link');
  if (logoutLink) {
    logoutLink.addEventListener('click', async function (e) {
      e.preventDefault();
      const token = localStorage.getItem('token');
      await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token }
      });
      localStorage.removeItem('token');
      window.location.href = '/'; // redirect to login
    });
  }
});
