// Set current year for copyright
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('current-year').textContent = new Date().getFullYear();
});

document.getElementById('randomize-button').addEventListener('click', async () => {
  const titleElement = document.getElementById('comic-title');
  const coverElement = document.getElementById('comic-cover');
  const detailLink = document.getElementById('comic-detail-link');
  const spinner = document.getElementById('loading-spinner');
  const button = document.getElementById('randomize-button');

  // Show loading state
  button.disabled = true;
  spinner.style.display = 'block';
  titleElement.textContent = 'Loading...';
  coverElement.style.display = 'none';
  detailLink.style.display = 'none';

  try {
      const response = await fetch('/random-comic');

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.comic) {
          // Update only essential elements
          titleElement.textContent = data.comic.title;
          coverElement.src = data.comic.coverUrl;
          coverElement.style.display = 'block';

          // Update detail link if available
          if (data.comic.urls?.length > 0) {
              const detailUrl = data.comic.urls.find(url => url.type === 'detail');
              if (detailUrl) {
                  detailLink.href = detailUrl.url;
                  detailLink.style.display = 'inline';
              }
          }
      } else {
          titleElement.textContent = 'No comic found';
      }
  } catch (error) {
      console.error('Error:', error);
      titleElement.textContent = error.message || 'Error loading comic. Please try again.';
  } finally {
      // Hide loading state
      spinner.style.display = 'none';
      button.disabled = false;
  }
});
