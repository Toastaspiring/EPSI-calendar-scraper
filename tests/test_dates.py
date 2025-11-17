import main

soup = main.fetch_page()
events = main.extract_events(soup)

print(f"\nExtracted {len(events)} events\n")

if events:
    print("First 3 events with dates:")
    for i, event in enumerate(events[:3], 1):
        print(f"\n{i}. {event.get('course', 'Unknown')}")
        print(f"   Date: {event.get('date', 'NO DATE')}")
        print(f"   Time: {event.get('time', 'N/A')}")

