document.addEventListener('DOMContentLoaded', function () {
    const backend_url = "http://192.168.2.172:80";
    
    // References to the login and registration forms
    const loginForm = document.getElementById('loginForm');
    const registrationForm = document.getElementById('registrationForm');

    // References to the show/hide registration/login links
    const showRegistrationLink = document.getElementById('showRegistrationForm');
    const showLoginLink = document.getElementById('showLoginForm');

    // Add event listener to show the registration form
    showRegistrationLink.addEventListener('click', function () {
        loginForm.style.display = 'none';
        registrationForm.style.display = 'block';
    });

    // Add event listener to show the login form
    showLoginLink.addEventListener('click', function () {
        registrationForm.style.display = 'none';
        loginForm.style.display = 'block';
    });

    // Add event listener to the login form
    loginForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form submission

        // Get the values from the login form
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        // Send a request to your backend for authentication (similar to your previous code)
        fetch(backend_url + '/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        })
        .then(response => {
            if (response.ok) {
                // Successful login
                console.log('Login successful');
                window.location.href = 'index.html'; // Redirect to index.html
            } else {
                // Failed login
                console.error('Login failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Add event listener to the registration form
    registrationForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form submission

        // Get the values from the registration form
        const email = document.getElementById('registerEmail').value;
        const firstName = document.getElementById('registerFirstName').value; // Retrieve first name
        const lastName = document.getElementById('registerLastName').value; // Retrieve last name
        const password = document.getElementById('registerPassword').value;

        // Send a request to your backend for registration
        fetch(backend_url + '/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, first_name: firstName, Last_name: lastName, password }), // Include first_name and Last_name
        })
        .then(response => {
            if (response.ok) {
                // Successful registration
                console.log('Registration successful');
                alert('Registration successful. You can now login.');
                registrationForm.style.display = 'none';
                loginForm.style.display = 'block';
            } else {
                // Failed registration
                console.error('Registration failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
