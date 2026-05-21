import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import {
  setCurrentInteraction,
  setAISuggestions,
  selectCurrentInteraction,
} from '../store/slices/formSlice';

import { chatAPI } from '../utils/api';
import '../styles/ChatPanel.css';


interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolUsed?: string;
}

interface ChatPanelProps {
  interactionId?: number;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ interactionId }) => {
  const dispatch = useDispatch();
  const currentInteraction = useSelector(selectCurrentInteraction);

  const [messages, setMessages] = useState<Message[]>([]);

  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message to chat
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(
        inputValue,
        interactionId ?? currentInteraction?.id,
        true,
        currentInteraction || undefined
      );

      // Update form with response data
      if (response.updated_interaction) {
        dispatch(setCurrentInteraction(response.updated_interaction));

        if (response.updated_interaction.ai_suggestions) {
          dispatch(setAISuggestions(response.updated_interaction.ai_suggestions));
        }
      }


      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: response.ai_response,
        timestamp: new Date(),
        toolUsed: response.tool_used,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content:
          'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h2>
          <span className="ai-badge">AI Assistant</span>
          Log interaction via chat
        </h2>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>👋 Welcome to AI-Assisted Interaction Logging!</p>
            <p>
              Simply describe your HCP interaction in natural language, and I'll
              automatically fill in all the details for you.
            </p>
            <div className="example-prompts">
              <p>Try something like:</p>
              <div className="prompt-example">
                "Today I met with Dr. Smith and discussed product X efficiency.
                The sentiment was positive and I shared the brochures."
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                {message.toolUsed && (
                  <div className="message-tool">Tool: {message.toolUsed}</div>
                )}
                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="input-container">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}

            placeholder="Describe your interaction..."
            disabled={isLoading}
            rows={3}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="send-btn"
          >
            {isLoading ? '⏳ Processing...' : '📤 Log'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
