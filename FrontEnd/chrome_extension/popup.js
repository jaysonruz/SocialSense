document.addEventListener('DOMContentLoaded', async function () {
  const instagramInput = document.getElementById('instagramInput');
  const submitBtn = document.getElementById('submitBtn');
  const instagramList = document.getElementById('instagramList');
  const extensionId = chrome.runtime.id;
  const backend_url = "http://192.168.2.172:80";
  
  // Common headers for fetch requests
  const fetchHeaders = {
      'Content-Type': 'application/json',
  };

  // Check if the JWT token exists in localStorage
  const jwtToken = localStorage.getItem('jwtToken');

  // If JWT token exists, add it to the headers
  if (jwtToken) {
      fetchHeaders['Authorization'] = `Bearer ${jwtToken}`;
  }

  // Add event listener for the "keydown" event on the input field
  instagramInput.addEventListener('keydown', function (event) {
      if (event.key === "Enter") {
          event.preventDefault(); // Prevent default behavior of Enter key (like line break)
          submitBtn.click(); // Programmatically click the submit button
      }
  });

  // --------------------Submit button function ----------------------
  submitBtn.addEventListener('click', async function () {
    const inputValue = instagramInput.value;
    instagramList.innerHTML = ` 
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-start; height: 100%; text-align: center;">
        <p style="margin-bottom: 100px;">This should take a minute, you can get back to your work and we will drop you a notification once this is ready</p>
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden"></span>
        </div>
    </div>`;

    const response = await fetch(backend_url + '/instagram_posts', {
        method: 'POST',
        headers: fetchHeaders, // Use the common headers
        body: JSON.stringify({
            instagram_id: inputValue,
        }),
    });

    
    if (response.ok) {
      const igPosts = await response.json();

      // Calculate the number of results
      const resultCount = igPosts.length;

      // Update the result count in the <p> element
      const resultCountElement = document.getElementById('resultCount');
      resultCountElement.textContent = `Results: ${resultCount}`;

      // Clear the existing list items
      instagramList.innerHTML = '';

      // Create and append new list items for each post in the response
      igPosts.forEach((post) => {
        console.log(post);
        const listItem = document.createElement('li');

        const errorFreePostHtml = `<li class="no-error">
        <div class="row">
          <div class="col-4">
            <div class="ratio ratio-1x1"> <img id="post_image" src="${post.displayUrl_hosted}" class="img-fluid post-img"> </div>
          </div>
          <div class="col-8">
            <p><strong>Caption:</strong><span class="caption">${post.caption}</span></p>
            <div class="row">
              <div class="col-6">
                <p>Total errors: ${post.total_errors}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="post-container">
          <div style="flex: 1;"> </div>
        </div>
      </li>`;
      const errorPostHTML = `
      <li class="red">
          <div class="row">
              <div class="col-12">
                  <div class="row position-relative">
                      <div class="right-icon" style="display: none;">
                          <img src="images/right-icon.svg" class="img-fluid">
                      </div>
                      <div class="col-4">
                          <div class="ratio ratio-1x1">
                              <img id="post_image" src="${post.displayUrl_hosted}" class="img-fluid post-img">
                          </div>
                      </div>
                      <div class="col-8 pe-3">
                          <p><strong>Caption:</strong><span class="caption">${highlightCorrectionsInCap(post.caption, post.corrections_list)}</span></p>
                          <div class="row align-items-center">
                              <div class="col-5">
                                  <p class="mb-0">Total errors: ${post.total_errors}</p>
                              </div>
                              <div class="col-7 d-flex text-end">
                                  <button class="btn btn-primary btn-sm btn1 light-grren fw-bold">Fix errors</button>
                                  <button class="btn btn-secondary btn-sm btn2 light-red fw-bold ms-2">Dismiss</button>
                              </div>
                          </div>
                      </div>
                  </div>
                  <div class="row mt-3">
                      <div class="col-12">
                          <div class="fix-error-box position-relative" style="display: none;">
                              <p class="fw-bold">Total errors fixed: ${post.total_errors}</p>
                              <p id="p1">${highlightCorrectionsInRes(post.correction_results, post.corrections_list)}</p>
                              <p class="copy-icon">
                                  <img id="copyButton" src="images/copy-icon.svg" class="img-fluid">
                              </p>
                              <div class="d-flex align-items-center">
                                  <button type="button" class="btn btn-primary btn-sm me-2 btn-green btn2">Accept feedback</button>
                                  <button type="button" class="btn btn-primary btn-sm btn-red btn2">Ignore feedback</button>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
          <div class="post-container">
              <div style="flex: 1;"> </div>
          </div>
      </li>`;
  

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
        const dismissBtn = listItem.querySelector('.btn2');
        const fixErrorsBox = listItem.querySelector('.fix-error-box');
        const redBackground = listItem.querySelector('.red');
        const rightIcon = listItem.querySelector('.right-icon');
        
        if (fixErrorsBtn) {
          fixErrorsBtn.addEventListener('click', function () {
            $(fixErrorsBox).slideDown();
            $(redBackground).css('background', 'white');
          });
        }
        // Add event listeners for "Yes" and "No" buttons
        const yesBtn = listItem.querySelector('.btn-green');
        const noBtn = listItem.querySelector('.btn-red');

        if (dismissBtn) {
          dismissBtn.addEventListener('click', async function () {
            await sendHelpfulFeedback(post, helpful=false,dismiss=true);
            $(fixErrorsBox).slideUp();
            $(redBackground).css('background', 'white');
            $(rightIcon).css('display', 'block');
          });
        }

        if (yesBtn) {
          yesBtn.addEventListener('mouseenter', function () {
            yesBtn.setAttribute('title', "This will give us data that our QC bot corrected something good");
          });
        
          yesBtn.addEventListener('mouseout', function () {
            yesBtn.removeAttribute('title');
          });

          yesBtn.addEventListener('click', async function () {
            await sendHelpfulFeedback(post, true);
            $(fixErrorsBox).slideUp();
            $(redBackground).css('background', 'white');
            $(rightIcon).css('display', 'block');
          });
        }
    
        if (noBtn) {
          noBtn.addEventListener('mouseenter', function () {
            noBtn.setAttribute('title', " this will give us feedback that our bots recommendation was ignored ");
          });
        
          noBtn.addEventListener('mouseout', function () {
            noBtn.removeAttribute('title');
          });

          noBtn.addEventListener('click', async function () {
            await sendHelpfulFeedback(post, false);
            $(fixErrorsBox).slideUp();
            $(redBackground).css('background', 'white');
            $(rightIcon).css('display', 'block');
          });
        }

        // Add event listener for the copy icon button
        const copyButton = listItem.querySelector('#copyButton');
        if (copyButton) {
          copyButton.addEventListener('click', function () {
            copyCorrectionResults(post.correction_results);
          });
        }
        // Add event listeners for other buttons as needed (e.g., .btn2)



      });

    // Save instagramList data to chrome.storage
    chrome.storage.local.set({ 'instagramListData': igPosts }, function () {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
      } else {
        console.log('Instagram list data saved to storage.');

        // Retrieve and log the saved data immediately after saving
        chrome.storage.local.get(['instagramListData'], function (result) {
          if (chrome.runtime.lastError) {
            console.error(chrome.runtime.lastError);
          } else {
            console.log('Retrieved Instagram list data:', result.instagramListData);
          }
        });
      }
    });

    
    } else {
      console.error('Error fetching Instagram posts:', response.status, response.statusText);
    }
  });
  
  async function sendHelpfulFeedback(post, helpful, dismiss=false) {
    const response = await fetch(backend_url + '/save_ig_posts', {
      method: 'POST',
      headers: fetchHeaders,
      body: JSON.stringify({
        "post_id": post.id,
        "ownerUsername":post.ownerUsername,
        "extensionId": extensionId,
        "caption":post.caption,
        "displayUrl_hosted":post.displayUrl_hosted,
        "url":post.url,
        "correction_results":post.correction_results,
        "helpful": helpful,
        "dismiss": dismiss,
      }),
    });
  
    if (response.ok) {
      console.log('Feedback sent successfully');
      
      console.log(`Extension ID: ${extensionId}`);
    } else {
      console.error('Error sending feedback:', response.status, response.statusText);
    }
  }
  
  function copyCorrectionResults(text) {
    const tempInput = document.createElement('textarea');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);

    // Show the notification
    const notification = document.querySelector('.notification');
    notification.classList.add('show');

    // Automatically hide the notification after a certain time
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000); // Hide after 3 seconds
}

  function highlightCorrectionsInCap(text, corrections_list) {
    corrections_list.forEach((correction) => {
      const originalText = correction.text;    // highlight words to be corrected 
      const regex = new RegExp(`\\b${escapeRegex(originalText)}\\b`, 'gi');
      text = text.replace(regex, `<span class="highlight"> ${originalText} </span>`);
    });
    return text;
  }

  function highlightCorrectionsInRes(text, corrections_list) {
    corrections_list.forEach((correction) => {
        const originalText = correction.correct;
        const regex = new RegExp(`\\b${escapeRegex(originalText)}\\b`, 'gi');
        text = text.replace(regex, `<span class="highlight">$&</span>`);
    });
    return text;
}

// Function to escape special characters in a regular expression
function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}



});
