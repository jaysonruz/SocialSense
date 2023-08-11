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
  
        const errorFreePostHtml = `<li class="no-error">
        <div class="row">
          <div class="col-4">
            <div class="ratio ratio-1x1"> <img id="post_image" src="${post.displayUrl_hosted}" class="img-fluid post-img"> </div>
          </div>
          <div class="col-8">
            <p><strong>Caption:</strong>${post.caption}</p>
            <div class="row">
      <div class="col-6">
        <p>Total errors: 0</p>
      </div>
      
     </div>
          
          </div>
        </div>
        <div class="post-container">
          <div style="flex: 1;"> </div>
        </div>
      </li>`
        const errorPostHTML = `
        <li class="red">
            <div class="row">
				<div class="col-12">
					<div class="row position-relative">
						<div class="right-icon" style="display: none;">
							<img src="images/right-icon.svg" class="img-fluid">
						</div>
						<div class="col-4">
                <div class="ratio ratio-1x1"> <img id="post_image" src="${post.displayUrl_hosted}" class="img-fluid post-img"> </div>
              </div>
              <div class="col-8">
                <p><strong>Caption:</strong>${post.caption}</p>
                <div class="row">
					<div class="col-6">
						<p>Total errors: 3</p>
					</div>
					<div class="col-6 text-end">
						<button class="btn btn-primary btn-sm btn1 light-grren fw-bold">Fix errors</button>
						
					</div>
				 </div>
              </div>
					</div>
					<div class="row">
						<div class="col-12">
							<div class="fix-error-box position-relative" style="display: none;">
				  	<p class="fw-bold">Total errors fixed: 3</p>
					<p id="p1">${post.correction_results}</p>
				  <p class="copy-icon"><img src="images/copy-icon.svg" class="img-fluid"></p>
				  <div class="d-flex align-items-center">
				  	<p class="fw-bold me-2 mb-0">Is it helpful?</p>
					  <button type="button" class="btn btn-primary btn-sm me-2 btn-green btn2">Yes</button>
					  <button type="button" class="btn btn-primary btn-sm btn-red btn2">No</button>
				  </div>
				  
			</div>
						</div>
					</div>
				</div>
              
            </div>
            <div class="post-container">
              <div style="flex: 1;"> </div>
            </div>
          </li>
        `;
        
        // Conditionally set the PostHTML based on the value of post.any_corrections
        let postHTML;
        if (post.any_corrections === true) {
          postHTML = errorPostHTML;
        } else {
          postHTML = errorFreePostHtml;
        }
        
        listItem.innerHTML = postHTML;
        instagramList.appendChild(listItem);
        
        // Add event listener for the "Fix errors" button
        const fixErrorsBtn = listItem.querySelector('.btn1');
        const fixErrorsBox = listItem.querySelector('.fix-error-box');
        const redBackground = listItem.querySelector('.red');
        const rightIcon = listItem.querySelector('.right-icon');

        if (fixErrorsBtn) {
          fixErrorsBtn.addEventListener('click', function () {
            $(fixErrorsBox).slideDown();
            $(redBackground).css('background', 'white');
          });
        }

        // Add event listeners for other buttons as needed (e.g., .btn2)

      });
    } else {
      console.error('Error fetching Instagram posts:', response.status, response.statusText);
    }
  });
});
