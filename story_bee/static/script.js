const API_URL = 'http://localhost:5000';
let token = localStorage.getItem('token');
let username = localStorage.getItem('username');

// Navigation
const sections = ['home', 'discover', 'write', 'profile'];
const navLinks = document.querySelectorAll('.nav-links a');
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-links');

hamburger.addEventListener('click', () => navMenu.classList.toggle('active'));

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const sectionId = link.getAttribute('href').substring(1);
        if (sectionId === 'login-signup') return showAuthModal();
        if (!token && sectionId === 'write') {
            showAuthModal();
            return;
        }
        if (!token && sectionId === 'profile') return showAuthModal();
        sections.forEach(s => document.getElementById(s).style.display = s === sectionId ? 'block' : 'none');
    });
});

// Authentication Modal
const authModal = document.getElementById('auth-modal');
const closeAuthModal = document.querySelector('.close');
const authForm = document.getElementById('auth-form');
const authSubmit = document.getElementById('auth-submit');
let isLogin = true;

function showAuthModal() {
    authModal.style.display = 'block';
    document.getElementById('modal-title').textContent = isLogin ? 'Login' : 'Signup';
    authSubmit.textContent = isLogin ? 'Login' : 'Signup';
    document.getElementById('toggle-auth').innerHTML = isLogin 
        ? `Don't have an account? <a href="#" id="switch-to-signup">Signup</a>`
        : `Already have an account? <a href="#" id="switch-to-signup">Login</a>`;
    document.getElementById('switch-to-signup').addEventListener('click', toggleAuthMode, { once: true });
}

function toggleAuthMode(e) {
    e.preventDefault();
    isLogin = !isLogin;
    showAuthModal();
}

document.getElementById('login-signup').addEventListener('click', showAuthModal);
closeAuthModal.addEventListener('click', () => authModal.style.display = 'none');

authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const endpoint = isLogin ? '/login' : '/signup';
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput, password })
    });
    const data = await response.json();

    if (response.ok) {
        if (isLogin) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', data.username);
            token = data.access_token;
            username = data.username;
            updateNav();
            authModal.style.display = 'none';
            loadProfile();
            sections.forEach(s => document.getElementById(s).style.display = s === 'home' ? 'block' : 'none');
            loadStories('story-grid');
            loadStories('discover-grid');
        } else {
            alert('Signup successful! Please login.');
            isLogin = true;
            showAuthModal();
        }
    } else {
        alert(data.error || 'Authentication failed');
    }
});

function updateNav() {
    document.getElementById('auth-link').style.display = token ? 'none' : 'block';
    document.getElementById('profile-link').style.display = token ? 'block' : 'none';
}

// Load Stories
async function loadStories(gridId, genre = '') {
    const url = genre ? `${API_URL}/get_stories?genre=${genre}` : `${API_URL}/get_stories`;
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    const response = await fetch(url, { headers });
    const stories = await response.json();
    const grid = document.getElementById(gridId);
    grid.innerHTML = stories.map(story => `
        <div class="story-card" data-id="${story.id}">
            <img src="${story.image_url}" alt="Story Cover" onerror="this.src='https://picsum.photos/200/300?random=5'">
            <h3>${story.title}</h3>
            <p>${story.content.slice(0, 50)}...</p>
            <span class="author">by ${story.author}</span>
            <span class="genre">${story.genre || 'No Genre'}</span>
            <div class="story-actions">
                <button class="like-btn ${story.is_liked ? 'liked' : ''}" data-id="${story.id}">
                    ❤️ ${story.like_count}
                </button>
                <button class="save-btn ${story.is_saved ? 'saved' : ''}" data-id="${story.id}">
                    ${story.is_saved ? '★ Saved' : '☆ Save'}
                </button>
            </div>
        </div>
    `).join('');
    document.querySelectorAll(`#${gridId} .story-card`).forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.classList.contains('like-btn') || e.target.classList.contains('save-btn')) return;
            showStoryModal(stories.find(s => s.id === parseInt(card.dataset.id)));
        });
    });
    document.querySelectorAll(`#${gridId} .like-btn`).forEach(btn => {
        btn.addEventListener('click', () => toggleLike(btn.dataset.id, gridId));
    });
    document.querySelectorAll(`#${gridId} .save-btn`).forEach(btn => {
        btn.addEventListener('click', () => toggleSave(btn.dataset.id, gridId));
    });
}

async function toggleLike(storyId, gridId) {
    if (!token) return showAuthModal();
    const response = await fetch(`${API_URL}/like_story`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ story_id: storyId })
    });
    if (response.ok) loadStories(gridId);
}

async function toggleSave(storyId, gridId) {
    if (!token) return showAuthModal();
    const response = await fetch(`${API_URL}/save_story`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ story_id: storyId })
    });
    if (response.ok) {
        loadStories(gridId);
        if (gridId !== 'profile-stories') loadProfile();
    }
}

// Story Reading Modal
const storyModal = document.getElementById('story-modal');
const closeStoryModal = document.querySelector('.close-story');

function showStoryModal(story) {
    document.getElementById('story-title-display').textContent = story.title;
    document.getElementById('story-image').src = story.image_url;
    document.getElementById('story-content-display').textContent = story.content;
    document.getElementById('story-author').textContent = `By ${story.author}`;
    document.getElementById('story-genre').textContent = `Genre: ${story.genre || 'None'}`;
    storyModal.style.display = 'block';
}

closeStoryModal.addEventListener('click', () => storyModal.style.display = 'none');

// Story Submission
document.getElementById('story-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!token) return showAuthModal();
    const title = document.getElementById('story-title').value;
    const content = document.getElementById('story-content').value;
    const imageUrl = document.getElementById('image-url').value || 'https://picsum.photos/200/300?random=5';
    const genre = document.getElementById('genre').value;

    try {
        const response = await fetch(`${API_URL}/submit_story`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ title, content, image_url: imageUrl, genre })
        });
        const data = await response.json();

        if (response.ok) {
            alert('Story submitted!');
            document.getElementById('story-form').reset();
            loadStories('story-grid');
            loadStories('discover-grid');
            loadProfile();
        } else {
            console.error('Submission failed with status:', response.status, 'Response:', data);
            alert(data.error || 'Submission failed - check console for details');
        }
    } catch (error) {
        console.error('Network or fetch error:', error);
        alert('Submission failed due to a network error - check console');
    }
});

// AI Story Generation
document.getElementById('generate-ai-story').addEventListener('click', async () => {
    if (!token) return showAuthModal();
    const partialStory = document.getElementById('story-content').value || 'Once upon a time...';
    const title = document.getElementById('story-title').value || 'AI-Generated Story';
    const imageUrl = document.getElementById('image-url').value || 'https://picsum.photos/200/300?random=6';
    const genre = document.getElementById('genre').value;

    const response = await fetch(`${API_URL}/generate_story`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ partial_story: partialStory, title, image_url: imageUrl, genre })
    });
    const data = await response.json();

    if (response.ok) {
        document.getElementById('story-content').value = data.continuation;
    } else {
        alert(data.error || 'Failed to generate story');
    }
});

// Discover Filter
document.getElementById('apply-filter').addEventListener('click', () => {
    const genre = document.getElementById('genre-filter').value;
    loadStories('discover-grid', genre);
});

// Profile
async function loadProfile() {
    if (!token) return;
    const response = await fetch(`${API_URL}/get_stories`, { headers: { 'Authorization': `Bearer ${token}` } });
    const stories = await response.json();
    const userStories = stories.filter(s => s.author === username);
    const savedStories = stories.filter(s => s.is_saved);
    document.getElementById('profile-username').textContent = `Welcome, ${username}!`;
    document.getElementById('profile-story-count').textContent = `Stories Published: ${userStories.length}`;
    const storyList = document.getElementById('profile-story-list');
    storyList.innerHTML = userStories.map(s => `<li>${s.title}</li>`).join('');
    const savedList = document.getElementById('profile-saved-list');
    savedList.innerHTML = savedStories.map(s => `<li>${s.title} by ${s.author}</li>`).join('');
}

// Initialize
updateNav();
loadStories('story-grid'); // Load stories on startup
showAuthModal();
localStorage.removeItem('token');
localStorage.removeItem('username');
token = null;
username = null;