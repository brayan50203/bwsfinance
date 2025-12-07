import React, { useState, useEffect } from 'react';
import {
  TrendingUp, TrendingDown, DollarSign, PiggyBank, 
  Wallet, CreditCard, ArrowUpRight, ArrowDownRight,
  RefreshCw, Loader2, AlertCircle
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  PieChart, Pie, Cell, ResponsiveContainer,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import AIFloatingButton from '../components/AIFloatingButton';

const DashboardFinanceira = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/dashboard', {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Erro ao carregar dados');
      }
      
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Erro:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Atualizar a cada 60 segundos
    const interval = setInterval(fetchData, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const formatPercent = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const calculateVariation = (current, previous) => {
    if (previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  };

  // Loading State
  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  // Error State
  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">
            Erro ao carregar
          </h2>
          <p className="text-gray-600 text-center mb-6">{error}</p>
          <button
            onClick={fetchData}
            className="w-full bg-indigo-600 text-white py-3 rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-5 h-5" />
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  // Calcular KPIs
  const taxaPoupanca = data.renda_total > 0 
    ? (data.saldo / data.renda_total) * 100 
    : 0;
  
  const taxaEndividamento = data.renda_total > 0
    ? (data.custos_total / data.renda_total) * 100
    : 0;
  
  const rentabilidadeMedia = data.variacao_investimentos.length > 0
    ? data.variacao_investimentos.reduce((acc, inv) => acc + inv.variacao, 0) / data.variacao_investimentos.length
    : 0;

  // Variações
  const variacaoRenda = calculateVariation(data.renda_total, data.renda_mes_anterior);
  const variacaoCustos = calculateVariation(data.custos_total, data.custos_mes_anterior);

  // Total de investimentos
  const totalInvestimentos = Object.values(data.investimentos).reduce((acc, val) => acc + val, 0);

  // Preparar dados dos gráficos
  const categoriasData = Object.entries(data.categorias).map(([name, value]) => ({
    name,
    value,
    percent: data.custos_total > 0 ? ((value / data.custos_total) * 100).toFixed(1) : 0
  }));

  const investimentosData = Object.entries(data.investimentos).map(([name, value]) => ({
    name: name === 'renda_fixa' ? 'Renda Fixa' : 
          name === 'acoes' ? 'Ações' :
          name === 'criptomoedas' ? 'Criptomoedas' : name,
    value,
    percent: totalInvestimentos > 0 ? ((value / totalInvestimentos) * 100).toFixed(1) : 0
  }));

  // Cores para os gráficos
  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6', '#6366f1'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard Financeira</h1>
              <p className="text-gray-500 mt-1">Visão geral das suas finanças</p>
            </div>
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              Atualizar
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Cards de Resumo */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Card: Renda Total */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-emerald-100 rounded-xl">
                <TrendingUp className="w-6 h-6 text-emerald-600" />
              </div>
              {variacaoRenda !== 0 && (
                <div className={`flex items-center gap-1 text-sm ${variacaoRenda > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                  {variacaoRenda > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  {formatPercent(variacaoRenda)}
                </div>
              )}
            </div>
            <h3 className="text-gray-500 text-sm font-medium mb-1">Renda Total</h3>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.renda_total)}</p>
            <p className="text-xs text-gray-400 mt-2">vs mês anterior: {formatCurrency(data.renda_mes_anterior)}</p>
          </div>

          {/* Card: Custos Totais */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-red-100 rounded-xl">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
              {variacaoCustos !== 0 && (
                <div className={`flex items-center gap-1 text-sm ${variacaoCustos < 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                  {variacaoCustos > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  {formatPercent(variacaoCustos)}
                </div>
              )}
            </div>
            <h3 className="text-gray-500 text-sm font-medium mb-1">Custos Totais</h3>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.custos_total)}</p>
            <p className="text-xs text-gray-400 mt-2">vs mês anterior: {formatCurrency(data.custos_mes_anterior)}</p>
          </div>

          {/* Card: Saldo Mensal */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl ${data.saldo >= 0 ? 'bg-indigo-100' : 'bg-red-100'}`}>
                <Wallet className={`w-6 h-6 ${data.saldo >= 0 ? 'text-indigo-600' : 'text-red-600'}`} />
              </div>
            </div>
            <h3 className="text-gray-500 text-sm font-medium mb-1">Saldo Mensal</h3>
            <p className={`text-2xl font-bold ${data.saldo >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              {formatCurrency(data.saldo)}
            </p>
            <p className="text-xs text-gray-400 mt-2">
              {data.saldo >= 0 ? 'Superávit' : 'Déficit'} no mês
            </p>
          </div>

          {/* Card: Investimentos */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-xl">
                <PiggyBank className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <h3 className="text-gray-500 text-sm font-medium mb-1">Investimentos</h3>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalInvestimentos)}</p>
            <p className="text-xs text-gray-400 mt-2">Valor total da carteira</p>
          </div>
        </div>

        {/* Gráficos: Linha 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Gráfico: Distribuição de Custos (Pizza) */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 Distribuição de Custos</h3>
            {categoriasData.length > 0 ? (
              <div className="flex flex-col lg:flex-row items-center gap-4">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={categoriasData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${percent}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categoriasData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-col gap-2 w-full lg:w-auto">
                  {categoriasData.slice(0, 5).map((cat, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
                      <span className="text-gray-600">{cat.name}</span>
                      <span className="font-semibold ml-auto">{cat.percent}%</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">Nenhuma despesa registrada</div>
            )}
          </div>

          {/* Gráfico: Carteira de Investimentos (Rosca) */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">💼 Composição da Carteira</h3>
            {investimentosData.length > 0 ? (
              <div className="flex flex-col lg:flex-row items-center gap-4">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={investimentosData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${percent}%`}
                    >
                      {investimentosData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-col gap-2 w-full lg:w-auto">
                  {investimentosData.map((inv, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
                      <span className="text-gray-600">{inv.name}</span>
                      <span className="font-semibold ml-auto">{inv.percent}%</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">Nenhum investimento registrado</div>
            )}
          </div>
        </div>

        {/* Gráficos: Linha 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Gráfico: Evolução do Saldo (Linha) */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">📈 Evolução do Saldo Mensal</h3>
            {data.historico_saldo.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={data.historico_saldo}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="mes" stroke="#999" />
                  <YAxis stroke="#999" tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Line type="monotone" dataKey="valor" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-400 py-12">Histórico insuficiente</div>
            )}
          </div>

          {/* Gráfico: Fluxo de Caixa (Área) */}
          <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">💹 Fluxo de Caixa Mensal</h3>
            {data.fluxo_mensal.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={data.fluxo_mensal}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="dia" stroke="#999" />
                  <YAxis stroke="#999" tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Area type="monotone" dataKey="renda" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="custo" stackId="2" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
                  <Legend />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-400 py-12">Sem movimentações no mês</div>
            )}
          </div>
        </div>

        {/* Gráfico: Rentabilidade por Ativo (Barras) */}
        <div className="bg-white rounded-2xl shadow-md p-6 border border-gray-100 mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">💰 Rentabilidade por Ativo</h3>
          {data.variacao_investimentos.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.variacao_investimentos}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="nome" stroke="#999" />
                <YAxis stroke="#999" tickFormatter={(value) => `${value}%`} />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="variacao" radius={[8, 8, 0, 0]}>
                  {data.variacao_investimentos.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.variacao >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-400 py-12">Nenhuma variação calculada</div>
          )}
        </div>

        {/* KPIs Inteligentes */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* KPI: Taxa de Poupança */}
          <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-white/20 rounded-xl">
                <PiggyBank className="w-6 h-6" />
              </div>
              <div className={`flex items-center gap-1 text-sm ${taxaPoupanca >= 20 ? 'opacity-100' : 'opacity-70'}`}>
                {taxaPoupanca >= 20 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {taxaPoupanca >= 20 ? 'Saudável' : 'Atenção'}
              </div>
            </div>
            <h3 className="text-sm font-medium opacity-90 mb-1">Taxa de Poupança</h3>
            <p className="text-3xl font-bold">{taxaPoupanca.toFixed(1)}%</p>
            <p className="text-xs opacity-75 mt-2">Meta: {'>'} 20% da renda</p>
          </div>

          {/* KPI: Taxa de Endividamento */}
          <div className={`bg-gradient-to-br rounded-2xl shadow-lg p-6 text-white ${
            taxaEndividamento <= 30 ? 'from-emerald-500 to-emerald-600' :
            taxaEndividamento <= 50 ? 'from-amber-500 to-amber-600' :
            'from-red-500 to-red-600'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-white/20 rounded-xl">
                <CreditCard className="w-6 h-6" />
              </div>
              <div className={`flex items-center gap-1 text-sm ${taxaEndividamento <= 30 ? 'opacity-100' : 'opacity-70'}`}>
                {taxaEndividamento <= 30 ? <ArrowDownRight className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}
                {taxaEndividamento <= 30 ? 'Excelente' : taxaEndividamento <= 50 ? 'Atenção' : 'Crítico'}
              </div>
            </div>
            <h3 className="text-sm font-medium opacity-90 mb-1">Taxa de Endividamento</h3>
            <p className="text-3xl font-bold">{taxaEndividamento.toFixed(1)}%</p>
            <p className="text-xs opacity-75 mt-2">Meta: {'<'} 30% da renda</p>
          </div>

          {/* KPI: Rentabilidade Média */}
          <div className={`bg-gradient-to-br rounded-2xl shadow-lg p-6 text-white ${
            rentabilidadeMedia > 0 ? 'from-indigo-500 to-indigo-600' : 'from-gray-500 to-gray-600'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-white/20 rounded-xl">
                <DollarSign className="w-6 h-6" />
              </div>
              <div className={`flex items-center gap-1 text-sm`}>
                {rentabilidadeMedia > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {rentabilidadeMedia > 0 ? 'Positivo' : 'Negativo'}
              </div>
            </div>
            <h3 className="text-sm font-medium opacity-90 mb-1">Rentabilidade Média</h3>
            <p className="text-3xl font-bold">{formatPercent(rentabilidadeMedia)}</p>
            <p className="text-xs opacity-75 mt-2">Média dos investimentos</p>
          </div>
        </div>
      </div>

      {/* AI Floating Button */}
      <AIFloatingButton />
    </div>
  );
};

export default DashboardFinanceira;
