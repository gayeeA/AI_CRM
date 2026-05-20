import { createStore } from "redux";

const initialState = {
  interactions: []
};

function reducer(state = initialState, action) {
  switch (action.type) {
    case "SET_INTERACTIONS":
      return { ...state, interactions: action.payload };
    default:
      return state;
  }
}

export const store = createStore(reducer);