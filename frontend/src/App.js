import React from "react";
import InteractionForm from "./components/InteractionForm";
import ChatAssistant from "./components/ChatAssistant";
import InteractionList from "./components/InteractionList";

function App() {
  return (
    <div>
      <h1>AI CRM HCP Module</h1>
      <InteractionForm />
      <ChatAssistant />
      <InteractionList />
    </div>
  );
}

export default App;