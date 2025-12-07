import sqlite3
import sys
sys.path.append('.')

from services.api_connectors import InvestmentAPIFactory

conn = sqlite3.connect('bws_finance.db')
cursor = conn.cursor()

# Buscar todos os investimentos ativos
rows = cursor.execute("""
    SELECT id, name, amount, current_value, quantity 
    FROM investments 
    WHERE investment_status = 'active' OR investment_status IS NULL
""").fetchall()

print(f"🔄 Atualizando {len(rows)} investimentos...")
api_factory = InvestmentAPIFactory()

for row in rows:
    inv_id, name, amount, old_current_value, quantity = row
    quantity = quantity or 1.0
    
    print(f"\n📊 {name} (ID: {inv_id})")
    print(f"   Quantidade: {quantity}")
    print(f"   Investido: R$ {amount:.2f}")
    print(f"   Current_value antigo: R$ {old_current_value:.2f}")
    
    try:
        # Buscar cotação atual
        market_data = api_factory.get_stock_with_fundamentals(name)
        
        if market_data and market_data.get('price'):
            price = market_data['price']
            new_current_value = price * quantity
            profit = new_current_value - amount
            profit_percent = (profit / amount * 100) if amount > 0 else 0
            
            print(f"   ✅ Cotação: R$ {price:.2f}")
            print(f"   💰 Valor atual: R$ {new_current_value:.2f}")
            print(f"   📈 Lucro: R$ {profit:.2f} ({profit_percent:+.2f}%)")
            
            # Atualizar no banco
            cursor.execute("""
                UPDATE investments 
                SET current_value = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_current_value, inv_id))
        else:
            print(f"   ⚠️ Não foi possível buscar cotação, mantendo valor atual")
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")

conn.commit()
conn.close()

print("\n✅ Atualização concluída!")
