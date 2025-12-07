import React, { useEffect, useState } from 'react';

export default function ContasHomeStyle() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [chartData, setChartData] = useState({ labels: [], values: [] });

  useEffect(() => {
    fetchAccounts();
    fetchTransactions();
  }, []);

  async function fetchAccounts() {
    setLoading(true);
    try {
      const res = await fetch('/api/accounts');
      const data = await res.json();
      setAccounts(data.accounts || data || []);
    } catch (err) {
      console.error(err);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }

  async function fetchTransactions() {
    try {
      const res = await fetch('/api/transactions?limit=10');
      const data = await res.json();
      setTransactions(data.transactions || data || []);
      
      // Gerar dados para gráfico
      const accountBalances = {};
      accounts.forEach(acc => {
        accountBalances[acc.name] = parseFloat(acc.current_balance || 0);
      });
      
      const labels = Object.keys(accountBalances);
      const values = Object.values(accountBalances);
      setChartData({ labels, values });
    } catch (err) {
      console.error(err);
      setTransactions([]);
    }
  }

  const totalBalance = accounts.reduce((sum, acc) => 
    sum + (parseFloat(acc.current_balance) || 0), 0
  );

  function getBankColor(name) {
    const n = name?.toLowerCase() || '';
    if (n.includes('itau') || n.includes('itaú')) return 'bg-gradient-to-br from-orange-500 to-orange-600';
    if (n.includes('bradesco')) return 'bg-gradient-to-br from-red-600 to-red-700';
    if (n.includes('santander')) return 'bg-gradient-to-br from-red-500 to-red-600';
    if (n.includes('bb') || n.includes('banco do brasil')) return 'bg-gradient-to-br from-yellow-400 to-yellow-500';
    if (n.includes('nubank')) return 'bg-gradient-to-br from-purple-600 to-purple-700';
    if (n.includes('inter')) return 'bg-gradient-to-br from-orange-500 to-orange-600';
    if (n.includes('c6')) return 'bg-gradient-to-br from-gray-800 to-black';
    if (n.includes('picpay')) return 'bg-gradient-to-br from-green-500 to-green-600';
    if (n.includes('mercado')) return 'bg-gradient-to-br from-blue-500 to-blue-600';
    return 'bg-gradient-to-br from-slate-600 to-slate-700';
  }

  function getBankInitials(name) {
    if (!name) return '$$';
    const words = name.trim().split(' ');
    if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
    return name.substring(0, 2).toUpperCase();
  }

  async function handleAddAccount(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {
      name: form.accountName.value,
      type: form.accountType.value,
      initial_balance: parseFloat(form.balance.value || 0),
      note: form.note.value
    };
    
    try {
      const res = await fetch('/api/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setShowModal(false);
        form.reset();
        fetchAccounts();
      } else {
        const data = await res.json();
        alert(data.message || 'Erro ao criar conta');
      }
    } catch (err) {
      alert('Erro: ' + err.message);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar + Header inspirado no HomeApplication */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">₿</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Minhas Contas</h1>
              <p className="text-sm text-gray-500">Gerencie suas contas bancárias</p>
            </div>
          </div>
          <button 
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg flex items-center gap-2"
          >
            <span className="text-xl">+</span>
            Nova Conta
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Card de resumo - estilo HomeApplication */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Saldo Total</p>
              <h2 className="text-5xl font-bold text-gray-800">
                R$ {totalBalance.toFixed(2)}
              </h2>
              <p className="text-sm text-gray-500 mt-2">{accounts.length} contas cadastradas</p>
            </div>
            <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center">
              <span className="text-5xl">💳</span>
            </div>
          </div>
        </div>

        {/* Gráfico de distribuição e histórico recente */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Gráfico de barras simples */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Distribuição por Conta</h3>
            <div className="space-y-3">
              {accounts.map(acc => {
                const balance = parseFloat(acc.current_balance || 0);
                const percentage = totalBalance > 0 ? (balance / totalBalance) * 100 : 0;
                return (
                  <div key={acc.id}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{acc.name}</span>
                      <span className="text-sm font-bold text-gray-800">R$ {balance.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div 
                        className={`h-full ${getBankColor(acc.name).replace('bg-gradient-to-br', 'bg-gradient-to-r')}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Últimas transações */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Últimas Movimentações</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {transactions.length > 0 ? transactions.slice(0, 5).map((tx, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      tx.type === 'receita' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                    }`}>
                      {tx.type === 'receita' ? '↑' : '↓'}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800 text-sm">{tx.description || tx.category || 'Transação'}</p>
                      <p className="text-xs text-gray-500">{tx.date || new Date().toLocaleDateString()}</p>
                    </div>
                  </div>
                  <p className={`font-bold ${tx.type === 'receita' ? 'text-green-600' : 'text-red-600'}`}>
                    {tx.type === 'receita' ? '+' : '-'} R$ {parseFloat(tx.amount || 0).toFixed(2)}
                  </p>
                </div>
              )) : (
                <div className="text-center py-8 text-gray-400">
                  <p>Nenhuma transação recente</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Grid de cartões - inspirado nos cards do HomeApplication */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-500">Carregando contas...</p>
            </div>
          </div>
        ) : accounts.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-100">
            <div className="w-32 h-32 bg-gray-100 rounded-full mx-auto mb-6 flex items-center justify-center">
              <span className="text-6xl">🏦</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Nenhuma conta cadastrada</h3>
            <p className="text-gray-500 mb-8 max-w-md mx-auto">
              Comece adicionando sua primeira conta bancária para gerenciar suas finanças
            </p>
            <button 
              onClick={() => setShowModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all"
            >
              Adicionar Primeira Conta
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {accounts.map(account => (
              <div 
                key={account.id}
                onClick={() => setSelectedAccount(account)}
                className="group cursor-pointer"
              >
                {/* Card estilo cartão de crédito - inspirado no HomeApplication */}
                <div className={`${getBankColor(account.name)} rounded-2xl p-6 text-white shadow-xl hover:shadow-2xl transition-all transform hover:scale-105 relative overflow-hidden`}>
                  {/* Padrão de fundo sutil */}
                  <div className="absolute top-0 right-0 w-40 h-40 bg-white opacity-5 rounded-full -mr-20 -mt-20"></div>
                  <div className="absolute bottom-0 left-0 w-32 h-32 bg-black opacity-10 rounded-full -ml-16 -mb-16"></div>
                  
                  <div className="relative z-10">
                    {/* Header do card */}
                    <div className="flex items-start justify-between mb-8">
                      <div>
                        <p className="text-xs font-semibold opacity-80 uppercase tracking-wider mb-1">
                          {account.type || 'Conta'}
                        </p>
                        <h3 className="text-xl font-bold">{account.name}</h3>
                      </div>
                      <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                        <span className="text-lg font-bold">{getBankInitials(account.name)}</span>
                      </div>
                    </div>

                    {/* Chip do cartão */}
                    <div className="mb-6">
                      <div className="w-12 h-9 bg-yellow-300 bg-opacity-40 rounded-md flex items-center justify-center backdrop-blur-sm">
                        <div className="w-8 h-6 border border-white border-opacity-40 rounded-sm"></div>
                      </div>
                    </div>

                    {/* Saldo */}
                    <div>
                      <p className="text-xs font-semibold opacity-80 uppercase tracking-wider mb-1">Saldo Disponível</p>
                      <p className="text-3xl font-bold tracking-wide">
                        R$ {parseFloat(account.current_balance || 0).toFixed(2)}
                      </p>
                    </div>

                    {/* Footer do card */}
                    <div className="mt-6 pt-4 border-t border-white border-opacity-20 flex items-center justify-between">
                      <p className="text-xs opacity-70">ID: {account.id}</p>
                      {account.active === 0 ? (
                        <span className="px-2 py-1 bg-red-500 bg-opacity-30 rounded text-xs font-semibold">Inativa</span>
                      ) : (
                        <span className="px-2 py-1 bg-green-400 bg-opacity-30 rounded text-xs font-semibold">Ativa</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Info adicional abaixo do card */}
                <div className="mt-3 px-2">
                  <div className="flex items-center justify-between text-sm">
                    <button className="text-blue-600 hover:text-blue-800 font-semibold hover:underline">
                      Ver Detalhes
                    </button>
                    <button className="text-gray-500 hover:text-gray-700">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal - estilo clean inspirado no HomeApplication */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-xl transform transition-all animate-fadeIn">
            {/* Header do modal */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-3xl">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold">Adicionar Nova Conta</h3>
                  <p className="text-blue-100 text-sm mt-1">Preencha os dados abaixo</p>
                </div>
                <button 
                  onClick={() => setShowModal(false)}
                  className="w-8 h-8 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full flex items-center justify-center transition-all"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            {/* Form */}
            <form onSubmit={handleAddAccount} className="p-6 space-y-5">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Nome da Conta <span className="text-red-500">*</span>
                </label>
                <input 
                  name="accountName"
                  required
                  placeholder="Ex: Nubank, Itaú, Carteira..."
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Tipo da Conta <span className="text-red-500">*</span>
                </label>
                <select 
                  name="accountType"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all"
                >
                  <option value="Corrente">Conta Corrente</option>
                  <option value="Poupança">Poupança</option>
                  <option value="Investimento">Investimento</option>
                  <option value="Carteira">Carteira Digital</option>
                  <option value="Outro">Outro</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  Saldo Inicial <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 font-semibold">R$</span>
                  <input 
                    name="balance"
                    type="number"
                    step="0.01"
                    required
                    defaultValue="0.00"
                    className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Observação</label>
                <textarea 
                  name="note"
                  rows={3}
                  placeholder="Adicione uma observação (opcional)"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all resize-none"
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button 
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-xl font-bold text-gray-700 hover:bg-gray-50 transition-all"
                >
                  Cancelar
                </button>
                <button 
                  type="submit"
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-bold hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all"
                >
                  Adicionar Conta
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal para conta selecionada */}
      {selectedAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl transform transition-all">
            <div className={`${getBankColor(selectedAccount.name)} text-white p-6 rounded-t-3xl`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold">{selectedAccount.name}</h3>
                <button 
                  onClick={() => setSelectedAccount(null)}
                  className="w-8 h-8 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full flex items-center justify-center"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p className="text-3xl font-bold">R$ {parseFloat(selectedAccount.current_balance || 0).toFixed(2)}</p>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm text-gray-500 mb-1">Tipo</p>
                  <p className="font-bold text-gray-800">{selectedAccount.type}</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-sm text-gray-500 mb-1">Status</p>
                  <p className="font-bold text-gray-800">{selectedAccount.active ? 'Ativa' : 'Inativa'}</p>
                </div>
              </div>

              {/* Histórico da conta */}
              <div className="bg-gray-50 rounded-xl p-4">
                <h4 className="font-bold text-gray-800 mb-3">Histórico Recente</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {transactions.filter(tx => tx.account_id === selectedAccount.id).length > 0 ? (
                    transactions.filter(tx => tx.account_id === selectedAccount.id).slice(0, 5).map((tx, idx) => (
                      <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-200 last:border-0">
                        <div>
                          <p className="text-sm font-semibold text-gray-700">{tx.description || tx.category}</p>
                          <p className="text-xs text-gray-500">{tx.date}</p>
                        </div>
                        <p className={`text-sm font-bold ${tx.type === 'receita' ? 'text-green-600' : 'text-red-600'}`}>
                          {tx.type === 'receita' ? '+' : '-'} R$ {parseFloat(tx.amount || 0).toFixed(2)}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-4">Sem transações nesta conta</p>
                  )}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700">
                  Editar
                </button>
                <button className="flex-1 px-6 py-3 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700">
                  Excluir
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
