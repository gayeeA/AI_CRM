import React from 'react';
import { Provider } from 'react-redux';
import store from './store/store';
import MainLayout from './components/MainLayout';
import './styles/App.css';

function App() {
  return (
    <Provider store={store}>
      <div className="app">
        <MainLayout />
      </div>
    </Provider>
  );
}

export default App;
