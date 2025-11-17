// Current mode: 'comic' or 'anime'
let currentMode = 'comic';

// Set current year for copyright
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('current-year').textContent = new Date().getFullYear();
  updateModeUI();
});

// Handle mode toggle
document.getElementById('mode-toggle').addEventListener('change', (e) => {
  currentMode = e.target.checked ? 'anime' : 'comic';
  updateModeUI();
});

function updateModeUI() {
  const modeLabels = document.querySelectorAll('.mode-label');
  const attributionText = document.getElementById('attribution-text');
  const sourceLink = document.getElementById('source-link');
  const currentYear = new Date().getFullYear();

  if (currentMode === 'anime') {
    // Anime mode
    modeLabels[0].classList.remove('active');
    modeLabels[1].classList.add('active');
    attributionText.innerHTML = `Data provided by MyAnimeList (via Jikan API). © ${currentYear}`;
    sourceLink.href = 'https://myanimelist.net';
    sourceLink.textContent = 'MyAnimeList';
  } else {
    // Comic mode
    modeLabels[0].classList.add('active');
    modeLabels[1].classList.remove('active');
    attributionText.innerHTML = `Data provided by Comic Vine. © <span id="current-year">${currentYear}</span>`;
    sourceLink.href = 'https://comicvine.gamespot.com';
    sourceLink.textContent = 'Comic Vine';
  }
}

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

  // Determine which endpoint to call
  const endpoint = currentMode === 'anime' ? '/random-anime' : '/random-comic';

  try {
      const response = await fetch(endpoint);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.comic) {
          // Update only essential elements
          titleElement.textContent = data.comic.title;
          coverElement.src = data.comic.coverUrl;
          coverElement.alt = currentMode === 'anime' ? 'Anime Cover' : 'Comic Cover';
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
          titleElement.textContent = `No ${currentMode} found`;
      }
  } catch (error) {
      console.error('Error:', error);
      titleElement.textContent = error.message || `Error loading ${currentMode}. Please try again.`;
  } finally {
      // Hide loading state
      spinner.style.display = 'none';
      button.disabled = false;
  }
});
