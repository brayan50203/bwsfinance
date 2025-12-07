import React, { useState, useEffect } from 'react';
import { AlertCircle, TrendingUp, TrendingDown, DollarSign, PieChart, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

const AIInsightCard = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/ai/insight', {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setInsights(data);
      }
    } catch (error) {
      console.error('Erro ao buscar insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low':
        return 'bg-green-50 border-green-200 text-green-800';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'medium':
        return <TrendingDown className="w-5 h-5 text-yellow-600" />;
      case 'low':
        return <TrendingUp className="w-5 h-5 text-green-600" />;
      default:
        return <Sparkles className="w-5 h-5 text-blue-600" />;
    }
  };

  const toggleExpand = (index) => {
    setExpanded(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-6 h-6 text-indigo-600 animate-pulse" />
          <h3 className="text-lg font-bold text-gray-800">BWS Insight AI</h3>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse bg-gray-100 h-16 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!insights || !insights.insights || insights.insights.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-6 h-6 text-indigo-600" />
          <h3 className="text-lg font-bold text-gray-800">BWS Insight AI</h3>
        </div>
        <p className="text-gray-500 text-sm">Nenhum insight disponível no momento.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-indigo-600" />
            <h3 className="text-lg font-bold text-gray-800">BWS Insight AI</h3>
          </div>
          <span className="text-xs text-gray-500">
            Análise do dia • {new Date().toLocaleDateString('pt-BR')}
          </span>
        </div>
      </div>

      {/* Insights */}
      <div className="p-4 space-y-3">
        {insights.insights.map((insight, index) => (
          <div
            key={index}
            className={`border rounded-lg overflow-hidden transition-all ${getSeverityColor(insight.severity)}`}
          >
            <div
              className="p-3 cursor-pointer flex items-center gap-3"
              onClick={() => toggleExpand(index)}
            >
              {getSeverityIcon(insight.severity)}
              <div className="flex-1">
                <h4 className="font-semibold text-sm">{insight.title}</h4>
                {!expanded[index] && (
                  <p className="text-xs mt-1 opacity-80 line-clamp-1">{insight.message}</p>
                )}
              </div>
              {expanded[index] ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </div>
            
            {expanded[index] && (
              <div className="px-3 pb-3 text-sm">
                <p>{insight.message}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Predictions */}
      {insights.predictions && insights.predictions.length > 0 && (
        <div className="p-4 border-t border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
          <h4 className="font-semibold text-sm text-gray-800 mb-2 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-600" />
            Previsão para 30 dias
          </h4>
          {insights.predictions.map((pred, index) => (
            <div key={index} className="text-sm text-gray-700">
              <span className="font-medium">Saldo previsto:</span>{' '}
              <span className={pred.predicted_balance >= 0 ? 'text-green-600' : 'text-red-600'}>
                R$ {pred.predicted_balance?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-gray-500 text-xs ml-2">
                ({pred.confidence}% confiança)
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Anomalies */}
      {insights.anomalies && insights.anomalies.length > 0 && (
        <div className="p-4 border-t border-gray-200 bg-red-50">
          <h4 className="font-semibold text-sm text-red-800 mb-2 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            Anomalias Detectadas
          </h4>
          <div className="space-y-2">
            {insights.anomalies.map((anomaly, index) => (
              <div key={index} className="text-sm text-red-700 flex items-start gap-2">
                <span className="text-red-500">•</span>
                <span>{anomaly.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIInsightCard;
