with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontra todas as linhas com @app.route('/transactions')
indices = [i for i, line in enumerate(lines) if "@app.route('/transactions')" in line]

if len(indices) > 1:
    # Remove a última ocorrência (que vai até o próximo @app.route ou final do arquivo)
    start_idx = indices[-1]
    end_idx = len(lines)
    
    # Procura o próximo @app.route
    for i in range(start_idx + 1, len(lines)):
        if '@app.route(' in lines[i] or 'if __name__' in lines[i]:
            end_idx = i
            break
    
    # Remove as linhas
    del lines[start_idx:end_idx]
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'✅ Rota duplicada removida! (linhas {start_idx}-{end_idx})')
else:
    print('Apenas uma rota /transactions encontrada')
