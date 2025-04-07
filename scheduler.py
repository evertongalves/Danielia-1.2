import schedule
import time
import threading
from sheets import gerar_relatorio, iniciar_prospeccao

def job():
    print("🕒 Executando tarefa agendada...")
    gerar_relatorio()
    iniciar_prospeccao()

def run_scheduler():
    schedule.every().day.at("09:00").do(job)
    schedule.every().day.at("17:00").do(job)  # Execução duas vezes ao dia!

    def run_continuously():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run_continuously)
    thread.daemon = True
    thread.start()
