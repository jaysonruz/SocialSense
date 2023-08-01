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
          // Create the HTML structure for each post
        const postHTML = `
        <div class="post-container" style="background-color: #ffffc2;" padding: 10px; display: flex; align-items: center;">
          <div style="width: 400px; height: auto; border-radius: 50%; overflow: hidden; margin-right: 10px;">
            <img style="width: 100%; height: 100%; display:block" crossorigin="anonymous" src="${post.displayUrl}" alt="${post.alt}">
          </div>
          <div style="flex: 1;">
            <p><strong>Display URL:</strong> <a href="${post.displayUrl}" target="_blank">${post.displayUrl}</a></p>
            <p><strong>URL:</strong> <a href="${post.url}" target="_blank">${post.url}</a></p>
            <p><strong>type:</strong> ${post.type}</p>
            <p><strong>Caption:</strong> ${post.caption}</p>
            <p><strong>any_corrections:</strong> ${post.any_corrections}</p>
            <p><strong>corrections_lists:</strong> ${post.corrections_list}</p>
            <p><strong>correction_results:</strong> ${post.correction_results}</p>
          </div>
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
  