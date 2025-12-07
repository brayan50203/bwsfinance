"""
Script de Teste do Módulo de Atualização de Investimentos
"""

import sys
import os

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.investment_updater import update_all_investments

print("=" * 70)
print("🧪 TESTE DO MÓDULO DE ATUALIZAÇÃO DE INVESTIMENTOS")
print("=" * 70)
print()

# Executar atualização
stats = update_all_investments()

print()
print("=" * 70)
print("📊 RESULTADO DO TESTE:")
print("=" * 70)
print(f"Total de investimentos: {stats['total']}")
print(f"✅ Atualizados com sucesso: {stats['success']}")
print(f"❌ Falhas: {stats['failed']}")
print(f"⏭️ Pulados: {stats['skipped']}")
print("=" * 70)
