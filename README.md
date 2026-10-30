# CineVibe: Movie Series & Franchise Recommender

#### Video Demo: <YOUR YOUTUBE VIDEO LINK HERE>

## Overview
**CineVibe** is a web-based application built with Python, Flask, SQLite, HTML, CSS, and JavaScript. The core goal of the project is to solve the common issue of "choice paralysis" when deciding what movie or franchise to watch. Unlike standard recommendation systems that suggest individual titles, CineVibe focuses specifically on curating and recommending complete movie series and franchises (ranging from trilogies to long-running sagas) categorized according to specific user moods, atmospheric vibes, and personal watch history preferences.

## Features
- **Mood & Vibe Filtering:** Allows users to select recommendations based on their current mood (e.g., high-octane action, mind-bending thrillers, comfort/feel-good movies, dark & gritty series).
- **Interactive Watchlist & Progress Tracking:** Logged-in users can mark series as watched, currently watching, or plan to watch, keeping track of their progress through entire franchises.
- **Dynamic Database Operations:** SQLite database integration dynamically manages users, franchise metadata, genre tags, and personal collection entries.
- **Responsive Web Interface:** Built using HTML5, modern CSS styling, and JavaScript to deliver a clean, desktop and mobile-friendly visual experience.

## File & Directory Structure

- `app.py`  
  Serves as the main routing logic and entry point for the Flask web application. It handles user authentication (login, registration, logout), manages session cookies, renders HTML templates with backend data, and processes HTTP requests for mood filtering and watchlist updates.

- `recommender.py`  
  Contains the custom recommendation algorithms and data-processing logic. It processes user input (such as selected mood tags or desired series length) and queries the database to return categorized lists of movie franchises sorted by relevance or vibe matches.

- `db.py`  
  Handles database interactions and helper functions for connecting to `recommender.db`. It encapsulates SQL query execution, user credential checking, watchlist additions/deletions, and database connections to maintain modular and clean code in `app.py`.

- `recommender.db`  
  An SQLite3 database containing tables for:
  - `users`: Stores user credentials (hashed passwords and usernames).
  - `franchises`: Stores detailed metadata on 50 to 100 movie series, including titles, release years, total movies, and overall runtime.
  - `vibes`: Defines mood tags associated with each franchise.
  - `user_watchlists`: Links users to their tracked franchises and completion statuses.

- `requirements.txt`  
  Lists all necessary Python dependencies (such as `Flask`, `CS50`, or `Werkzeug`) required to run the environment smoothly.

- `templates/`  
  Directory containing Jinja2-powered HTML templates:
  - `layout.html`: Base layout template providing navigation bars, headers, and footer elements across all pages.
  - `index.html`: Home page presenting mood selection carousels and top recommendations.
  - `recommend.html`: Displays filtered movie series matching user preferences.
  - `watchlist.html`: Displays user dashboard with saved franchises and watch progress.
  - `login.html` & `register.html`: Standard authentication interfaces for user management.

- `static/`  
  Houses visual assets, custom stylesheets (`styles.css`), and frontend JavaScript scripts for handling dynamic modal popups and asynchronous UI updating without full page refreshes.

## Design Decisions

### 1. Focusing on Franchises Over Individual Movies
Most mainstream movie platforms recommend individual movies. I made a deliberate architectural choice to build a dataset around entire movie series and franchises. Managing franchises requires tracking aggregated data (total runtimes, release spanning years, number of entries) and handling relational data structures where a user completes steps across a series rather than checking off a single film.

### 2. Separation of Database Logic (`db.py` & `recommender.py`)
Rather than writing raw SQL queries directly inside Flask route handlers in `app.py`, I separated database management functions into `db.py` and algorithmic matching logic into `recommender.py`. This modular design keeps `app.py` readable, easier to debug, and maintains a strict separation of concerns.

### 3. SQLite for Lightweight and Fast Local Storage
Using SQLite through Python's sqlite3 module provided an ideal balance between low latency for quick query responses and low overhead. Since database read requests happen every time a user alters mood selections, indexed queries on tag tables ensure instant UI updates.

### 4. Custom Vibe Taxonomy
Instead of relying solely on standard genres like "Action" or "Drama," I created a hybrid tagging schema that combines traditional genres with atmospheric "vibes" (e.g., "Late Night Binge," "Mind-Bender," "Adrenaline Rush"). This approach delivers significantly more accurate results for modern viewer preferences.

## Acknowledgments
Developed as the Final Project for Harvard University's CS50x: Introduction to Computer Science.
