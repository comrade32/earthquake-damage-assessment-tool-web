document.addEventListener("DOMContentLoaded", function() {
    const signupForm = document.getElementById("signupForm");

    signupForm.addEventListener("submit", async function(event) {
        event.preventDefault();
        const messageBox = document.getElementById('SignUpmsg');
        // Collect form field values
        const data = {
            name: signupForm.name.value.trim(),
            email: signupForm.email.value.trim(),
            mobile: signupForm.mobile.value.trim(),
            address: signupForm.address.value.trim(),
            username: signupForm.username.value.trim(),
            password: signupForm.password.value.trim()
        };

        // Basic validation
        if (!data.name || !data.email || !data.username || !data.password) {
            alert("Please fill in all required fields.");
            return;
        }

        try {
            // Send POST request
            const response = await fetch("/api/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // alert(result.message || "User registered successfully! Please login.");
                messageBox.textContent = "User registered successfully! Please login.";
                signupForm.reset();
                // Optionally redirect to login page
                // Show message for 2.5 seconds, then redirect
                setTimeout(() => {
                window.location.href = "/";
                }, 2500);
                } else {
                    alert(result.message || "Failed to register user.");
                }
        } catch (error) {
            alert("An error occurred during signup. Please try again later.");
            console.error("Signup error:", error);
        }
    });
});
