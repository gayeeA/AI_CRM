import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store';
import { InteractionForm } from './components/InteractionForm';
import { AIAssistant } from './components/AIAssistant';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <div className="min-h-screen bg-slate-50/50 p-6">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 xl:col-span-8">
            <InteractionForm />
          </div>
          <div className="lg:col-span-5 xl:col-span-4">
            <AIAssistant />
          </div>
        </div>
      </div>
    </Provider>
  );
};

export default App;