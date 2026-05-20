import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type{ RootState } from '../store';
import { updateFormState } from '../store/interactionSlice';
import { AlertTriangle, Sparkles } from 'lucide-react';

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

export const AIAssistant: React.FC = () => {
  const dispatch = useDispatch();
  const currentFormState = useSelector((state: RootState) => state.interaction);
  
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'ai',
      text: 'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;

    const userText = inputValue;
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          current_state: currentFormState,
        }),
      });

      if (!response.ok) throw new Error('Network error processing tool logic');
      const data = await response.json();

      setMessages((prev) => [...prev, { sender: 'ai', text: data.reply }]);
      
      if (data.form_state) {
        dispatch(updateFormState(data.form_state));
      }
    } catch (error) {
      setMessages((prev) => [...prev, { sender: 'ai', text: 'Error executing autonomous pipeline changes.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col h-[calc(100vh-120px)] min-h-[650px] p-4 justify-between">
      <div className="space-y-4 flex-1 overflow-y-auto pr-1">
        <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
          <Sparkles className="w-4 h-4 text-blue-500 animate-pulse" />
          <h3 className="text-sm font-bold text-slate-700">AI Assistant</h3>
          <span className="text-[10px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded font-medium ml-auto">Log via Chat</span>
        </div>

        <div className="space-y-3">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 text-xs rounded-xl max-w-[90%] tracking-normal leading-relaxed ${
                msg.sender === 'ai'
                  ? 'bg-slate-50 border border-slate-100 text-slate-600 font-normal mr-auto'
                  : 'bg-blue-600 text-white font-medium ml-auto shadow-sm shadow-blue-100'
              }`}
            >
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="text-xs text-slate-400 italic animate-pulse p-2">
              Running Groq execution node...
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Describe interaction..."
            className="flex-1 text-xs px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-400"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-slate-800 text-white text-xs px-4 py-2.5 rounded-lg flex items-center gap-1.5 font-semibold hover:bg-slate-900 transition-colors disabled:bg-slate-300"
          >
            <AlertTriangle className="w-3.5 h-3.5" /> Log
          </button>
        </div>
      </div>
    </div>
  );
};