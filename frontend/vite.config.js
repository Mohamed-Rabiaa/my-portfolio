/**
 * Vite Configuration File
 * 
 * This file contains the Vite build tool configuration for the React portfolio application.
 * Vite is a fast build tool that provides instant server start and lightning fast HMR.
 * 
 * @see {@link https://vite.dev/config/} Official Vite configuration documentation
 * @author Your Name
 * @version 1.0.0
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Vite Configuration Object
 * 
 * Defines the build configuration for the development and production environments.
 * Currently configured with React plugin for JSX transformation and Fast Refresh.
 * 
 * @type {import('vite').UserConfig}
 */
export default defineConfig({
  /** 
   * Vite plugins array
   * - react(): Enables React support with Fast Refresh for development
   */
  plugins: [react()],
})
