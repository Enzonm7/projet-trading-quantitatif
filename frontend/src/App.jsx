import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Card from './components/Card'
import Button from './components/Button'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={
          <div className="space-y-4">
            <Card>
              <p className="text-slate-700">Ceci est une Card</p>
            </Card>
            <div className="flex gap-3">
              <Button>Primary</Button>
              <Button variante="secondary">Secondary</Button>
              <Button variante="danger">Danger</Button>
            </div>
          </div>
          } />
        <Route path="/exploration" element={<div className="text-2xl font-bold">Exploration (à venir)</div>} />
        <Route path="/backtest" element={<div className="text-2xl font-bold">Backtest (à venir)</div>} />
        <Route path="/performance" element={<div className="text-2xl font-bold">Performance (à venir)</div>} />
        <Route path="/ml-insights" element={<div className="text-2xl font-bold">ML Insights (à venir)</div>} />
      </Routes>
    </Layout>
  )
}

export default App