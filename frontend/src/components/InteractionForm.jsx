import React, { useState } from "react";
import axios from "axios";

export default function InteractionForm() {
  const [form, setForm] = useState({
    hcp_name: "",
    topics: "",
    sentiment: "",
    outcome: ""
  });

  const submit = async () => {
    await axios.post("http://localhost:8000/log", form);
    alert("Saved!");
  };

  return (
    <div>
      <h2>Log Interaction</h2>
      <input placeholder="HCP Name" onChange={e => setForm({...form, hcp_name:e.target.value})}/>
      <input placeholder="Topics" onChange={e => setForm({...form, topics:e.target.value})}/>
      <input placeholder="Sentiment" onChange={e => setForm({...form, sentiment:e.target.value})}/>
      <input placeholder="Outcome" onChange={e => setForm({...form, outcome:e.target.value})}/>
      <button onClick={submit}>Submit</button>
    </div>
  );
}