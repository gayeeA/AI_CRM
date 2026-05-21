import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../store';

interface Material {
  type: string;
}

interface Sample {
  name: string;
  quantity?: number;
  description?: string;
}

interface InteractionData {
  id?: number;
  hcp_name: string;
  hcp_type: string;
  interaction_type: string;
  date: string;
  time: string;
  attendees?: string;
  topics_discussed?: string;
  materials_shared: Material[];
  samples_distributed: Sample[];
  sentiment: 'Positive' | 'Neutral' | 'Negative';
  outcomes?: string;
  follow_up_actions?: string;
  ai_suggestions: string[];
  ai_summary?: string;
  extracted_entities?: Record<string, any>;
}

interface FormState {
  currentInteraction: InteractionData | null;
  isLoading: boolean;
  error: string | null;
  savedInteractions: InteractionData[];
  hasChanges: boolean;
}

const initialState: FormState = {
  currentInteraction: {
    hcp_name: '',
    hcp_type: 'Doctor',
    interaction_type: 'Meeting',
    date: new Date().toLocaleDateString('en-GB'),
    time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }),
    attendees: '',
    topics_discussed: '',
    materials_shared: [],
    samples_distributed: [],
    sentiment: 'Neutral',
    outcomes: '',
    follow_up_actions: '',
    ai_suggestions: [],
  },
  isLoading: false,
  error: null,
  savedInteractions: [],
  hasChanges: false,
};

const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    // Update single form field
    updateField: (state, action: PayloadAction<{ field: keyof InteractionData; value: any }>) => {
      if (state.currentInteraction) {
        (state.currentInteraction as any)[action.payload.field] = action.payload.value;
        state.hasChanges = true;
      }
    },

    // Update entire interaction data
    updateInteraction: (state, action: PayloadAction<Partial<InteractionData>>) => {
      if (state.currentInteraction) {
        state.currentInteraction = {
          ...state.currentInteraction,
          ...action.payload,
        };
        state.hasChanges = true;
      }
    },

    // Set loading state
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    // Set error
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },

    // Add material
    addMaterial: (state, action: PayloadAction<Material>) => {
      if (state.currentInteraction) {
        state.currentInteraction.materials_shared.push(action.payload);
        state.hasChanges = true;
      }
    },

    // Remove material
    removeMaterial: (state, action: PayloadAction<number>) => {
      if (state.currentInteraction) {
        state.currentInteraction.materials_shared.splice(action.payload, 1);
        state.hasChanges = true;
      }
    },

    // Add sample
    addSample: (state, action: PayloadAction<Sample>) => {
      if (state.currentInteraction) {
        state.currentInteraction.samples_distributed.push(action.payload);
        state.hasChanges = true;
      }
    },

    // Remove sample
    removeSample: (state, action: PayloadAction<number>) => {
      if (state.currentInteraction) {
        state.currentInteraction.samples_distributed.splice(action.payload, 1);
        state.hasChanges = true;
      }
    },

    // Reset form
    resetForm: (state) => {
      state.currentInteraction = {
        hcp_name: '',
        hcp_type: 'Doctor',
        interaction_type: 'Meeting',
        date: new Date().toLocaleDateString('en-GB'),
        time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }),
        attendees: '',
        topics_discussed: '',
        materials_shared: [],
        samples_distributed: [],
        sentiment: 'Neutral',
        outcomes: '',
        follow_up_actions: '',
        ai_suggestions: [],
      };
      state.hasChanges = false;
      state.error = null;
    },

    // Set current interaction (from API)
    setCurrentInteraction: (state, action: PayloadAction<InteractionData>) => {
      state.currentInteraction = action.payload;
      state.hasChanges = false;
    },

    // Add to saved interactions
    addSavedInteraction: (state, action: PayloadAction<InteractionData>) => {
      state.savedInteractions.push(action.payload);
    },

    // Clear changes flag
    clearChanges: (state) => {
      state.hasChanges = false;
    },

    // Update sentiment
    setSentiment: (state, action: PayloadAction<'Positive' | 'Neutral' | 'Negative'>) => {
      if (state.currentInteraction) {
        state.currentInteraction.sentiment = action.payload;
        state.hasChanges = true;
      }
    },

    // Update AI suggestions
    setAISuggestions: (state, action: PayloadAction<string[]>) => {
      if (state.currentInteraction) {
        state.currentInteraction.ai_suggestions = action.payload;
      }
    },
  },
});

export const {
  updateField,
  updateInteraction,
  setLoading,
  setError,
  addMaterial,
  removeMaterial,
  addSample,
  removeSample,
  resetForm,
  setCurrentInteraction,
  addSavedInteraction,
  clearChanges,
  setSentiment,
  setAISuggestions,
} = formSlice.actions;

export const selectFormState = (state: RootState) => state.form;
export const selectCurrentInteraction = (state: RootState) => state.form.currentInteraction;
export const selectIsLoading = (state: RootState) => state.form.isLoading;
export const selectError = (state: RootState) => state.form.error;

export default formSlice.reducer;
