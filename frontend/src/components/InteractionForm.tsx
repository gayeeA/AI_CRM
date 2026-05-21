import React, { useState } from 'react';

import { useDispatch, useSelector } from 'react-redux';

import {
  updateField,
  addMaterial,

  removeMaterial,
  addSample,
  removeSample,
  selectCurrentInteraction,
  setSentiment,
} from '../store/slices/formSlice';

import '../styles/InteractionForm.css';

interface InteractionFormProps {
  readOnly?: boolean;
}

export const InteractionForm: React.FC<InteractionFormProps> = ({ readOnly = true }) => {
  const dispatch = useDispatch();
  const interaction = useSelector(selectCurrentInteraction);

  const [newMaterial, setNewMaterial] = useState('');
  const [newSample, setNewSample] = useState({ name: '', quantity: 1 });

  if (!interaction) return null;

  const handleFieldChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    dispatch(updateField({ field: name as any, value }));
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(updateField({ field: 'date', value: e.target.value }));
  };

  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(updateField({ field: 'time', value: e.target.value }));
  };

  const handleAddMaterial = () => {
    if (newMaterial.trim()) {
      dispatch(addMaterial({ type: newMaterial.trim() }));
      setNewMaterial('');
    }
  };

  const handleRemoveMaterial = (index: number) => {

    dispatch(removeMaterial(index));
  };

  const handleAddSample = () => {
    if (newSample.name.trim()) {
      dispatch(addSample(newSample));
      setNewSample({ name: '', quantity: 1 });
    }
  };

  const handleRemoveSample = (index: number) => {
    dispatch(removeSample(index));
  };

  const handleSentimentChange = (sentiment: 'Positive' | 'Neutral' | 'Negative') => {
    dispatch(setSentiment(sentiment));
  };

  const normalizeSentiment = (value: string | undefined) =>
    value?.trim().toLowerCase() as 'positive' | 'neutral' | 'negative' | undefined;

  return (
    <div className="interaction-form">
      <h2>Log HCP Interaction</h2>

      {/* Interaction Details Section */}
      <div className="form-section">
        <h3>Interaction Details</h3>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="hcp_name">HCP Name</label>
            <input
              id="hcp_name"
              name="hcp_name"
              type="text"
              placeholder="Search or select HCP..."
              value={interaction.hcp_name}
              onChange={handleFieldChange}
              readOnly={readOnly}
            />
          </div>

          <div className="form-group">
            <label htmlFor="interaction_type">Interaction Type</label>
            <select
              id="interaction_type"
              name="interaction_type"
              value={interaction.interaction_type}
              onChange={handleFieldChange}
              disabled={readOnly}
            >
              <option value="Meeting">Meeting</option>
              <option value="Call">Call</option>
              <option value="Email">Email</option>
              <option value="Conference">Conference</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="date">Date</label>
            <div className="date-input-wrapper">
              <input
                id="date"
                name="date"
                type="text"
                value={interaction.date}
                onChange={handleDateChange}
                readOnly={readOnly}
              />
              <span className="calendar-icon">📅</span>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="time">Time</label>
            <div className="time-input-wrapper">
              <input
                id="time"
                name="time"
                type="text"
                value={interaction.time}
                onChange={handleTimeChange}
                readOnly={readOnly}
              />
              <span className="clock-icon">⏰</span>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="attendees">Attendees</label>
          <input
            id="attendees"
            name="attendees"
            type="text"
            placeholder="Enter names or search..."
            value={interaction.attendees || ''}
            onChange={handleFieldChange}
            readOnly={readOnly}
          />
        </div>

        <div className="form-group">
          <label htmlFor="topics_discussed">Topics Discussed</label>
          <textarea
            id="topics_discussed"
            name="topics_discussed"
            placeholder="Enter key discussion points..."
            value={interaction.topics_discussed || ''}
            onChange={handleFieldChange}
            readOnly={readOnly}
            rows={3}
          />
        </div>
      </div>

      {/* Materials and Samples Section */}
      <div className="form-section">
        <h3>Materials Shared / Samples Distributed</h3>

        <div className="materials-section">
          <label>Materials Shared</label>
          <div className="materials-list">
            {interaction.materials_shared.length === 0 ? (
              <p className="empty-state">No materials added</p>
            ) : (
              interaction.materials_shared.map((material: { type: string }, index: number) => (

                <div className="material-item">
                  <span>{material.type}</span>
                  {!readOnly && (
                    <button
                      className="remove-btn"
                      onClick={() => handleRemoveMaterial(index)}
                      aria-label="Remove material"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
          {!readOnly && (
            <div className="add-material">
              <input
                type="text"
                placeholder="Material name..."
                value={newMaterial}
                onChange={(e) => setNewMaterial(e.target.value)}
              />
              <button onClick={handleAddMaterial} className="search-btn">
                🔍 Search/Add
              </button>
            </div>
          )}
        </div>

        <div className="samples-section">
          <label>Samples Distributed</label>
          <div className="samples-list">
            {interaction.samples_distributed.length === 0 ? (
              <p className="empty-state">No samples added</p>
            ) : (
              interaction.samples_distributed.map((sample: { name: string; quantity?: number; description?: string }, index: number) => (

                <div key={index} className="sample-item">
                  <span>
                    {sample.name} {sample.quantity && `(Qty: ${sample.quantity})`}
                  </span>
                  {!readOnly && (
                    <button
                      className="remove-btn"
                      onClick={() => handleRemoveSample(index)}
                      aria-label="Remove sample"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
          {!readOnly && (
            <div className="add-sample">
              <input
                type="text"
                placeholder="Sample name..."
                value={newSample.name}
                onChange={(e) => setNewSample({ ...newSample, name: e.target.value })}
              />
              <input
                type="number"
                min="1"
                placeholder="Qty"
                value={newSample.quantity}
                onChange={(e) => setNewSample({ ...newSample, quantity: parseInt(e.target.value) || 1 })}
                style={{ width: '60px' }}
              />
              <button onClick={handleAddSample} className="add-btn">
                ➕ Add Sample
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Sentiment Section */}
      <div className="form-section">
        <h3>Observed/Inferred HCP Sentiment</h3>
        <div className="sentiment-options">
          {(['Positive', 'Neutral', 'Negative'] as const).map((sentiment) => (
            <label key={sentiment} className="sentiment-option">
              <input
                type="radio"
                name="sentiment"
                value={sentiment}
                checked={
                  normalizeSentiment(interaction.sentiment) ===
                  sentiment.toLowerCase()
                }
                onChange={() => handleSentimentChange(sentiment)}
                disabled={readOnly}
              />
              <span className={`sentiment-label ${sentiment.toLowerCase()}`}>
                {sentiment}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Outcomes and Follow-up Section */}
      <div className="form-section">
        <div className="form-group">
          <label htmlFor="outcomes">Outcomes</label>
          <textarea
            id="outcomes"
            name="outcomes"
            placeholder="Key outcomes or agreements..."
            value={interaction.outcomes || ''}
            onChange={handleFieldChange}
            readOnly={readOnly}
            rows={2}
          />
        </div>

        <div className="form-group">
          <label htmlFor="follow_up_actions">Follow-up Actions</label>
          <textarea
            id="follow_up_actions"
            name="follow_up_actions"
            placeholder="Enter next steps or tasks..."
            value={interaction.follow_up_actions || ''}
            onChange={handleFieldChange}
            readOnly={readOnly}
            rows={2}
          />
        </div>
      </div>

      {/* AI Suggestions Section */}
      {interaction.ai_suggestions && interaction.ai_suggestions.length > 0 && (
        <div className="form-section ai-suggestions">
          <h3>AI Suggested Follow-ups</h3>
          <ul className="suggestions-list">
            {interaction.ai_suggestions.map((suggestion: string, index: number) => (
              <li key={index}>

                <span className="bullet">•</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default InteractionForm;
