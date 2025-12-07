#!/usr/bin/env python
# -*- coding: utf-8 -*-

template_content = '''{% extends "base.html" %}

{% block title %}Importar Extrato{% endblock %}

{% block content %}
<div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
    <div class="max-w-2xl mx-auto">
        <div class="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <h1 class="text-3xl font-bold text-gray-800 mb-6">📊 Importar Extrato Bancário</h1>
            
            <form id="importForm" class="space-y-6">
                <div class="space-y-2">
                    <label class="block text-sm font-semibold text-gray-700">Tipo de Importação</label>
                    <select id="importType" name="import_type" required class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all">
                        <option value="account">Importar para Conta Bancária</option>
                        <option value="card">Importar para Cartão de Crédito</option>
                    </select>
                </div>

                <div id="accountSelectDiv" class="space-y-2">
                    <label class="block text-sm font-semibold text-gray-700">Conta Bancária</label>
                    <select id="accountSelect" name="account_id" class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all">
                        <option value="">Carregando contas...</option>
                    </select>
                </div>

                <div id="cardSelectDiv" class="space-y-2" style="display: none;">
                    <label class="block text-sm font-semibold text-gray-700">Cartão de Crédito</label>
                    <select id="cardSelect" name="card_id" class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all">
                        <option value="">Carregando cartões...</option>
                    </select>
                </div>

                <div class="space-y-2">
                    <label class="block text-sm font-semibold text-gray-700">Arquivo do Extrato</label>
                    <div class="relative">
                        <input type="file" name="file" id="fileInput" required accept=".csv,.ofx,.pdf" 
                               class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-green-50 file:text-green-700 file:font-semibold hover:file:bg-green-100 cursor-pointer">
                    </div>
                    <p class="text-xs text-gray-500 mt-1">Formatos aceitos: CSV, OFX, PDF</p>
                </div>

                <div class="flex items-center space-x-3 p-4 bg-blue-50 rounded-xl">
                    <input type="checkbox" id="autoCateg" name="auto_categorize" checked 
                           class="w-5 h-5 text-green-500 rounded focus:ring-2 focus:ring-green-200">
                    <label for="autoCateg" class="text-sm font-medium text-gray-700">Categorizar automaticamente</label>
                </div>

                <button type="submit" id="importBtn" 
                        class="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl hover:from-green-600 hover:to-emerald-600 transform hover:-translate-y-0.5 transition-all duration-200">
                    <span id="btnText">📥 Importar Extrato</span>
                    <span id="btnLoading" style="display: none;">⏳ Importando...</span>
                </button>
            </form>

            <div id="result" class="mt-6 p-4 rounded-xl hidden"></div>
        </div>
    </div>
</div>

<script>
let accounts = [];
let cards = [];

document.getElementById('importType').addEventListener('change', function() {
    const isCard = this.value === 'card';
    document.getElementById('accountSelectDiv').style.display = isCard ? 'none' : 'block';
    document.getElementById('cardSelectDiv').style.display = isCard ? 'block' : 'none';
    if (isCard) {
        document.getElementById('accountSelect').removeAttribute('required');
        document.getElementById('cardSelect').setAttribute('required', 'required');
    } else {
        document.getElementById('cardSelect').removeAttribute('required');
        document.getElementById('accountSelect').setAttribute('required', 'required');
    }
});

fetch('/api/accounts-list')
    .then(r => r.json())
    .then(data => {
        accounts = data.accounts || [];
        const sel = document.getElementById('accountSelect');
        sel.innerHTML = '<option value="">Selecione uma conta</option>';
        accounts.forEach(acc => {
            sel.innerHTML += `<option value="${acc.id}">${acc.name} - ${acc.bank}</option>`;
        });
    })
    .catch(e => console.error('Erro carregando contas:', e));

fetch('/api/cards-list')
    .then(r => r.json())
    .then(data => {
        cards = data.cards || [];
        const sel = document.getElementById('cardSelect');
        sel.innerHTML = '<option value="">Selecione um cartão</option>';
        cards.forEach(card => {
            sel.innerHTML += `<option value="${card.id}">${card.name} - Final ${card.last4}</option>`;
        });
    })
    .catch(e => console.error('Erro carregando cartões:', e));

document.getElementById('importForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btn = document.getElementById('importBtn');
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    const result = document.getElementById('result');
    
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files || !fileInput.files[0]) {
        result.className = 'mt-6 p-4 rounded-xl bg-red-50 border-2 border-red-200';
        result.innerHTML = '<p class="text-red-700 font-semibold">❌ Selecione um arquivo</p>';
        result.classList.remove('hidden');
        return;
    }
    
    const importType = document.getElementById('importType').value;
    const selectedId = importType === 'card' 
        ? document.getElementById('cardSelect').value 
        : document.getElementById('accountSelect').value;
    
    if (!selectedId) {
        result.className = 'mt-6 p-4 rounded-xl bg-red-50 border-2 border-red-200';
        result.innerHTML = `<p class="text-red-700 font-semibold">❌ Selecione ${importType === 'card' ? 'um cartão' : 'uma conta'}</p>`;
        result.classList.remove('hidden');
        return;
    }
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('import_type', importType);
    if (importType === 'card') {
        formData.append('card_id', selectedId);
    } else {
        formData.append('account_id', selectedId);
    }
    formData.append('auto_categorize', document.getElementById('autoCateg').checked ? 'true' : 'false');
    
    try {
        const response = await fetch('/api/import/manual', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            result.className = 'mt-6 p-4 rounded-xl bg-green-50 border-2 border-green-200';
            result.innerHTML = `<p class="text-green-700 font-semibold">✅ ${data.message || 'Importado com sucesso!'}</p>`;
        } else {
            result.className = 'mt-6 p-4 rounded-xl bg-red-50 border-2 border-red-200';
            result.innerHTML = `<p class="text-red-700 font-semibold">❌ ${data.message || 'Erro na importação'}</p>`;
        }
        result.classList.remove('hidden');
    } catch (error) {
        result.className = 'mt-6 p-4 rounded-xl bg-red-50 border-2 border-red-200';
        result.innerHTML = `<p class="text-red-700 font-semibold">❌ Erro: ${error.message}</p>`;
        result.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
});
</script>
{% endblock %}'''

with open('templates/importar_extrato.html', 'w', encoding='utf-8') as f:
    f.write(template_content)

print("✅ Template criado com sucesso!")
