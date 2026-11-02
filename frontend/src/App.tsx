import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { router } from './router';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
