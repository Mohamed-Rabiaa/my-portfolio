/**
 * @fileoverview Main entry point for the Portfolio React application.
 * This file initializes the React application and renders it to the DOM.
 * 
 * @author Portfolio Application
 * @version 1.0.0
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

/**
 * Application initialization and rendering.
 * 
 * This is the main entry point of the React application. It:
 * - Creates a React root using the new React 18 createRoot API
 * - Wraps the App component in StrictMode for development checks
 * - Renders the application to the DOM element with id 'root'
 * 
 * StrictMode helps identify potential problems by:
 * - Identifying components with unsafe lifecycles
 * - Warning about legacy string ref API usage
 * - Warning about deprecated findDOMNode usage
 * - Detecting unexpected side effects
 * - Detecting legacy context API
 * 
 * @see {@link https://react.dev/reference/react/StrictMode} React StrictMode documentation
 * @see {@link https://react.dev/reference/react-dom/client/createRoot} createRoot API documentation
 */
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
