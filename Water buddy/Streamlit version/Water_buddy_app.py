import streamlit as st
import matplotlib.pyplot as plt
import os, json, pickle
from datetime import date, datetime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# ---------------- CONFIG ----------------
st.set_page_config(page_title="💧 WaterBuddy", layout="centered")

# ---------------- THEME ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

def switch_theme():
    st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"

theme = st.session_state.theme
themes = {
    "Light": {
        "bg": "#fdfcfb",
        "sidebar": "#f4f1ed",
        "text": "#333333",
        "primary": "#4da6ff",
        "accent": "#80c7ff",
        "metric": "#1a4d80",
        "button_bg": "#4da6ff",
        "button_hover": "#3399ff"
    },
    "Dark": {
        "bg": "#000000",
        "sidebar": "#cf5d21",
        "text": "#ffffff",
        "primary": "#6ca8ff",
        "accent": "#3399ff",
        "metric": "#8dc6ff",
        "button_bg": "#6ca8ff",
        "button_hover": "#3399ff"
    }
}
colors = themes[theme]

st.markdown(f"""
<style>
body, [class*="block-container"] {{
    background-color: {colors['bg']};
    color: {colors['text']};
    font-family: 'Segoe UI', sans-serif;
}}
section[data-testid="stSidebar"] {{
    background-color: {colors['sidebar']} !important;
    border-right: 1px solid rgba(200,200,200,0.1);
    padding: 1rem;
}}
div.stButton > button {{
    background-color: {colors['button_bg']};
    color: white;
    border-radius: 15px;
    border: none;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    font-size: 0.95rem;
    margin: 0.3rem 0;
    width: 100%;
    transition: all 0.3s ease;
}}
div.stButton > button:hover {{
    background-color: {colors['button_hover']};
    transform: scale(1.03);
}}
div[data-testid="stMetricValue"] {{
    color: {colors['metric']};
    font-size: 1.2rem;
    font-weight: bold;
}}
.footer {{
    text-align: center;
    font-size: 0.85rem;
    color: {'#999' if theme == 'Dark' else '#8a817c'};
    padding: 1.5rem 0;
}}
@keyframes pulseGlow {{
    0% {{ box-shadow: 0 0 10px 2px rgba(255,69,0,0.4); }}
    50% {{ box-shadow: 0 0 20px 5px rgba(255,69,0,0.7); }}
    100% {{ box-shadow: 0 0 10px 2px rgba(255,69,0,0.4); }}
}}
.pulse {{
    animation: pulseGlow 1.5s infinite;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- USER MANAGEMENT ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "google_authenticated" not in st.session_state:
    st.session_state.google_authenticated = False

def load_user_data(username):
    filename = f"{username}_history.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {"total_ml": 0, "goal_ml": 2200, "hourly_log": {}, "date": date.today().isoformat(),
            "name": username, "age":0, "occupation":"", "password":"","google_signed_in":False}

def save_user_data(username, data):
    with open(f"{username}_history.json","w") as f:
        json.dump(data, f, indent=2)

# ---------------- GOOGLE SIGN-IN ----------------
CLIENT_SECRETS_FILE = r"C:\Users\Jeyaditya\AppData\Local\Programs\Python\Python313\Python folder\Bheema mam\Water buddy\client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/userinfo.email",
          "openid"]

def save_credentials(creds):
    with open("google_creds.pkl", "wb") as f:
        pickle.dump(creds, f)

def load_credentials():
    if os.path.exists("google_creds.pkl"):
        with open("google_creds.pkl", "rb") as f:
            return pickle.load(f)
    return None

def google_sign_in():
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri="http://localhost:8501/"
        )
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
        st.write(f"[Click here to sign in with Google]({auth_url})")
    except Exception as e:
        st.error("⚠️ Please provide a valid client_secrets.json file path.")
        st.write(e)

# ---------------- LOGIN SCREEN ----------------
def login_screen():
    st.title("💧 Welcome to WaterBuddy")
    choice = st.radio("Login / Signup / Guest", ["Login", "Signup", "Guest"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice=="Login" and st.button("Login"):
        user_data_file = f"{username}_history.json"
        if os.path.exists(user_data_file):
            data = load_user_data(username)
            if password == data.get("password",""):
                st.session_state.user = username
            else:
                st.error("Incorrect password!")
        else:
            st.error("User not found!")

    if choice=="Signup" and st.button("Create Account"):
        if username:
            data = load_user_data(username)
            data["password"] = password
            save_user_data(username, data)
            st.success("Account created! Please login.")
        else:
            st.warning("Enter a username to signup.")

    if choice=="Guest" and st.button("Continue as Guest"):
        st.session_state.user = f"guest_{datetime.now().timestamp()}"

    st.markdown("OR")
    if st.button("Sign in with Google"):
        google_sign_in()

# ---------------- PROGRESS BAR ----------------
def display_progress_bar(total, goal):
    progress_percent = (total/goal)*100 if goal>0 else 0
    progress_bar_value = min(progress_percent/100, 1.0)
    color = colors["primary"] if progress_percent<=100 else "#FF4500"
    glow_class = "pulse" if progress_percent>100 else ""
    st.markdown(f"""
    <div style="border: 1px solid #ccc; width:100%; height:32px; border-radius:12px; background-color:{'#ddd' if theme=='Light' else '#333'};">
        <div class="{glow_class}" style="
            width:{progress_bar_value*100}%;
            height:100%;
            background: linear-gradient(to right,{color},{colors['accent']});
            border-radius:12px;
            text-align:center;
            font-weight:bold;
            line-height:32px;
            color:{'black' if theme=='Light' else 'white'};
            transition: width 0.3s ease, box-shadow 0.3s ease;
        ">{int(progress_percent)}%</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- MAIN APP ----------------
creds = load_credentials()
if creds and creds.valid and not st.session_state.google_authenticated:
    st.session_state.user = creds.id_token.get('email', 'google_user')
    st.session_state.google_authenticated = True
    user_data = load_user_data(st.session_state.user)
    user_data["google_signed_in"] = True
    save_user_data(st.session_state.user, user_data)

if st.session_state.user is None:
    login_screen()
else:
    username = st.session_state.user
    state = load_user_data(username)

    def add_water(amount):
        hour = str(datetime.now().hour)
        state["total_ml"] += amount
        state["hourly_log"][hour] = state["hourly_log"].get(hour,0)+amount
        save_user_data(username,state)
        st.success(f"Added {amount} ml 💧")

    def percent(total, goal):
        return int((total/goal)*100) if goal>0 else 0

    def reset_day():
        state["total_ml"] = 0
        state["hourly_log"] = {}
        state["date"] = date.today().isoformat()
        save_user_data(username, state)
        st.success("Day has been reset! All water intake set to 0 for today.")

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=90)
        st.title(f"WaterBuddy 💧 ({username})")
        st.markdown("---")
        page = st.radio("Navigation", ["🏠 Home","📈 Charts","⚙️ Settings","💡 Tips","👤 Profile"])
        st.markdown("---")
        st.metric("Today's Progress", f"{percent(state['total_ml'],state['goal_ml'])}%", f"{state['total_ml']}/{state['goal_ml']} ml")
        display_progress_bar(state['total_ml'], state['goal_ml'])
        st.markdown("---")
        st.button(f"Switch to {'🌙 Dark' if theme=='Light' else '☀️ Light'} Mode", on_click=switch_theme)

    if page=="🏠 Home":
        st.header("💧 Stay Hydrated")
        col1,col2,col3 = st.columns(3)
        col1.button("+100 ml", on_click=add_water,args=(100,))
        col2.button("+250 ml", on_click=add_water,args=(250,))
        col3.button("+500 ml", on_click=add_water,args=(500,))
        amount = st.number_input("Manual Entry (ml)",50,2000,250,50)
        if st.button("Add Water Intake"):
            add_water(amount)
        st.metric("Total Intake", f"{state['total_ml']} ml")
        display_progress_bar(state['total_ml'], state['goal_ml'])
        # ---- Reset Button under Total Intake ----
        if st.button("🔄 Reset Today's Intake"):
            reset_day()

    elif page=="📈 Charts":
        st.header("📊 Hydration Trends")
        hourly_data = [state["hourly_log"].get(str(h),0) for h in range(24)]
        hours = [f"{h:02d}" for h in range(24)]
        plt.figure(figsize=(8,3))
        plt.bar(hours,hourly_data,color=colors["primary"])
        plt.xlabel("Hour of Day")
        plt.ylabel("Water (ml)")
        plt.title("Hourly Intake")
        st.pyplot(plt)

    elif page=="⚙️ Settings":
        st.header("⚙️ Personalize Your Experience")
        state["name"] = st.text_input("Name", state.get("name",""))
        state["age"] = st.number_input("Age",0,120,state.get("age",0))
        state["occupation"] = st.text_input("Occupation", state.get("occupation",""))
        state["goal_ml"] = st.number_input("Daily Goal (ml)",1000,5000,step=100,value=state.get("goal_ml",2200))
        state["password"] = st.text_input("Change Password", type="password", value=state.get("password",""))
        if st.button("Save Changes"):
            save_user_data(username,state)
            st.success("Settings saved ✅")

        creds = load_credentials()
        if creds and creds.valid:
            st.success("✅ Signed in with Google")
            st.write(f"Email: {creds.id_token.get('email')}")
        else:
            if st.button("Sign in with Google"):
                google_sign_in()

    elif page=="💡 Tips":
        st.header("💡 Smart Hydration Tips")
        tips = [
            "Drink a glass of water after waking up.",
            "Carry a reusable bottle.",
            "Flavor water with fruit.",
            "Set reminders throughout the day.",
            "Hydrate before/after exercise."
        ]
        for tip in tips: st.write(f"- {tip}")

    elif page=="👤 Profile":
        st.header("👤 Profile Details")
        st.write(f"Name: {state.get('name','')}")
        st.write(f"Age: {state.get('age',0)}")
        st.write(f"Occupation: {state.get('occupation','')}")
        st.write(f"Daily Goal: {state.get('goal_ml',0)} ml")
        st.write(f"Google Signed In: {'✅' if state.get('google_signed_in',False) else '❌'}")

    # Footer
    st.markdown('<div class="footer">Made with ❤️ by WaterBuddy | A healthy habit, simplified.</div>', unsafe_allow_html=True)
