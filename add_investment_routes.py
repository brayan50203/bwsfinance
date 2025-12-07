with open('app.py', 'a', encoding='utf-8') as f:
    f.write("""
@app.route('/investments/edit', methods=['POST'])
@login_required
def edit_investment():
    user = get_current_user()
    data = request.get_json()
    
    investment_id = data.get('id')
    name = data.get('name')
    inv_type = data.get('type')
    amount = float(data.get('amount', 0))
    
    db = get_db()
    db.execute(\"\"\"
        UPDATE investments 
        SET name = ?, type = ?, invested_value = ?, current_value = ?
        WHERE id = ? AND user_id = ? AND tenant_id = ?
    \"\"\", (name, inv_type, amount, amount, investment_id, user['id'], user['tenant_id']))
    
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'message': 'Investimento atualizado!'})

@app.route('/investments/delete', methods=['POST'])
@login_required
def delete_investment():
    user = get_current_user()
    data = request.get_json()
    
    investment_id = data.get('id')
    
    db = get_db()
    db.execute(\"\"\"
        DELETE FROM investments 
        WHERE id = ? AND user_id = ? AND tenant_id = ?
    \"\"\", (investment_id, user['id'], user['tenant_id']))
    
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'message': 'Investimento excluído!'})
""")
print('✅ Rotas de editar e excluir investimentos adicionadas!')
