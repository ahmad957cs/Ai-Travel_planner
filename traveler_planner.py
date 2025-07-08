import os
import json
import re
import requests
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_file
from dotenv import load_dotenv
from traveler_profile import traveler_profiles
from prompt_engine import prompt_engine
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from datetime import datetime, timedelta
import io
import csv

load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")
tavily_api = os.getenv("TAVILY_API_KEY")
rapidapi_key = os.getenv("RAPIDAPI_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(10), nullable=True)
    reset_code = db.Column(db.String(10), nullable=True)
    reset_code_expiry = db.Column(db.DateTime, nullable=True)
    profiles = db.relationship('TravelerProfile', backref='user', lazy=True)
    plans = db.relationship('TravelPlan', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_code(self):
        self.reset_code = str(random.randint(100000, 999999))
        self.reset_code_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

class TravelerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    budget = db.Column(db.String(50))
    interests = db.Column(db.String(200))  # Comma-separated
    preferences = db.Column(db.String(200))

class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination = db.Column(db.String(100))
    departure_city = db.Column(db.String(100))
    checkin_date = db.Column(db.String(20))
    checkout_date = db.Column(db.String(20))
    days = db.Column(db.Integer)
    budget = db.Column(db.String(50))
    preferences = db.Column(db.String(200))
    itinerary = db.Column(db.Text)  # Store as JSON string
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

CITY_IMAGES = {
    "tokyo": "https://images.unsplash.com/photo-1507699622108-4be3abd695ad",
    "paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
    "istanbul": "https://images.unsplash.com/photo-1520975922203-29a1b1277cc1",
    "bangkok": "https://images.unsplash.com/photo-1580201665630-bd7fcfef897f",
    "new york": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
    "dubai": "https://images.unsplash.com/photo-1526483360412-f8581a6ae0a7",
    "default": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
}

def get_dest_id(city):
    try:
        url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params={"name": city, "locale": "en-us"})
        data = response.json()
        if data and "dest_id" in data[0]:
            return data[0]["dest_id"]
    except:
        return None
    return None

# -- Robust JSON cleaner --
def safe_json_loads(text):
    try:
        # Check if text is empty or None
        if not text or not text.strip():
            raise ValueError("Empty response from Groq API")
        
        start = text.find('{')
        end = text.rfind('}') + 1
        
        # Check if we found valid JSON brackets
        if start == -1 or end == 0:
            raise ValueError("No valid JSON structure found in response")
        
        json_str = text[start:end]

        # Clean up format
        json_str = json_str.replace('\n', '').replace('\r', '')
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # remove trailing commas

        return json.loads(json_str)
    except Exception as e:
        return {
            "itinerary": {
                "Day 1": [
                    "🏛️ Visit local cultural sites and museums",
                    "🍽️ Try authentic local cuisine for lunch",
                    "🌅 Explore main attractions and landmarks",
                    "🍽️ Enjoy traditional dinner at local restaurant"
                ]
            },
            "budget_analysis": {
                "accommodation": {"estimated": 100, "range": "80-150"},
                "food": {"estimated": 80, "range": "60-120"},
                "transportation": {"estimated": 30, "range": "20-50"},
                "activities": {"estimated": 50, "range": "30-80"},
                "miscellaneous": {"estimated": 20, "range": "10-30"}
            },
            "travel_tips": {
                "cultural": ["Respect local customs", "Learn basic local phrases"],
                "practical": ["Use public transportation", "Carry local currency"],
                "safety": ["Stay in well-lit areas", "Keep valuables secure"],
                "food": ["Try local specialties", "Drink bottled water"]
            },
            "personalized_recommendations": {
                "based_on_interests": ["Visit museums and galleries", "Try cultural activities"],
                "budget_optimization": ["Use public transport", "Eat at local markets"],
                "hidden_gems": ["Explore local neighborhoods", "Visit free attractions"]
            },
            "_error_info": f"API Error: {str(e)} | Response: {text[:200] if text else 'No response'}..."
        }

def get_or_create_user_id():
    """Get or create a user ID for session management using the database"""
    if 'user_id' not in session:
        # Create a new user in the database
        user = User()
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
    return session['user_id']

def update_traveler_profile(user_id, form_data):
    """Update traveler profile based on form data using both database and in-memory system"""
    # Update database profile
    profile = TravelerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = TravelerProfile(user_id=user_id)
        db.session.add(profile)
    
    # Update budget
    budget = form_data.get('budget')
    if budget:
        profile.budget = f"${budget}"
        # Also update in-memory profile
        traveler_profiles.update_budget_profile(str(user_id), f"${budget}")
    
    # Update interests
    preferences = form_data.get('preferences')
    if preferences:
        interests = [interest.strip() for interest in preferences.split(',') if interest.strip()]
        profile.interests = ','.join(interests)
        profile.preferences = preferences
        # Also update in-memory profile
        traveler_profiles.update_interests_profile(str(user_id), interests)
    
    # Add travel preferences to in-memory profile
    if any([form_data.get('destination'), form_data.get('days'), form_data.get('departure_city')]):
        travel_prefs = {
            'destination': form_data.get('destination'),
            'days': form_data.get('days'),
            'departure_city': form_data.get('departure_city'),
            'checkin_date': form_data.get('checkin_date'),
            'checkout_date': form_data.get('checkout_date')
        }
        traveler_profiles.add_travel_preferences(str(user_id), travel_prefs)
    
    db.session.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    result = None
    destination = ""
    bg_image = CITY_IMAGES["default"]
    profile_summary = None
    personalized_recommendations = None
    user_plans = []

    user_id = session.get('user_id')

    if request.method == "POST":
        destination = request.form.get("destination", "").strip()
        departure_city = request.form.get("departure_city", "").strip()
        budget = request.form.get("budget")
        days = request.form.get("days")
        preferences = request.form.get("preferences")
        checkin = request.form.get("checkin_date")
        checkout = request.form.get("checkout_date")

        bg_image = CITY_IMAGES.get(destination.lower(), CITY_IMAGES["default"])

        # Update traveler profile
        form_data = {
            'destination': destination,
            'departure_city': departure_city,
            'budget': budget,
            'days': days,
            'preferences': preferences,
            'checkin_date': checkin,
            'checkout_date': checkout
        }
        update_traveler_profile(user_id, form_data)
        
        # Get profile summary and recommendations
        profile_summary = traveler_profiles.get_profile_summary(user_id)
        personalized_recommendations = traveler_profiles.get_recommendations(user_id, destination)

        # Tavily Flights
        try:
            res = requests.post("https://api.tavily.com/search", json={
                "api_key": tavily_api,
                "query": f"cheap flights from {departure_city} to {destination} under ${budget}",
                "search_depth": "basic"
            }, headers={"Content-Type": "application/json"})
            flight_data = res.json()
            answer = flight_data.get("answer")
            results = flight_data.get("results", [])
            if answer and isinstance(answer, str) and answer.strip():
                flights = [answer.strip()]
            else:
                flights = [f"{r['title']} — {r['url']}" for r in results[:3]] if results else ["None"]
        except Exception as e:
            flights = [f"❌ Flights Error: {str(e)}"]

        # Booking Hotels
        hotels = []
        dest_id = get_dest_id(destination)
        try:
            if not dest_id:
                raise Exception("Dest ID not found")
            res = requests.get("https://booking-com.p.rapidapi.com/v1/hotels/search", headers={
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
            }, params={
                "checkout_date": checkout,
                "checkin_date": checkin,
                "dest_type": "city",
                "dest_id": dest_id,
                "order_by": "price",
                "adults_number": "1",
                "locale": "en-us",
                "units": "metric",
                "room_number": "1",
                "filter_by_currency": "USD",
                "page_number": "0"
            })
            for h in res.json().get("result", [])[:3]:
                hotels.append({
                    "name": h.get("hotel_name", "N/A"),
                    "price": f"${int(h.get('price_breakdown', {}).get('gross_price', 0))}/night"
                })
        except:
            hotels = [
                {"name": f"{destination.title()} Grand Hotel", "price": "$120/night"},
                {"name": f"{destination.title()} Central Inn", "price": "$95/night"}
            ]

        # Enhanced Groq LLaMA Itinerary with Profile Context
        try:
            # Build comprehensive prompt with profile context
            profile_context = profile_summary.get('profile_data', {})
            prompt = prompt_engine.build_comprehensive_prompt(
                destination=destination,
                days=int(days),
                budget=int(budget),
                preferences=preferences or "General",
                traveler_profile=profile_context
            )
            
            groq_res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={
                "Authorization": f"Bearer {groq_api}",
                "Content-Type": "application/json"
            }, json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}]
            })
            content = groq_res.json()['choices'][0]['message']['content']
            parsed = safe_json_loads(content)
            
            # Extract different components from the response
            itinerary = parsed.get("itinerary", {"Day 1": ["❌ No itinerary found"]})
            budget_analysis = parsed.get("budget_analysis", {})
            travel_tips = parsed.get("travel_tips", {})
            personalized_recs = parsed.get("personalized_recommendations", {})
            
        except Exception as e:
            itinerary = {"Day 1": [f"❌ Groq Error: {str(e)}"]}
            budget_analysis = {}
            travel_tips = {}
            personalized_recs = {}

        result = {
            "flights": flights,
            "hotels": hotels,
            "itinerary": itinerary,
            "budget_analysis": budget_analysis,
            "travel_tips": travel_tips,
            "personalized_recommendations": personalized_recs
        }

        # --- Save TravelPlan to DB ---
        plan = TravelPlan(
            user_id=user_id,
            destination=destination,
            departure_city=departure_city,
            checkin_date=checkin,
            checkout_date=checkout,
            days=int(days) if days else None,
            budget=f"${budget}" if budget else None,
            preferences=preferences,
            itinerary=json.dumps(result) if result else None
        )
        db.session.add(plan)
        db.session.commit()
        flash("Travel plan created successfully!", "success")

    # --- Retrieve all plans for the user ---
    user_plans = TravelPlan.query.filter_by(user_id=user_id).order_by(TravelPlan.created_at.desc()).all()
    
    # Always sync profile and get summary for display
    sync_profile_from_database(user_id)
    profile_summary = traveler_profiles.get_profile_summary(str(user_id))

    return render_template("index.html", 
                         result=result, 
                         destination=destination, 
                         bg_image=bg_image,
                         profile_summary=profile_summary,
                         personalized_recommendations=personalized_recommendations,
                         user_plans=user_plans)

@app.route("/profile")
@login_required
def view_profile():
    user_id = session.get('user_id')
    sync_profile_from_database(user_id)
    profile_summary = traveler_profiles.get_profile_summary(str(user_id))
    user_plans = TravelPlan.query.filter_by(user_id=user_id).order_by(TravelPlan.created_at.desc()).all()
    # Parse plan details for each plan
    plans_with_details = []
    for plan in user_plans:
        details = {}
        try:
            details = json.loads(plan.itinerary) if plan.itinerary else {}
        except Exception as e:
            print(f"[DEBUG] Error parsing itinerary for plan {plan.id}: {e}")
            details = {}
        print(f"[DEBUG] Plan ID: {plan.id}, Details: {details}")
        plans_with_details.append({'plan': plan, 'details': details})
    return render_template("profile.html", profile_summary=profile_summary, plans_with_details=plans_with_details)

def sync_profile_from_database(user_id):
    """Sync database profile data with in-memory profile system"""
    # Get database profile
    db_profile = TravelerProfile.query.filter_by(user_id=user_id).first()
    if not db_profile:
        return
    
    # Create profile in memory if it doesn't exist
    if str(user_id) not in traveler_profiles.profiles:
        traveler_profiles.create_profile(str(user_id))
    
    # Sync budget
    if db_profile.budget:
        traveler_profiles.update_budget_profile(str(user_id), db_profile.budget)
    
    # Sync interests
    if db_profile.interests:
        interests = [interest.strip() for interest in db_profile.interests.split(',') if interest.strip()]
        traveler_profiles.update_interests_profile(str(user_id), interests)

@app.route("/plan/<int:plan_id>")
@login_required
def view_plan(plan_id):
    plan = TravelPlan.query.get_or_404(plan_id)
    if plan.user_id != session.get('user_id'):
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    itinerary = json.loads(plan.itinerary) if plan.itinerary else {}
    return render_template("plan_detail.html", plan=plan, itinerary=itinerary)

@app.route("/plan/<int:plan_id>/edit", methods=["GET", "POST"])
@login_required
def edit_plan(plan_id):
    plan = TravelPlan.query.get_or_404(plan_id)
    if plan.user_id != session.get('user_id'):
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    if request.method == "POST":
        plan.destination = request.form.get("destination")
        plan.departure_city = request.form.get("departure_city")
        plan.checkin_date = request.form.get("checkin_date")
        plan.checkout_date = request.form.get("checkout_date")
        plan.days = int(request.form.get("days")) if request.form.get("days") else plan.days
        plan.budget = request.form.get("budget")
        plan.preferences = request.form.get("preferences")
        db.session.commit()
        flash("Travel plan updated successfully!", "success")
        return render_template("plan_detail.html", plan=plan, itinerary=json.loads(plan.itinerary) if plan.itinerary else {})
    return render_template("plan_edit.html", plan=plan)

@app.route("/plan/<int:plan_id>/delete", methods=["POST"])
@login_required
def delete_plan(plan_id):
    plan = TravelPlan.query.get_or_404(plan_id)
    if plan.user_id != session.get('user_id'):
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    db.session.delete(plan)
    db.session.commit()
    flash("Travel plan deleted.", "info")
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        user = User(name=name, email=email)
        user.set_password(password)
        # Generate verification code
        code = str(random.randint(100000, 999999))
        user.verification_code = code
        user.is_verified = False
        db.session.add(user)
        db.session.commit()
        # Send only one professional email with code and welcome message
        send_verification_email(email, code)
        session['pending_user_id'] = user.id
        flash('Registration successful! Please check your email for the verification code.', 'success')
        return redirect(url_for('verify'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')
        
        email = email.lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                session['pending_user_id'] = user.id
                flash('Please verify your email before logging in.', 'error')
                return redirect(url_for('verify'))
            session['user_id'] = user.id
            # Set session permanent if remember me is checked
            if remember_me:
                session.permanent = True
                # Set session lifetime to 30 days
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    user_id = session.get('pending_user_id')
    if not user_id:
        flash('No verification in progress. Please register first.', 'error')
        return redirect(url_for('register'))
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('register'))
    if request.method == 'POST':
        code = request.form.get('code')
        if code == user.verification_code:
            user.is_verified = True
            user.verification_code = None
            db.session.commit()
            session.pop('pending_user_id', None)
            flash('Email verified! You can now login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification code. Please try again.', 'error')
    return render_template('verify.html', email=user.email)

# --- Email Utility ---
def send_verification_email(to_email, code):
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    print(f"[DEBUG] Sending verification code: {code} to {to_email}")
    if not gmail_user or not gmail_password:
        print('Gmail credentials not set in .env')
        return False
    subject = 'Welcome to AI Travel Planner - Verify Your Email'
    body = f"""
    <div style='font-family: Arial, sans-serif; max-width: 500px; margin: auto; border: 1px solid #eee; border-radius: 8px; box-shadow: 0 2px 8px #f0f0f0; padding: 24px;'>
        <h2 style='color: #2d7ff9;'>Welcome to AI Travel Planner!</h2>
        <p>Dear Traveler,</p>
        <p>Thank you for creating an account with us. Your registration was <b>successful</b>!</p>
        <p style='margin-top: 24px; font-size: 16px;'>
            <b>Your verification code:</b>
            <span style='display: inline-block; background: #f5f5f5; color: #2d7ff9; font-size: 22px; letter-spacing: 2px; padding: 8px 18px; border-radius: 6px; margin-left: 10px;'>{code}</span>
        </p>
        <p style='margin-top: 24px;'>Please enter this code on the verification page to activate your account.</p>
        <hr style='margin: 32px 0;'>
        <p style='color: #888;'>If you did not sign up for AI Travel Planner, please ignore this email.</p>
        <p style='color: #888;'>Safe travels!<br>AI Travel Planner Team</p>
    </div>
    """
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, msg.as_string())
        server.quit()
        print(f"[DEBUG] Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print('[ERROR] Failed to send email:', e)
        return False

def send_reset_email(to_email, code):
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    print(f"[DEBUG] Sending reset code: {code} to {to_email}")
    if not gmail_user or not gmail_password:
        print('[ERROR] Gmail credentials not set in .env')
        return False
    subject = 'Password Reset - AI Travel Planner'
    body = f"""
    <div style='font-family: Arial, sans-serif; max-width: 500px; margin: auto; border: 1px solid #eee; border-radius: 8px; box-shadow: 0 2px 8px #f0f0f0; padding: 24px;'>
        <h2 style='color: #a855f7;'>Password Reset Request</h2>
        <p>Dear Traveler,</p>
        <p>We received a request to reset your password for your AI Travel Planner account.</p>
        <p style='margin-top: 24px; font-size: 16px;'>
            <b>Your password reset code:</b>
            <span style='display: inline-block; background: #f5f5f5; color: #a855f7; font-size: 22px; letter-spacing: 2px; padding: 8px 18px; border-radius: 6px; margin-left: 10px;'>{code}</span>
        </p>
        <p style='margin-top: 24px;'>Please enter this code on the password reset page. This code will expire in <b>15 minutes</b>.</p>
        <hr style='margin: 32px 0;'>
        <p style='color: #888;'>If you did not request a password reset, you can safely ignore this email.</p>
        <p style='color: #888;'>Safe travels!<br>AI Travel Planner Team</p>
    </div>
    """
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, msg.as_string())
        server.quit()
        print(f"[DEBUG] Reset email sent successfully to {to_email}")
        return True
    except Exception as e:
        print('[ERROR] Failed to send reset email:', e)
        return False

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        user = User.query.filter_by(email=email).first()
        if user:
            user.generate_reset_code()
            email_sent = send_reset_email(email, user.reset_code)
            if email_sent:
                session['reset_email'] = email
                flash('Password reset code has been sent to your email.', 'success')
                return redirect(url_for('reset_password'))
            else:
                flash('Failed to send reset email. Please contact support or check your email settings.', 'error')
        else:
            flash('Email not found.', 'error')
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash('No password reset in progress.', 'error')
        return redirect(url_for('forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        new_password = request.form.get('new_password')
        
        if not code or not new_password:
            flash('All fields are required.', 'error')
            return render_template('reset_password.html')
        
        if user.reset_code != code:
            flash('Invalid reset code.', 'error')
            return render_template('reset_password.html')
        
        if user.reset_code_expiry < datetime.utcnow():
            flash('Reset code has expired. Please request a new one.', 'error')
            return redirect(url_for('forgot_password'))
        
        user.set_password(new_password)
        user.reset_code = None
        user.reset_code_expiry = None
        db.session.commit()
        session.pop('reset_email', None)
        flash('Password has been reset successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/download_profile_csv')
@login_required
def download_profile_csv():
    user_id = session.get('user_id')
    sync_profile_from_database(user_id)
    profile_data = traveler_profiles.profiles.get(str(user_id))
    if not profile_data:
        return "No profile data found", 404

    output = io.StringIO()
    writer = csv.writer(output)
    # Write profile summary
    writer.writerow(['Profile Field', 'Value'])
    writer.writerow(['User ID', profile_data.get('user_id', '')])
    writer.writerow(['Created At', profile_data.get('created_at', '')])
    writer.writerow(['Last Updated', profile_data.get('last_updated', '')])
    for node in profile_data.get('nodes', {}).values():
        if node['type'] == 'budget':
            writer.writerow(['Budget', node['data'].get('budget_range', '')])
        if node['type'] == 'interests':
            writer.writerow(['Interests', ', '.join(node['data'].get('interests', []))])
    writer.writerow([])  # Blank row

    # Write trip details
    writer.writerow(['Trip #', 'Destination', 'Dates', 'Budget', 'Flights', 'Hotels', 'Itinerary', 'Budget Analysis', 'Travel Tips', 'Recommendations'])
    user_plans = TravelPlan.query.filter_by(user_id=user_id).order_by(TravelPlan.created_at.desc()).all()
    for idx, plan in enumerate(user_plans, 1):
        try:
            details = json.loads(plan.itinerary) if plan.itinerary else {}
        except Exception:
            details = {}
        flights = '; '.join(details.get('flights', []))
        hotels = '; '.join([f"{h.get('name', '')} ({h.get('price', '')})" for h in details.get('hotels', [])])
        itinerary = ' | '.join([f"{day}: {', '.join(acts)}" for day, acts in details.get('itinerary', {}).items()])
        budget_analysis = '; '.join([f"{k}: {v}" for k, v in details.get('budget_analysis', {}).items()])
        travel_tips = '; '.join([f"{k}: {', '.join(v)}" for k, v in details.get('travel_tips', {}).items()])
        recommendations = '; '.join([f"{k}: {', '.join(v)}" for k, v in details.get('personalized_recommendations', {}).items()])
        writer.writerow([
            idx,
            plan.destination,
            f"{plan.checkin_date} to {plan.checkout_date}",
            plan.budget,
            flights,
            hotels,
            itinerary,
            budget_analysis,
            travel_tips,
            recommendations
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name=f'traveler_profile_{user_id}.csv',
        mimetype='text/csv'
    )

@app.route('/clear_profile', methods=['POST'])
@login_required
def clear_profile():
    user_id = session.get('user_id')
    # Delete from database
    db_profile = TravelerProfile.query.filter_by(user_id=user_id).first()
    if db_profile:
        db.session.delete(db_profile)
        db.session.commit()
    # Delete from in-memory
    if str(user_id) in traveler_profiles.profiles:
        del traveler_profiles.profiles[str(user_id)]
    return {"status": "success"}

# --- Create DB Tables if not exist ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)