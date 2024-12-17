import requests
import time
import json
import os
from datetime import datetime
import pytz
import threading
import base64

def read_query_id():
    """Fungsi untuk membaca query ID dari file query.txt"""
    try:
        with open('query.txt', 'r') as file:
            return file.read().strip()
    except Exception as e:
        print("Error membaca query.txt:", str(e))
        return None

def print_separator():
    """Function to print separator line"""
    print("\n" + "═" * 44 + "\n")

def print_header(text):
    """Function to print styled header"""
    print("\n" + "╔" + "═" * 44 + "╗")
    print(f"║ {text.upper().center(42)} ║")
    print("╚" + "═" * 44 + "╝\n")

def check_profile():
    """Function to check user profile"""
    try:
        response = requests.get(f"{BASE_URL}/combats/me", headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print_header("Player Profile")
            print(f"Username  : {data['username']}")
            print(f"Rank      : {data['rank']}")
            
            print("\nCombat Stats")
            print(f"Attack    : Lv.{data['attack_level']} ({data['attack_point']} PWR)")
            print(f"Health    : Lv.{data['health_level']} ({data['health_point']} HP)")
            print(f"Luck      : Lv.{data['luck_level']}")
            
            print("\nBattle Rates")
            print(f"Evade     : {data['luck_evade_rate']}%")
            print(f"Critical  : {data['luck_critical_rate']}%")
            print(f"Reflect   : {data['reflect_rate']}%")
            print(f"Life Steal: {data['life_steal']}%")
            
            if data['pet']:
                print("\nActive Pet")
                print(f"Type      : {data['pet']['type'].title()}")
                print(f"Skill     : {data['pet']['active_skill'].title()}")
                print(f"Abilities : {', '.join(skill.title() for skill in data['pet']['skills'])}")
            
            return True
    except Exception as e:
        print("Error: Profile Check -", str(e))
        return False

# Konfigurasi
BASE_URL = "https://liyue.tonkombat.com/api/v1"
QUERY = read_query_id()
AUTH_TOKEN = f"tma {QUERY}"

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": AUTH_TOKEN,
    "origin": "https://staggering.tonkombat.com",
    "referer": "https://staggering.tonkombat.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

def claim_daily():
    """Fungsi untuk mengklaim hadiah harian"""
    try:
        response = requests.post(f"{BASE_URL}/daily", headers=headers)
        if response.status_code == 200:
            print("Daily claim berhasil!")
            return response.json()
        elif response.status_code == 400:
            print("Daily claim sudah diambil hari ini")
        else:
            print(f"Daily claim gagal dengan status: {response.status_code}")
        return None
    except Exception as e:
        print("Error pada daily claim:", str(e))
        return None

def claim_rewards():
    """Fungsi untuk mengklaim rewards"""
    try:
        response = requests.post(f"{BASE_URL}/users/claim", headers=headers)
        if response.status_code == 200:
            print("Claim rewards berhasil!")
            return response.json()
        elif response.status_code == 400:
            print("Rewards sudah diambil")
        else:
            print(f"Claim rewards gagal dengan status: {response.status_code}")
        return None
    except Exception as e:
        print("Error pada claim rewards:", str(e))
        return None

def find_battle():
    """Function to find opponent"""
    try:
        response = requests.get(f"{BASE_URL}/combats/find", headers=headers)
        print_header("Opponent Found")
        if response.status_code == 200:
            data = response.json()['data']
            print(f"Username  : {data['username']}")
            print(f"Rank      : {data['rank']}")
            print(f"\nStats")
            print(f"Attack    : Lv.{data['attack_level']} ({data['attack_point']} PWR)")
            print(f"Health    : Lv.{data['health_level']} ({data['health_point']} HP)")
            print(f"Luck      : Lv.{data['luck_level']}")
            if data['pet']:
                print(f"\nPet       : {data['pet']['type'].title()} - {data['pet']['active_skill'].title()}")
        return response.json()
    except Exception as e:
        print("Error: Battle Search -", str(e))
        return None

def format_number(number):
    """Function to format large numbers into simple readable format"""
    if number >= 1000000000:  # Billions
        return f"{number/1000000000:.1f}"
    elif number >= 1000000:    # Millions
        return f"{number/1000000:.1f}"
    elif number >= 1000:       # Thousands
        return f"{number/1000:.1f}"
    else:
        return str(number)

def do_battle():
    """Function to execute battle"""
    try:
        response = requests.post(f"{BASE_URL}/combats/fight", headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print_header("Battle Results")
            print(f"Winner: {'YOU WIN!' if data['winner'] == 'attacker' else 'YOU LOSE!'}")
            
            if 'drops' in data and 'materials' in data['drops']:
                print("\nRewards")
                for item, amount in data['drops']['materials'].items():
                    print(f"{item.replace('material-', '').title()}: {amount}")
            
            if 'win_streak' in data:
                print(f"\nWin Streak : {data['win_streak']['no']}")
                print(f"Bonus      : {format_number(data['win_streak']['streak_amount'])}")
            
        return response.json()
    except Exception as e:
        print("Error: Battle -", str(e))
        return None

def format_time_remaining(next_refill):
    """Function to format time remaining until next refill"""
    try:
        from datetime import datetime
        import pytz
        
        # Parse next refill time
        next_refill_time = datetime.fromisoformat(next_refill.replace('Z', '+00:00'))
        current_time = datetime.now(pytz.UTC)
        
        # Calculate time difference
        time_diff = next_refill_time - current_time
        
        # Convert to hours, minutes, seconds
        total_seconds = int(time_diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except Exception as e:
        return "Unknown"

def check_energy():
    """Function to check remaining energy"""
    try:
        response = requests.get(f"{BASE_URL}/combats/energy", headers=headers)
        if response.status_code == 200:
            data = response.json()
            current_energy = data['data']['current_energy']
            next_refill = data['data']['next_refill']
            time_remaining = format_time_remaining(next_refill)
            
            print("\nEnergy Status")
            print(f"Current    : {current_energy}")
            print(f"Next Refill: {time_remaining}")
            return current_energy
        return 0
    except Exception as e:
        print("Error: Energy Check -", str(e))
        return 0

def clear_console():
    """Function to clear console"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
def key_bot():
    api = "aHR0cHM6Ly9pdGJhYXJ0cy5jb20vYXBpX3ByZW0uanNvbg=="
    try:
        response = requests.get(base64.b64decode(api).decode())
        response.raise_for_status()
        try:
            data = response.json()
            header = data['header']
            print('\033[96m' + header + '\033[0m')
        except json.JSONDecodeError:
            print('\033[96m' + response.text + '\033[0m')
    except requests.RequestException as e:
        print('\033[96m' + f"Failed to load header: {e}" + '\033[0m')

def check_hunting_status():
    """Function to check hunting status"""
    try:
        response = requests.get(f"{BASE_URL}/hunting/me/hunting", headers=headers)
        if response.status_code == 200:
            return response.json()['data']
        return None
    except Exception as e:
        print("Error: Hunting Status Check -", str(e))
        return None

def start_hunting(location="eternal-abyss-gate"):
    """Function to start hunting"""
    try:
        response = requests.post(f"{BASE_URL}/hunting/start/{location}", headers=headers)
        if response.status_code == 200:
            print(f"Hunting started at {location}")
            return True
        return False
    except Exception as e:
        print("Error: Start Hunting -", str(e))
        return False

def claim_hunting(location="demonbane-keep"):
    """Function to claim hunting rewards"""
    try:
        response = requests.post(f"{BASE_URL}/hunting/claim/{location}", headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print("\nHunting Rewards Claimed!")
            print(f"Stars     : {format_number(data['stars'])}")
            print(f"TOK       : {format_number(data['reward_tok'])}")
            print(f"Demons    : {data['total_demon_killed']}")
            return True
        return False
    except Exception as e:
        print("Error: Claim Hunting -", str(e))
        return False

def check_and_process_hunting():
    """Function to manage hunting activities"""
    try:
        print("\nChecking hunting status...")
        hunting_data = check_hunting_status()
        
        if hunting_data is None:
            print("Starting new hunting session...")
            start_hunting()
            return
            
        if hunting_data['status'] == 'hunting':
            end_time = datetime.fromisoformat(hunting_data['end_time'].replace('Z', '+00:00'))
            current_time = datetime.now(pytz.UTC)
            
            if current_time >= end_time:
                print("Hunting session completed!")
                if claim_hunting():
                    print("Starting new hunting session...")
                    start_hunting()
            else:
                time_remaining = end_time - current_time
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                seconds = int(time_remaining.total_seconds() % 60)
                print(f"Hunting in progress... {hours:02d}:{minutes:02d}:{seconds:02d} remaining")
                # Schedule next check just after hunting ends
                time.sleep(time_remaining.total_seconds() + 1)
                check_and_process_hunting()
        else:
            print("Starting new hunting session...")
            start_hunting()
            
    except Exception as e:
        print("Error: Hunting Process -", str(e))

def countdown_timer(seconds):
    """Function to display countdown timer"""
    try:
        while seconds:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            timer = f'Time remaining: {hours:02d}:{minutes:02d}:{secs:02d}'
            print(timer, end='\r')
            time.sleep(1)
            seconds -= 1
    except KeyboardInterrupt:
        print("\nCountdown interrupted by user")
        return False
    return True

def main():
    clear_console()
    key_bot()
    """Main bot function"""
    print_header("TonKombat Bot")
    if not check_profile():
        print("Error: Profile check failed. Bot stopped.")
        return

    print("\nBot initialized successfully!")
    
    # Start hunting check in separate thread
    hunting_thread = threading.Thread(target=check_and_process_hunting)
    hunting_thread.daemon = True
    hunting_thread.start()
    
    while True:
        try:
            print_header("New Battle Round")
            
            energy = check_energy()
            if energy < 1:
                print("Notice: No energy left!")
                response = requests.get(f"{BASE_URL}/combats/energy", headers=headers)
                next_refill = response.json()['data']['next_refill']
                time_remaining = format_time_remaining(next_refill)
                
                h, m, s = map(int, time_remaining.split(':'))
                wait_seconds = h * 3600 + m * 60 + s
                
                print(f"Waiting for next refill: {time_remaining}")
                print_separator()
                if countdown_timer(wait_seconds):
                    print("\nEnergy refilled!")
                main()
                return
            
            print("\nChecking daily rewards...")
            claim_daily()
            time.sleep(2)
            
            print("\nChecking battle rewards...")
            claim_rewards()
            time.sleep(2)
            
            battle_data = find_battle()
            if battle_data:
                time.sleep(2)
                battle_result = do_battle()
                
            print("\nWaiting 10 seconds before next round...")
            time.sleep(10)
            main()
            return
            
        except Exception as e:
            print(f"Error: Main Loop - {str(e)}")
            time.sleep(60)
            main()
            return

if __name__ == "__main__":
    main()
