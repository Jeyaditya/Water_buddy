# 1000406_Jeyaditya.A_AIY1_FA2
A water buddy companion that makes drinking water fun and goal filled!
### Water buddy

This README explains what the app does,why each feature exists, and how everything is working behind the scenes in a semi-formal way.

---

# **What is WaterBuddy?**

WaterBuddy is your daily hydration companion.
It motivates you, tracks your water intake, teaches you good habits, shows progress visually, and even cheers for you when you reach your goal.

 A cute sea-turtle mascot appears on every page, reacting to your progress:

* Below 25% → sad turtle
* 25–75% → calm turtle
* 75–99% → excited turtle (wiggles!)
* 100% → dancing + jumping turtle

It also gives hydration tips and speaks to you with emotional altered bot voice.

WaterBuddy is designed to look like a real mobile wellness assistant.


# **Core Features**

## **1. Login, Signup, Guest Mode**

From the start screen, you can:
* Login
* Create an account
* Enter as a guest

Your age and career are collected early to personalise hydration goals.

The app stores each user’s data in a separate JSON file like:

username_history.json

## **2. Automatic Hydration Goal Based on Age**

Your daily goal changes based on scientifically accepted hydration guidelines:

| Age   | Goal    |
| ----- | ------- |
| 4–8   | 1200 ml |
| 9–13  | 1700 ml |
| 14–64 | 2200 ml |
| 65+   | 1800 ml |

You can still update your age anytime — the app auto-adjusts your goal.


## ✔ **3. Voice Assistant (6 Languages!)**

Supported languages:

* English
* Hindi
* Tamil
* Spanish
* French
* Japanese
Right now english is the only one that is enabled.
Its voice changes based on emotion:

* Happy → higher pitch, faster
* Sad → lower pitch
* Angry → faster
* Calm → slower

The mascot and voice are emotion-aware.

---

## ✔ **4. Progress Tracking**

You can log water via:

* +100 ml
* +250 ml
* +500 ml
* Manual entry (50–2000 ml)

Every sip updates:

* Hourly log
* Daily log
* Monthly log
* XP / Levels
* Mascot mood
* Voice lines
* Charts

## **5. Persistent Mascot Sidebar**

Your mascot lives on the right side bar, visible from every page.

It shows:

* A hydration message
* A motivational tip
* Your current progress image
* Special animations (wiggle / jump)

Images used:

* images/0.png
* images/25.png
* images/50.png
* images/100.png
The images are named on par with the percentage in which they will be enabled.
These are converted into base64 and embedded directly, so they load perfectly on Streamlit Cloud. Meaning there is no chance that the URL gets broken.


## **6. Charts & Analytics**

Beautiful matplotlib charts:
* Hourly intake (bar)
* Weekly hydration (line)
* Monthly hydration (bar)

Colors auto-adapt to Dark/Light themes.

## **7. Reminders & Smart Features**

You can choose:

* No reminders
* Once per hour
* Twice per hour
* Thrice per hour

The browser sends notifications politely.

There is also a placeholder “weather-aware hydration” feature which is still a work under progress.

## **8. Dark Mode + Light Mode**

A custom theme engine controls:

* Background
* Text
* Sidebar
* Buttons
* Metrics
* Progress bar

## **9. XP & Level System**

Every 50 ml water = XP
Fill XP → Level Up
Level ups trigger balloons 🎈

## **10. Persistent Data Across Sessions**

User progress, logs, reminders, voice settings, and profile updates are saved immediately.

## **UI & UX Design Goals**

WaterBuddy is intentionally:

* Friendly
* Motivating
* Non-judgmental
* Fun to use
* Smooth with no flickering
* Clean layout
* Mobile-friendly

The mascot acts like a real companion, not just an image.

# **Technical Notes**

### Streamlit rerun fix

The app uses a safe rerun system that prevents Streamlit's “experimental_rerun” glitch by handling it after UI rendering.

### Right-side fixed mascot

CSS positions the mascot using:

css
position: fixed;
right: 18px;
top: 50%;
transform: translateY(-50%);

### Speech bubble theme adapts

Speech bubble becomes dark or light depending on the selected theme.

### Manual entry double-trigger fixed

Using distinct Streamlit keys prevents Enter from submitting twice.

### Base64 image embedding

This ensures the mascot works on:

* Local machine
* Streamlit Cloud
* Mobile browsers

---

# **How to Run Locally**

1. Install dependencies (Inside the requirements.txt):

```
pip install streamlit matplotlib
```

2. Place your folder structure like:


waterbuddy/
  ├─ images/
  │   ├─ 0.png
  │   ├─ 25.png
  │   ├─ 50.png
  │   ├─ 100.png
  ├─ waterbuddy_final_v2.py

3. Run (In windows power shell) aka Command prompt:


streamlit run Water_buddy.py



# **Why WaterBuddy is Special**

This is not a simple hydration tracker.
This is a full personality-based health companion:

* Talks to you
* Reacts to your habits
* Animates with joy
* Gives tips
* Tracks your levels
* Shows confetti
* Lives on every page

I have built something that makes you want to drink water for a waiting someone else (mascot)!
# **Credits**

* Created By: Jeyaditya A
* Class: Artificial Intelligence python programming Year 1
* Mentor: Syed Ali Beema
* School Name: Jain Vidyalaya
