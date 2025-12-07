import React, { useEffect, useState } from 'react';
import { 
  BanknotesIcon, 
  PlusIcon, 
  MagnifyingGlassIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

export default function ContasV2() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // grid | list
  const [hideBalances, setHideBalances] = useState(false);

  useEffect(() => {
    fetchAccounts();
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

  const filteredAccounts = accounts.filter(acc => 
    acc.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalBalance = filteredAccounts.reduce((sum, acc) => 
    sum + (parseFloat(acc.current_balance) || 0), 0
  );

  const activeAccounts = filteredAccounts.filter(a => a.active !== 0).length;
  const positiveAccounts = filteredAccounts.filter(a => parseFloat(a.current_balance || 0) > 0).length;
  const negativeAccounts = filteredAccounts.filter(a => parseFloat(a.current_balance || 0) < 0).length;

  function getBankIcon(name) {
    const n = name?.toLowerCase() || '';
    if (n.includes('itau') || n.includes('itaú')) return '🟠';
    if (n.includes('bradesco')) return '🔴';
    if (n.includes('santander')) return '🔴';
    if (n.includes('bb') || n.includes('banco do brasil')) return '🟡';
    if (n.includes('nubank')) return '🟣';
    if (n.includes('inter')) return '🟠';
    if (n.includes('c6')) return '⚫';
    if (n.includes('picpay')) return '🟢';
    if (n.includes('mercado')) return '🔵';
    return '💳';
  }

  async function handleAddAccount(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {
      name: form.name.value,
      type: form.type.value,
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                <BanknotesIcon className="w-10 h-10 text-blue-600" />
                Minhas Contas
              </h1>
              <p className="text-gray-500 mt-1">Gerencie todas as suas contas em um só lugar</p>
            </div>
            <button 
              onClick={() => setShowModal(true)}
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
            >
              <PlusIcon className="w-5 h-5" />
              Nova Conta
            </button>
          </div>

          {/* Search and filters */}
          <div className="flex items-center gap-4 bg-white rounded-xl p-4 shadow-sm">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="text"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Buscar conta..."
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                {viewMode === 'grid' ? '📋 Lista' : '🔲 Grade'}
              </button>
              <button 
                onClick={() => setHideBalances(!hideBalances)}
                className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-2"
              >
                {hideBalances ? <EyeSlashIcon className="w-5 h-5" /> : <EyeIcon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium opacity-90">Saldo Total</span>
              <BanknotesIcon className="w-6 h-6 opacity-75" />
            </div>
            <p className="text-3xl font-bold">
              {hideBalances ? '•••••' : `R$ ${totalBalance.toFixed(2)}`}
            </p>
            <p className="text-xs opacity-75 mt-1">{activeAccounts} contas ativas</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium opacity-90">Saldo Positivo</span>
              <ArrowTrendingUpIcon className="w-6 h-6 opacity-75" />
            </div>
            <p className="text-3xl font-bold">{positiveAccounts}</p>
            <p className="text-xs opacity-75 mt-1">contas no azul</p>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium opacity-90">Saldo Negativo</span>
              <ArrowTrendingDownIcon className="w-6 h-6 opacity-75" />
            </div>
            <p className="text-3xl font-bold">{negativeAccounts}</p>
            <p className="text-xs opacity-75 mt-1">contas no vermelho</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium opacity-90">Total de Contas</span>
              <span className="text-2xl opacity-75">💳</span>
            </div>
            <p className="text-3xl font-bold">{filteredAccounts.length}</p>
            <p className="text-xs opacity-75 mt-1">cadastradas</p>
          </div>
        </div>

        {/* Accounts Grid/List */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAccounts.map(account => (
              <div key={account.id} className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all border border-gray-100">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">{getBankIcon(account.name)}</div>
                    <div>
                      <h3 className="font-bold text-gray-800">{account.name}</h3>
                      <p className="text-xs text-gray-500">{account.type}</p>
                    </div>
                  </div>
                  {account.active === 0 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">Inativa</span>
                  )}
                </div>
                
                <div className="border-t border-gray-100 pt-4">
                  <p className="text-xs text-gray-500 mb-1">Saldo Atual</p>
                  <p className={`text-2xl font-bold ${parseFloat(account.current_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {hideBalances ? '•••••' : `R$ ${parseFloat(account.current_balance || 0).toFixed(2)}`}
                  </p>
                </div>

                <div className="flex items-center gap-2 mt-4">
                  <button className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg text-sm font-medium hover:bg-blue-100">
                    Ver Detalhes
                  </button>
                  <button className="px-3 py-2 bg-gray-50 text-gray-600 rounded-lg text-sm hover:bg-gray-100">
                    ⋮
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Conta</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase">Tipo</th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Saldo</th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-gray-600 uppercase">Status</th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredAccounts.map(account => (
                  <tr key={account.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{getBankIcon(account.name)}</span>
                        <div>
                          <p className="font-semibold text-gray-800">{account.name}</p>
                          <p className="text-xs text-gray-500">ID: {account.id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{account.type}</td>
                    <td className={`px-6 py-4 text-right font-bold ${parseFloat(account.current_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {hideBalances ? '•••••' : `R$ ${parseFloat(account.current_balance || 0).toFixed(2)}`}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${account.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                        {account.active ? 'Ativa' : 'Inativa'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium mr-3">Editar</button>
                      <button className="text-red-600 hover:text-red-800 text-sm font-medium">Excluir</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {filteredAccounts.length === 0 && !loading && (
          <div className="bg-white rounded-2xl p-12 text-center shadow-lg">
            <div className="text-6xl mb-4">🏦</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Nenhuma conta encontrada</h3>
            <p className="text-gray-500 mb-6">Adicione sua primeira conta para começar</p>
            <button 
              onClick={() => setShowModal(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700"
            >
              Adicionar Conta
            </button>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg animate-fadeIn">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-2xl font-bold text-gray-800">Nova Conta</h3>
              <p className="text-gray-500 text-sm mt-1">Preencha os dados da nova conta</p>
            </div>
            
            <form onSubmit={handleAddAccount} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Nome da Conta *</label>
                <input 
                  name="name"
                  required
                  placeholder="Ex: Nubank, Itaú, Bradesco..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Tipo *</label>
                <select 
                  name="type"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option>Corrente</option>
                  <option>Poupança</option>
                  <option>Investimento</option>
                  <option>Carteira Digital</option>
                  <option>Outro</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Saldo Inicial *</label>
                <input 
                  name="balance"
                  type="number"
                  step="0.01"
                  required
                  defaultValue="0.00"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Observação</label>
                <textarea 
                  name="note"
                  rows={3}
                  placeholder="Adicione uma observação (opcional)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button 
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-6 py-3 border border-gray-300 rounded-xl font-semibold text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button 
                  type="submit"
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 shadow-lg"
                >
                  Salvar Conta
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
