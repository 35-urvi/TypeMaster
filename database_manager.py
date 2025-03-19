import sqlite3
import csv
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_file):
        """Initialize the database connection"""
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
    
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        # Create test_results table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            test_mode TEXT,
            difficulty TEXT,
            wpm REAL,
            accuracy REAL,
            errors INTEGER,
            correct_chars INTEGER,
            total_chars INTEGER,
            test_duration REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
        ''')
        
        # Create words table for word lists
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            difficulty TEXT,
            words TEXT
        )
        ''')
        
        # Create paragraphs table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            difficulty TEXT,
            content TEXT
        )
        ''')
        
        self.conn.commit()
        
        # Initialize with default word lists if empty
        self.cursor.execute("SELECT COUNT(*) FROM word_lists")
        if self.cursor.fetchone()[0] == 0:
            self.initialize_word_lists()
            
        # Initialize with default paragraphs if empty
        self.cursor.execute("SELECT COUNT(*) FROM paragraphs")
        if self.cursor.fetchone()[0] == 0:
            self.initialize_paragraphs()
    
    def initialize_word_lists(self):
        """Initialize default word lists for different difficulty levels"""
        beginner_words = "the and that have with this from they will each about how some her more would first also their one what other word were many these their she your them then state would like time been when two could made over did more years some most only into used year must such now any than last own see work out part even new just day are after where most here both between life being under never".replace(",", "")
        
        intermediate_words = "system political government history university international development environment management organization technology different education experience information important director movement president sometimes performance application department information knowledge situation understanding significant successful particular operation environment development production security financial effective relationship following structure university everything movement situation opportunity character development government beautiful knowledge president experience individual performance particular community throughout organization collection investment relationship generation population character direction management professional immediately development different operation necessary equipment production significant understand experience".replace(",", "")
        
        advanced_words = "notwithstanding nevertheless consequently simultaneously approximately extraordinary sophisticated characteristics implementation particularly significantly unfortunately recommendation standardization administration characteristics representatives acknowledgment opportunities responsibility questionnaire categorically implementation understanding contradictory sophisticated approximately unfortunately transcendental misconception authorization disproportionately extraordinarily indistinguishable characteristics constitutional interpretation philosophical psychological extraordinary differentiation recommendation disestablishment epistemological extraterritorial phenomenological representational biodiversity representative environmentally incomprehensible".replace(",", "")
        
        self.cursor.execute("INSERT INTO word_lists (difficulty, words) VALUES (?, ?)", 
                         ("beginner", beginner_words))
        self.cursor.execute("INSERT INTO word_lists (difficulty, words) VALUES (?, ?)", 
                         ("intermediate", intermediate_words))
        self.cursor.execute("INSERT INTO word_lists (difficulty, words) VALUES (?, ?)", 
                         ("advanced", advanced_words))
        self.conn.commit()
    
    def initialize_paragraphs(self):
        """Initialize default paragraphs for different difficulty levels"""
        beginner = "The quick brown fox jumps over the lazy dog. She sells sea shells by the sea shore. How much wood would a woodchuck chuck if a woodchuck could chuck wood? All good things must come to an end. Early to bed and early to rise makes a man healthy, wealthy and wise."
        
        intermediate = "Technology has revolutionized the way we live, work, and communicate. With the advent of smartphones, social media, and instant messaging, people can now connect with others from anywhere in the world. However, this constant connectivity also raises concerns about privacy, digital addiction, and the impact on face-to-face social interactions. As we continue to embrace new technologies, it's important to consider both their benefits and potential drawbacks."
        
        advanced = "The proliferation of artificial intelligence in contemporary society represents a paradigm shift in how humans interact with technology. The philosophical implications of machine learning algorithms that can adapt, predict, and potentially surpass human decision-making capabilities raises profound questions about consciousness, free will, and the nature of intelligence itself. Furthermore, the socioeconomic ramifications of widespread automation necessitate careful consideration of workforce displacement, wealth distribution, and the redefinition of labor in a post-industrial economy. While proponents emphasize efficiency gains and novel problem-solving approaches, critics caution against exacerbating inequality and diminishing human agency in critical domains."
        
        self.cursor.execute("INSERT INTO paragraphs (difficulty, content) VALUES (?, ?)", 
                         ("beginner", beginner))
        self.cursor.execute("INSERT INTO paragraphs (difficulty, content) VALUES (?, ?)", 
                         ("intermediate", intermediate))
        self.cursor.execute("INSERT INTO paragraphs (difficulty, content) VALUES (?, ?)", 
                         ("advanced", advanced))
        self.conn.commit()
    
    def get_words(self, difficulty):
        """Get word list for a specific difficulty level"""
        self.cursor.execute("SELECT words FROM word_lists WHERE difficulty = ?", 
                         (difficulty,))
        result = self.cursor.fetchone()
        if result:
            return result[0].split()
        return []
    
    def get_paragraph(self, difficulty):
        """Get a random paragraph for a specific difficulty level"""
        self.cursor.execute("SELECT content FROM paragraphs WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1", 
                         (difficulty,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return ""
    
    def save_test_results(self, username, mode, difficulty, wpm, accuracy, errors, correct_chars, total_chars, test_duration):
        """Save test results to database"""
        self.cursor.execute('''
        INSERT INTO test_results 
        (username, test_mode, difficulty, wpm, accuracy, errors, correct_chars, total_chars, test_duration, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, mode, difficulty, wpm, accuracy, errors, correct_chars, total_chars, test_duration, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        
        # Get the ID of the inserted row
        test_id = self.cursor.lastrowid
        
        # Update user stats if not guest
        if username != "guest":
            self.cursor.execute(
                """SELECT tests_completed, avg_wpm, avg_accuracy FROM users WHERE username = ?""",
                (username,)
            )
            stats = self.cursor.fetchone()
            
            if stats:
                tests_completed, avg_wpm, avg_accuracy = stats
                tests_completed += 1
                
                # Calculate new averages
                new_avg_wpm = ((avg_wpm * (tests_completed - 1)) + wpm) / tests_completed
                new_avg_accuracy = ((avg_accuracy * (tests_completed - 1)) + accuracy) / tests_completed
                
                # Update user stats
                self.cursor.execute(
                    """UPDATE users 
                       SET tests_completed = ?, avg_wpm = ?, avg_accuracy = ? 
                       WHERE username = ?""",
                    (tests_completed, new_avg_wpm, new_avg_accuracy, username)
                )
                self.conn.commit()
        
        return test_id
    
    def get_user_history(self, username):
        """Get test history for a specific user"""
        self.cursor.execute('''
        SELECT test_mode, difficulty, wpm, accuracy, errors, test_duration, timestamp 
        FROM test_results 
        WHERE username = ? 
        ORDER BY timestamp DESC
        ''', (username,))
        return self.cursor.fetchall()
    
    def get_user_progress(self, username):
        """Get WPM and accuracy progress over time for a specific user"""
        self.cursor.execute('''
        SELECT wpm, accuracy, timestamp 
        FROM test_results 
        WHERE username = ? 
        ORDER BY timestamp ASC
        ''', (username,))
        return self.cursor.fetchall()
    
    def get_leaderboard(self, limit=10):
        """Get top scores from all users"""
        self.cursor.execute('''
        SELECT username, wpm, accuracy, test_mode, difficulty, timestamp 
        FROM test_results 
        ORDER BY wpm DESC 
        LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def export_results(self, username):
        """Export user results to CSV file"""
        # Get user history
        history = self.get_user_history(username)
        
        # Create CSV file
        with open('typing_results.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['Test Mode', 'Difficulty', 'WPM', 'Accuracy (%)', 'Errors', 'Duration (s)', 'Timestamp'])
            # Write data
            for row in history:
                writer.writerow(row)
    
    def close(self):
        """Close database connection"""
        self.conn.close()