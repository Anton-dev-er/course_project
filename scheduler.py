import schedule
from notification import daily_notify

schedule.every().day.at('10:00').do(daily_notify)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
