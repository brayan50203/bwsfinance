import React, { useState, useEffect } from 'react';

export default function ImportarExtrato() {
  const [file, setFile] = useState(null);
  const [accountId, setAccountId] = useState('');
  const [accounts, setAccounts] = useState([]);
  const [autoCategorize, setAutoCategorize] = useState(true);
  const [loading, setLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [importHistory, setImportHistory] = useState([]);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Buscar contas ao carregar
  useEffect(() => {
    fetchAccounts();
    fetchImportHistory();
  }, []);

  async function fetchAccounts() {
    try {
      const res = await fetch('/api/accounts');
      const data = await res.json();
      setAccounts(data.accounts || []);
      if (data.accounts?.length > 0) {
        setAccountId(data.accounts[0].id);
      }
    } catch (err) {
      console.error('Erro ao buscar contas:', err);
    }
  }

  async function fetchImportHistory() {
    try {
      const res = await fetch('/api/import/status');
      const data = await res.json();
      if (data.success) {
        setImportHistory(data.imports || []);
      }
    } catch (err) {
      console.error('Erro ao buscar histórico:', err);
    }
  }

  function handleFileChange(e) {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validTypes = ['text/csv', 'application/vnd.ofx', 'application/pdf', 'text/plain'];
      const validExtensions = ['.csv', '.ofx', '.pdf'];
      const fileExtension = selectedFile.name.toLowerCase().slice(selectedFile.name.lastIndexOf('.'));
      
      if (validExtensions.includes(fileExtension)) {
        setFile(selectedFile);
        setMessage({ type: '', text: '' });
      } else {
        setMessage({ type: 'error', text: 'Formato inválido. Use: .csv, .ofx ou .pdf' });
        setFile(null);
      }
    }
  }

  async function handlePreview() {
    if (!file) {
      setMessage({ type: 'error', text: 'Selecione um arquivo primeiro' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/import/preview', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      if (data.success) {
        setPreviewData(data);
        setPreviewMode(true);
        setMessage({ 
          type: 'success', 
          text: `✅ Arquivo analisado: ${data.total} transações encontradas` 
        });
      } else {
        setMessage({ type: 'error', text: data.error || 'Erro ao processar arquivo' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao conectar com o servidor' });
    } finally {
      setLoading(false);
    }
  }

  async function handleImport() {
    if (!file || !accountId) {
      setMessage({ type: 'error', text: 'Selecione um arquivo e uma conta' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('account_id', accountId);
    formData.append('auto_categorize', autoCategorize);

    try {
      const res = await fetch('/api/import/manual', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      if (data.success) {
        setMessage({ type: 'success', text: data.message });
        setFile(null);
        setPreviewMode(false);
        setPreviewData(null);
        fetchImportHistory();
        
        // Limpar input file
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.value = '';
        
        // Recarregar página após 2 segundos
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        setMessage({ type: 'error', text: data.error || 'Erro ao importar' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao conectar com o servidor' });
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR');
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">📥 Importar Extrato Bancário</h1>
          <p className="text-gray-600">Importe seus extratos em formato OFX, CSV ou PDF automaticamente</p>
        </div>

        {/* Mensagens */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-100 border border-green-300 text-green-800' :
            message.type === 'error' ? 'bg-red-100 border border-red-300 text-red-800' :
            'bg-blue-100 border border-blue-300 text-blue-800'
          }`}>
            {message.text}
          </div>
        )}

        {/* Card Principal */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <span>📄</span> Upload de Arquivo
          </h2>

          {/* Upload Area */}
          <div className="space-y-6">
            {/* Seleção de Arquivo */}
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                Selecionar Arquivo de Extrato
              </label>
              <div className="relative">
                <input
                  id="fileInput"
                  type="file"
                  accept=".csv,.ofx,.pdf"
                  onChange={handleFileChange}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Formatos aceitos: .csv, .ofx, .pdf (máx. 10MB)
              </p>
              {file && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    ✅ Arquivo selecionado: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(2)} KB)
                  </p>
                </div>
              )}
            </div>

            {/* Seleção de Conta */}
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                Conta Destino
              </label>
              <select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none"
              >
                {accounts.length === 0 ? (
                  <option>Nenhuma conta cadastrada</option>
                ) : (
                  accounts.map(acc => (
                    <option key={acc.id} value={acc.id}>
                      {acc.name} - {formatCurrency(acc.current_balance)}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Opções */}
            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoCategorize}
                  onChange={(e) => setAutoCategorize(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-semibold text-gray-700">
                  🤖 Categorizar transações automaticamente (IA)
                </span>
              </label>
              <p className="text-xs text-gray-500 ml-7 mt-1">
                A IA tentará categorizar as transações baseada em palavras-chave
              </p>
            </div>

            {/* Botões */}
            <div className="flex gap-4">
              <button
                onClick={handlePreview}
                disabled={!file || loading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl font-bold hover:from-indigo-600 hover:to-purple-600 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading && !previewMode ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analisando...
                  </>
                ) : (
                  <>👁️ Pré-visualizar</>
                )}
              </button>

              <button
                onClick={handleImport}
                disabled={!file || !accountId || loading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl font-bold hover:from-green-600 hover:to-emerald-600 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading && previewMode ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Importando...
                  </>
                ) : (
                  <>📥 Importar Agora</>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Pré-visualização */}
        {previewMode && previewData && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              👁️ Pré-visualização das Transações
            </h2>

            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-sm text-gray-600">Total</p>
                  <p className="text-2xl font-bold text-blue-600">{previewData.total}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Tipo de Arquivo</p>
                  <p className="text-2xl font-bold text-blue-600 uppercase">{previewData.file_type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Exibindo</p>
                  <p className="text-2xl font-bold text-blue-600">{Math.min(previewData.transactions.length, 50)}</p>
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Data</th>
                    <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Descrição</th>
                    <th className="px-4 py-3 text-left text-sm font-bold text-gray-700">Tipo</th>
                    <th className="px-4 py-3 text-right text-sm font-bold text-gray-700">Valor</th>
                  </tr>
                </thead>
                <tbody>
                  {previewData.transactions.slice(0, 20).map((trans, idx) => (
                    <tr key={idx} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm">{formatDate(trans.date)}</td>
                      <td className="px-4 py-3 text-sm">{trans.description}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 text-xs rounded font-semibold ${
                          trans.type === 'Receita' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {trans.type}
                        </span>
                      </td>
                      <td className={`px-4 py-3 text-sm text-right font-bold ${
                        trans.type === 'Receita' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatCurrency(trans.value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {previewData.transactions.length > 20 && (
              <p className="text-center text-sm text-gray-500 mt-4">
                Mostrando primeiras 20 de {previewData.total} transações
              </p>
            )}
          </div>
        )}

        {/* Histórico de Importações */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <span>📊</span> Histórico de Importações
          </h2>

          {importHistory.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Nenhuma importação realizada ainda</p>
          ) : (
            <div className="space-y-4">
              {importHistory.map(imp => (
                <div key={imp.id} className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-all">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
                        📄
                      </div>
                      <div>
                        <p className="font-bold text-gray-800">{imp.file_name}</p>
                        <p className="text-sm text-gray-500">
                          {imp.account_name} • {formatDate(imp.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">
                        <span className="font-bold text-green-600">{imp.imported_transactions}</span> importadas
                      </p>
                      <p className="text-xs text-gray-500">
                        {imp.duplicated_transactions} duplicadas
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
