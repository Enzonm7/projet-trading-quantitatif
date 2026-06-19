import { createContext, useContext, useState } from 'react'

const PairContext = createContext(null)

export function PairProvider({ children }) {
  const [paireSelectionnee, setPaireSelectionnee] = useState({
    tickerA: '',
    tickerB: '',
    dateDebut: '2020-01-01',
    dateFin: '2024-01-01',
    capital: '',
  })

  return (
    <PairContext.Provider value={{ paireSelectionnee, setPaireSelectionnee }}>
      {children}
    </PairContext.Provider>
  )
}

export function usePair() {
  return useContext(PairContext)
}