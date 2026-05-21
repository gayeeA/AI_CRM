import React from 'react';
import InteractionForm from './InteractionForm';
import ChatPanel from './ChatPanel';
import '../styles/MainLayout.css';

export const MainLayout: React.FC = () => {
  return (
    <div className="main-layout">
      <div className="layout-container">
        <div className="form-panel">
          <InteractionForm />
        </div>

        <div className="chat-panel-container">
          <ChatPanel />
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
