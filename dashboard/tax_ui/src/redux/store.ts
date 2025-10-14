// src/redux/store.ts
import {configureStore} from '@reduxjs/toolkit';
import {useDispatch} from 'react-redux'; 
import {combineReducers} from 'redux';
import ClientProfilesReducer from './reducer/user/ClientProfilesReducer';

const reducer = combineReducers({
  clientProfiles: ClientProfilesReducer,
});

export const store = configureStore({
  reducer: reducer,
});
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
export const useAppDispatch = () => useDispatch<AppDispatch>();