#!/usr/bin/env python3
"""
Script para aplicar migração de preferências de usuário
"""
import sqlite3
import os

def apply_migration():
    db_path = 'bws_finance.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    print("=" * 60)
    print("MIGRAÇÃO: Preferências de Usuário e Perfil")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Adicionar colunas de perfil se não existirem
        if 'phone' not in columns:
            print("[MIGRAÇÃO] Adicionando coluna 'phone' à tabela users...")
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            print("✅ Coluna 'phone' adicionada")
        
        if 'birthdate' not in columns:
            print("[MIGRAÇÃO] Adicionando coluna 'birthdate' à tabela users...")
            cursor.execute("ALTER TABLE users ADD COLUMN birthdate TEXT")
            print("✅ Coluna 'birthdate' adicionada")
        
        if 'bio' not in columns:
            print("[MIGRAÇÃO] Adicionando coluna 'bio' à tabela users...")
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
            print("✅ Coluna 'bio' adicionada")
        
        if 'avatar' not in columns:
            print("[MIGRAÇÃO] Adicionando coluna 'avatar' à tabela users...")
            cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
            print("✅ Coluna 'avatar' adicionada")
        
        # Criar tabela de preferências
        print("\n[MIGRAÇÃO] Criando tabela user_preferences...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                user_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                language TEXT DEFAULT 'pt-BR',
                currency TEXT DEFAULT 'BRL',
                timezone TEXT DEFAULT 'America/Sao_Paulo',
                dark_mode INTEGER DEFAULT 0,
                compact_dashboard INTEGER DEFAULT 0,
                show_balance INTEGER DEFAULT 1,
                save_search_history INTEGER DEFAULT 1,
                allow_analytics INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """)
        print("✅ Tabela user_preferences criada")
        
        # Criar índices
        print("\n[MIGRAÇÃO] Criando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_tenant ON user_preferences(tenant_id)")
        print("✅ Índices criados")
        
        # Criar preferências padrão para todos os usuários existentes
        print("\n[MIGRAÇÃO] Criando preferências padrão para usuários existentes...")
        cursor.execute("""
            INSERT OR IGNORE INTO user_preferences (id, user_id, tenant_id, language, currency, timezone)
            SELECT 
                lower(hex(randomblob(16))),
                u.id,
                u.tenant_id,
                'pt-BR',
                'BRL',
                'America/Sao_Paulo'
            FROM users u
            WHERE NOT EXISTS (
                SELECT 1 FROM user_preferences WHERE user_id = u.id
            )
        """)
        prefs_created = cursor.rowcount
        print(f"✅ {prefs_created} preferências padrão criadas")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        # Verificar resultados
        cursor.execute("SELECT COUNT(*) FROM user_preferences")
        total_prefs = cursor.fetchone()[0]
        print(f"\n📊 Total de preferências: {total_prefs}")
        
    except sqlite3.Error as e:
        print(f"\n❌ ERRO na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    apply_migration()
