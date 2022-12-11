import { Route, Routes, useLocation } from 'react-router-dom';
import HomePage from '@/pages/HomePage';
import { PageLayout } from './components/layout';

function App() {
  const location = useLocation();

  return (
    <PageLayout>
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<HomePage />} />
        <Route path="/*">Page Not Found</Route>
      </Routes>
    </PageLayout>
  );
}

export default App;
