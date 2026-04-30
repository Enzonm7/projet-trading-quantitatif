import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Exploration from './pages/Exploration'
import Backtest from './pages/Backtest'
import Performance from './pages/Performance'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/exploration" element={<Exploration />} />
        <Route path="/backtest" element={<Backtest />} />
        <Route path="/performance" element={<Performance />} />
        <Route path="/ml-insights" element={<div className="text-2xl font-bold">ML Insights (à venir)</div>} />
      </Routes>
    </Layout>
  )
}

export default App