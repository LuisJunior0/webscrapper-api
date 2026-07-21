from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
from app.services.monitoramento import atualizar_precos

# Definindo o timezone padrão do scheduler para SP
tz = pytz.timezone("America/Sao_Paulo")
scheduler = BlockingScheduler(timezone=tz)

job = scheduler.add_job(
    func=atualizar_precos,
    trigger="interval",
    hour=12
)

scheduler.start()