// document.getElementById('loginForm').addEventListener('submit', async function(e) {
//     e.preventDefault();
//     const username = document.getElementById('username').value;
//     const password = document.getElementById('password').value;
//     const response = await fetch('/api/login', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ username, password })
//     });
//     const result = await response.json();
//     const messageBox = document.getElementById('loginMessage');
//     if (result.success) {
//         messageBox.textContent = result.message;
//         messageBox.style.color = "limegreen";
//         // Redirect on success, if needed
//         window.location.href = "/dashboard";
//     } else {
//         messageBox.textContent = result.message;
//         messageBox.style.color = "red";
//     }
// });




document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const result = await response.json();
    const messageBox = document.getElementById('loginMessage');
    if (result.success) {
        // Store the token on successful login
        localStorage.setItem('token', result.token);
        
        messageBox.textContent = "Login successful";
        messageBox.style.color = "limegreen";
        
        // Redirect on success
        window.location.href = "/dashboard";
    } else {
        messageBox.textContent = result.message;
        messageBox.style.color = "red";
    }
});
