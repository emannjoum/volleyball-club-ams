import streamlit as st
import pandas as pd
import random
from st_supabase_connection import SupabaseConnection
from utils import get_next_session_date

@st.cache_resource # to prevent reloading on every interaction
def get_connection():
    return st.connection(
        "supabase", 
        type=SupabaseConnection,
        url=st.secrets.connections.supabase.url, 
        key=st.secrets.connections.supabase.key
    )

conn = get_connection()

def load_players():
    try:
        query = conn.table("players").select("name").order("name").execute()
        if query.data: return [row["name"] for row in query.data]
        return []
    except: return []

def get_roster_with_pins():
    try:
        query = conn.table("players").select("name, position, access_code").order("name").execute()
        if query.data: return pd.DataFrame(query.data)
        return pd.DataFrame(columns=["name", "position", "access_code"])
    except: return pd.DataFrame(columns=["name", "position", "access_code"])

def verify_player_pin(name, pin):
    try:
        query = conn.table("players").select("access_code").eq("name", name).execute()
        if query.data and query.data[0]["access_code"] == pin: return True
        return False
    except: return False

def add_player(name, position):
    pin = str(random.randint(1000, 9999))
    try:
        conn.table("players").insert({"name": name, "position": position, "access_code": pin}).execute()
        conn.table("player_credits").insert({"player": name, "remaining_sessions": 0}).execute()
        return pin 
    except Exception as e:
        st.error(f"Error adding player: {e}")
        return None

def edit_player(original_name, new_name, position, pin):
    try:
        conn.table("players").update({
            "name": new_name, "position": position, "access_code": pin
        }).eq("name", original_name).execute()
        return True
    except Exception as e:
        st.error(f"Error updating player: {e}")
        return False

def load_player_credits(player_name):
    try:
        query = conn.table("player_credits").select("remaining_sessions").eq("player", player_name).execute()
        if query.data: return query.data[0]["remaining_sessions"]
        return 0
    except: return 0

def update_player_credits(player_name, sessions_to_add, plan_type="Custom Adjustment"):
    try:
        current_sessions = load_player_credits(player_name)
        new_total = current_sessions + sessions_to_add
        conn.table("player_credits").upsert({"player": player_name, "remaining_sessions": new_total}).execute()
        if sessions_to_add > 0:
            conn.table("payment_history").insert({"player": player_name, "sessions_added": sessions_to_add, "plan_type": plan_type}).execute()
        return True
    except: return False

def load_payment_history():
    try:
        query = conn.table("payment_history").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(query.data)
        if df.empty: return pd.DataFrame(columns=["created_at", "player", "plan_type", "sessions_added"])
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%b %d, %Y')
        df = df.rename(columns={"created_at": "Date", "player": "Player", "plan_type": "Payment Plan", "sessions_added": "Sessions Added"})
        return df[['Date', 'Player', 'Payment Plan', 'Sessions Added']]
    except: return pd.DataFrame(columns=["Date", "Player", "Payment Plan", "Sessions Added"])

def save_attendance(player_name, new_status, target_date=None):
    if not target_date: target_date = get_next_session_date()
    
    status_costs = {
        "Unavailable": 0,
        "Available": 1,
        "Double Session": 2
    }
    
    try:
        existing = conn.table("attendance").select("*").eq("player", player_name).eq("date", target_date).execute()
        current_sessions = load_player_credits(player_name)
        
        if existing.data:
            old_status = existing.data[0]['status']
            if old_status == new_status: 
                return False
            
            # calc the difference in cost between the old and new status
            old_cost = status_costs.get(old_status, 0)
            new_cost = status_costs.get(new_status, 0)
            ticket_difference = new_cost - old_cost
            
            # deduct or refund the difference
            conn.table("player_credits").upsert({
                "player": player_name, 
                "remaining_sessions": current_sessions - ticket_difference
            }).execute()
            
            conn.table("attendance").update({"status": new_status}).eq("player", player_name).eq("date", target_date).execute()
            return True
            
        else:
            # بirst time setting attendance for this date
            new_cost = status_costs.get(new_status, 0)
            if new_cost > 0:
                conn.table("player_credits").upsert({
                    "player": player_name, 
                    "remaining_sessions": current_sessions - new_cost
                }).execute()
                
            conn.table("attendance").insert({"player": player_name, "status": new_status, "date": target_date}).execute()
            return True
            
    except Exception as e:
        st.error(f"DB Error: {e}")
        return False

def get_current_attendance_status(player_name, date):
    try:
        query = conn.table("attendance").select("status").eq("player", player_name).eq("date", date).execute()
        if query.data: return query.data[0]['status']
        return None
    except: return None

def load_attendance():
    try:
        query = conn.table("attendance").select("*").execute()
        df = pd.DataFrame(query.data)
        if df.empty: return pd.DataFrame(columns=["date", "player", "status", "created_at"])
        return df
    except: return pd.DataFrame(columns=["date", "player", "status", "created_at"])

def get_schedule_overrides():
    try:
        query = conn.table("schedule_overrides").select("*").execute()
        return query.data if query.data else []
    except: return []

def add_schedule_override(date_str, status):
    try:
        conn.table("schedule_overrides").upsert({"session_date": date_str, "status": status}).execute()
        return True
    except: return False

def delete_schedule_override(date_str):
    try:
        conn.table("schedule_overrides").delete().eq("session_date", date_str).execute()
        return True
    except: return False

def save_stats(player_name, h, s, p, sv, d):
    try:
        data = {"player": player_name, "hitting": h, "setting": s, "passing": p, "serving": sv, "defense": d}
        conn.table("player_stats_history").insert(data).execute()
        return True
    except: return False

def load_player_stats(player_name):
    try:
        query = conn.table("player_stats_history").select("*").eq("player", player_name).execute()
        if query.data: 
            df = pd.DataFrame(query.data)
            return {
                "hitting": round(df["hitting"].mean(), 1),
                "setting": round(df["setting"].mean(), 1),
                "passing": round(df["passing"].mean(), 1),
                "serving": round(df["serving"].mean(), 1),
                "defense": round(df["defense"].mean(), 1)
            }
        return {"hitting": 3, "setting": 3, "passing": 3, "serving": 3, "defense": 3}
    except: return {"hitting": 3, "setting": 3, "passing": 3, "serving": 3, "defense": 3}