import random
import requests
import pyttsx3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'news_website'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
mail = Mail(app)

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# News API Configuration
API_KEY = '2f2adc9c744b4e92a2c18d4b93e621a2'
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

# Function to fetch news
def get_news(categories, countries):
    articles = []
    for country in countries:
        for category in categories:
            params = {
                'apiKey': API_KEY,
                'category': category,
                'country': country
            }
            response = requests.get(NEWS_API_URL, params=params)
            articles.extend(response.json().get('articles', []))
    return articles
# Trending Keywords Data (predefined)
TRENDING_KEYWORDS = ["AI", "Space Exploration", "Electric Cars", "Climate Change", "Cryptocurrency"]

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')  # Retrieve user query from request
    sort_by = request.args.get('sort_by', 'relevance')  # Default to relevance
    
    # Fetch news articles based on the query and sorting option
    news = get_news_by_query_and_sort(query, sort_by)
    return render_template(
        'search_results.html',
        title="Search Results",
        query=query,
        sort_by=sort_by,
        news=news,
        trending_keywords=TRENDING_KEYWORDS
    )

def get_news_by_query_and_sort(query, sort_by):
    params = {
        'apiKey':'2f2adc9c744b4e92a2c18d4b93e621a2' ,
        'q': query,
        'sortBy': sort_by  # Sort results based on user selection (relevance, publishedAt, popularity)
    }
    response = requests.get(NEWS_API_URL, params=params)
    return response.json().get('articles', [])


# Function to convert text to speech and save as an audio file
def text_to_speech(text, filename='news.mp3'):
    engine.save_to_file(text, filename)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 110)
    engine.runAndWait()
    return filename

@app.route('/speak', methods=['POST'])
def speak():
    text = request.form['text']
    audio_file = text_to_speech(text)
    return send_file(audio_file, as_attachment=True, mimetype='audio/mpeg')

# Function to generate and send OTP
def send_otp(email):
    otp = random.randint(100000, 999999)  # Generate a random 6-digit OTP
    try:
        msg = Message('Your OTP for Password Reset', sender='your_email@gmail.com', recipients=[email])
        msg.body = f'Your OTP for password reset is: {otp}'
        mail.send(msg)
        return otp
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        if 'user_id' in session:
            # Extract form data
            full_name = request.form['full_name']
            email = request.form['email']
            phone_number = request.form['phone_number']
            subject = request.form['subject']
            message = request.form['message']

            # Insert data into the database
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO feedback (full_name, email, phone_number, subject, message) VALUES (%s, %s, %s, %s, %s)',
                           (full_name, email, phone_number, subject, message))
            mysql.connection.commit()
            cursor.close()
            
            flash('Feedback submitted successfully!', 'success')
            return redirect(url_for('feedback'))
        else:
            flash('Please sign in to submit feedback.', 'warning')
            return redirect(url_for('signin'))
    return render_template('feedback_form.html', title='Feedback')



@app.route('/')
def home():
    news = get_news(['general'], ['us','gb'])
    return render_template('home.html', title="Home", news=news)

@app.route('/politics')
def politics():
    news = get_news(['politics'], ['us'])
    return render_template('politics.html', title="Politics", news=news)

@app.route('/sports')
def sports():
    news = get_news(['sports'], ['us','gb'])
    return render_template('sports.html', title="Sports", news=news)

@app.route('/world')
def world():
    news = get_news(['health','science','sports','technology','entertainment','business'], ['us', 'gb'])
    return render_template('world.html', title="World", news=news)

@app.route('/technology')
def technology():
    news = get_news(['technology', 'business'], ['us', 'ca'])
    return render_template('technology.html', title="Technology", news=news)

@app.route('/entertainment')
def entertainment():
    news = get_news(['entertainment'], ['us','gb'])
    return render_template('entertainment.html', title="Entertainment", news=news)
@app.route('/about')
def about():
    return render_template('about.html', title="About Us")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))  
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('signin.html', title='Sign In')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashPassword = bcrypt.generate_password_hash(password).decode("utf-8")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('signup'))
        else:
            cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, hashPassword))
            mysql.connection.commit()
            cursor.close()
            flash('Account created successfully! Please sign in.', 'success')
            return redirect(url_for('signin'))

    return render_template('signup.html', title='Sign Up')


# Sign Out Route
@app.route('/signout')
def signout():
    session.pop('user_id', None)
    flash('You have been signed out.', 'info')
    return redirect(url_for('signin'))

# Save News Route (requires sign-in)
@app.route('/save_news', methods=['POST'])
def save_news():
    if 'user_id' not in session:
        flash('Please sign in to save news.', 'warning')
        return redirect(url_for('signin'))

    user_id = session['user_id']
    news_title = request.form['news_title']
    news_description = request.form['news_description']
    news_url = request.form['news_url']
    news_image = request.form['news_image']

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO saved_news (user_id, title, description, url, image) VALUES (%s, %s, %s, %s, %s)',
                   (user_id, news_title, news_description, news_url, news_image))
    mysql.connection.commit()
    cursor.close()

    flash('News saved successfully!', 'success')
    return redirect(url_for('home'))

# Saved News Route (requires sign-in)
@app.route('/saved_news')
def saved_news():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM saved_news WHERE user_id = %s', (user_id,))
    saved_news = cursor.fetchall()
    cursor.close()

    return render_template('saved_news.html', title='Saved News', saved_news=saved_news)
# Remove Saved News Route (requires sign-in)
@app.route('/remove_article/<int:id>', methods=['DELETE'])
def remove_article(id):
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM saved_news WHERE id = %s AND user_id = %s', (id, session['user_id'],))
    mysql.connection.commit()
    cursor.close()
    
    return '', 204

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            otp_response = send_otp(email)
            if otp_response.startswith("Error:"):
                return f"<h3>{otp_response}</h3>"
            else:
                session['otp'] = otp_response
                session['reset_email'] = email
                flash('OTP has been sent to your email.', 'info')
                return redirect(url_for('reset_password'))
        else:
            flash('Email not found. Please try again.', 'danger')
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html', title='Forgot Password')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == ['POST']:
        otp = request.form['otp']
        new_password = request.form['new_password']

        if 'otp' in session and int(otp) == session['otp']:
            email = session['reset_email']
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE users SET password = %s WHERE email = %s', (new_password, email))
            mysql.connection.commit()
            cursor.close()
            session.pop('otp', None)
            session.pop('reset_email', None)
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('signin'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            return redirect(url_for('reset_password'))

    return render_template('reset_password.html', title='Reset Password')

# Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
