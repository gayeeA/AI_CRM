import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';
import { Calendar, Clock, Mic, Search, Package } from 'lucide-react';

export const InteractionForm: React.FC = () => {
  const formData = useSelector((state: RootState) => state.interaction);

  return (
    <div className="bg-white rounded-3xl shadow-sm border border-slate-100 p-6 space-y-6">
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-slate-800">Log HCP Interaction</h2>
        <p className="text-sm text-slate-500">Use the AI assistant panel to populate and update interaction details automatically.</p>
      </div>

      <div className="bg-slate-50 rounded-3xl border border-slate-200 p-6 space-y-6">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800">Interaction Details</h3>
            <p className="text-xs text-slate-400">This structured form reflects what the AI assistant logs for each HCP interaction.</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label htmlFor="hcp-name" className="text-xs font-semibold text-slate-600">HCP Name</label>
            <div className="relative">
              <input
                id="hcp-name"
                type="text"
                readOnly
                value={formData.hcp_name}
                placeholder="Search or select HCP..."
                className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none cursor-not-allowed"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="interaction-type" className="text-xs font-semibold text-slate-600">Interaction Type</label>
            <select
              id="interaction-type"
              disabled
              value={formData.interaction_type}
              className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none appearance-none cursor-not-allowed"
            >
              <option value="Meeting">Meeting</option>
              <option value="Call">Call</option>
              <option value="Email">Email</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label htmlFor="interaction-date" className="text-xs font-semibold text-slate-600">Date</label>
            <div className="relative flex items-center">
              <input
                id="interaction-date"
                type="text"
                readOnly
                value={formData.date}
                className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none cursor-not-allowed"
              />
              <Calendar className="absolute right-3 w-4 h-4 text-slate-400" />
            </div>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="interaction-time" className="text-xs font-semibold text-slate-600">Time</label>
            <div className="relative flex items-center">
              <input
                id="interaction-time"
                type="text"
                readOnly
                value={formData.time}
                className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none cursor-not-allowed"
              />
              <Clock className="absolute right-3 w-4 h-4 text-slate-400" />
            </div>
          </div>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="attendees" className="text-xs font-semibold text-slate-600">Attendees</label>
          <input
            id="attendees"
            type="text"
            readOnly
            value={formData.attendees.join(', ')}
            placeholder="Enter names or search..."
            className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none cursor-not-allowed"
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="topics-discussed" className="text-xs font-semibold text-slate-600">Topics Discussed</label>
          <div className="relative">
            <textarea
              id="topics-discussed"
              readOnly
              rows={3}
              value={formData.topics_discussed}
              placeholder="Enter key discussion points..."
              className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none resize-none cursor-not-allowed"
            />
            <Mic className="absolute bottom-3 right-3 w-4 h-4 text-slate-400" />
          </div>
          <button type="button" disabled className="text-xs bg-slate-100 text-slate-600 font-medium px-3 py-1.5 rounded-lg flex items-center gap-1 cursor-not-allowed">
            ✨ Summarize from Voice Note (Requires Consent)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div className="border border-slate-200 rounded-3xl bg-white p-4 space-y-3">
          <div className="flex items-center justify-between gap-4">
            <span className="text-xs font-semibold text-slate-600">Materials Shared</span>
            <button disabled className="text-xs border border-slate-200 bg-slate-50 px-2.5 py-1 rounded-md text-slate-600 flex items-center gap-1 font-medium cursor-not-allowed">
              <Search className="w-3 h-3" /> Search/Add
            </button>
          </div>
          <div className="text-xs italic text-slate-400">
            {formData.materials_shared.length > 0 ? formData.materials_shared.join(', ') : 'No materials added.'}
          </div>
        </div>

        <div className="border border-slate-200 rounded-3xl bg-white p-4 space-y-3">
          <div className="flex items-center justify-between gap-4">
            <span className="text-xs font-semibold text-slate-600">Samples Distributed</span>
            <button disabled className="text-xs border border-slate-200 bg-slate-50 px-2.5 py-1 rounded-md text-slate-600 flex items-center gap-1 font-medium cursor-not-allowed">
              <Package className="w-3 h-3" /> Add Sample
            </button>
          </div>
          <div className="text-xs italic text-slate-400">
            {formData.samples_distributed.length > 0 ? formData.samples_distributed.join(', ') : 'No samples added.'}
          </div>
        </div>
      </div>

      <fieldset className="space-y-2 border border-slate-200 rounded-3xl bg-white p-4">
        <legend className="text-xs font-semibold text-slate-600">Observed/Inferred HCP Sentiment</legend>
        <div className="flex items-center gap-6">
          {['Positive', 'Neutral', 'Negative'].map((mode) => (
            <label key={mode} htmlFor={`sentiment-${mode.toLowerCase()}`} className="flex items-center gap-2 text-xs font-medium text-slate-600 cursor-not-allowed">
              <input
                id={`sentiment-${mode.toLowerCase()}`}
                type="radio"
                disabled
                checked={formData.sentiment === mode}
                className="w-3.5 h-3.5 text-blue-600 border-slate-300 focus:ring-0 cursor-not-allowed"
              />
              <span>{mode === 'Positive' ? '😊 ' : mode === 'Neutral' ? '😐 ' : '🙁 '}{mode}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="space-y-1.5">
        <label htmlFor="outcomes" className="text-xs font-semibold text-slate-600">Outcomes</label>
        <textarea
          id="outcomes"
          readOnly
          rows={2}
          value={formData.outcomes}
          placeholder="Key outcomes or agreements..."
          className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none resize-none cursor-not-allowed"
        />
      </div>

      <div className="space-y-1.5">
        <label htmlFor="follow-up-actions" className="text-xs font-semibold text-slate-600">Follow-up Actions</label>
        <textarea
          id="follow-up-actions"
          readOnly
          rows={2}
          value={formData.follow_up_actions}
          placeholder="Enter next steps or tasks..."
          className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none resize-none cursor-not-allowed"
        />
      </div>

      <div className="pt-2 space-y-1">
        <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">AI Suggested Follow-ups:</p>
        <div className="text-xs text-blue-500 font-medium space-y-1">
          <p className="hover:underline cursor-pointer">+ Schedule follow-up meeting in 2 weeks</p>
          <p className="hover:underline cursor-pointer">+ Send OncoBoost Phase III PDF</p>
          <p className="hover:underline cursor-pointer">+ Add Dr. Sharma to advisory board invite list</p>
        </div>
      </div>
    </div>
  );
};