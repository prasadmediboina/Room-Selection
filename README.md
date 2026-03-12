📚 AI-Assisted Smart Library & Resource Management System
Status Python Stack

A modernized Library Resource Planning (LRP) system designed to address the "Discoverability" and "Scheduling" challenges in academic libraries. This project moves beyond simple record-keeping by integrating Natural Language Processing (NLP) for search, Machine Learning for recommendations, and a Temporal Constraint Engine for conflict-free room booking.

🚀 Key Technical Capabilities
1. Hybrid Search Engine (NLP + Fuzzy Logic)
Problem: Traditional SQL queries fail when students make spelling errors (e.g., "Pythen" vs "Python").
Solution: Implemented Levenshtein Distance algorithms (via fuzzywuzzy) to quantify string similarity.
Outcome: The system detects user intent and retrieves relevant results even with ~20% character error rate in search queries.
2. Context-Aware Recommendation Engine
Algorithm: A hybrid approach using Category Filtering + TF-IDF Vectorization.
Logic:
Strict Filtering: Prioritizes books within the same domain (e.g., Law books recommend other Law books).
Content Similarity: Uses Cosine Similarity on Title+Author vectors to rank results within that domain.
Fallback: Scans the global dataset only if the local category is empty.
3. Temporal Resource Scheduling (Room Booking)
A robust rule-based engine that manages discussion room allocations.

Constraints Enforced:
Time-Lock: Server-side validation rejects past time slots.
Concurrency Check: O(n) scan ensuring neither the leader nor any group member is double-booked across concurrent sessions.
ID Compliance: Enforces strict Regex patterns (^\d{2}[a-zA-Z]{3}\d{4}$) to prevent ghost bookings.
Capacity Control: Enforces a hard limit of 6 students per group.
4. Admin Command Center (Non-Destructive)
Disaster Recovery: Automated "Black Box" backup system. The database is backed up to a /backups directory with a timestamp before any bulk deletion occurs.
Silent Updates: Uses AJAX to toggle inventory status (Available/Issued) instantly without page reloads.
Safety First: The "Delete Book" capability was removed to prevent accidental data loss. Admins can only mark items as "Out of Stock."
🛠️ Tech Stack
Backend: Python (Flask)
Data Persistence: CSV / Pandas (Flat-file architecture for portability)
AI/ML: scikit-learn (Vectorization), fuzzywuzzy (String Matching)
Frontend: HTML5, Bootstrap 5, Custom Neumorphic CSS
Security: Session-based authentication, Input Sanitization
⚙️ Installation & Setup
Clone the Repository

git clone [https://github.com/your-username/smart-library-system.git](https://github.com/your-username/smart-library-system.git)
cd smart-library-system
Install Dependencies

pip install -r requirements.txt
Initialize Data

Ensure Books_data - Sheet1.csv is present in the root directory.
Note: If bookings.csv exists from a previous session, delete it to ensure a clean state (Column headers have been updated).
Run the Application

python app.py
Access the application at http://127.0.0.1:5000/.

🔐 Admin Access
The system includes a secured Admin Dashboard.

Login Route: /login
Default Credentials: (Configured for Demo)
Username: 24bca7976 (Case Insensitive)
Password: 08082006
Note: To clear all room bookings (Start New Day), you will be prompted to re-enter the admin password for security.

⚠️ Known Limitations (Prototype Status)
Persistence: The application uses CSV files for data storage. While effective for portability and academic demonstration, this is not ACID-compliant and not suitable for high-concurrency production environments.
Scalability: The AI Recommendation Engine computes the similarity matrix in memory on startup. Performance is optimal for <5,000 books.
Security: Credentials are hardcoded for ease of demonstration. In production, these must be hashed (Argon2/Bcrypt) and stored in environment variables.
📂 Project Structure
├── app.py                  # Main Server & Logic Controller
├── ai_engine.py            # ML Logic (Search & Recs)
├── Books_data - Sheet1.csv # Inventory Database
├── bookings.csv            # Reservation Database (Auto-generated)
├── backups/                # Disaster Recovery Snapshots
├── templates/              # UI Files
│   ├── base.html           # Neumorphic Layout
│   ├── admin.html          # Dashboard (AJAX)
│   ├── rooms.html          # Booking Grid
│   └── ...
└── requirements.txt        # Dependencies

👨‍💻 Developed by prasad mediboina
Engineering Student | Full Stack Developer
