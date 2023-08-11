document.addEventListener('DOMContentLoaded', function () {
    const instagramInput = document.getElementById('instagramInput');
    const submitBtn = document.getElementById('submitBtn');
    const instagramList = document.getElementById('instagramList');
    const backend_url = "http://192.168.2.172:80";
  
    submitBtn.addEventListener('click', async function () {
      const inputValue = instagramInput.value;
  
      const response = await fetch(backend_url + '/instagram_posts', {
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
        <div class="post-container">
          <div >
          <img id="post_image" src="${post.displayUrl_hosted}">
          </div>
          <div style="flex: 1;">
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
  