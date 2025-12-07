"""
Popula todas as categorias e subcategorias do BWS Finance v2.0
Estrutura completa de categorias para uso pessoal e profissional
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = 'bws_finance.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_category(name, type_, icon, subcategories, keywords=None, tenant_id='default'):
    """
    Cria uma categoria e suas subcategorias
    
    Args:
        name: Nome da categoria
        type_: 'Receita' ou 'Despesa'
        icon: Emoji/ícone
        subcategories: Lista de subcategorias
        keywords: Lista de palavras-chave para IA (opcional)
        tenant_id: ID do tenant (default para categorias globais)
    """
    db = get_db()
    
    # Criar categoria principal
    category_id = str(uuid.uuid4())
    
    db.execute("""
        INSERT OR IGNORE INTO categories (id, tenant_id, name, type, icon, parent_id, active, created_at)
        VALUES (?, ?, ?, ?, ?, NULL, 1, CURRENT_TIMESTAMP)
    """, (category_id, tenant_id, name, type_, icon))
    
    # Criar subcategorias usando parent_id
    for subcategory in subcategories:
        subcat_id = str(uuid.uuid4())
        db.execute("""
            INSERT OR IGNORE INTO categories (id, tenant_id, name, type, icon, parent_id, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        """, (subcat_id, tenant_id, subcategory, type_, '📁', category_id))
    
    db.commit()
    db.close()
    
    print(f"✅ {icon} {name} ({type_}) - {len(subcategories)} subcategorias")

def populate_all_categories():
    """Popula todas as categorias do BWS Finance v2.0"""
    
    print("="*60)
    print("🚀 POPULANDO CATEGORIAS DO BWS FINANCE V2.0")
    print("="*60)
    
    # ==========================================
    # 💰 RECEITAS
    # ==========================================
    print("\n💰 RECEITAS:")
    
    create_category(
        name="Salário e Renda Fixa",
        type_="Receita",
        icon="💼",
        subcategories=[
            "Salário",
            "Comissão",
            "Bônus",
            "13º Salário",
            "Hora Extra",
            "PLR",
            "Férias"
        ]
    )
    
    create_category(
        name="Vendas e Serviços",
        type_="Receita",
        icon="💸",
        subcategories=[
            "Venda de Produtos",
            "Prestação de Serviços",
            "Marketplace",
            "Loja Virtual",
            "Freelance",
            "Consultoria"
        ]
    )
    
    create_category(
        name="Investimentos",
        type_="Receita",
        icon="📈",
        subcategories=[
            "Dividendos",
            "Juros de Renda Fixa",
            "Lucro de Ações",
            "Criptomoedas",
            "Fundos Imobiliários",
            "CDB",
            "Tesouro Direto",
            "LCI/LCA"
        ]
    )
    
    create_category(
        name="Reembolsos",
        type_="Receita",
        icon="💰",
        subcategories=[
            "Despesas Reembolsadas",
            "Cashback",
            "Garantia Devolvida",
            "Vale-Refeição",
            "Vale-Transporte"
        ]
    )
    
    create_category(
        name="Outros Recebimentos",
        type_="Receita",
        icon="🎁",
        subcategories=[
            "Pix Recebido",
            "Transferência",
            "Presente",
            "Doação",
            "Aporte Próprio",
            "Herança",
            "Prêmio"
        ]
    )
    
    create_category(
        name="Empréstimos Recebidos",
        type_="Receita",
        icon="💵",
        subcategories=[
            "Empréstimo Bancário",
            "Crédito Pessoal",
            "Limite de Conta",
            "Empréstimo entre Amigos"
        ]
    )
    
    create_category(
        name="Renda Internacional",
        type_="Receita",
        icon="🌎",
        subcategories=[
            "PayPal",
            "Wise",
            "Upwork",
            "Remessa do Exterior",
            "Freelance Internacional"
        ]
    )
    
    # ==========================================
    # 💳 DESPESAS
    # ==========================================
    print("\n💳 DESPESAS:")
    
    create_category(
        name="Moradia",
        type_="Despesa",
        icon="🏠",
        subcategories=[
            "Aluguel",
            "Condomínio",
            "Água",
            "Luz",
            "Gás",
            "Internet",
            "Telefone Fixo",
            "Manutenção",
            "Limpeza",
            "Móveis",
            "IPTU"
        ]
    )
    
    create_category(
        name="Transporte",
        type_="Despesa",
        icon="🚗",
        subcategories=[
            "Combustível",
            "Uber",
            "99",
            "Manutenção Veículo",
            "Estacionamento",
            "Seguro Auto",
            "IPVA",
            "Licenciamento",
            "Pedágio",
            "Lavagem"
        ]
    )
    
    create_category(
        name="Alimentação",
        type_="Despesa",
        icon="🍽️",
        subcategories=[
            "Supermercado",
            "Restaurante",
            "iFood",
            "Rappi",
            "Lanches",
            "Feira",
            "Padaria",
            "Açougue",
            "Hortifruti"
        ]
    )
    
    create_category(
        name="Cuidados Pessoais",
        type_="Despesa",
        icon="💇",
        subcategories=[
            "Barbearia",
            "Salão de Beleza",
            "Academia",
            "Farmácia",
            "Estética",
            "Roupas",
            "Calçados",
            "Cosméticos",
            "Perfumaria"
        ]
    )
    
    create_category(
        name="Saúde",
        type_="Despesa",
        icon="👨‍⚕️",
        subcategories=[
            "Plano de Saúde",
            "Consultas",
            "Exames",
            "Medicamentos",
            "Dentista",
            "Terapia",
            "Fisioterapia",
            "Hospital",
            "Ótica"
        ]
    )
    
    create_category(
        name="Educação",
        type_="Despesa",
        icon="🎓",
        subcategories=[
            "Mensalidade Escola",
            "Mensalidade Faculdade",
            "Livros",
            "Cursos Online",
            "Material Escolar",
            "Udemy",
            "Coursera",
            "Idiomas"
        ]
    )
    
    create_category(
        name="Lazer e Entretenimento",
        type_="Despesa",
        icon="🎮",
        subcategories=[
            "Netflix",
            "Spotify",
            "Amazon Prime",
            "Disney+",
            "Cinema",
            "Viagens",
            "Festas",
            "Jogos",
            "Shows",
            "Teatro"
        ]
    )
    
    create_category(
        name="Compras e Consumo",
        type_="Despesa",
        icon="🛍️",
        subcategories=[
            "Eletrônicos",
            "Roupas",
            "Calçados",
            "Acessórios",
            "Decoração",
            "Amazon",
            "Mercado Livre",
            "Shopee",
            "Magazine Luiza"
        ]
    )
    
    create_category(
        name="Cartões de Crédito",
        type_="Despesa",
        icon="💳",
        subcategories=[
            "Fatura Cartão",
            "Juros Cartão",
            "Anuidade",
            "Encargos",
            "Tarifa"
        ]
    )
    
    create_category(
        name="Impostos e Taxas",
        type_="Despesa",
        icon="🧾",
        subcategories=[
            "IPTU",
            "IPVA",
            "IRPF",
            "Taxas Bancárias",
            "Tarifa Pix",
            "DOC/TED",
            "MEI",
            "Alvará"
        ]
    )
    
    create_category(
        name="Assinaturas e Serviços",
        type_="Despesa",
        icon="📱",
        subcategories=[
            "Google One",
            "Microsoft 365",
            "iCloud",
            "Dropbox",
            "Adobe",
            "Canva Pro",
            "ChatGPT Plus",
            "GitHub",
            "Hosting"
        ]
    )
    
    create_category(
        name="Profissional e Negócios",
        type_="Despesa",
        icon="💼",
        subcategories=[
            "Material de Trabalho",
            "Domínio",
            "Hospedagem",
            "Marketing",
            "Equipamentos",
            "Software",
            "Contador",
            "Jurídico",
            "Escritório"
        ]
    )
    
    create_category(
        name="Dívidas e Financiamentos",
        type_="Despesa",
        icon="🏦",
        subcategories=[
            "Financiamento Veículo",
            "Financiamento Imóvel",
            "Empréstimo Pessoal",
            "Consórcio",
            "Crediário",
            "Carnê"
        ]
    )
    
    create_category(
        name="Viagens",
        type_="Despesa",
        icon="🏖️",
        subcategories=[
            "Passagens Aéreas",
            "Hotel",
            "Alimentação em Viagem",
            "Transporte Local",
            "Seguro Viagem",
            "Passeios",
            "Souvenirs"
        ]
    )
    
    create_category(
        name="Família e Filhos",
        type_="Despesa",
        icon="🧸",
        subcategories=[
            "Escola",
            "Fraldas",
            "Brinquedos",
            "Mesada",
            "Roupa Infantil",
            "Babá",
            "Pensão Alimentícia"
        ]
    )
    
    create_category(
        name="Pets",
        type_="Despesa",
        icon="🐾",
        subcategories=[
            "Ração",
            "Veterinário",
            "Pet Shop",
            "Vacinas",
            "Banho e Tosa",
            "Remédios Pet"
        ]
    )
    
    create_category(
        name="Tecnologia",
        type_="Despesa",
        icon="🧑‍💻",
        subcategories=[
            "Celular",
            "Notebook",
            "Computador",
            "Periféricos",
            "Monitor",
            "Headset",
            "Mouse",
            "Teclado",
            "Licenças de Software"
        ]
    )
    
    create_category(
        name="Manutenção e Reparos",
        type_="Despesa",
        icon="⚙️",
        subcategories=[
            "Eletrodomésticos",
            "Conserto de Computador",
            "Conserto de Automóvel",
            "Manutenção Residência",
            "Pintura",
            "Encanador",
            "Eletricista"
        ]
    )
    
    create_category(
        name="Doações e Presentes",
        type_="Despesa",
        icon="🎁",
        subcategories=[
            "Presentes",
            "Doações",
            "Caridade",
            "Dízimo",
            "Ofertas",
            "Aniversários"
        ]
    )
    
    create_category(
        name="Investimentos (Aportes)",
        type_="Despesa",
        icon="📊",
        subcategories=[
            "Aporte em Ações",
            "Aporte em CDB",
            "Aporte em Tesouro",
            "Aporte em Cripto",
            "Aporte em Fundos",
            "Reserva de Emergência"
        ]
    )
    
    create_category(
        name="Outros Gastos",
        type_="Despesa",
        icon="💸",
        subcategories=[
            "Multas",
            "Perdas",
            "Despesas Diversas",
            "Não Categorizado"
        ]
    )
    
    print("\n" + "="*60)
    print("✅ CATEGORIAS POPULADAS COM SUCESSO!")
    print("="*60)
    
    # Mostrar resumo
    db = get_db()
    
    receitas = db.execute("SELECT COUNT(*) as total FROM categories WHERE type = 'Receita' AND parent_id IS NULL").fetchone()
    despesas = db.execute("SELECT COUNT(*) as total FROM categories WHERE type = 'Despesa' AND parent_id IS NULL").fetchone()
    subcats = db.execute("SELECT COUNT(*) as total FROM categories WHERE parent_id IS NOT NULL").fetchone()
    
    print(f"\n📊 RESUMO:")
    print(f"   💰 Receitas: {receitas['total']} categorias principais")
    print(f"   💳 Despesas: {despesas['total']} categorias principais")
    print(f"   📂 Subcategorias: {subcats['total']} no total")
    
    db.close()

if __name__ == "__main__":
    populate_all_categories()
