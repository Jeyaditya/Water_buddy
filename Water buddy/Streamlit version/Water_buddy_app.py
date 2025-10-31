```python
import streamlit as st
import matplotlib.pyplot as plt
import os, json, pickle, time
import datetime as dt
from datetime import date
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from streamlit.components.v1 import html

st.set_page_config(page_title="💧 WaterBuddy", layout="centered")

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
        "bg": "#0c0c0c",
        "sidebar": "#1a1a1a",
        "text": "#ffffff",
        "primary": "#6ca8ff",
        "accent": "#2e6fe3",
        "metric": "#8dc6ff",
        "button_bg": "#3c7cff",
        "button_hover": "#5a96ff"
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
.mascot-container {{
    position: fixed;
    right: 18px;
    bottom: 100px;
    width: 120px;
    height: 120px;
    z-index: 9999;
    pointer-events: none;
}}
.mascot {{
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    transition: transform 0.4s ease, filter 0.4s ease;
}}
.mascot.happy {{ transform: translateY(-6px) scale(1.05); filter: hue-rotate(10deg) saturate(1.2); }}
.mascot.sad {{ transform: translateY(0px) scale(0.98) rotate(-2deg); filter: grayscale(0.2) contrast(0.9); }}
.mascot.angry {{
    transform: translateY(-2px) scale(1.02) rotate(2deg);
    box-shadow: 0 0 18px rgba(255,0,0,0.35);
    animation: shake 0.5s infinite;
}}
@keyframes shake {{
    0% {{ transform: translateX(0px); }}
    25% {{ transform: translateX(-3px); }}
    50% {{ transform: translateX(3px); }}
    75% {{ transform: translateX(-2px); }}
    100% {{ transform: translateX(0px); }}
}}
.mascot-face {{
    font-size: 3.2rem;
    line-height: 1;
    user-select: none;
}}
.mascot-bubble {{
    position: absolute;
    bottom: 120px;
    right: 0;
    background: rgba(0,0,0,0.6);
    color: white;
    padding: 6px 10px;
    border-radius: 10px;
    font-size: 0.9rem;
    pointer-events: none;
    white-space: nowrap;
    transform: translateY(6px);
    transition: transform 0.3s ease, opacity 0.3s ease;
    opacity: 0;
}
.mascot.show-bubble .mascot-bubble {{
    transform: translateY(0);
    opacity: 1;
}}
</style>
""", unsafe_allow_html=True)

def update_hydration_logs(state, amount):
    now = dt.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    month_str = now.strftime("%Y-%m")
    if "daily_log" not in state:
        state["daily_log"] = {}
    if "monthly_log" not in state:
        state["monthly_log"] = {}
    state["daily_log"][date_str] = state["daily_log"].get(date_str, 0) + amount
    state["monthly_log"][month_str] = state["monthly_log"].get(month_str, 0) + amount
    if "hourly_log" not in state:
        state["hourly_log"] = {}
    current_hour = str(now.hour)
    state["hourly_log"][current_hour] = state["hourly_log"].get(current_hour, 0) + amount
    state["last_update_iso"] = now.isoformat()

if "user" not in st.session_state:
    st.session_state.user = None

if "google_authenticated" not in st.session_state:
    st.session_state.google_authenticated = False

def load_user_data(username):
    filename = f"{username}_history.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {
        "total_ml": 0, "goal_ml": 2200, "hourly_log": {},
        "date": date.today().isoformat(), "name": username,
        "age": 0, "occupation": "", "password": "",
        "google_signed_in": False, "reminders_per_hour": 0,
        "daily_log": {}, "monthly_log": {}, "last_update_iso": None
    }

def save_user_data(username, data):
    with open(f"{username}_history.json","w") as f:
        json.dump(data, f, indent=2)

CLIENT_SECRETS_FILE = "client_secrets.json"
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

def show_browser_notification(title, message):
    js_code = f"""
    <script>
    if (Notification.permission === "granted") {{
        new Notification("{title}", {{
            body: "{message}",
            icon: "https://cdn-icons-png.flaticon.com/512/869/869869.png"
        }});
    }} else if (Notification.permission !== "denied") {{
        Notification.requestPermission().then(function(permission) {{
            if (permission === "granted") {{
                new Notification("{title}", {{
                    body: "{message}",
                    icon: "https://cdn-icons-png.flaticon.com/512/869/869869.png"
                }});
            }}
        }});
    }}
    </script>
    
    html(js_code)

def handle_notifications(state):
    reminders = state.get("reminders_per_hour", 0)
    if reminders == 0:
        return
    current_minute = int(time.strftime("%M"))
    interval = 60 // reminders
    if interval > 0 and current_minute % interval == 0:
        show_browser_notification(
            "💧 Time to drink water!",
            f"Stay hydrated — your WaterBuddy reminder ({reminders}x/hour)."
        )

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
        st.session_state.user = f"guest_{dt.datetime.now().timestamp()}"
    st.markdown("OR")
    if st.button("Sign in with Google"):
        st.write("This is a feature that will be added in a future update")

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
        now_hour = str(dt.datetime.now().hour)
        state["total_ml"] = state.get("total_ml", 0) + amount
        if "hourly_log" not in state:
            state["hourly_log"] = {}
        state["hourly_log"][now_hour] = state["hourly_log"].get(now_hour,0)+amount
        update_hydration_logs(state, amount)
        save_user_data(username,state)
        st.success(f"Added {amount} ml 💧")

    def percent(total, goal):
        return int((total/goal)*100) if goal>0 else 0

    def reset_day():
        state["total_ml"] = 0
        state["hourly_log"] = {}
        state["date"] = date.today().isoformat()
        state["daily_log"][date.today().isoformat()] = 0
        save_user_data(username, state)
        st.success("Day has been reset! All water intake set to 0 for today.")

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=90)
        st.title(f"WaterBuddy 💧 ({username})")
        st.markdown("---")
        page = st.radio("Navigation", ["🏠 Home","📈 Charts","⚙️ Settings","💡 Tips","👤 Profile"])
        st.markdown("---")
        st.metric("Today's Progress", f"{percent(state.get('total_ml',0),state.get('goal_ml',2200))}%", f"{state.get('total_ml',0)}/{state.get('goal_ml',2200)} ml")
        display_progress_bar(state.get('total_ml',0), state.get('goal_ml',2200))
        st.markdown("---")
        st.button(f"Switch to {'🌙 Dark' if theme=='Light' else '☀️ Light'} Mode", on_click=switch_theme)
        st.subheader("🔔 Notification Settings")
        notification_choice = st.selectbox(
            "Reminder frequency",
            ("None", "Once per hour", "Twice per hour", "Thrice per hour"),
            index=0 if state.get("reminders_per_hour",0) not in (1,2,3) else list({1:"Once per hour",2:"Twice per hour",3:"Thrice per hour"}.keys()).index(state.get("reminders_per_hour",0)) if False else 0
        )
        reminder_mapping = {"None": 0, "Once per hour": 1, "Twice per hour": 2, "Thrice per hour": 3}
        state["reminders_per_hour"] = reminder_mapping.get(notification_choice, 0)
        save_user_data(username, state)

    def compute_weekly_series(state):
        today = dt.date.today()
        series = []
        labels = []
        for i in range(6, -1, -1):
            day = today - dt.timedelta(days=i)
            key = day.isoformat()
            series.append(state.get("daily_log", {}).get(key, 0))
            labels.append(day.strftime("%a"))
        return labels, series

    def compute_monthly_series(state):
        today = dt.date.today()
        labels = []
        series = []
        for i in range(5, -1, -1):
            month = (today.replace(day=1) - dt.timedelta(days=i*30)).strftime("%Y-%m")
            labels.append(month)
            series.append(state.get("monthly_log", {}).get(month, 0))
        return labels, series

    def compute_yearly_series(state):
        this_year = dt.date.today().year
        labels = []
        series = []
        for m in range(1,13):
            key = f"{this_year}-{m:02d}"
            labels.append(dt.date(this_year,m,1).strftime("%b"))
            series.append(state.get("monthly_log", {}).get(key, 0))
        return labels, series

    def render_mascot(state):
        now = dt.datetime.now()
        last_iso = state.get("last_update_iso")
        last_update = None
        if last_iso:
            try:
                last_update = dt.datetime.fromisoformat(last_iso)
            except:
                last_update = None
        goal = state.get("goal_ml", 2200)
        total = state.get("total_ml", 0)
        pct = percent(total, goal)
        state_str = "neutral"
        bubble = "Keep going!"
        if pct >= 100:
            state_str = "happy"
            bubble = "Yay! Goal reached 🎉"
        else:
            if last_update:
                hours_since = (now - last_update).total_seconds() / 3600.0
                if hours_since >= 3 and total==0:
                    state_str = "angry"
                    bubble = "Hey! You haven't logged water for 3+ hours 😠"
                elif total < goal*0.25:
                    state_str = "sad"
                    bubble = "Drink up — you're low on water 😢"
                else:
                    state_str = "neutral"
                    bubble = "Keep sipping!"
            else:
                state_str = "neutral"
                bubble = "Let's start hydrating!"
        face = "🙂"
        if state_str == "happy":
            face = "😄"
        elif state_str == "sad":
            face = "😟"
        elif state_str == "angry":
            face = "😠"
        bubble_html = f'<div class="mascot-bubble">{bubble}</div>'
        mascot_html = f'''
        <div class="mascot-container mascot-show">
          <div id="mascot" class="mascot {state_str} {'show-bubble' if True else ''}">
            <div class="mascot-face">{face}</div>
            {bubble_html}
          </div>
        </div>
        <script>
        setTimeout(()=>{{
            const m = document.getElementById("mascot");
            if(m) m.classList.add("show-bubble");
            setTimeout(()=>{{ if(m) m.classList.remove("show-bubble"); }},4000);
        }},600);
        </script>
        '''
        st.markdown(mascot_html, unsafe_allow_html=True)

    if page=="🏠 Home":
        st.header("💧 Stay Hydrated")
        col1,col2,col3 = st.columns(3)
        col1.button("+100 ml", on_click=add_water,args=(100,))
        col2.button("+250 ml", on_click=add_water,args=(250,))
        col3.button("+500 ml", on_click=add_water,args=(500,))
        amount = st.number_input("Manual Entry (ml)",50,2000,250,50)
        if st.button("Add Water"):
            add_water(int(amount))
        st.metric("Total Intake", f"{state.get('total_ml',0)} ml")
        display_progress_bar(state.get('total_ml',0), state.get('goal_ml',2200))
        if st.button("🔄 Reset Today's Intake"):
            reset_day()
        render_mascot(state)

    elif page=="📈 Charts":
        st.header("📊 Hydration Trends")
        hourly_data = [state.get("hourly_log",{}).get(str(h),0) for h in range(24)]
        hours = [f"{h:02d}" for h in range(24)]
        plt.figure(figsize=(8,3))
        plt.bar(hours,hourly_data)
        plt.xlabel("Hour of Day")
        plt.ylabel("Water (ml)")
        plt.title("Hourly Intake")
        st.pyplot(plt)
        labels_w, series_w = compute_weekly_series(state)
        plt.figure(figsize=(8,3))
        plt.plot(labels_w, series_w, marker='o')
        plt.title("Last 7 Days")
        plt.xlabel("Day")
        plt.ylabel("Water (ml)")
        st.pyplot(plt)
        labels_m, series_m = compute_monthly_series(state)
        plt.figure(figsize=(8,3))
        plt.bar(labels_m, series_m)
        plt.title("Last 6 Months (approx)")
        plt.xlabel("Month")
        plt.ylabel("Water (ml)")
        st.pyplot(plt)
        labels_y, series_y = compute_yearly_series(state)
        plt.figure(figsize=(8,3))
        plt.plot(labels_y, series_y, marker='o')
        plt.title(f"Year {dt.date.today().year}")
        plt.xlabel("Month")
        plt.ylabel("Water (ml)")
        st.pyplot(plt)
        render_mascot(state)

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
        render_mascot(state)

    elif page=="💡 Tips":
        st.header("💡 Smart Hydration Tips")
        for tip in [
            "Drink a glass of water after waking up.",
            "Carry a reusable bottle.",
            "Flavor water with fruit.",
            "Set reminders throughout the day.",
            "Hydrate before/after exercise."
        ]:
            st.write(f"- {tip}")
        render_mascot(state)

    elif page=="👤 Profile":
        st.header("👤 Profile Details")
        st.write(f"Name: {state.get('name','')}")
        st.write(f"Age: {state.get('age',0)}")
        st.write(f"Occupation: {state.get('occupation','')}")
        st.write(f"Daily Goal: {state.get('goal_ml',0)} ml")
        st.write(f"Google Signed In: {'✅' if state.get('google_signed_in',False) else '❌'}")
        render_mascot(state)

    handle_notifications(state)

    st.markdown('<div class="footer">Made with ❤️ by WaterBuddy | A healthy habit, simplified.</div>', unsafe_allow_html=True)

