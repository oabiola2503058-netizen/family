#!/usr/bin/python

import streamlit as st
from datetime import datetime
import base64
import time
import smtplib
from email.mime.text import MIMEText
import database as db

st.set_page_config(page_title="Family Portal", page_icon="🏠", layout="centered")

# Initialize database
db.init_db()

# --- ADMIN CONFIGURATION ---
ADMIN_EMAIL = "oabiola.2503058@stu.cu.edu.ng"  # Your admin email address
SENDER_EMAIL = "your_real_email@gmail.com"     # Sender Gmail address
SENDER_PASSWORD = "12345$"     # Gmail App Password

ADMIN_MASTER_PASSWORD = "mummy12345$"  # Set your admin password here

def send_admin_notification(user_name, user_email, event_type="signup"):
    """Sends a single email to the admin alerting them of a sign-up or reset request."""
    try:
        if event_type == "signup":
            subject = f"🎉 New Family Member Signed Up: {user_name}"
            body = f"Hello Admin,\n\nA new user has registered on the Family Portal!\n\nDetails:\n- User/Role: {user_name}\n- User Email: {user_email}"
        else:
            subject = f"🚨 Password Reset Requested: {user_name}"
            body = f"Hello Admin,\n\nFamily member '{user_name}' ({user_email}) requested a password reset.\n\nPlease use the Admin Reset tab to set a new password for them."

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ADMIN_EMAIL

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Initialize Session States
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

st.title("🏠 Private Family Portal")

# ------------------- AUTHENTICATION SCREEN -------------------
if st.session_state["logged_in_user"] is None:
    tab1, tab2, tab3, tab4 = st.tabs(["🔒 Log In", "📝 Sign Up", "🔑 Request Reset", "⚙️ Admin Reset"])

    # --- LOG IN TAB ---
    with tab1:
        st.subheader("Welcome Back!")
        registered_users = db.get_all_users()

        if not registered_users:
            st.info("No registered users found yet! Please go to the **Sign Up** tab to create your account first.")
        else:
            user_options = {f"{u[0]} ({u[1]})": u[0] for u in registered_users}
            selected_label = st.selectbox("Select who you are:", list(user_options.keys()))
            selected_username = user_options[selected_label]
            password = st.text_input("Enter your Password:", type="password", key="login_pass")

            if st.button("Log In"):
                if db.authenticate_user(selected_username, password):
                    st.session_state["logged_in_user"] = selected_username
                    st.success(f"Welcome back, {selected_username}!")
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")

    # --- SIGN UP TAB (WITH AUTOMATIC ADMIN ALERT) ---
    with tab2:
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a Username:")
        new_email = st.text_input("Enter your Email Address:")
        role_options = [
            "Emmanuel", "Grandma", "Big Daddy", "Daddy PH", "Big Mummy", "Aunty tope", 
            "Kanyisola", "Aunty Ayoola", "Isaac", "Damilola", "Olamide", "Peter", "Uncle Bayo"
        ]
        selected_role = st.selectbox("Who are you?:", role_options)
        new_password = st.text_input("Create a Password:", type="password", key="signup_pass")

        if st.button("Sign Up"):
            if not new_username.strip() or not new_password.strip() or not new_email.strip():
                st.warning("Please fill in all fields (username, email, and password).")
            else:
                if db.add_user(new_username.strip(), new_password, selected_role, new_email.strip()):
                    # Trigger notification to admin on new sign up
                    send_admin_notification(
                        user_name=f"{new_username.strip()} ({selected_role})", 
                        user_email=new_email.strip(), 
                        event_type="signup"
                    )
                    st.success("Account created! Switch to 'Log In' tab.")
                else:
                    st.error("That username is already taken.")

    # --- FORGOT PASSWORD (REQUEST TO ADMIN) ---
    with tab3:
        st.subheader("Request Password Reset")
        st.write("If you forgot your password, select your name below to alert the Admin.")
        
        registered_users = db.get_all_users()
        if registered_users:
            user_options = {f"{u[0]} ({u[1]})": u[0] for u in registered_users}
            reset_label = st.selectbox("Select your profile:", list(user_options.keys()), key="request_reset_select")
            reset_user = user_options[reset_label]

            if st.button("Send Reset Request to Admin"):
                user_email = db.get_user_email(reset_user)
                if user_email:
                    if send_admin_notification(reset_user, user_email, event_type="reset"):
                        st.success("Notification sent to Admin! They will reset your password shortly.")
                    else:
                        st.info("Request recorded. Please contact the Admin directly to set your new password.")
                else:
                    st.error("No email found for this user account.")

    # --- ADMIN RESET PANEL (PROTECTED) ---
    with tab4:
        st.subheader("⚙️ Admin Direct Password Reset")
        st.caption("Admin tool to manually overwrite a forgotten user password.")
        
        admin_pass_input = st.text_input("Enter Admin Master Password:", type="password", key="admin_auth_pass")

        if admin_pass_input:
            if admin_pass_input == ADMIN_MASTER_PASSWORD:
                st.success("✅ Admin Verified")
                st.divider()

                registered_users = db.get_all_users()
                if registered_users:
                    admin_user_options = {f"{u[0]} ({u[1]})": u[0] for u in registered_users}
                    target_label = st.selectbox("Select account to change password for:", list(admin_user_options.keys()), key="admin_target_select")
                    target_user = admin_user_options[target_label]
                    
                    new_admin_set_pass = st.text_input("Type new password for user:", type="password", key="admin_new_pass")

                    if st.button("Save New Password"):
                        if new_admin_set_pass.strip():
                            db.reset_user_password(target_user, new_admin_set_pass.strip())
                            st.success(f"Password for **{target_user}** successfully updated! They can now log in with their new password.")
                        else:
                            st.warning("Please enter a valid new password.")
            else:
                st.error("❌ Incorrect Admin Master Password. Access denied.")
        else:
            st.info("🔒 Please enter the Admin Master Password above to unlock this panel.")

# ------------------- MAIN PORTAL (LOGGED IN) -------------------
else:
    current_user = st.session_state["logged_in_user"]
    st.sidebar.markdown(f"👤 Logged in as: **{current_user}**")
    if st.sidebar.button("Log Out"):
        st.session_state["logged_in_user"] = None
        st.rerun()

    menu = ["🗓️ Countdowns", "📸 Memory Album", "🧠 Family Trivia", "💬 Private Messages"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # --- COUNTDOWNS ---
    if choice == "🗓️ Countdowns":
        st.header("🗓️ Upcoming Family Events")
        with st.expander("➕ Add New Event"):
            title = st.text_input("Event Name:")
            target_date = st.date_input("Event Date:")
            if st.button("Save Event"):
                if title:
                    db.add_countdown(title, str(target_date), current_user)
                    st.success("Event added!")
                    st.rerun()

        countdowns = db.get_countdowns()
        if countdowns:
            for item in countdowns:
                event_title, event_date_str, creator = item
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
                days_left = (event_date - datetime.today().date()).days
                st.metric(label=f"{event_title} (by {creator})", value=f"{days_left} Days Left", delta=event_date_str)
        else:
            st.info("No upcoming events yet.")

    # --- NOSTALGIC PHOTO ALBUM ---
    elif choice == "📸 Memory Album":
        st.header("📸 Nostalgic Family Photo Album")
        st.write("Share classic throwback pictures, family trips, and milestone memories!")

        with st.expander("🖼️ Upload a New Nostalgic Photo"):
            event_title = st.text_input("Event / Memory Title (e.g., Summer Trip 2012):")
            caption = st.text_area("Memory Caption / Story:")
            uploaded_file = st.file_uploader("Choose a photo (JPG, PNG)", type=["jpg", "jpeg", "png"])

            if st.button("Post to Album"):
                if event_title and uploaded_file:
                    image_bytes = uploaded_file.read()
                    db.add_photo(event_title, caption, image_bytes, current_user)
                    st.success("Photo uploaded successfully to the family album!")
                    st.rerun()
                else:
                    st.warning("Please provide an event title and upload an image.")

        st.divider()
        st.subheader("🖼️ Family Gallery")

        photos = db.get_photos()
        if not photos:
            st.info("No nostalgic photos added yet. Be the first to upload one above!")
        else:
            for event_title, caption, image_b64, uploader, timestamp in photos:
                img_data = base64.b64decode(image_b64)
                
                with st.container():
                    st.image(img_data, use_container_width=True)
                    st.markdown(f"### 📍 {event_title}")
                    if caption:
                        st.write(f"*{caption}*")
                    st.caption(f"Shared by **{uploader}** on {timestamp[:10]}")
                    st.divider()

    # --- TRIVIA (WITH START BUTTON & CLEAN SUBMISSION) ---
    elif choice == "🧠 Family Trivia":
        import streamlit.components.v1 as components

        st.header("🧠 Weekly Family Trivia")

        WEEKLY_TRIVIA = [
            {
                "id": "q1",
                "question": "1. What is Aunty Ayoola's middle name??",
                "options": ["Lasebikan", "Michelle", "Elise", "Atinuke"],
                "answer": "Elise"
            },
            {
                "id": "q2",
                "question": "2. Which year did the family have a major gathering in Lagos last?",
                "options": ["2024", "2025", "2023", "2023"],
                "answer": "2025"
            },
            {
                "id": "q3",
                "question": "3. What was Late Marian Atinuke favourite food ?",
                "options": ["Ikpere", "Iyan ati ogbono", "Adalu", "Ewa riro"],
                "answer": "Adalu"
            },
            {
                "id": "q4",
                "question": "4. What date is Daddy Kanyin's birthday?",
                "options": ["3rd", "2nd", "1st", "16th"],
                "answer": "3rd"
            },
            {
                "id": "q5",
                "question": "5. What university did Big daddy attend?",
                "options": ["Babcock University", "Obafemi Awolowo University", "Yaba College of technology", "Lagos state University"],
                "answer": "Yaba College of technology"
            }    
        ]
        
        POINTS_PER_QUESTION = 20

        # Session State Initialization
        if "quiz_started" not in st.session_state:
            st.session_state.quiz_started = False
        if "quiz_submitted" not in st.session_state:
            st.session_state.quiz_submitted = False
        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = {}

        # 1. START QUIZ SCREEN
        if not st.session_state.quiz_started and not st.session_state.quiz_submitted:
            st.info("📋 **Quiz Rules:**\n- You will have **2 minutes** once you press start.\n- Leaving the tab or letting the timer reach 0:00 will automatically submit your choices.")
            if st.button("🚀 Start Quiz", type="primary"):
                st.session_state.quiz_started = True
                st.session_state.quiz_start_time = time.time()
                st.rerun()

        # 2. ACTIVE QUIZ SCREEN (QUESTIONS & REAL-TIME TIMER)
        elif st.session_state.quiz_started and not st.session_state.quiz_submitted:
            elapsed_time = int(time.time() - st.session_state.quiz_start_time)
            seconds_left = max(0, 120 - elapsed_time)

            if seconds_left <= 0:
                st.session_state.quiz_submitted = True
                st.rerun()

            # Live JS Countdown Bar
            components.html(f"""
                <div style="font-family: sans-serif; background-color: #f0f2f6; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #d6d8db;">
                    <span style="font-size: 14px; color: #555;">⏳ Time Remaining: </span>
                    <strong id="timer-display" style="font-size: 20px; color: #d9534f;">02:00</strong>
                </div>

                <script>
                var timeLeft = {seconds_left};
                var timerElem = document.getElementById("timer-display");

                function updateTimerDisplay(seconds) {{
                    var mins = Math.floor(seconds / 60);
                    var secs = seconds % 60;
                    timerElem.innerText = (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
                }}

                updateTimerDisplay(timeLeft);

                var timerInterval = setInterval(function() {{
                    timeLeft--;
                    if (timeLeft >= 0) {{
                        updateTimerDisplay(timeLeft);
                    }}
                    if (timeLeft <= 0) {{
                        clearInterval(timerInterval);
                        triggerSubmit();
                    }}
                }}, 1000);

                function triggerSubmit() {{
                    const submitBtn = window.parent.document.querySelector('button[kind="primary"]');
                    if (submitBtn) {{
                        submitBtn.click();
                    }}
                }}

                document.addEventListener("visibilitychange", function() {{
                    if (document.visibilityState === 'hidden') {{
                        triggerSubmit();
                    }}
                }});
                </script>
            """, height=65)

            with st.form("weekly_trivia_form"):
                user_choices = {}
                for q in WEEKLY_TRIVIA:
                    user_choices[q["id"]] = st.radio(
                        q["question"], 
                        q["options"], 
                        index=None,
                        key=f"widget_{q['id']}"
                    )
                
                submit_clicked = st.form_submit_button("Submit Quiz Answers", type="primary")

                if submit_clicked:
                    st.session_state.quiz_answers = user_choices
                    st.session_state.quiz_submitted = True
                    st.rerun()

        # 3. QUIZ COMPLETED / RESULTS SCREEN
        elif st.session_state.quiz_submitted:
            total_earned = 0
            max_possible = len(WEEKLY_TRIVIA) * POINTS_PER_QUESTION
            
            st.subheader("📝 Quiz Results")
            for q in WEEKLY_TRIVIA:
                user_ans = st.session_state.quiz_answers.get(q["id"])
                correct_ans = q["answer"]
                
                if user_ans == correct_ans:
                    total_earned += POINTS_PER_QUESTION
                    st.success(f"✅ **{q['question']}**\n\nYour Answer: *{user_ans}* (+{POINTS_PER_QUESTION} pts)")
                else:
                    st.error(f"❌ **{q['question']}**\n\nYour Answer: *{user_ans or 'Unanswered'}* | Correct Answer: **{correct_ans}**")

            db.update_score(current_user, total_earned)
            st.info(f"🎉 You scored **{total_earned} / {max_possible}** points! Your score has been saved to the leaderboard.")

        st.divider()
        st.subheader("🏆 Family Leaderboard")
        board = db.get_leaderboard()
        for user, score in board:
            st.write(f"- **{user}**: {score} pts")

    # --- PRIVATE MESSAGING ---
    elif choice == "💬 Private Messages":
        st.header("💬 Private Messages")
        all_users = db.get_all_users()
        other_users = [u[0] for u in all_users if u[0] != current_user]

        if not other_users:
            st.info("No other registered members found to message yet.")
        else:
            recipient = st.selectbox("Select recipient:", other_users)
            messages = db.get_messages(current_user, recipient)
            st.subheader(f"Chat with {recipient}")
            
            for sender, rcp, msg, time in messages:
                if sender == current_user:
                    st.markdown(f"**You** ({time}): {msg}")
                else:
                    st.markdown(f"**{sender}** ({time}): {msg}")

            new_msg = st.text_input("Type your message:", key="chat_msg_input")
            if st.button("Send"):
                if new_msg.strip():
                    db.send_message(current_user, recipient, new_msg)
                    st.rerun()
