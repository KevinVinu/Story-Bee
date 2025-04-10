<b>StoryBee - A Creative Storytelling Platform</b>


StoryBee is a web-based storytelling platform where users can write, share, and explore short stories. Built with Flask (Python) on the backend and vanilla JavaScript, HTML, and CSS on the frontend, it offers an interactive experience for creating tales, generating AI-assisted stories, and engaging with others' works through liking and saving features. The app uses SQLite for data storage and integrates with the DeepSeek API (via OpenRouter) for AI story generation.

<div>Features
User Authentication: Sign up and log in to access personalized features like writing and saving stories.
Story Creation: Write and submit your own short stories with optional image URLs and genres.
AI Story Generation: Provide a story starter, and let the AI (DeepSeek) complete it with a single click.
Story Exploration: Browse all stories on the homepage or filter by genre in the "Discover" section.
Like & Save: Like stories to show appreciation (updates a like count) and save them to your profile.
Profile Page: View your published stories and saved favorites.

  
Responsive Design: Enjoy a clean, mobile-friendly interface with a hamburger menu for navigation.</div>
How It Works

Backend (Flask):
Manages user authentication with JWT tokens.
Handles story CRUD operations using SQLite.
Provides API endpoints for story submission, retrieval, liking, saving, and AI generation.
Integrates with the DeepSeek API for story continuations.


Frontend (JavaScript/HTML/CSS):
Dynamically renders stories in a grid layout.
Manages user interactions (login, submission, liking/saving) via fetch requests.
Displays modals for authentication and story reading.
Database (SQLite):
Stores users, stories, likes, and saved stories with relational integrity.


Files
app.py
The core Flask application file defining routes, database models, and API logic:
/signup & /login: User registration and authentication.
/submit_story: Submit a new story (requires login).
/get_stories: Retrieve stories, with optional genre filtering.
/like_story & /save_story: Toggle likes and saves (requires login).
/generate_story: Call the DeepSeek API to complete a story (requires login).
Uses SQLAlchemy for database management and PyJWT for token handling.


index.html
The main HTML file structuring the app:
Sections: Home (story grid), Discover (filtered grid), Write (story form), Profile (user info).
Modals for login/signup and story reading.
Links to styles.css and script.js.


script.js
The JavaScript file driving frontend interactivity:
Handles navigation between sections.
Manages authentication modal and form submissions.
Fetches and displays stories dynamically.
Implements like/save functionality with real-time updates.
Triggers AI story generation and updates the form.


styles.css
The CSS file for styling:
Responsive story grid layout with cards.
Hamburger menu for mobile navigation.
Modal designs for authentication and story reading.
Button and form styling for a cohesive look.


stories.db
The SQLite database file (auto-generated):
Stores User, Story, Likes, and SavedStories tables.
Populated with dummy data on first run (e.g., "The High Bee" by kevin).
Dependencies
Python Libraries (Backend)
flask: Web framework.
flask_sqlalchemy: ORM for SQLite.
flask_cors: Cross-origin resource sharing.
flask_jwt_extended: JWT authentication.
bcrypt: Password hashing.
requests: HTTP requests to DeepSeek API.
pyjwt: Manual JWT decoding.
Frontend
Vanilla JavaScript, HTML, and CSS—no external libraries.
External API
DeepSeek via OpenRouter (https://openrouter.ai/api/v1/chat/completions).
