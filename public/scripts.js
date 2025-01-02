document.getElementById('randomize-button').addEventListener('click', async () => {
  const titleElement = document.getElementById('comic-title');
  const coverElement = document.getElementById('comic-cover');
  const detailLink = document.getElementById('comic-detail-link');
  
  // Reset display state
  titleElement.textContent = 'Loading...';
  coverElement.style.display = 'none';
  detailLink.style.display = 'none';
  
  try {
      const response = await fetch('/random-comic');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
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
      titleElement.textContent = 'Error loading comic';
  }
});