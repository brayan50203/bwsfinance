import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Procurar o padrão e substituir
pattern = r"return render_template\('accounts\.html',\s+user=user,\s+accounts=\[dict\(a\) for a in accounts\]\)"
replacement = """return render_template('accounts.html',
                         user=user,
                         accounts=[dict(a) for a in accounts],
                         total_balance=total_balance)"""

content = re.sub(pattern, replacement, content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Corrigido!")
