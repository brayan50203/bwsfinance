import React, { useEffect, useState } from 'react';
import AccountCard from '../components/AccountCard';
import AccountTable from '../components/AccountTable';
import AccountModal from '../components/AccountModal';

export default function Contas() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);

  useEffect(() => {
    fetchAccounts();
  }, []);

  async function fetchAccounts() {
    setLoading(true);
    try {
      const res = await fetch('/api/accounts');
      const json = await res.json();
      setAccounts(json.accounts || json || []);
    } catch (err) {
      console.error('Erro ao buscar contas', err);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }

  function computeTotals() {
    const total = accounts.reduce((s, a) => s + (parseFloat(a.current_balance) || 0), 0);
    const banks = accounts.filter(a => /bank|banco|itau|bradesco|santander|bb|nubank|inter|c6/i.test(a.name)).length;
    const wallets = accounts.filter(a => /wallet|carteira|picpay|mercado pago|mercado/i.test(a.name) || /carteira/i.test(a.type)).length;
    const inactive = accounts.filter(a => a.active === 0 || a.active === false || a.active === '0').length;
    return { total, banks, wallets, inactive };
  }

  async function handleCreate(payload) {
    try {
      const res = await fetch('/api/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok) {
        setShowModal(false);
        fetchAccounts();
      } else {
        alert(data.message || 'Erro ao criar conta');
      }
    } catch (err) {
      alert('Erro ao criar conta: ' + err.message);
    }
  }

  async function handleDelete(id) {
    if (!confirm('Tem certeza que deseja excluir essa conta?')) return;
    try {
      const res = await fetch(`/api/accounts/${id}`, { method: 'DELETE' });
      if (res.ok) fetchAccounts();
      else alert('Erro ao excluir');
    } catch (err) {
      alert('Erro ao excluir: ' + err.message);
    }
  }

  const totals = computeTotals();

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">💳 Contas</h1>
          <p className="text-sm text-gray-500">Gerencie suas contas bancárias e carteiras digitais.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <select value={year} onChange={e => setYear(e.target.value)} className="border rounded px-3 py-2">
              {Array.from({ length: 5 }).map((_, i) => {
                const y = new Date().getFullYear() - i;
                return <option key={y} value={y}>{y}</option>;
              })}
            </select>
            <select value={month} onChange={e => setMonth(e.target.value)} className="border rounded px-3 py-2">
              {Array.from({ length: 12 }).map((_, i) => <option key={i+1} value={i+1}>{i+1}</option>)}
            </select>
            <button onClick={() => {/* no-op filter for now */}} className="bg-blue-600 text-white px-3 py-2 rounded">Filtrar</button>
          </div>
          <button onClick={() => setShowModal(true)} className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">+ Adicionar Conta</button>
        </div>
      </div>

      {/* Cards resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
        <AccountCard title="Saldo Total" value={`R$ ${totals.total.toFixed(2)}`} color="purple" icon="wallet" />
        <AccountCard title="Contas Bancárias" value={`${totals.banks} contas`} color="blue" icon="banknote" />
        <AccountCard title="Carteiras Digitais" value={`${totals.wallets} carteiras`} color="green" icon="smartphone" />
        <AccountCard title="Contas Inativas" value={`${totals.inactive} conta(s)`} color="red" icon="x-circle" />
      </div>

      {/* Tabela de contas */}
      <div className="bg-white shadow rounded-xl p-4">
        <AccountTable accounts={accounts} loading={loading} onDelete={handleDelete} onRefresh={fetchAccounts} />
      </div>

      <AccountModal open={showModal} onClose={() => setShowModal(false)} onSave={handleCreate} />
    </div>
  );
}
