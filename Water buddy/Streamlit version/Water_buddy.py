# waterbuddy_final_v2.py
import streamlit as st
import matplotlib.pyplot as plt
import os, json, time, random, base64
from datetime import date, datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="💧 WaterBuddy", layout="centered")

# ---------------- Session defaults ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "user" not in st.session_state:
    st.session_state.user = None

# safe rerun flag helper
def safe_rerun():
    st.session_state["_trigger_rerun"] = True

# at end of script we'll call st.rerun() if requested
# ---------------- Theme ----------------
def switch_theme():
    st.session_state.theme = "Dark" if st.session_state.theme=="Light" else "Light"

theme = st.session_state.theme
themes = {
    "Light": {"bg":"#fdfcfb","sidebar":"#f4f1ed","text":"#222","primary":"#3BAFDA","accent":"#7DD3FC","metric":"#005C91","button_bg":"#3BAFDA","button_hover":"#2C9DC7"},
    "Dark": {"bg":"#0B1117","sidebar":"#12161a","text":"#E8F1F2","primary":"#4DC3FA","accent":"#2E93E6","metric":"#7DD3FC","button_bg":"#2E93E6","button_hover":"#47B0FF"}
}
colors = themes[theme]

# ---------------- Global CSS ----------------
st.markdown(f"""
<style>
/* base colors */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [class*="block-container"] {{
    background-color: {colors['bg']} !important;
    color: {colors['text']} !important;
    margin:0 !important; padding:0 !important; font-family:'Segoe UI',sans-serif !important;
}}
/* ensure all text follows theme */
body, p, span, div, label, input, textarea, select, .stMarkdown, .stText, .stMetric, .css-1d391kg p {{
    color: inherit !important;
}}
.stApp header {{ background-color:transparent !important; backdrop-filter:none !important; }}
[data-testid="stSidebar"] {{ background-color:{colors['sidebar']} !important; color:{colors['text']} !important; border-right:1px solid rgba(255,255,255,0.03); }}
div.stButton > button {{
    background-color:{colors['button_bg']} !important; color:white !important; border-radius:12px !important;
    padding:0.5rem 1rem !important; font-weight:600 !important; transition: all 0.16s ease !important;
}}
div.stButton > button:hover {{ background-color:{colors['button_hover']} !important; transform:scale(1.03); }}
.pulse {{ animation: shimmerGlow 2s ease-in-out infinite; }}
@keyframes shimmerGlow {{
    0% {{ box-shadow:0 0 6px 1px rgba(0,150,255,0.12); }}
    50% {{ box-shadow:0 0 16px 5px rgba(0,200,255,0.22); }}
    100% {{ box-shadow:0 0 6px 1px rgba(0,150,255,0.12); }}
}}

/* Right persistent mascot (large ~300px) */
.mascot-sidebar {{
    position: fixed;
    right: 18px;
    top: 50%;
    transform: translateY(-50%);
    width: 320px;
    text-align: center;
    z-index: 9999;
    background: rgba(255,255,255,0.02);
    border-radius: 16px;
    padding: 12px;
    pointer-events: none; /* don't block page clicks */
}}
/* default dark bubble */
.mascot-bubble {{
    background: rgba(0,0,0,0.75);
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-size: 0.98rem;
    display:inline-block;
    max-width:300px;
    box-shadow:0 6px 18px rgba(0,0,0,0.18);
    pointer-events: auto;
}}
/* light bubble variant for light theme */
.mascot-bubble.light {{
    background: rgba(255,255,255,0.95);
    color: #222;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}}
.mascot-bubble.bounce {{ animation: bounce 0.9s ease-in-out 1; }}
@keyframes bounce {{ 0% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px); }} 100% {{ transform: translateY(0); }} }}
.mascot-img {{ width:300px; height:auto; border-radius:16px; transition: transform 0.35s ease-in-out; display:block; margin:0 auto; pointer-events:none; }}
.mascot-img.wiggle {{ animation: wiggle 1.4s infinite; transform-origin:center; }}
@keyframes wiggle {{
  0%,100% {{ transform: rotate(0deg); }}
  25% {{ transform: rotate(3deg); }}
  50% {{ transform: rotate(0deg); }}
  75% {{ transform: rotate(-3deg); }}
}}
.mascot-img.jump {{ animation: jump 1s ease-in-out 3; }}
@keyframes jump {{ 0% {{transform:translateY(0px);}} 30% {{transform:translateY(-36px);}} 60% {{transform:translateY(0px);}} 100% {{transform:translateY(0px);}} }}

@media (max-width:900px){{
  .mascot-sidebar {{ right:8px; width:220px; }}
  .mascot-img {{ width:200px; }}
  .mascot-bubble {{ max-width:200px; font-size:0.9rem; }}
}}

/* Light-theme form controls override to ensure readability */
input, textarea, select {{
    background: {'#ffffff' if theme=='Light' else 'transparent'} !important;
    color: {'#222' if theme=='Light' else 'inherit'} !important;
    border: 1px solid {'rgba(0,0,0,0.08)' if theme=='Light' else 'rgba(255,255,255,0.06)'} !important;
    border-radius: 8px !important;
    padding: 6px 8px !important;
}}
::placeholder {{ color: rgba(0,0,0,0.4) !important; }}
</style>
""", unsafe_allow_html=True)

# ---------------- Data helpers ----------------
def load_user_data(username):
    fn = f"{username}_history.json"
    if os.path.exists(fn):
        try:
            with open(fn,"r") as f:
                return json.load(f)
        except: pass
    # include default voice fields
    return {"total_ml":0,"goal_ml":2200,"hourly_log":{},"daily_log":{},"monthly_log":{},
            "date":date.today().isoformat(),"name":username,"password":"","age":20,"career":"",
            "health_conditions":[],"reminders_per_hour":0,"xp":0,"level":1,"last_update_iso":None,
            "last_spoken_pct":None,"profile_prompt_shown":False,"voice_lang":"en","voice_lang_name":"English"}

def save_user_data(username,data):
    with open(f"{username}_history.json","w") as f:
        json.dump(data,f,indent=2)

def update_hydration_logs(state,amount):
    now=datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    month_str = now.strftime("%Y-%m")
    state.setdefault("daily_log",{})[date_str]=state.get("daily_log",{}).get(date_str,0)+amount
    state.setdefault("monthly_log",{})[month_str]=state.get("monthly_log",{}).get(month_str,0)+amount
    hour=str(now.hour)
    state.setdefault("hourly_log",{})[hour]=state.get("hourly_log",{}).get(hour,0)+amount
    state["last_update_iso"]=now.isoformat()
    state["date"]=date.today().isoformat()

def percent(total,goal):
    return int((total/goal)*100) if goal>0 else 0

def update_xp(state,amount):
    xp_gain = amount//50
    state["xp"]=state.get("xp",0)+xp_gain
    lvl=state.get("level",1)
    leveled_up=False
    while state["xp"]>=100+(lvl-1)*50:
        state["xp"]-=100+(lvl-1)*50
        lvl+=1
        leveled_up=True
    state["level"]=lvl
    return leveled_up

def auto_day_rollover(state,username):
    today_str=date.today().isoformat()
    if state.get("date")!=today_str:
        state["total_ml"]=state.get("daily_log",{}).get(today_str,0)
        state["hourly_log"]={}
        state["date"]=today_str
        save_user_data(username,state)

# ---------------- Series helpers ----------------
def compute_weekly_series(state):
    today=date.today()
    labels, series=[],[]
    for i in range(6,-1,-1):
        d=today-timedelta(days=i)
        labels.append(d.strftime("%a"))
        series.append(state.get("daily_log",{}).get(d.isoformat(),0))
    return labels, series

def compute_monthly_series(state):
    today=date.today()
    labels, series=[],[]
    for i in range(5,-1,-1):
        first = (today.replace(day=1)-timedelta(days=30*i))
        key=first.strftime("%Y-%m")
        labels.append(first.strftime("%b %y"))
        series.append(state.get("monthly_log",{}).get(key,0))
    return labels, series

# ---------------- Voice helper (multilingual, emotion-aware) ----------------
def speak(text, mood="neutral", lang="en"):
    # map to broad language codes; browser may select best available voice
    lang_map = {"en":"en-US","hi":"hi-IN","ta":"ta-IN","es":"es-ES","fr":"fr-FR","ja":"ja-JP"}
    name_map = {"en":"English","hi":"Hindi","ta":"Tamil","es":"Spanish","fr":"French","ja":"Japanese"}
    voice_lang = lang_map.get(lang, "en-US")
    lang_name = name_map.get(lang, "English")
    full_text = f"({lang_name}) {text}"
    text_js = full_text.replace('"','\\"').replace("\n","\\n")
    pitch = 1.0; rate = 1.0; volume = 1.0
    if mood == "happy": pitch, rate = 1.35, 1.08
    elif mood == "sad": pitch, rate = 0.85, 0.92
    elif mood == "angry": pitch, rate = 0.95, 1.15
    elif mood == "calm": pitch, rate = 1.0, 0.95

    components.html(f"""
    <script>
      try {{
        const utter = new SpeechSynthesisUtterance("{text_js}");
        utter.lang = "{voice_lang}";
        utter.pitch = {pitch};
        utter.rate = {rate};
        utter.volume = {volume};
        const voices = speechSynthesis.getVoices();
        if (voices && voices.length) {{
          const primary = voices.find(v=>v.lang && v.lang.startsWith("{voice_lang.split('-')[0]}"));
          if(primary) utter.voice = primary;
        }}
        speechSynthesis.cancel();
        speechSynthesis.speak(utter);
      }} catch(e) {{ console.log("speech error", e); }}
    </script>
    """, height=0)

# ---------------- Mascot (persistent right-side, uses base64 embed for reliability) ----------------
MOTIVATIONAL_TIPS = [
    "Tip: Drink a glass of water before each meal.",
    "Keep a water bottle on your desk for easy sips.",
    "Small sips often work better than chugging.",
    "Add a slice of lemon for flavor and refreshment.",
    "Hydrated brains focus better — keep sipping!"
]

def _img_to_data_uri(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        ext = os.path.splitext(path)[1].lower().replace('.','') or 'png'
        return f"data:image/{ext};base64,{b64}"
    except Exception:
        return None

def render_mascot(state, lang="en"):
    total=state.get("total_ml",0)
    goal=state.get("goal_ml",2200)
    pct=percent(total,goal)

    if pct>=100:
        img_file = "images/100.png"
        base_bubble = "🎉 Woohoo! Goal achieved! You did it!"
        mood = "happy"
        confetti = True
    elif pct>=75:
        img_file = "images/50.png"
        base_bubble = "Almost there! You're this close to finishing it 💪"
        mood = "happy"
        confetti = False
    elif pct>=25:
        img_file = "images/25.png"
        base_bubble = "Nice progress! Stay hydrated 🌊"
        mood = "calm"
        confetti = False
    else:
        img_file = "images/0.png"
        base_bubble = "Drink up — you're low on water 😢"
        mood = "sad"
        confetti = False

    tip = random.choice(MOTIVATIONAL_TIPS) if pct < 100 else "Celebrate! Keep this habit going."
    bubble_html = f"{base_bubble}<br><span style='font-size:12px;opacity:0.86;display:block;margin-top:6px'>{tip}</span>"

    last_spoken = state.get("last_spoken_pct", None)
    if last_spoken != pct:
        if pct>=100:
            speak_text = "Congratulations! You've reached your hydration goal!"
        elif pct>=75:
            speak_text = "You're this close to finishing it! Keep going!"
        elif pct>=25:
            speak_text = "Nice progress! Keep taking small sips."
        else:
            speak_text = "You're running low on water. Take a sip now."
        try:
            speak(speak_text, mood=mood, lang=state.get("voice_lang","en"))
        except:
            pass
        state["last_spoken_pct"] = pct

    # choose bubble variant for Light vs Dark
    bubble_variant_class = "light" if st.session_state.get("theme","Light")=="Light" else ""
    bubble_class = f"mascot-bubble {bubble_variant_class} bounce" if confetti else f"mascot-bubble {bubble_variant_class}"
    img_anim_class = "mascot-img wiggle" if (75 <= pct < 100) else "mascot-img"
    if pct >= 100:
        img_anim_class = "mascot-img wiggle jump"

    data_uri = _img_to_data_uri(img_file)
    if data_uri:
        img_tag = f'<img src="{data_uri}" class="{img_anim_class}" alt="Mascot" />'
    else:
        img_tag = '<div style="font-size:72px;line-height:1">🐢</div>'

    st.markdown(f"""
    <div class="mascot-sidebar">
      <div class="{bubble_class}">{bubble_html}</div>
      {img_tag}
    </div>
    """, unsafe_allow_html=True)

    if confetti:
        components.html("""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <script>
        (function(){
            const duration = 3500;
            const end = Date.now() + duration;
            (function frame() {
                confetti({
                    particleCount: 80,
                    spread: 120,
                    startVelocity: 40,
                    origin: { x: 0.85, y: 0.4 }
                });
                if (Date.now() < end) requestAnimationFrame(frame);
            })();
        })();
        </script>
        """, height=0)

# ---------------- Progress bar ----------------
def display_progress_bar(total,goal):
    progress_percent=percent(total,goal)
    progress_value=min(progress_percent/100,1.0)
    color=colors["primary"] if progress_percent<=100 else "#FF4500"
    glow_class="pulse" if progress_percent>=100 else ""
    st.markdown(f"""
    <div style="border:1px solid rgba(0,0,0,0.08); width:100%; height:36px; border-radius:12px; background-color:{'#fff' if st.session_state.get('theme','Light')=='Light' else '#222'};">
      <div class="{glow_class}" style="width:{progress_value*100}%; height:100%;
      background:linear-gradient(90deg,{color} 0%, {colors['accent']} 100%);
      border-radius:12px;text-align:center;font-weight:bold;line-height:36px;
      color:{'black' if st.session_state.get('theme','Light')=='Light' else 'white'};transition:width .3s ease;">
      {int(progress_percent)}%
      </div>
    </div>
    """,unsafe_allow_html=True)

# ---------------- Notifications / Reminders ----------------
def handle_notifications(state):
    try:
        rem=int(state.get("reminders_per_hour",0))
        if rem<=0: return
        interval=max(1,60//rem)
        minute=int(time.strftime("%M"))
        if minute%interval==0:
            js=f"""
            <script>
            if(Notification && Notification.permission==='granted') {{
                new Notification("💧 Time to drink water!", {{ body:"Stay hydrated — WaterBuddy", icon:"0.png" }});
            }} else if(Notification && Notification.permission!=='denied') {{
                Notification.requestPermission().then(p=>{{ if(p==='granted') new Notification("💧 Time to drink water!", {{ body:"Stay hydrated — WaterBuddy", icon:"0.png" }}); }});
            }}
            </script>
            """
            components.html(js,height=0)
    except: pass

# ---------------- Login ----------------
def login_screen():
    st.title("💧 Welcome to WaterBuddy")
    choice = st.radio("Login / Signup / Guest", ["Login","Signup","Guest"])
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    # added: age and career inputs on the login/signup screen so profile is set before Home
    age_input = st.number_input("Age",4,100,value=20, key="login_age")
    career_input = st.text_input("Career/Occupation", value="", key="login_career")

    st.markdown("**Tip:** After logging in, go to ⚙️ Settings to set up your profile (age, career) for accurate goals.")

    if choice=="Login" and st.button("Login", key="login_btn"):
        fn=f"{username}_history.json"
        if os.path.exists(fn):
            data=load_user_data(username)
            if password==data.get("password",""):
                # update age/career if provided
                try:
                    data["age"]=int(age_input)
                except:
                    pass
                if career_input:
                    data["career"]=career_input
                save_user_data(username,data)
                st.session_state.user=username
                safe_rerun()
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")

    if choice=="Signup" and st.button("Create Account", key="signup_btn"):
        if not username:
            st.error("Please enter a username to create an account.")
        else:
            data=load_user_data(username)
            data["password"] = password
            try:
                data["age"]=int(age_input)
            except:
                data["age"]=20
            data["career"]=career_input
            save_user_data(username, data)
            st.success("Account created! Please login.")

    if choice=="Guest" and st.button("Continue as Guest", key="guest_btn"):
        guestname = f"guest_{int(datetime.now().timestamp())}"
        data=load_user_data(guestname)
        data["password"] = ""
        try:
            data["age"]=int(age_input)
        except:
            data["age"]=20
        data["career"]=career_input
        save_user_data(guestname, data)
        st.session_state.user=guestname
        safe_rerun()

# ---------------- Age-based helper ----------------
def set_goal_by_age(state):
    age=state.get("age",20)
    if 4<=age<=8: goal=1200
    elif 9<=age<=13: goal=1700
    elif 14<=age<=64: goal=2200
    else: goal=1800
    state["goal_ml"]=goal
    save_user_data(st.session_state.user,state)

# ---------------- MAIN APP ----------------
if st.session_state.user is None:
    login_screen()
else:
    username = st.session_state.user
    state = load_user_data(username)
    auto_day_rollover(state,username)

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=90)
        st.title(f"WaterBuddy 💧 ({username})")

        page = st.radio("Navigation", ["🏠 Home","📈 Charts","🔔 Reminders","⚙️ Settings","💡 Tips","👤 Profile"], index=0)
        st.markdown("---")
        # keep only metric in sidebar to avoid duplicate progress bars
        st.metric("Today's Progress",f"{percent(state.get('total_ml',0),state.get('goal_ml',2200))}%",f"{state.get('total_ml',0)}/{state.get('goal_ml',2200)} ml")
        st.markdown("---")
        st.button(f"Switch to {'🌙 Dark' if st.session_state.get('theme','Light')=='Light' else '☀️ Light'} Mode",on_click=switch_theme)
        st.markdown("---")
        # language select: show full names but keep codes internally
        display_names = ["English","Hindi","Tamil","Spanish","French","Japanese"]
        codes = ["en","hi","ta","es","fr","ja"]
        cur_code = state.get("voice_lang","en")
        try:
            cur_index = codes.index(cur_code)
        except:
            cur_index = 0
        sel = st.selectbox("🌍 Voice language", display_names, index=cur_index)
        sel_index = display_names.index(sel)
        sel_code = codes[sel_index]
        state["voice_lang"] = sel_code
        state["voice_lang_name"] = sel
        # trigger a short confirmation speak when language changes
        try:
            speak(f"Voice set to {sel}", lang=sel_code)
        except:
            pass
        save_user_data(username,state)

    set_goal_by_age(state)

    # ---------------- Pages ----------------
    if page=="🏠 Home":
        st.header("💧 Stay Hydrated")
        c1,c2,c3 = st.columns(3)

        def add_water(a):
            try: a=int(a)
            except: return
            state["total_ml"]=state.get("total_ml",0)+a
            update_hydration_logs(state,a)
            leveled_up=update_xp(state,a)
            save_user_data(username,state)
            st.success(f"Added {a} ml 💧")
            try:
                # speak uses code in state and speak() prefixes language name
                speak(f"Added {a} milliliters. Good job!", mood="happy" if percent(state['total_ml'],state['goal_ml'])>=75 else "calm", lang=state.get("voice_lang","en"))
            except: pass
            if leveled_up:
                st.balloons()
            # do not render progress bar here to avoid duplicate
            save_user_data(username,state)

        c1.button("+100 ml", on_click=add_water,args=(100,), key="b100")
        c2.button("+250 ml", on_click=add_water,args=(250,), key="b250")
        c3.button("+500 ml", on_click=add_water,args=(500,), key="b500")

        # manual entry with distinct keys to avoid Enter double-trigger
        manual_key = "manual_intake_"+username
        a = st.number_input("Manual Entry (ml)",50,2000,250,50, key=manual_key)
        add_trigger = st.button("Add Water", key="add_btn_"+username)
        if add_trigger:
            add_water(a)

        st.metric("Total Intake",f"{state['total_ml']} ml")
        # single progress bar displayed in Home (only here)
        display_progress_bar(state['total_ml'],state['goal_ml'])
        if st.button("🔄 Reset Today's Intake", key="reset_btn"):
            state["total_ml"]=0
            state["hourly_log"]={}
            state["daily_log"][date.today().isoformat()]=0
            save_user_data(username,state)
            st.success("Day has been reset!")

    elif page=="📈 Charts":
        st.header("📊 Hydration Trends")
        hourly_data=[state.get("hourly_log",{}).get(str(h),0) for h in range(24)]
        hours=[f"{h:02d}" for h in range(24)]
        plt.figure(figsize=(9,3))
        if st.session_state.get("theme","Light")=="Dark": plt.rcParams.update({"text.color":colors["text"],"axes.labelcolor":colors["text"],"xtick.color":colors["text"],"ytick.color":colors["text"]})
        plt.bar(hours,hourly_data,color=colors["primary"])
        plt.xlabel("Hour of Day"); plt.ylabel("Water (ml)"); plt.title("Hourly Intake")
        st.pyplot(plt); plt.close()

        labels_w, series_w = compute_weekly_series(state)
        plt.figure(figsize=(9,3)); plt.plot(labels_w,series_w,marker="o",linestyle="-",color=colors['accent'])
        plt.title("Last 7 Days"); plt.xlabel("Day"); plt.ylabel("Water (ml)")
        st.pyplot(plt); plt.close()

        labels_m, series_m = compute_monthly_series(state)
        plt.figure(figsize=(9,3)); plt.bar(labels_m,series_m,color=colors["accent"])
        plt.title("Last 6 Months"); plt.xlabel("Month"); plt.ylabel("Water (ml)")
        st.pyplot(plt); plt.close()

    elif page=="🔔 Reminders":
        st.header("🔔 Reminders & Smart Features")
        st.write("Manage reminder frequency and snooze behavior here.")
        options = ("None","Once per hour","Twice per hour","Thrice per hour")
        rem_current = state.get("reminders_per_hour",0)
        sel_index = rem_current if rem_current in (0,1,2,3) else 0
        notification_choice = st.selectbox("Reminder frequency", options, index=sel_index)
        reminder_mapping = {"None":0,"Once per hour":1,"Twice per hour":2,"Thrice per hour":3}
        state["reminders_per_hour"] = reminder_mapping.get(notification_choice, 0)
        st.write("Snooze / Remind me later:")
        if st.button("Remind me later (snooze)", key="snooze_btn"):
            reason = st.selectbox("Why are you skipping?", ["Busy","No water nearby","Not thirsty","Other"], key="snooze_reason")
            st.info(f"Reminder snoozed. Reason: {reason}")
        st.markdown("---")
        st.subheader("Smart features (demo)")
        st.checkbox("Enable weather-based adjustments (demo)", value=False)
        st.info("Weather-based reminders will be available in future updates.")
        save_user_data(username,state)

    elif page=="⚙️ Settings":
        st.header("⚙️ Settings")
        username_new = st.text_input("Change Username", value=state.get("name",username))
        if st.button("Update Username", key="update_name") and username_new:
            state["name"]=username_new
            save_user_data(username,state)
            st.success("Username updated!")

        password_new = st.text_input("Change Password", type="password", key="pwd")
        if st.button("Update Password", key="update_pwd") and password_new:
            state["password"]=password_new
            save_user_data(username,state)
            st.success("Password updated!")

        age_new = st.number_input("Age",4,100,value=state.get("age",20), key="age_input")
        career_new = st.text_input("Career/Occupation",state.get("career",""), key="career_input")
        health_new = st.text_area("Health Conditions (comma separated)"," ,".join(state.get("health_conditions",[])), key="health_input")

        if st.button("Save Profile", key="save_profile"):
            state["age"]=age_new
            state["career"]=career_new
            state["health_conditions"]=[h.strip() for h in health_new.split(",") if h.strip()]
            set_goal_by_age(state)
            save_user_data(username,state)
            st.success("Profile saved!")

    elif page=="💡 Tips":
        st.header("💡 Water Tips")
        tips=["Drink a glass of water before each meal",
              "Keep a water bottle on your desk",
              "Add lemon or cucumber for flavor",
              "Set hourly reminders",
              "Track your progress in WaterBuddy"]
        for t in tips: st.info(t)

    elif page=="👤 Profile":
        st.header("👤 Profile")
        st.write(f"Username: {state.get('name',username)}")
        st.write(f"Level: {state.get('level',1)}")
        st.write(f"XP: {state.get('xp',0)}")
        st.write(f"Age: {state.get('age',20)}")
        st.write(f"Career: {state.get('career','')}")
        st.write(f"Health Conditions: {', '.join(state.get('health_conditions',[]))}")
        st.write(f"Daily Goal: {state.get('goal_ml',2200)} ml")
        st.write(f"Today's Intake: {state.get('total_ml',0)} ml")
        st.write("💡 Keep going! Every sip counts!")

    # ---------------- persistent mascot (render once per page) ----------------
    render_mascot(state, lang=state.get("voice_lang","en"))

    # handle notifications and save
    handle_notifications(state)
    save_user_data(username,state)

# final safe rerun handler - executes after UI built if flagged
if st.session_state.get("_trigger_rerun", False):
    st.session_state["_trigger_rerun"] = False
    st.rerun()
