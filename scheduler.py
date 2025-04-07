import schedule
import time
import threading

def job():
    print("Executando tarefa agendada...")

def run_scheduler():
    schedule.every().day.at("09:00").do(job)

    def run_continuously():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run_continuously)
    thread.start()
