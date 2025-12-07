import sqlite3
from datetime import datetime

conn = sqlite3.connect('bws_finance.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("RECALCULANDO LIMITES DOS CARTÕES")
print("=" * 60)

# Buscar todos os cartões ativos
cards = cursor.execute('SELECT id, name FROM cards WHERE active = 1').fetchall()

for card in cards:
    card_id = card['id']
    card_name = card['name']
    
    # Calcular total usado (transações tipo Despesa com este cartão)
    result = cursor.execute('''
        SELECT COALESCE(SUM(value), 0) as total_used
        FROM transactions
        WHERE card_id = ? AND type = 'Despesa'
    ''', (card_id,)).fetchone()
    
    total_used = result['total_used']
    
    # Atualizar o used_limit
    cursor.execute('''
        UPDATE cards
        SET used_limit = ?
        WHERE id = ?
    ''', (total_used, card_id))
    
    print(f"💳 {card_name}: R$ {total_used:.2f} usado")

conn.commit()
print("\n✅ Limites recalculados com sucesso!")

# Mostrar resultado final
print("\n" + "=" * 60)
print("LIMITES ATUALIZADOS:")
print("=" * 60)

cards = cursor.execute('''
    SELECT name, limit_amount, used_limit 
    FROM cards 
    WHERE active = 1
''').fetchall()

for card in cards:
    limit_amount = card['limit_amount'] or 0
    used_limit = card['used_limit'] or 0
    available = limit_amount - used_limit
    percent = (used_limit / limit_amount * 100) if limit_amount > 0 else 0
    
    print(f"\n💳 {card['name']}")
    print(f"   Limite Total: R$ {limit_amount:.2f}")
    print(f"   Usado: R$ {used_limit:.2f} ({percent:.1f}%)")
    print(f"   Disponível: R$ {available:.2f}")
    
    if available < 0:
        print("   ⚠️ CRÍTICO: Limite ultrapassado!")
    elif percent > 80:
        print("   ⚠️ ATENÇÃO: Limite quase esgotado!")
    elif percent > 50:
        print("   ⚡ Aviso: Mais de 50% do limite usado")
    else:
        print("   ✅ Limite saudável")

conn.close()
print("\n" + "=" * 60)
