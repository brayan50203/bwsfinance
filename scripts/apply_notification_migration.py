#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aplica migração de notificações ao banco de dados
"""

import sqlite3
import os

def apply_notification_migration():
    """Aplica tabelas de notificações"""
    db_path = 'bws_finance.db'
    
    if not os.path.exists(db_path):
        print("[ERRO] Banco de dados não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("[MIGRAÇÃO] Aplicando tabelas de notificações...")
        
        # Verificar se tabela antiga existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        old_table_exists = cursor.fetchone() is not None
        
        if old_table_exists:
            print("[AVISO] Tabela 'notifications' antiga encontrada. Fazendo backup e recriando...")
            
            # Renomear tabela antiga
            cursor.execute("ALTER TABLE notifications RENAME TO notifications_old_backup")
            print("[OK] Backup da tabela antiga criado")
        
        # Ler schema
        with open('migrations/add_notifications_tables.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Remover comentários inline que causam problemas
        import re
        schema = re.sub(r'--[^\n]*\n', '\n', schema)
        
        # Executar
        cursor.executescript(schema)
        conn.commit()
        
        # Verificar tabelas criadas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('notifications', 'notification_preferences', 'notification_logs')
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"[OK] Tabelas criadas: {', '.join(tables)}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM notification_preferences")
        pref_count = cursor.fetchone()[0]
        
        print(f"[OK] {pref_count} preferências padrão criadas")
        
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"[ERRO] Falha na migração: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRAÇÃO: Sistema de Notificações")
    print("=" * 60)
    
    success = apply_notification_migration()
    
    if success:
        print("\n✅ Migração concluída com sucesso!")
        print("\nPróximos passos:")
        print("1. Reinicie o servidor Flask")
        print("2. Acesse http://127.0.0.1:5000/notifications/preferences")
        print("3. Configure seus canais de notificação")
    else:
        print("\n❌ Migração falhou. Verifique os logs acima.")
