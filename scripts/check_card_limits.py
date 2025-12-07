import sqlite3

conn = sqlite3.connect('bws_finance.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("VERIFICAÇÃO DE LIMITES DOS CARTÕES")
print("=" * 60)

cards = cursor.execute('''
    SELECT id, name, limit_amount, used_limit 
    FROM cards 
    WHERE active = 1
''').fetchall()

if not cards:
    print("❌ Nenhum cartão ativo encontrado")
else:
    for card in cards:
        limit_amount = card['limit_amount'] or 0
        used_limit = card['used_limit'] or 0
        available = limit_amount - used_limit
        percent = (used_limit / limit_amount * 100) if limit_amount > 0 else 0
        
        print(f"\n💳 {card['name']}")
        print(f"   Limite Total: R$ {limit_amount:.2f}")
        print(f"   Usado: R$ {used_limit:.2f} ({percent:.1f}%)")
        print(f"   Disponível: R$ {available:.2f}")
        
        if percent > 80:
            print("   ⚠️ ATENÇÃO: Limite quase esgotado!")
        elif percent > 50:
            print("   ⚡ Aviso: Mais de 50% do limite usado")

print("\n" + "=" * 60)

# Verificar transações com cartão
print("\nTRANSAÇÕES COM CARTÃO:")
print("=" * 60)

transactions = cursor.execute('''
    SELECT t.description, t.value, t.date, c.name as card_name, t.installment_id
    FROM transactions t
    JOIN cards c ON t.card_id = c.id
    WHERE t.card_id IS NOT NULL AND t.type = 'Despesa'
    ORDER BY t.date DESC
    LIMIT 10
''').fetchall()

if not transactions:
    print("❌ Nenhuma transação com cartão encontrada")
else:
    for trans in transactions:
        installment_mark = " 📦 [PARCELADO]" if trans['installment_id'] else ""
        print(f"• {trans['date']} | {trans['card_name']} | {trans['description']} | R$ {trans['value']:.2f}{installment_mark}")

conn.close()
print("\n✅ Verificação concluída!")
