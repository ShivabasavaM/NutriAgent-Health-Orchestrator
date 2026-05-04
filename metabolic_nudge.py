import os
import sys
import requests
from dotenv import load_dotenv

from app.fitbit_client import FitbitClient
from app import database

load_dotenv()

fitbit = FitbitClient()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_daily_stats():
    """Pulls current data from PostgreSQL and Fitbit."""
    conn = database.get_connection()
    if not conn: return None
    
    cursor = conn.cursor()
    cursor.execute("SELECT daily_calorie_target FROM users WHERE id = 1")
    target_row = cursor.fetchone()
    target = target_row['daily_calorie_target'] if (target_row and target_row['daily_calorie_target'] is not None) else 2000

    cursor.execute("SELECT COALESCE(SUM(calories_in), 0) as eaten FROM daily_logs WHERE user_id = 1 AND date = CURRENT_DATE")
    eaten_row = cursor.fetchone()
    cursor.execute("SELECT EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - last_active))/3600 as hours_inactive FROM users WHERE id = 1")
    time_row = cursor.fetchone()
    
    if time_row and time_row['hours_inactive'] and time_row['hours_inactive'] > 24:
        print("User has been inactive for >24h. Skipping nudge.")
        cursor.close()
        database.release_connection(conn)
        return None
    eaten = eaten_row['eaten'] if eaten_row else 0
    
    cursor.close()
    conn.close()

    burned = fitbit.get_calories_today()
    remaining = (target + burned) - eaten
    
    return {"target": target, "eaten": eaten, "burned": burned, "remaining": remaining}

def generate_meal_nudge(stats, meal_type):
    """Generates a specific message based on the time of day and calorie count."""
    remaining = stats['remaining']
    
    if meal_type == "breakfast":
        return "🌅 Good morning! It's time for breakfast. Let's start the day with some good protein to get your metabolism firing."
        
    elif meal_type == "lunch":
        if remaining > 1000:
            return "🍲 Lunchtime! You have plenty of calories left. Make sure you fuel up for the afternoon."
        else:
            return "🥗 Lunch check-in! You are burning through your calories quickly. Opt for a high-volume, low-calorie lunch today."
            
    elif meal_type == "dinner":
        if remaining > 500:
            return f"🍽️ Dinner time! You have {remaining} kcal left. Enjoy a solid meal!"
        elif remaining > 0:
            return f"⚠️ Dinner time! You only have {remaining} kcal left. Keep this meal very light."
        else:
            return f"🛑 You are currently over your calorie budget by {abs(remaining)} kcal. Focus on a walk and a light salad tonight!"
            
    elif meal_type == "night":
        if remaining < 0:
            return f"💧 End of day check! We went over budget by {abs(remaining)} kcal today, but that's okay. Drink a glass of water and let's reset tomorrow."
        else:
            return "🌙 Great job today! You stayed within your metabolic budget. Drink some water and get a good night's sleep."
            
    return "Check-in time!"

def send_telegram_message(text):
    """Sends the message via Telegram API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    
    meal_type = sys.argv[1].lower() if len(sys.argv) > 1 else "general"
    
    stats = get_daily_stats()
    if stats:
        message = generate_meal_nudge(stats, meal_type)
        
        final_text = (
            f"🧬 *Metabolic Health Coach*\n\n"
            f"{message}\n\n"
            f"📊 Eaten: {stats['eaten']} kcal\n"
            f"🔥 Burned: {stats['burned']} kcal\n"
            f"🎯 Left: {stats['remaining']} kcal"
        )
        
        send_telegram_message(final_text)