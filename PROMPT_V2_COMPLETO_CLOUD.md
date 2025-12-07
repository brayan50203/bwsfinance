# 🚀 PROMPT COMPLETO V2 - SISTEMA DE INVESTIMENTOS PROFISSIONAL

## 📋 ÍNDICE
1. [Contexto Atual](#contexto-atual)
2. [Problemas a Corrigir](#problemas-a-corrigir)
3. [Layout Ideal (HTML Pronto)](#layout-ideal)
4. [Sistema de Autenticação](#sistema-de-autenticação)
5. [Integração com APIs](#integração-com-apis)
6. [Estrutura de Arquivos](#estrutura-de-arquivos)
7. [Checklist de Validação](#checklist-de-validação)

---

## 🎯 CONTEXTO ATUAL

### ✅ O que já está funcionando:
- **Backend Flask** completo com SQLite
- **Módulo de atualização** (`services/investment_updater.py`)
- **APIs integradas**: Yahoo Finance, CoinGecko, Tesouro Direto
- **Scheduler automático**: Atualização diária às 08:00
- **Logs persistentes**: `logs/investments.log`
- **Rota manual**: `POST /admin/update-investments`
- **Banco de dados** com tabelas: investments, users, accounts, cards, transactions

### ❌ O que precisa ser corrigido:
1. **Dashboard offline/com erro** - não carrega ou dá erro 500
2. **Tela de investimentos sem design** - precisa de layout moderno
3. **Falta sistema de login** - qualquer um acessa tudo
4. **Falta feedback visual** - usuário não sabe se atualizou
5. **Falta gráficos** - dados não visualizados graficamente

---

## 🚨 PROBLEMAS A CORRIGIR (PRIORIDADE)

### 1. Dashboard Offline
**Sintoma**: Erro 500, página em branco, ou "Cannot GET /dashboard"

**Possíveis causas**:
- Rota `/dashboard` com erro no Python
- Query SQL retornando None
- Template não encontrado
- Variável não definida no Jinja2

**Solução esperada**:
```python
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user = get_current_user()
        
        # Buscar investimentos com fallback
        investments_summary = db.execute("""
            SELECT 
                COUNT(*) as total_investments,
                COALESCE(SUM(amount), 0) as total_invested,
                COALESCE(SUM(current_value), 0) as total_current
            FROM investments
            WHERE user_id = ?
        """, (user['id'],)).fetchone() or {
            'total_investments': 0,
            'total_invested': 0,
            'total_current': 0
        }
        
        # Sempre passar dicionário, nunca None
        return render_template('dashboard.html', 
                             user=user,
                             investments_summary=dict(investments_summary))
    except Exception as e:
        print(f"Erro no dashboard: {e}")
        return render_template('error.html', error=str(e)), 500
```

### 2. Tela de Investimentos sem Design
**Problema atual**: Layout básico, sem cartões, sem cores, sem gráficos

**Solução**: Implementar o layout abaixo ⬇️

---

## 🎨 LAYOUT IDEAL (HTML PRONTO PARA CLONAR)

### 📄 `templates/investments_new.html` (MODELO COMPLETO)

```html
{% extends "base.html" %}

{% block title %}Investimentos - BWS Finance{% endblock %}

{% block content %}
<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-lg">
        <div class="container mx-auto px-6 py-8">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-4xl font-bold text-gray-800 dark:text-white">
                        📈 Meus Investimentos
                    </h1>
                    <p class="text-gray-600 dark:text-gray-400 mt-2">
                        Acompanhe sua carteira em tempo real
                    </p>
                </div>
                
                <div class="flex gap-4">
                    <button onclick="updateInvestments()" 
                            id="updateBtn"
                            class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2 shadow-lg">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        <span id="updateText">Atualizar Agora</span>
                    </button>
                    
                    <button onclick="openAddModal()" 
                            class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2 shadow-lg">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        Novo Investimento
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Resumo Cards -->
    <div class="container mx-auto px-6 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <!-- Total Investido -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border-l-4 border-blue-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Investido</p>
                        <h3 class="text-3xl font-bold text-gray-800 dark:text-white mt-2">
                            R$ {{ "%.2f"|format(summary.total_invested) }}
                        </h3>
                    </div>
                    <div class="bg-blue-100 dark:bg-blue-900 p-4 rounded-full">
                        <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <!-- Valor Atual -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border-l-4 border-green-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Valor Atual</p>
                        <h3 class="text-3xl font-bold text-gray-800 dark:text-white mt-2">
                            R$ {{ "%.2f"|format(summary.total_current) }}
                        </h3>
                    </div>
                    <div class="bg-green-100 dark:bg-green-900 p-4 rounded-full">
                        <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <!-- Rentabilidade -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border-l-4 {{ 'border-green-500' if summary.profit_percent >= 0 else 'border-red-500' }}">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Rentabilidade</p>
                        <h3 class="text-3xl font-bold {{ 'text-green-600' if summary.profit_percent >= 0 else 'text-red-600' }} mt-2">
                            {{ "%.2f"|format(summary.profit_percent) }}%
                        </h3>
                        <p class="text-sm {{ 'text-green-600' if summary.profit_loss >= 0 else 'text-red-600' }} font-semibold">
                            R$ {{ "%.2f"|format(summary.profit_loss) }}
                        </p>
                    </div>
                    <div class="bg-{{ 'green' if summary.profit_percent >= 0 else 'red' }}-100 dark:bg-{{ 'green' if summary.profit_percent >= 0 else 'red' }}-900 p-4 rounded-full">
                        <svg class="w-8 h-8 text-{{ 'green' if summary.profit_percent >= 0 else 'red' }}-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <!-- Total de Ativos -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border-l-4 border-purple-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total de Ativos</p>
                        <h3 class="text-3xl font-bold text-gray-800 dark:text-white mt-2">
                            {{ summary.total_investments }}
                        </h3>
                        <p class="text-sm text-gray-500 mt-1">
                            Atualizado: {{ summary.last_update[:16] if summary.last_update else 'Nunca' }}
                        </p>
                    </div>
                    <div class="bg-purple-100 dark:bg-purple-900 p-4 rounded-full">
                        <svg class="w-8 h-8 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                        </svg>
                    </div>
                </div>
            </div>
        </div>

        <!-- Lista de Investimentos por Tipo -->
        <div class="space-y-6">
            <!-- Ações -->
            {% if investments_by_type.acao %}
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
                <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
                    <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                        📊 Ações ({{ investments_by_type.acao|length }})
                    </h2>
                </div>
                <div class="p-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {% for inv in investments_by_type.acao %}
                        <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-5 hover:shadow-lg transition border border-gray-200 dark:border-gray-600">
                            <div class="flex justify-between items-start mb-3">
                                <div>
                                    <h3 class="font-bold text-lg text-gray-800 dark:text-white">{{ inv.name }}</h3>
                                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ inv.investment_type }}</p>
                                </div>
                                <span class="px-3 py-1 rounded-full text-xs font-semibold {{ 'bg-green-100 text-green-800' if inv.profit >= 0 else 'bg-red-100 text-red-800' }}">
                                    {{ "%.2f"|format(inv.profit_percent) }}%
                                </span>
                            </div>
                            
                            <div class="space-y-2">
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-600 dark:text-gray-400">Investido:</span>
                                    <span class="font-semibold text-gray-800 dark:text-white">R$ {{ "%.2f"|format(inv.amount) }}</span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-600 dark:text-gray-400">Atual:</span>
                                    <span class="font-bold {{ 'text-green-600' if inv.profit >= 0 else 'text-red-600' }}">
                                        R$ {{ "%.2f"|format(inv.current_value) }}
                                    </span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-600 dark:text-gray-400">Lucro/Prejuízo:</span>
                                    <span class="font-bold {{ 'text-green-600' if inv.profit >= 0 else 'text-red-600' }}">
                                        R$ {{ "%.2f"|format(inv.profit) }}
                                    </span>
                                </div>
                            </div>
                            
                            <!-- Mini Chart -->
                            <div class="mt-4">
                                <canvas id="chart-{{ inv.id }}" height="60"></canvas>
                            </div>
                            
                            <div class="mt-4 flex gap-2">
                                <button onclick="editInvestment('{{ inv.id }}')" 
                                        class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium transition">
                                    Editar
                                </button>
                                <button onclick="deleteInvestment('{{ inv.id }}')" 
                                        class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                    🗑️
                                </button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- Criptomoedas -->
            {% if investments_by_type.cripto %}
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
                <div class="bg-gradient-to-r from-orange-600 to-orange-700 px-6 py-4">
                    <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                        ₿ Criptomoedas ({{ investments_by_type.cripto|length }})
                    </h2>
                </div>
                <div class="p-6">
                    <!-- Similar structure as Ações -->
                </div>
            </div>
            {% endif %}

            <!-- Tesouro Direto -->
            {% if investments_by_type.tesouro %}
            <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
                <div class="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4">
                    <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                        🏛️ Tesouro Direto ({{ investments_by_type.tesouro|length }})
                    </h2>
                </div>
                <div class="p-6">
                    <!-- Similar structure as Ações -->
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>

<!-- Loading Overlay -->
<div id="loadingOverlay" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-2xl p-8 flex flex-col items-center gap-4">
        <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600"></div>
        <p class="text-gray-800 dark:text-white font-semibold text-lg">Atualizando investimentos...</p>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Função para atualizar investimentos
async function updateInvestments() {
    const btn = document.getElementById('updateBtn');
    const text = document.getElementById('updateText');
    const overlay = document.getElementById('loadingOverlay');
    
    // Mostrar loading
    btn.disabled = true;
    text.textContent = 'Atualizando...';
    overlay.classList.remove('hidden');
    
    try {
        const response = await fetch('/admin/update-investments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            text.textContent = 'Atualizado ✅';
            setTimeout(() => location.reload(), 1000);
        } else {
            alert('Erro: ' + (data.error || 'Falha ao atualizar'));
            text.textContent = 'Atualizar Agora';
            btn.disabled = false;
            overlay.classList.add('hidden');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro de conexão. Tente novamente.');
        text.textContent = 'Atualizar Agora';
        btn.disabled = false;
        overlay.classList.add('hidden');
    }
}

// Criar mini charts
{% for inv in all_investments %}
if (document.getElementById('chart-{{ inv.id }}')) {
    new Chart(document.getElementById('chart-{{ inv.id }}'), {
        type: 'line',
        data: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [{
                data: [{{ inv.amount }}, {{ inv.amount * 1.02 }}, {{ inv.amount * 1.05 }}, {{ inv.amount * 1.03 }}, {{ inv.amount * 1.08 }}, {{ inv.current_value }}],
                borderColor: '{{ "#10b981" if inv.profit >= 0 else "#ef4444" }}',
                backgroundColor: '{{ "rgba(16, 185, 129, 0.1)" if inv.profit >= 0 else "rgba(239, 68, 68, 0.1)" }}',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });
}
{% endfor %}
</script>
{% endblock %}
```

---

## 🔐 SISTEMA DE AUTENTICAÇÃO (CÓDIGO COMPLETO)

### 📄 `auth/routes.py`

```python
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid

auth_bp = Blueprint('auth', __name__)

def get_db():
    db = sqlite3.connect('bws_finance.db')
    db.row_factory = sqlite3.Row
    return db

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if not email or not password or not name:
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('auth.register'))
        
        db = get_db()
        
        # Verificar se email já existe
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('Email já cadastrado', 'error')
            return redirect(url_for('auth.register'))
        
        # Criar usuário
        user_id = str(uuid.uuid4())
        tenant_id = 1  # Default tenant
        password_hash = generate_password_hash(password)
        
        db.execute("""
            INSERT INTO users (id, tenant_id, email, password_hash, name, is_admin, active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, tenant_id, email, password_hash, name, 0, 1))
        
        db.commit()
        db.close()
        
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email e senha são obrigatórios', 'error')
            return redirect(url_for('auth.login'))
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ? AND active = 1', (email,)).fetchone()
        db.close()
        
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Email ou senha incorretos', 'error')
            return redirect(url_for('auth.login'))
        
        # Criar sessão
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        session['is_admin'] = user['is_admin']
        
        flash(f'Bem-vindo, {user["name"]}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da conta', 'success')
    return redirect(url_for('auth.login'))
```

### 📄 `auth/__init__.py`

```python
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from . import routes
```

### 📄 Integração no `app.py`

```python
# Adicionar após os outros blueprints
from auth import auth_bp
app.register_blueprint(auth_bp)

# Middleware de autenticação
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Faça login para acessar esta página', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Aplicar em todas as rotas protegidas
@app.route('/dashboard')
@login_required
def dashboard():
    # ... código existente ...
```

---

## 🌐 INTEGRAÇÃO COM APIs (MELHORIAS)

### Adicionar cache para evitar rate limit:

```python
import time
from functools import lru_cache

# Cache por 5 minutos
@lru_cache(maxsize=100)
def get_stock_price_cached(ticker, timestamp):
    """timestamp usado para invalidar cache"""
    return get_stock_price(ticker)

# Usar assim:
current_timestamp = int(time.time() / 300)  # Muda a cada 5 min
price = get_stock_price_cached('PETR4', current_timestamp)
```

---

## 📁 ESTRUTURA FINAL DE ARQUIVOS

```
bwsfinnance v02 final - 2025-10-18_12-48/
├── nik0finance-base/
│   ├── app.py ✅
│   ├── scheduler.py ✅
│   ├── auth/
│   │   ├── __init__.py ⭐ CRIAR
│   │   └── routes.py ⭐ CRIAR
│   ├── services/
│   │   └── investment_updater.py ✅
│   ├── routes/
│   │   ├── accounts.py ✅
│   │   ├── investments.py ✅
│   │   ├── installments.py ✅
│   │   └── recurring.py ✅
│   ├── templates/
│   │   ├── base.html ✅
│   │   ├── dashboard.html ✅ (corrigir)
│   │   ├── investments.html ⭐ SUBSTITUIR pelo novo layout
│   │   ├── auth/
│   │   │   ├── login.html ⭐ CRIAR
│   │   │   └── register.html ⭐ CRIAR
│   │   └── error.html ⭐ CRIAR
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css ⭐ CRIAR
│   │   └── js/
│   │       └── investments.js ⭐ CRIAR
│   ├── logs/
│   │   └── investments.log ✅
│   └── bws_finance.db ✅
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### 1. Dashboard
- [ ] Carrega sem erro 500
- [ ] Mostra card de investimentos
- [ ] Botão de atualizar funciona
- [ ] Loading aparece durante atualização
- [ ] Dados do usuário logado aparecem

### 2. Tela de Investimentos
- [ ] Layout moderno carrega
- [ ] Cards por tipo (Ações, Cripto, Tesouro)
- [ ] Mini gráficos aparecem (Chart.js)
- [ ] Cores dinâmicas (verde/vermelho) funcionam
- [ ] Botões de editar/deletar funcionam

### 3. Sistema de Login
- [ ] /auth/register cria usuário
- [ ] Senha é hasheada (bcrypt)
- [ ] /auth/login autentica
- [ ] Sessão persiste entre requests
- [ ] Logout limpa sessão
- [ ] Rotas protegidas redirecionam para login

### 4. Atualização de Investimentos
- [ ] Scheduler roda às 08:00
- [ ] Atualização manual funciona
- [ ] APIs retornam dados (Yahoo, CoinGecko)
- [ ] Logs são gerados corretamente
- [ ] Erros de API são capturados e logados

### 5. Responsividade
- [ ] Mobile (< 768px) layout OK
- [ ] Tablet (768-1024px) layout OK
- [ ] Desktop (> 1024px) layout OK
- [ ] Dark mode funciona

---

## 🚀 ENTREGA ESPERADA

**Ao finalizar, o sistema deve:**

1. ✅ **Dashboard online** - sem erros, com dados reais
2. ✅ **Login funcional** - registro, login, logout, sessões
3. ✅ **Tela de investimentos moderna** - layout do código acima
4. ✅ **Gráficos funcionando** - Chart.js renderizando
5. ✅ **Atualização automática** - scheduler + manual
6. ✅ **APIs integradas** - Yahoo, CoinGecko, Tesouro
7. ✅ **Logs persistentes** - investments.log atualizado
8. ✅ **100% compatível** - código existente funciona

---

## 🧱 TECNOLOGIAS OBRIGATÓRIAS

- **Backend**: Python 3.11, Flask 3.1.2, SQLite
- **Auth**: Flask sessions + bcrypt
- **Frontend**: HTML5, Tailwind CSS 3.x, Chart.js 4.x
- **APIs**: yfinance, requests, CoinGecko API
- **Scheduler**: APScheduler 3.11.0

---

## 🔥 PRONTO PARA A CLOUD!

Cole este prompt completo no **Gemini ou outro modelo** e peça:

> "Implemente tudo acima. Corrija o dashboard, crie o sistema de login, aplique o novo layout de investimentos com gráficos, e garanta 100% de compatibilidade com o código existente."

**🎯 Resultado esperado**: Sistema completo, profissional e pronto para produção em até 2 horas de execução pela IA.
