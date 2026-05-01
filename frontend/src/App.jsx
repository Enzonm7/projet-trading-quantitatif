import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Exploration from './pages/Exploration'
import Backtest from './pages/Backtest'
import Performance from './pages/Performance'
import MLInsights from './pages/MLInsights'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/exploration" element={<Exploration />} />
        <Route path="/backtest" element={<Backtest />} />
        <Route path="/performance" element={<Performance />} />
        <Route path="/ml-insights" element={<MLInsights />} />
      </Routes>
    </Layout>
  )
}

export default App