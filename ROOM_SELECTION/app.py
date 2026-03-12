from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from ai_engine import smart_search, recommend_books, issue_book_logic, load_data, add_new_book, update_book_status, delete_book_logic
import pandas as pd
import os
from datetime import datetime
import re  # <--- NEW: For Regex Validation

app = Flask(__name__)
app.secret_key = 'secure_admin_key_2025'

# --- CONFIGURATION ---
ADMIN_USER = "24bca7976"
ADMIN_PASS = "08082006"
ROOMS_FILE = 'bookings.csv'

# Regex for Student ID: 2 digits + 3 letters + 4 digits (e.g., 24bca7976)
ID_PATTERN = re.compile(r"^\d{2}[a-zA-Z]{3}\d{4}$")

# ==========================================
#        BOOKING SYSTEM ENGINE
# ==========================================

def get_bookings():
    if not os.path.exists(ROOMS_FILE): return []
    try:
        df = pd.read_csv(ROOMS_FILE)
        df.columns = df.columns.str.strip()
        # Ensure all columns exist to avoid KeyErrors on old CSVs
        if 'members' not in df.columns: df['members'] = ""
        return df.to_dict('records')
    except:
        return []

def save_booking(room_id, student_name, time_slot, members):
    """Writes a new booking to CSV with member details."""
    new_data = pd.DataFrame([{
        'room_id': room_id,
        'student_name': student_name, 
        'time_slot': time_slot,
        'members': members # New Column
    }])
    header = not os.path.exists(ROOMS_FILE)
    new_data.to_csv(ROOMS_FILE, mode='a', header=header, index=False)

def validate_booking(room_id, student_name, time_slot, members_str):
    """Runs strict validation constraints."""
    current_hour = datetime.now().hour
    bookings = get_bookings()
    
    # 1. Validate Leader ID Format
    if not ID_PATTERN.match(student_name):
        return f"Invalid Leader ID '{student_name}'. Must be like '21abc1234'."

    # 2. Parse & Validate Member IDs
    # Split by comma, strip spaces, remove empty strings
    member_list = [m.strip() for m in members_str.split(',') if m.strip()]
    member_list.append(student_name) # Add leader to the check list
    
    # Check Max Capacity
    if len(member_list) > 6:
        return f"Group too large ({len(member_list)}). Max 6 students allowed."

    # Check Member ID Formats
    for m in member_list:
        if not ID_PATTERN.match(m):
            return f"Invalid Member ID '{m}'. All IDs must follow format '2 digits + 3 letters + 4 digits'."

    # 3. Time Constraints
    if int(time_slot) <= current_hour:
        return "Cannot book past time slots."
    if not (9 <= int(time_slot) <= 17):
        return "Library is closed (9 AM - 6 PM)."
    
    # 4. Concurrency Check (The "No Double Dipping" Rule)
    for b in bookings:
        b_room = str(b.get('room_id'))
        b_time = str(b.get('time_slot'))
        
        # Room Busy?
        if b_room == str(room_id) and b_time == str(time_slot):
            return "Room is already booked."
            
        # Check if ANY member in the new group is already in an existing booking
        existing_members = str(b.get('members', '')).split(',') + [str(b.get('student_name', ''))]
        
        # Overlap check
        for new_person in member_list:
            for existing_person in existing_members:
                if new_person.lower() == existing_person.strip().lower() and b_time == str(time_slot):
                    return f"Student '{new_person}' is already part of another booking at this time."
            
    return "Success"

# ==========================================
#              WEB ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username').lower() == ADMIN_USER and \
           request.form.get('password') == ADMIN_PASS:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        flash("❌ Access Denied")
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('is_admin'): return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'title' in request.form:
            add_new_book(request.form['title'], request.form['author'], request.form['category'])
            flash("✅ Book Added!")
        elif 'clear_bookings' in request.form:
            if os.path.exists(ROOMS_FILE): os.remove(ROOMS_FILE)
            flash("🧹 All Room Bookings Cleared!")

    books = load_data().to_dict('records')
    bookings = sorted(get_bookings(), key=lambda x: int(x['time_slot'])) if get_bookings() else []
    return render_template('admin.html', books=books, bookings=bookings)

@app.route('/api/update_status', methods=['POST'])
def api_update_status():
    if not session.get('is_admin'): return jsonify({'success': False}), 403
    data = request.json
    if update_book_status(data['bid'], data['status']):
        return jsonify({'success': True})
    return jsonify({'success': False}), 500

@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    msg = ""
    current_hour = datetime.now().hour
    
    if request.method == 'POST':
        r = request.form.get('room_id')
        s = request.form.get('student_name') # Leader
        t = request.form.get('time_slot')
        m = request.form.get('members') # CSV String
        
        if r and s and t:
            valid = validate_booking(r, s, t, m)
            if valid == "Success":
                save_booking(r, s, t, m)
                msg = "✅ Booked Successfully!"
            else:
                msg = f"❌ {valid}"
    
    bookings = get_bookings()
    # Create a nice tooltip string for the UI
    taken = {}
    for b in bookings:
        key = f"{b['room_id']}_{b['time_slot']}"
        taken[key] = f"{b['student_name']} + {len(str(b.get('members','')).split(',')) if b.get('members') else 0} others"

    return render_template('rooms.html', message=msg, taken=taken, current_hour=current_hour)

@app.route('/admin/delete_booking/<room>/<time>')
def delete_booking_route(room, time):
    if not session.get('is_admin'): return redirect(url_for('login'))
    df = pd.read_csv(ROOMS_FILE)
    df = df[~((df['room_id'].astype(str) == room) & (df['time_slot'].astype(str) == time))]
    df.to_csv(ROOMS_FILE, index=False)
    flash(f"Booking removed for Room {room}")
    return redirect(url_for('admin'))

@app.route('/search')
def search():
    q = request.args.get('q', '')
    return render_template('results.html', query=q, books=smart_search(q))

@app.route('/recommend/<path:title>')
def recommend(title):
    return render_template('results.html', query=f"Recommendations: {title}", books=recommend_books(title))

@app.route('/issue/<path:title>')
def issue(title):
    if issue_book_logic(title): return render_template('success.html', title=title)
    return "Error."

if __name__ == '__main__':
    app.run(debug=True)