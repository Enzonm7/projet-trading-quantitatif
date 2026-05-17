import { Routes, Route } from 'react-router-dom'
import { PairProvider } from './context/PairContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Exploration from './pages/Exploration'
import Backtest from './pages/Backtest'
import Performance from './pages/Performance'
import MLInsights from './pages/MLInsights'

function App() {
  return (
    <PairProvider>
      <Layout>
        <Routes>
          <Route path="/"            element={<Dashboard />}   />
          <Route path="/exploration" element={<Exploration />} />
          <Route path="/backtest"    element={<Backtest />}    />
          <Route path="/performance" element={<Performance />} />
          <Route path="/ml-insights" element={<MLInsights />}  />
        </Routes>
      </Layout>
    </PairProvider>
  )
}

export default App