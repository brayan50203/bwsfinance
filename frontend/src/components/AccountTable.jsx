import React from 'react';

export default function AccountTable({ accounts = [], loading, onDelete, onRefresh }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold">Lista de Contas</h3>
        <div className="flex items-center gap-2">
          <button onClick={onRefresh} className="text-sm px-3 py-1 bg-gray-100 rounded">Atualizar</button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Banco / Carteira</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Saldo Atual</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Última Atualização</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Ações</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {loading && (
              <tr><td colSpan={5} className="px-4 py-6 text-center">Carregando...</td></tr>
            )}
            {!loading && accounts.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-500">Nenhuma conta encontrada</td></tr>
            )}
            {!loading && accounts.map(account => (
              <tr key={account.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-md bg-gray-100 flex items-center justify-center text-sm font-bold">
                      {/* small logo placeholder */}
                      {account.name?.slice(0,2).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{account.name}</div>
                      <div className="text-xs text-gray-500">ID: {account.id}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{account.type}</td>
                <td className="px-4 py-3 text-right font-bold">R$ {parseFloat(account.current_balance || 0).toFixed(2)}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{account.updated_at || account.updated || '-'}</td>
                <td className="px-4 py-3 text-right text-sm">
                  <button className="text-blue-600 hover:underline mr-3">Editar</button>
                  <button onClick={() => onDelete(account.id)} className="text-red-600 hover:underline">Excluir</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
