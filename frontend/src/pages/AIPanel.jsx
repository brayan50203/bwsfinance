import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, AlertTriangle, MessageSquare, BarChart3, Sparkles } from 'lucide-react';
import AIChat from '../components/AIChat';
import AIInsightCard from '../components/AIInsightCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AIPanel = () => {
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('insights');

  useEffect(() => {
    fetchAIData();
  }, []);

  const fetchAIData = async () => {
    try {
      const [summaryRes, alertsRes, predictionsRes] = await Promise.all([
        fetch('http://localhost:5000/api/ai/summary', { credentials: 'include' }),
        fetch('http://localhost:5000/api/ai/alerts', { credentials: 'include' }),
        fetch('http://localhost:5000/api/ai/predict?days=30', { credentials: 'include' })
      ]);

      const summaryData = await summaryRes.json();
      const alertsData = await alertsRes.json();
      const predictionsData = await predictionsRes.json();

      if (summaryData.success) setSummary(summaryData);
      if (alertsData.success) setAlerts(alertsData.alerts || []);
      if (predictionsData.success) setPredictions(predictionsData.predictions || []);
    } catch (error) {
      console.error('Erro ao buscar dados da IA:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'insights', label: 'Insights do Dia', icon: Sparkles },
    { id: 'predictions', label: 'Previsões', icon: TrendingUp },
    { id: 'alerts', label: 'Alertas', icon: AlertTriangle },
    { id: 'chat', label: 'Chat com IA', icon: MessageSquare }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-16 h-16 text-indigo-600 animate-pulse mx-auto mb-4" />
          <p className="text-gray-600">Carregando análise da IA...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-10 h-10" />
            <h1 className="text-3xl font-bold">BWS Insight AI</h1>
          </div>
          <p className="text-indigo-100">
            Análise Financeira Inteligente • Última atualização: {new Date().toLocaleString('pt-BR')}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-4 border-b-2 transition ${
                    activeTab === tab.id
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-gray-600 hover:text-gray-800'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                  {tab.id === 'alerts' && alerts.length > 0 && (
                    <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {alerts.length}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <AIInsightCard />
              
              {summary && summary.summary && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                    Resumo da Análise
                  </h3>
                  <div className="prose prose-sm max-w-none text-gray-700">
                    {summary.summary}
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Status da IA</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-600">Sistema Ativo</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Insights gerados:</span> {summary?.insights?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Anomalias detectadas:</span> {summary?.anomalies?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Previsões ativas:</span> {summary?.predictions?.length || 0}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Predictions Tab */}
        {activeTab === 'predictions' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
              Previsão de Saldo - Próximos 30 Dias
            </h3>
            
            {predictions.length > 0 ? (
              <div className="space-y-6">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={predictions}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="days" label={{ value: 'Dias', position: 'insideBottom', offset: -5 }} />
                    <YAxis />
                    <Tooltip formatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`} />
                    <Line type="monotone" dataKey="predicted_balance" stroke="#4f46e5" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {predictions.map((pred, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="text-sm text-gray-600 mb-1">
                        Em {pred.days} dias
                      </div>
                      <div className={`text-2xl font-bold ${pred.predicted_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        R$ {pred.predicted_balance?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Confiança: {pred.confidence}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Dados insuficientes para gerar previsões.
              </p>
            )}
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {alerts.length > 0 ? (
              alerts.map((alert, index) => (
                <div key={index} className="bg-white border-l-4 border-red-500 rounded-lg shadow p-6">
                  <div className="flex items-start gap-4">
                    <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-800 mb-2">{alert.title}</h4>
                      <p className="text-gray-600">{alert.message}</p>
                      <div className="mt-2 text-sm text-gray-500">
                        Severidade: <span className="font-medium text-red-600">Alta</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <AlertTriangle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Nenhum alerta no momento. Tudo está sob controle! 🎉</p>
              </div>
            )}
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <AIChat />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIPanel;
