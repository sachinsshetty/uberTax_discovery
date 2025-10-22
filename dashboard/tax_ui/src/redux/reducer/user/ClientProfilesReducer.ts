import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

const API_URL = import.meta.env.VITE_DWANI_API_BASE_URL || 'http://localhost:8000/';

export const fetchClientProfiles = createAsyncThunk<
  Array<{
    clientId: string;
    companyName: string;
    country: string;
    newRegulation: string;
    deadline: string | null;
    status: string;
  }>,
  void,
  { rejectValue: string }
>(
  'sanjeeviniApp/fetchClientProfiles',
  async (_, thunkAPI) => {
    try {
      const url = `${API_URL}api/clients`;
      console.log('Redux fetching from:', url); // Debug log
      const response = await fetch(url);
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Redux HTTP ${response.status}: ${response.statusText} - Body: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Redux fetched clients:', data); // Debug log
      return data;
    } catch (error) {
      console.error('Redux error fetching clients:', error);
      return thunkAPI.rejectWithValue('Failed to fetch clients.');
    }
  }
);

interface ClientProfile {
  clientId: string;
  companyName: string;
  country: string;
  newRegulation: string;
  deadline: string | null;
  status: string;
}

interface ClientState {
  clientData: ClientProfile[];
  loading: boolean;
  error: string | null;
}

const initialState: ClientState = {
  clientData: [],
  loading: false,
  error: null,
};

export const clientSlice = createSlice({
  name: 'clientProfiles',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchClientProfiles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchClientProfiles.fulfilled, (state, action) => {
        state.loading = false;
        state.clientData = action.payload;
      })
      .addCase(fetchClientProfiles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Something went wrong';
      });
  },
});

export default clientSlice.reducer;