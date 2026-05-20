import React, { useState } from "react";
import axios from "axios";

export default function ChatAssistant() {
  const [msg, setMsg] = useState("");
  const [response, setResponse] = useState("");

  const send = async () => {
    const res = await axios.post("http://localhost:8000/chat", {
      text: msg
    });
    setResponse(res.data.output);
  };

  return (
    <div>
      <h2>AI Assistant</h2>
      <input onChange={e => setMsg(e.target.value)} />
      <button onClick={send}>Send</button>
      <p>{response}</p>
    </div>
  );
}