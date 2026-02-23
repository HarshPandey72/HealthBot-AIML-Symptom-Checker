#                    win.title("🏥 HealthBot — AIML Symptom Checker")
import tkinter as tk
from tkinter import scrolledtext, END
import requests
import aiml
import os

# ─────────────────────────────────────────
#  AIML Kernel Setup
# ─────────────────────────────────────────
kernel = aiml.Kernel()
#kernel.setQuiet(True)

AIML_FILE = "health.aiml"
BRAIN_FILE = "health_brain.brn"

if os.path.isfile(BRAIN_FILE):
    kernel.loadBrain(BRAIN_FILE)
else:
    kernel.learn(AIML_FILE)
    kernel.saveBrain(BRAIN_FILE)

# ─────────────────────────────────────────
#  API Config  ( Google AI studio — free tier)
# ─────────────────────────────────────────
API_NINJAS_KEY = "AIzaSyADHqFirmrldCU2zD4FZCpT4LykYwCahBY"   # ← Replace with your key

# Symptom-to-condition knowledge base (offline fallback + enrichment)
SYMPTOM_INFO = {
    "headache": {
        "conditions": ["Tension Headache", "Migraine", "Dehydration", "Sinusitis", "Hypertension"],
        "tips": ["Rest in a quiet, dark room", "Stay hydrated (drink water)", "Apply cold/warm compress on forehead", "Avoid bright screens", "Take OTC pain reliever if needed"],
        "warning": "Seek immediate help if headache is sudden, severe, or with stiff neck/vision changes.",
        "emoji": "🤕"
    },
    "fever": {
        "conditions": ["Viral Infection", "Flu (Influenza)", "COVID-19", "Malaria", "Typhoid", "UTI"],
        "tips": ["Rest and stay hydrated", "Take paracetamol to reduce fever", "Use a cool damp cloth on forehead", "Wear light clothing", "Monitor temperature regularly"],
        "warning": "See a doctor if fever is above 103°F (39.4°C) or lasts more than 3 days.",
        "emoji": "🌡️"
    },
    "cough": {
        "conditions": ["Common Cold", "Flu", "COVID-19", "Bronchitis", "Allergies", "Asthma"],
        "tips": ["Drink warm fluids (honey + lemon tea)", "Gargle with salt water", "Avoid cold drinks and smoking", "Use steam inhalation", "Keep throat moist"],
        "warning": "See a doctor if cough produces blood, lasts >3 weeks, or is with high fever.",
        "emoji": "😷"
    },
    "cold": {
        "conditions": ["Common Cold (Rhinovirus)", "Flu", "Sinusitis", "COVID-19"],
        "tips": ["Rest and sleep well", "Drink warm soups and fluids", "Use saline nasal spray", "Take steam inhalation", "Vitamin C supplements may help"],
        "warning": "See a doctor if symptoms worsen after 10 days.",
        "emoji": "🤧"
    },
    "nausea": {
        "conditions": ["Food Poisoning", "Gastritis", "Motion Sickness", "Migraine", "Pregnancy", "Anxiety"],
        "tips": ["Eat small, bland meals (crackers, rice)", "Sip cold water or ginger tea", "Avoid strong smells and fatty foods", "Rest in a sitting position", "Try deep breathing"],
        "warning": "See a doctor if nausea is severe, persistent, or with blood in vomit.",
        "emoji": "🤢"
    },
    "vomiting": {
        "conditions": ["Food Poisoning", "Gastroenteritis", "Motion Sickness", "Appendicitis", "Migraine"],
        "tips": ["Stay hydrated with small sips of water/ORS", "Avoid solid food initially", "Rest in a comfortable position", "Avoid strong odors", "Try ginger tea after settling"],
        "warning": "🚨 Seek urgent care if vomiting blood or is prolonged beyond 24 hours.",
        "emoji": "🤮"
    },
    "back pain": {
        "conditions": ["Muscle Strain", "Herniated Disc", "Sciatica", "Poor Posture", "Kidney Issues"],
        "tips": ["Apply hot/cold compress", "Gentle stretching and movement", "Maintain good posture", "Avoid heavy lifting", "Sleep on a firm mattress"],
        "warning": "See a doctor if pain radiates down the leg or is with numbness/weakness.",
        "emoji": "🦴"
    },
    "stomach pain": {
        "conditions": ["Gastritis", "IBS", "Food Poisoning", "Appendicitis", "Ulcer", "Gas"],
        "tips": ["Drink warm water", "Avoid spicy/oily food", "Apply warm compress to stomach", "Try peppermint or ginger tea", "Rest and avoid stress"],
        "warning": "🚨 Seek immediate care if pain is severe, sudden, or in lower right abdomen (appendicitis).",
        "emoji": "🤕"
    },
    "dizziness": {
        "conditions": ["Low Blood Pressure", "Dehydration", "Anemia", "Inner Ear Problem", "Vertigo"],
        "tips": ["Sit or lie down immediately", "Drink water", "Avoid sudden movements", "Eat a light snack if blood sugar is low", "Rest in a cool place"],
        "warning": "See a doctor if dizziness is sudden, severe, or with fainting/chest pain.",
        "emoji": "😵"
    },
    "fatigue": {
        "conditions": ["Anemia", "Hypothyroidism", "Diabetes", "Depression", "Sleep Disorder", "Vitamin Deficiency"],
        "tips": ["Ensure 7-8 hours of quality sleep", "Stay hydrated", "Exercise regularly", "Eat iron-rich foods", "Manage stress with relaxation techniques"],
        "warning": "See a doctor if fatigue is persistent (>2 weeks) with no obvious cause.",
        "emoji": "😴"
    },
    "sore throat": {
        "conditions": ["Strep Throat", "Tonsillitis", "Common Cold", "Flu", "Acid Reflux"],
        "tips": ["Gargle warm salt water", "Drink warm honey-lemon tea", "Avoid cold drinks", "Use throat lozenges", "Rest your voice"],
        "warning": "See a doctor if throat is very red, swollen, or with white patches.",
        "emoji": "🤒"
    },
    "rash": {
        "conditions": ["Allergic Reaction", "Eczema", "Contact Dermatitis", "Heat Rash", "Chickenpox"],
        "tips": ["Avoid scratching", "Apply cool compress", "Use hypoallergenic soap", "Wear loose, breathable clothing", "Identify and avoid triggers"],
        "warning": "🚨 Seek urgent care if rash spreads rapidly, is with breathing difficulty, or after insect sting.",
        "emoji": "🔴"
    },
    "joint pain": {
        "conditions": ["Arthritis", "Gout", "Lupus", "Viral Infection", "Bursitis"],
        "tips": ["Rest the affected joint", "Apply ice for swelling", "Gentle range-of-motion exercises", "Anti-inflammatory diet", "OTC pain relievers"],
        "warning": "See a doctor if joint is swollen, red, warm, or pain is severe.",
        "emoji": "🦵"
    },
    "insomnia": {
        "conditions": ["Stress & Anxiety", "Depression", "Sleep Apnea", "Poor Sleep Hygiene", "Caffeine Overuse"],
        "tips": ["Set a regular sleep schedule", "Limit screen time 1hr before bed", "Avoid caffeine in evenings", "Try relaxation/meditation", "Keep bedroom dark and cool"],
        "warning": "See a doctor if insomnia persists >1 month or severely impacts daily life.",
        "emoji": "🌙"
    },
    "anxiety": {
        "conditions": ["Generalized Anxiety Disorder", "Panic Disorder", "Stress", "Thyroid Issues"],
        "tips": ["Practice deep breathing (4-7-8 method)", "Regular physical exercise", "Limit caffeine and alcohol", "Talk to someone you trust", "Try mindfulness/meditation"],
        "warning": "Seek professional help if anxiety is severe, persistent, or interferes with daily life.",
        "emoji": "😰"
    },
}

def match_symptom(user_input: str):
    """Find best matching symptom from the knowledge base."""
    user_input = user_input.lower()
    for key in SYMPTOM_INFO:
        if key in user_input:
            return key, SYMPTOM_INFO[key]
    # Check individual words
    words = user_input.split()
    for word in words:
        for key in SYMPTOM_INFO:
            if word in key or key in word:
                return key, SYMPTOM_INFO[key]
    return None, None

# ─────────────────────────────────────────
#  API Fetch Functions
# ─────────────────────────────────────────
def fetch_symptom_info(symptom_text: str) -> str:
    symptom_text = symptom_text.strip().lower()

    # First try local knowledge base
    matched_key, info = match_symptom(symptom_text)

    # Try API Ninjas for extra data
    api_data = None
    try:
        if API_NINJAS_KEY != "YOUR_API_NINJAS_KEY_HERE":
            # Use API Ninjas symptom checker
            headers = {"X-Api-Key": API_NINJAS_KEY}
            # Search nutrition or health endpoint
            response = requests.get(
                f"https://api.api-ninjas.com/v1/nutrition?query={symptom_text}",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                api_data = response.json()
    except Exception:
        pass  # fallback to local data

    # Build response
    if info:
        emoji = info.get("emoji", "🏥")
        conditions = ", ".join(info["conditions"])
        tips = "\n   ".join([f"• {t}" for t in info["tips"]])
        warning = info.get("warning", "")

        result = (
            f"\n{emoji} Symptom Analysis: {matched_key.title()}\n"
            f"{'─'*40}\n"
            f"📋 Possible Conditions:\n   {conditions}\n\n"
            f"💡 Home Care Tips:\n   {tips}\n\n"
            f"⚠️  {warning}\n\n"
            f"{'─'*40}\n"
            f"🩺 DISCLAIMER: This is general information only.\n"
            f"   Please consult a qualified doctor for proper diagnosis.\n"
        )
        return result
    else:
        return (
            f"\n🔍 I searched for: '{symptom_text}'\n"
            f"{'─'*40}\n"
            f"I don't have specific data for this symptom yet.\n\n"
            f"💡 General advice:\n"
            f"   • Rest and stay hydrated\n"
            f"   • Monitor your symptoms\n"
            f"   • Consult a doctor if symptoms persist or worsen\n\n"
            f"🩺 For accurate diagnosis, please visit a healthcare professional.\n"
            f"📞 Emergency: Call 112 or 108\n"
        )

def fetch_disease_info(disease: str) -> str:
    disease = disease.strip().lower()
    
    # Check if any known symptom keyword matches
    matched_key, info = match_symptom(disease)
    if info:
        return fetch_symptom_info(disease)

    return (
        f"\n🔬 Disease/Condition: {disease.title()}\n"
        f"{'─'*40}\n"
        f"I don't have detailed info on '{disease}' yet.\n\n"
        f"💡 You can:\n"
        f"   • Visit WHO: https://www.who.int\n"
        f"   • Visit WebMD: https://www.webmd.com\n"
        f"   • Consult your doctor for accurate information\n\n"
        f"🩺 Always get professional medical advice.\n"
    )

# ─────────────────────────────────────────
#  Chat Logic
# ─────────────────────────────────────────
def process_message(user_input: str) -> str:
    response = kernel.respond(user_input.upper())

    if response.startswith("FETCH_SYMPTOM:"):
        symptom = response.split("FETCH_SYMPTOM:", 1)[1].strip().lower()
        return fetch_symptom_info(symptom)

    if response.startswith("FETCH_DISEASE:"):
        disease = response.split("FETCH_DISEASE:", 1)[1].strip().lower()
        return fetch_disease_info(disease)

    return response

# ─────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────
def send_message(event=None):
    user_text = entry_var.get().strip()
    if not user_text:
        return

    chat_box.config(state=tk.NORMAL)
    chat_box.insert(END, f"\n🧑 You: {user_text}\n", "user")
    entry_var.set("")

    bot_reply = process_message(user_text)
    chat_box.insert(END, f"🤖 HealthBot: {bot_reply}\n", "bot")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(END)

def clear_chat():
    chat_box.config(state=tk.NORMAL)
    chat_box.delete("1.0", END)
    chat_box.insert(END, "🤖 HealthBot: Chat cleared! Tell me your symptoms.\n", "bot")
    chat_box.config(state=tk.DISABLED)

# ── Window ──
win = tk.Tk()
win.title("🏥 HealthBot — AIML Symptom Checker")
win.geometry("800x650")
win.resizable(False, False)
win.configure(bg="#0d1f1a")

# ── Title Bar ──
title_frame = tk.Frame(win, bg="#2e7d32", pady=10)
title_frame.pack(fill=tk.X)

tk.Label(
    title_frame,
    text="🏥  HealthBot — AIML Symptom Checker",
    font=("Segoe UI", 18, "bold"),
    bg="#2e7d32", fg="white"
).pack()

tk.Label(
    title_frame,
    text='Try: "I have a headache"  |  "I feel fever"  |  "Symptoms of flu"  |  HELP',
    font=("Segoe UI", 10),
    bg="#2e7d32", fg="#c8e6c9"
).pack()

# ── Disclaimer Banner ──
disc_frame = tk.Frame(win, bg="#b71c1c", pady=4)
disc_frame.pack(fill=tk.X)
tk.Label(
    disc_frame,
    text="⚠️  This app is NOT a substitute for professional medical advice. Always consult a doctor.",
    font=("Segoe UI", 9, "bold"),
    bg="#b71c1c", fg="white"
).pack()

# ── Chat Box ──
chat_frame = tk.Frame(win, bg="#0d1f1a", padx=12, pady=8)
chat_frame.pack(fill=tk.BOTH, expand=True)

chat_box = scrolledtext.ScrolledText(
    chat_frame,
    state=tk.DISABLED,
    wrap=tk.WORD,
    font=("Consolas", 12),
    bg="#132218",
    fg="#e8f5e9",
    insertbackground="white",
    relief=tk.FLAT,
    bd=0,
    padx=10, pady=10
)
chat_box.tag_config("user", foreground="#80cbc4", font=("Consolas", 12, "bold"))
chat_box.tag_config("bot",  foreground="#a5d6a7", font=("Consolas", 12))
chat_box.pack(fill=tk.BOTH, expand=True)

# Welcome message
chat_box.config(state=tk.NORMAL)
chat_box.insert(END, "🤖 HealthBot: Hello! 👋 I'm HealthBot, your AIML-powered symptom checker!\n", "bot")
chat_box.insert(END, "🤖 HealthBot: Tell me your symptoms. Example: \"I have a headache\" or type HELP.\n", "bot")
chat_box.insert(END, "🤖 HealthBot: 🚨 For emergencies, call 112 or 108 immediately!\n\n", "bot")
chat_box.config(state=tk.DISABLED)

# ── Input Area ──
input_frame = tk.Frame(win, bg="#0d1f1a", padx=12, pady=10)
input_frame.pack(fill=tk.X)

entry_var = tk.StringVar()
entry = tk.Entry(
    input_frame,
    textvariable=entry_var,
    font=("Segoe UI", 13),
    bg="#1b3a2a", fg="white",
    insertbackground="white",
    relief=tk.FLAT, bd=0
)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 8))
entry.bind("<Return>", send_message)
entry.focus()

send_btn = tk.Button(
    input_frame, text="Send 💬",
    font=("Segoe UI", 12, "bold"),
    bg="#2e7d32", fg="white",
    relief=tk.FLAT, bd=0,
    padx=14, pady=8,
    activebackground="#1b5e20",
    cursor="hand2",
    command=send_message
)
send_btn.pack(side=tk.LEFT)

clear_btn = tk.Button(
    input_frame, text="Clear 🗑️",
    font=("Segoe UI", 12),
    bg="#37474f", fg="white",
    relief=tk.FLAT, bd=0,
    padx=12, pady=8,
    activebackground="#263238",
    cursor="hand2",
    command=clear_chat
)
clear_btn.pack(side=tk.LEFT, padx=(6, 0))

# ── Quick Symptom Buttons ──
quick_frame = tk.Frame(win, bg="#0d1f1a", padx=12, pady=6)
quick_frame.pack(fill=tk.X)

tk.Label(
    quick_frame,
    text="Quick Symptoms:",
    font=("Segoe UI", 9),
    bg="#0d1f1a", fg="#81c784"
).pack(side=tk.LEFT, padx=(0, 8))

for symptom in ["Headache", "Fever", "Cough", "Nausea", "Fatigue", "Back Pain"]:
    def make_cmd(s=symptom):
        def cmd():
            entry_var.set(f"I have {s.lower()}")
            send_message()
        return cmd
    tk.Button(
        quick_frame,
        text=symptom,
        font=("Segoe UI", 9),
        bg="#1b5e20", fg="white",
        relief=tk.FLAT, bd=0,
        padx=8, pady=4,
        activebackground="#2e7d32",
        cursor="hand2",
        command=make_cmd()
    ).pack(side=tk.LEFT, padx=3)

# ── Status Bar ──
tk.Label(
    win,
    text="💡 Press Enter or click Send  •  AIML brain loaded ✅  •  Emergency: 112 / 108",
    font=("Segoe UI", 9),
    bg="#071410", fg="#546e7a",
    anchor="w", padx=10
).pack(fill=tk.X, side=tk.BOTTOM)

win.mainloop()
