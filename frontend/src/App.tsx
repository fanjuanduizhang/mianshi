import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { Practice } from './pages/Practice'
import { Interview } from './pages/Interview'
import { Resume } from './pages/Resume'
import { JDMatch } from './pages/JDMatch'
import { RAG } from './pages/RAG'
import { Skills } from './pages/Skills'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/practice" element={<Practice />} />
        <Route path="/interview" element={<Interview />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/jd-match" element={<JDMatch />} />
        <Route path="/rag" element={<RAG />} />
        <Route path="/skills" element={<Skills />} />
      </Routes>
    </Layout>
  )
}

export default App
