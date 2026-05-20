import React, { useEffect, useState } from "react";
import axios from "axios";

export default function InteractionList() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/interactions")
      .then(res => setData(res.data));
  }, []);

  return (
    <div>
      <h2>Interactions</h2>
      {data.map(i => (
        <div key={i.id}>
          <p>{i.hcp_name} - {i.topics}</p>
        </div>
      ))}
    </div>
  );
}