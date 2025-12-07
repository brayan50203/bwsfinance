import React, { useState } from 'react';

export default function AccountModal({ open, onClose, onSave }) {
  const [name, setName] = useState('');
  const [type, setType] = useState('Corrente');
  const [initialBalance, setInitialBalance] = useState('0.00');
  const [note, setNote] = useState('');

  if (!open) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    const payload = { name, type, initial_balance: parseFloat(initialBalance || 0), note };
    await onSave(payload);
    setName(''); setType('Corrente'); setInitialBalance('0.00'); setNote('');
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">Nova Conta</h3>
          <button onClick={onClose} className="text-gray-500">✖</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700">Nome da Conta</label>
            <input value={name} onChange={e=>setName(e.target.value)} required className="mt-1 block w-full border rounded px-3 py-2" />
          </div>
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700">Tipo</label>
            <select value={type} onChange={e=>setType(e.target.value)} className="mt-1 block w-full border rounded px-3 py-2">
              <option>Corrente</option>
              <option>Poupança</option>
              <option>Investimento</option>
              <option>Carteira</option>
              <option>Outro</option>
            </select>
          </div>
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700">Saldo Inicial</label>
            <input value={initialBalance} onChange={e=>setInitialBalance(e.target.value)} required className="mt-1 block w-full border rounded px-3 py-2" />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">Observação</label>
            <textarea value={note} onChange={e=>setNote(e.target.value)} className="mt-1 block w-full border rounded px-3 py-2" />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded bg-gray-200">Cancelar</button>
            <button type="submit" className="px-4 py-2 rounded bg-green-600 text-white">Salvar</button>
          </div>
        </form>
      </div>
    </div>
  );
}
