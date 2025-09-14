#!/usr/bin/env python3
"""
Script to view and analyze medication logs
"""

import json
import os
from datetime import datetime

def load_logs():
    """Load medication logs from file"""
    log_file = "medication_log.json"
    if not os.path.exists(log_file):
        print("❌ No log file found. Run the medication system first.")
        return []
    
    try:
        with open(log_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("❌ Error reading log file. It may be corrupted.")
        return []

def view_all_logs():
    """Display all medication logs"""
    logs = load_logs()
    
    if not logs:
        return
    
    print("📋 All Medication Logs")
    print("=" * 60)
    
    for i, log in enumerate(logs, 1):
        timestamp = log.get('timestamp', 'Unknown')
        time_str = log.get('time_str', 'Unknown')
        pill_name = log.get('pill_name', 'Unknown')
        status = log.get('status', 'Unknown')
        details = log.get('details', '')
        
        print(f"{i:2d}. {timestamp[:19]} | {time_str} | {pill_name:12s} | {status:15s} | {details}")

def view_today_logs():
    """Display today's medication logs"""
    logs = load_logs()
    today = datetime.now().date().isoformat()
    
    today_logs = [log for log in logs if log.get('date') == today]
    
    if not today_logs:
        print("📅 No logs found for today.")
        return
    
    print(f"📅 Today's Medication Logs ({today})")
    print("=" * 60)
    
    for i, log in enumerate(today_logs, 1):
        timestamp = log.get('timestamp', 'Unknown')
        time_str = log.get('time_str', 'Unknown')
        pill_name = log.get('pill_name', 'Unknown')
        status = log.get('status', 'Unknown')
        details = log.get('details', '')
        
        print(f"{i:2d}. {timestamp[11:19]} | {time_str} | {pill_name:12s} | {status:15s} | {details}")

def view_medication_summary():
    """Show summary of medication adherence"""
    logs = load_logs()
    
    if not logs:
        print("❌ No logs to analyze.")
        return
    
    print("📊 Medication Adherence Summary")
    print("=" * 40)
    
    # Group by medication
    meds = {}
    for log in logs:
        pill_name = log.get('pill_name', 'Unknown')
        if pill_name not in meds:
            meds[pill_name] = {'total': 0, 'taken': 0, 'missed': 0}
        
        meds[pill_name]['total'] += 1
        status = log.get('status', '')
        
        if 'escalated' in status or 'missed' in status:
            meds[pill_name]['missed'] += 1
        elif 'taken' in status:
            meds[pill_name]['taken'] += 1
    
    for pill_name, stats in meds.items():
        adherence_rate = (stats['taken'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{pill_name:15s}: {stats['taken']:2d}/{stats['total']:2d} taken ({adherence_rate:5.1f}%)")

def export_logs_to_csv():
    """Export logs to CSV format"""
    logs = load_logs()
    
    if not logs:
        print("❌ No logs to export.")
        return
    
    csv_file = "medication_logs.csv"
    
    try:
        import csv
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Date', 'Time', 'Medication', 'Status', 'Details'])
            
            for log in logs:
                writer.writerow([
                    log.get('timestamp', ''),
                    log.get('date', ''),
                    log.get('time_str', ''),
                    log.get('pill_name', ''),
                    log.get('status', ''),
                    log.get('details', '')
                ])
        
        print(f"✅ Logs exported to {csv_file}")
        
    except ImportError:
        print("❌ CSV module not available. Install with: pip install csv")

def main():
    """Main menu"""
    while True:
        print("\n🏥 Medication Log Viewer")
        print("=" * 30)
        print("1. View all logs")
        print("2. View today's logs")
        print("3. View medication summary")
        print("4. Export to CSV")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            view_all_logs()
        elif choice == '2':
            view_today_logs()
        elif choice == '3':
            view_medication_summary()
        elif choice == '4':
            export_logs_to_csv()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
