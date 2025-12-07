import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ContasHomeStyle from './pages/Contas_HomeStyle';
import DashboardFinanceira from './pages/DashboardFinanceira';
import AIPanel from './pages/AIPanel';
import ImportarExtrato from './components/ImportarExtrato';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardFinanceira />} />
        <Route path="/contas" element={<ContasHomeStyle />} />
        <Route path="/ai" element={<AIPanel />} />
        <Route path="/importar" element={<ImportarExtrato />} />
      </Routes>
    </Router>
  );
}

export default App;
