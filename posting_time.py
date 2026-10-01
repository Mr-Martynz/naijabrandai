from datetime import datetime


def recommend_posting_time(current_date: str = None) -> dict:
    """
    Recommends the best time to post for a Nigerian audience, based on general
    engagement patterns and whether it's currently a high-activity season
    (Detty December, Owambe/wedding season).

    Args:
        current_date: Optional date string in 'YYYY-MM-DD' format. Defaults to today.
    """
    if current_date:
        date = datetime.strptime(current_date, "%Y-%m-%d")
    else:
        date = datetime.now()

    month = date.month
    weekday = date.weekday()  # Monday = 0, Sunday = 6

    # Seasonal context
    if month == 12:
        season_note = "It's Detty December — engagement is high all month, post daily if you can."
    elif month in (11, 1, 2):
        season_note = "Wedding/Owambe season is active — good time for event-themed posts."
    else:
        season_note = "Regular season — consistency matters more than any single perfect time."

    # Day-of-week pattern
    if weekday in (4, 5, 6):  # Fri, Sat, Sun
        best_window = "7:00 PM – 10:00 PM"
        day_note = "Weekends see the highest engagement — people are relaxed and scrolling more."
    else:
        best_window = "8:00 PM – 9:30 PM"
        day_note = "Weekday evenings, after work hours, perform best."

    return {
        "best_window": best_window,
        "day_note": day_note,
        "season_note": season_note,
    }


if __name__ == "__main__":
    print(recommend_posting_time())
    print(recommend_posting_time("2026-12-15"))