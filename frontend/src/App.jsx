import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/exploration" element={<div className="text-2xl font-bold">Exploration (à venir)</div>} />
        <Route path="/backtest" element={<div className="text-2xl font-bold">Backtest (à venir)</div>} />
        <Route path="/performance" element={<div className="text-2xl font-bold">Performance (à venir)</div>} />
        <Route path="/ml-insights" element={<div className="text-2xl font-bold">ML Insights (à venir)</div>} />
      </Routes>
    </Layout>
  )
}

export default App