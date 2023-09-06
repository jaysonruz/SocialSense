// Define your backend URL here
const backend_url = "http://192.168.2.172:80";

function createNotification(title, message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "/icons/icon16.png", // Use a placeholder icon or a default icon URL
    title: title,
    message: message,
    silent: false, // Ensure that the notification sound is not muted
  }, function(notificationId) {
    if (chrome.runtime.lastError) {
      console.error("Error creating notification:", chrome.runtime.lastError);
    } else {
      console.log("Notification created with ID:", notificationId);
    }
  });
}




// Function to fetch Instagram posts and store them in chrome.storage.local
async function fetchInstagramPosts(inputValue) {
  // Common headers for fetch requests
  const fetchHeaders = {
    'Content-Type': 'application/json',
  };

  // Check if the JWT token exists in chrome.storage.local
  chrome.storage.local.get(['jwtToken'], function (result) {
    const jwtToken = result.jwtToken;
    if (jwtToken) {
      fetchHeaders['Authorization'] = `Bearer ${jwtToken}`;

      fetch(backend_url + '/instagram_posts', {
        method: 'POST',
        headers: fetchHeaders,
        body: JSON.stringify({
          instagram_id: inputValue,
        }),
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error(`Error fetching Instagram posts: ${response.status} ${response.statusText}`);
          }
        })
        .then((igPosts) => {
          // Store the fetched data in chrome.storage.local
          chrome.storage.local.set({ 'instagramListData': igPosts }, function () {
            if (chrome.runtime.lastError) {
              console.error(chrome.runtime.lastError);
            } else {
              console.log('Instagram list data saved to storage.');

              // Show a notification
              createNotification("Data Loaded", "Instagram data has been loaded.");

              console.log('createNotification successful!');

            }
          });
        })
        .catch((error) => {
          console.error(error);
        });
    } else {
      console.error('JWT token not found in storage.');
    }
  });
}

// Listen for messages from the popup script
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === "fetchInstagramPosts") {
    fetchInstagramPosts(request.inputValue, function (igPosts) {
      sendResponse({ igPosts }); // Send the response with the fetched data
    });
    
    // Return true to indicate that you will send a response asynchronously
    return true;
  }
});
