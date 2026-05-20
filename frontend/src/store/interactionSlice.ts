import { createSlice} from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
export interface InteractionState {
  hcp_name: string;
  interaction_type: string;
  date: string;
  time: string;
  attendees: string[];
  topics_discussed: string;
  materials_shared: string[];
  samples_distributed: string[];
  sentiment: 'Positive' | 'Neutral' | 'Negative';
  outcomes: string;
  follow_up_actions: string;
}

const initialState: InteractionState = {
  hcp_name: '',
  interaction_type: 'Meeting',
  date: '19-04-2025',
  time: '19:36',
  attendees: [],
  topics_discussed: '',
  materials_shared: [],
  samples_distributed: [],
  sentiment: 'Neutral',
  outcomes: '',
  follow_up_actions: '',
};

export const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateFormState: (state, action: PayloadAction<Partial<InteractionState>>) => {
      return { ...state, ...action.payload };
    },
    resetForm: () => initialState,
  },
});

export const { updateFormState, resetForm } = interactionSlice.actions;
export default interactionSlice.reducer;