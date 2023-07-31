document.addEventListener('DOMContentLoaded', function () {
    const instagramInput = document.getElementById('instagramInput');
    const submitBtn = document.getElementById('submitBtn');
    const instagramList = document.getElementById('instagramList');
    const backend_url = "http://127.0.0.1:8000/";
  
    submitBtn.addEventListener('click', async function () {
      const inputValue = instagramInput.value;
  
      const response = await fetch(backend_url + 'instagram_posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          instagram_id: inputValue,
        }),
      });
  
      if (response.ok) {
        const igPosts = await response.json();
  
        // Clear the existing list items
        instagramList.innerHTML = '';
  
        // Create and append new list items for each post in the response
        igPosts.forEach((post) => {
          const listItem = document.createElement('li');
  
          // Create the HTML structure for each post
          const postHTML = `
            <div>
              <p>${post.caption}</p>
              <img src="${post.displayUrl}" alt="${post.alt}">
              <br>
            </div>
          `;
  
          listItem.innerHTML = postHTML;
          instagramList.appendChild(listItem);
        });
      } else {
        console.error('Error fetching Instagram posts:', response.status, response.statusText);
      }
    });
  });
  