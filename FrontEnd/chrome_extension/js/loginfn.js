document.addEventListener('DOMContentLoaded', async function () {
    const backend_url = "http://192.168.2.172:80";
    
    // Define the URL for the main content (e.g., index.html)
    const mainContentURL = 'index.html';

    // References to the login and registration forms
    const loginForm = document.getElementById('loginForm');
    const registrationForm = document.getElementById('registrationForm');

    // References to the show/hide registration/login links
    const showRegistrationLink = document.getElementById('showRegistrationForm');
    const showLoginLink = document.getElementById('showLoginForm');

    //#-------------------------------
    const jwtToken = localStorage.getItem('jwtToken');
    console.log(`jwtToken is in local storage: ${jwtToken}`);

    // Check if a JWT token exists in local storage
    if (jwtToken) {
      // Send the token to the /validate_token endpoint for validation
      const response = await fetch(backend_url + '/validate_token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${jwtToken}` // Include the JWT token in the Authorization header
        },
      });

      if (response.ok) {
        // Token is valid, you can perform auto-login actions here
        console.log('Token is valid. Auto-login successful.');
        // Redirect to your main content or perform other auto-login actions
        window.location.href = 'index.html';
      } else {
        // Token is invalid or expired, remove it from local storage
        console.error('Token is invalid or expired.');
        localStorage.removeItem('jwtToken');
      }
    }
    //#-----------------------------------

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

    // Function to handle JWT token
    function handleJwtToken(token) {
        // You can store the token in localStorage or sessionStorage for future requests
        console.log("Token saved!");

        localStorage.setItem('jwtToken', token);

        // Redirect to the main content (index.html)
        window.location.href = mainContentURL;
    }

    // Add event listener to the login form
    loginForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form submission

        // Get the values from the login form
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        // Create a URL-encoded form data object
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        // Send a request to your backend for authentication
        fetch(backend_url + '/login', {
            method: 'POST',
            body: formData, // Use the form data
        })
        .then(response => {
            if (response.ok) {
                // Successful login
                response.json().then(data => {
                    handleJwtToken(data.access_token);
                });
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
        const firstName = document.getElementById('registerFirstName').value;
        const lastName = document.getElementById('registerLastName').value;
        const password = document.getElementById('registerPassword').value;

        // Send a request to your backend for registration
        fetch(backend_url + '/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, first_name: firstName, Last_name: lastName, password }),
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
