import { BrowserRouter as Router } from 'react-router-dom';
import App from '@/App';
import { RecoilRoot } from 'recoil';

function Root() {
  return (
    <RecoilRoot>
      <Router>
        <App />
      </Router>
    </RecoilRoot>
  );
}

export default Root;
