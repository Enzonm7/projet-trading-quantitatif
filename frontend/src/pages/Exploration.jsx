import { useState } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import PairsList from '../components/PairsList'
import ApiService from '../services/ApiService'
import { PageTitle, SectionTitle, FormGrid, InputGroup, ErreurMsg } from '../components/UI'

function Exploration() {
  const [tickers, setTickers]     = useState('AAPL,MSFT,JPM,BAC,PEP,KO')
  const [dateDebut, setDateDebut] = useState('2023-01-01')
  const [dateFin, setDateFin]     = useState('2024-01-01')
  const [chargement, setChargement] = useState(false)
  const [paires, setPaires]       = useState([])
  const [erreur, setErreur]       = useState(null)
  const [aLance, setALance] = useState(false)

  const lancerDetection = async () => {
    setChargement(true)
    setErreur(null)
    setPaires([])
    setALance(false)          
    try {
      const listeTickers = tickers.split(',').map((t) => t.trim())
      const reponse = await ApiService.detecterPaires(listeTickers, dateDebut, dateFin)
      console.log(reponse.data)
      setPaires(reponse.data.paires)
    } catch {
      setErreur("Erreur lors de la détection. Vérifie que l'API est démarrée.")
    } finally {
      setChargement(false)
      setALance(true)         
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <PageTitle titre="Exploration" sous="Détection de paires · Corrélation & Cointégration" />

      <Card>
        <SectionTitle>Configuration</SectionTitle>
        <FormGrid cols={3}>
          <InputGroup label="Tickers (séparés par des virgules)" span={3}>
            <input
              type="text"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              placeholder="AAPL,MSFT,JPM,BAC"
            />
          </InputGroup>
          <InputGroup label="Date début">
            <input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} />
          </InputGroup>
          <InputGroup label="Date fin">
            <input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} />
          </InputGroup>
          <InputGroup label=" " style={{ display: 'flex', alignItems: 'flex-end' }}>
            <Button onClick={lancerDetection} disabled={chargement} style={{ width: '100%' }}>
              {chargement ? 'Détection...' : 'Détecter les paires →'}
            </Button>
          </InputGroup>
        </FormGrid>
        <ErreurMsg message={erreur} />
      </Card>

      {aLance && (
        <Card>
          <SectionTitle>
            Résultats — {paires.length} paire(s) détectée(s)
          </SectionTitle>
          {paires.length === 0
            ? <p style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                Aucune paire cointégrée détectée sur cette période. Essaie d'autres tickers ou une période plus longue.
              </p>
            : <PairsList paires={paires} dateDebut={dateDebut} dateFin={dateFin} />
          }
        </Card>
      )}
    </div>
  )
}

export default Exploration
