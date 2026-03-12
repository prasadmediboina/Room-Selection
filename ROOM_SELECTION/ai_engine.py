import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from fuzzywuzzy import process

FILENAME = 'Books_data - Sheet1.csv'

def load_data():
    try:
        df = pd.read_csv(FILENAME)
        # Clean data
        df['title'] = df['title'].astype(str).fillna('')
        df['author'] = df['author'].astype(str).fillna('Unknown')
        df['category'] = df['category'].astype(str).fillna('General')
        df['status'] = df['status'].astype(str).fillna('available')
        
        # Create Search Index
        df['content'] = df['title'] + " " + df['author'] + " " + df['category']
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# Global Data Load
df = load_data()

# Train AI (TF-IDF)
if not df.empty:
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['content'])

def save_data():
    """Saves changes (like issuing a book) back to CSV"""
    df.to_csv(FILENAME, index=False)

def smart_search(query):
    """Finds books by Title, Author, or Category (Handles Typos)"""
    if df.empty or not query: return []
    query = str(query).lower().strip()
    
    # 1. Exact/Partial Match
    mask = df['content'].str.lower().str.contains(query, regex=False)
    results = df[mask].to_dict('records')

    # 2. Fuzzy Fallback
    if len(results) < 3:
        all_titles = df['title'].tolist()
        fuzzy_matches = process.extract(query, all_titles, limit=5)
        for title, score in fuzzy_matches:
            if score > 50:
                if not any(d['title'] == title for d in results):
                    results.append(df[df['title'] == title].iloc[0].to_dict())
    
    return results[:12] 

# --- NEW IMPROVED RECOMMENDATION LOGIC ---
def recommend_books(book_title):
    """
    Hybrid Recommendation:
    1. Filter by SAME CATEGORY first (Strict).
    2. Then use AI Similarity within that category.
    """
    if df.empty: return []
    try:
        # 1. Find the book in our DB
        exact_title = process.extractOne(book_title, df['title'])[0]
        book_row = df[df['title'] == exact_title].iloc[0]
        book_category = book_row['category']
        
        # 2. Filter: Get all books in the SAME Category
        # (Exclude the book itself)
        category_books = df[
            (df['category'] == book_category) & 
            (df['title'] != exact_title)
        ]
        
        # 3. If we have books in the same category, return them!
        if not category_books.empty:
            # Optional: You could still rank these by TF-IDF if you want, 
            # but for a small dataset, just returning the same category is better.
            return category_books.head(5).to_dict('records')
            
        # 4. Fallback: If category is unique (no other books), use global AI
        idx = df.index[df['title'] == exact_title].tolist()[0]
        cosine_sim = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix)
        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        book_indices = [i[0] for i in sim_scores[1:6]]
        
        return df.iloc[book_indices].to_dict('records')

    except Exception as e:
        print(f"Rec Error: {e}")
        return []

def issue_book_logic(title):
    """Updates status to 'Issued'"""
    try:
        idx = df.index[df['title'] == title].tolist()[0]
        df.at[idx, 'status'] = 'issued'
        save_data()
        return True
    except:
        return False

# Admin functions... (Include your add/update/delete functions here as before)
# ... (Copy the admin functions from previous steps if needed)
def add_new_book(title, author, category, status='available'):
    global df, tfidf_matrix
    try:
        new_id = df['bid'].max() + 1 if not df.empty else 1
        new_row = {'bid': new_id, 'title': title, 'author': author, 'category': category, 'status': status, 'content': f"{title} {author} {category}"}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data()
        # Retrain AI
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['content'])
        return True
    except: return False

def update_book_status(bid, new_status):
    try:
        idx = df.index[df['bid'] == int(bid)].tolist()
        if not idx: return False
        df.at[idx[0], 'status'] = new_status
        save_data()
        return True
    except: return False

def delete_book_logic(bid):
    global df
    try:
        df = df[df['bid'] != int(bid)]
        save_data()
        return True
    except: return False