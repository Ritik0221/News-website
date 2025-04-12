// Function to show sign-in alert
function showSignInAlert() {
    alert('Please sign in to submit feedback.');
}
function showSaveNewsAlert() {
    alert('Please sign in to save this news article.');
}
function showSaveNewssuccess() {
    alert('News Saved Successfully');
}
// Function for text-to-speech
function textToSpeech(text) {
    console.log('Text-to-Speech function called with text:', text);  // Debugging

    // Check if the browser supports the Web Speech API
    if ('speechSynthesis' in window) {
        const speech = new SpeechSynthesisUtterance(text);
        speech.lang = 'en-US'; // Set the language (you can change this as needed)
        window.speechSynthesis.speak(speech);
        console.log('Speech synthesis started');  // Debugging
    } else {
        alert("Sorry, your browser doesn't support text-to-speech.");
        console.log('Web Speech API not supported');  // Debugging
    }
}

// Sidebar Toggle
document.getElementById('sidebar-toggle').addEventListener('click', function () {
    const sidebar = document.getElementById('sidebar');
    const isSidebarVisible = sidebar.classList.contains('show');
    const mainContent = document.querySelector('main');

    if (isSidebarVisible) {
        sidebar.classList.remove('show');
        mainContent.classList.remove('sidebar-visible');
        setTimeout(() => sidebar.style.display = 'none', 500);  // Wait for transition to finish
    } else {
        sidebar.style.display = 'block';
        setTimeout(() => sidebar.classList.add('show'), 10);  // Ensure the transition happens
        mainContent.classList.add('sidebar-visible');
    }
    document.body.style.overflow = isSidebarVisible ? 'auto' : 'hidden'; // Prevent background scrolling when sidebar is open
});

// Close Sidebar When Clicking Outside
document.addEventListener('click', function (event) {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const isSidebarVisible = sidebar.classList.contains('show');

    if (isSidebarVisible && !sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
        sidebar.classList.remove('show');
        document.querySelector('main').classList.remove('sidebar-visible');
        setTimeout(() => sidebar.style.display = 'none', 500);  // Wait for transition to finish
        document.body.style.overflow = 'auto';  // Enable background scrolling
    }
});

// Loader Bar Animation and Tooltip Initialization
document.addEventListener('DOMContentLoaded', function () {
    const loaderBar = document.getElementById('loader-bar');
    loaderBar.style.width = '100%';

    setTimeout(() => {
        loaderBar.style.display = 'none';
    }, 1000);

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
});

// Function to highlight active menu item
function highlightActiveMenuItem() {
    const path = window.location.pathname;
    const navItems = document.querySelectorAll('.navbar a');

    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === path) {
            item.classList.add('active');
        }
    });
}

// Call the function on page load
document.addEventListener('DOMContentLoaded', function () {
    highlightActiveMenuItem();
});

function removeArticle(articleId) {
    fetch(`/remove_article/${articleId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            // Smoothly remove the article from the DOM
            const articleCard = document.querySelector(`.custom-card[data-article-id="${articleId}"]`);
            if (articleCard) {
                articleCard.style.transition = 'opacity 0.5s ease-out';
                articleCard.style.opacity = '0';
                setTimeout(() => {
                    articleCard.remove();
                }, 500); // Match the transition duration
            }
        } else {
            alert('Failed to remove article');
        }
    })
    .catch(error => console.error('Error:', error));
}

