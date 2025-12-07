"""
SCHEDULER - Agendador de Tarefas Automáticas
Executa transações recorrentes diariamente às 00:01
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

scheduler = BackgroundScheduler()

def start_scheduler():
    """Inicia o agendador"""
    from routes.recurring import execute_recurring_transactions
    from services.investment_updater import update_all_investments
    
    # Executar transações recorrentes todos os dias às 00:01
    scheduler.add_job(
        func=execute_recurring_transactions,
        trigger=CronTrigger(hour=0, minute=1),
        id='execute_recurring_transactions',
        name='Execute Recurring Transactions',
        replace_existing=True
    )
    
    # Atualizar investimentos todos os dias às 08:00
    scheduler.add_job(
        func=update_all_investments,
        trigger=CronTrigger(hour=8, minute=0),
        id='update_investments',
        name='Update Investments Quotes',
        replace_existing=True
    )
    
    # Também permitir execução manual a cada 1 hora (para testes)
    # scheduler.add_job(
    #     func=execute_recurring_transactions,
    #     trigger='interval',
    #     hours=1,
    #     id='execute_recurring_hourly',
    #     name='Execute Recurring Hourly (Test)',
    #     replace_existing=True
    # )
    
    scheduler.start()
    print("[OK] Scheduler iniciado! Transacoes recorrentes serao executadas as 00:01")
    print("[OK] Atualizacao de investimentos agendada para 08:00")

def stop_scheduler():
    """Para o agendador"""
    scheduler.shutdown()
    print("[STOP] Scheduler parado")

def trigger_manual_execution():
    """Executa manualmente (para testes)"""
    from routes.recurring import execute_recurring_transactions
    print("[RUN] Executando transacoes recorrentes manualmente...")
    count = execute_recurring_transactions()
    return count

def trigger_investments_update():
    """Atualiza investimentos manualmente"""
    from services.investment_updater import update_all_investments
    print("[UPDATE] Atualizando investimentos manualmente...")
    stats = update_all_investments()
    return stats
