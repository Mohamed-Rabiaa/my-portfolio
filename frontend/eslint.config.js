/**
 * ESLint Configuration File
 * 
 * This file contains the ESLint configuration for the React portfolio application.
 * ESLint is a static code analysis tool for identifying problematic patterns in JavaScript code.
 * This configuration includes React-specific rules and modern JavaScript standards.
 * 
 * @see {@link https://eslint.org/docs/user-guide/configuring} ESLint configuration guide
 * @author Your Name
 * @version 1.0.0
 */

import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

/**
 * ESLint Configuration Array
 * 
 * Defines linting rules and configurations for JavaScript and JSX files.
 * Includes React Hooks rules, React Refresh rules, and custom overrides.
 * 
 * @type {import('eslint').Linter.Config[]}
 */
export default defineConfig([
  /** Global ignore patterns - excludes dist folder from linting */
  globalIgnores(['dist']),
  {
    /** File patterns to apply this configuration to */
    files: ['**/*.{js,jsx}'],
    
    /** Extended configurations from recommended rulesets */
    extends: [
      js.configs.recommended,                    // ESLint recommended rules
      reactHooks.configs['recommended-latest'],  // React Hooks best practices
      reactRefresh.configs.vite,                 // React Refresh for Vite
    ],
    
    /** Language options for parsing JavaScript/JSX */
    languageOptions: {
      ecmaVersion: 2020,           // ECMAScript version
      globals: globals.browser,    // Browser global variables
      parserOptions: {
        ecmaVersion: 'latest',     // Latest ECMAScript features
        ecmaFeatures: { jsx: true }, // Enable JSX parsing
        sourceType: 'module',      // ES6 modules
      },
    },
    
    /** Custom ESLint rules */
    rules: {
      /** Allow unused variables that start with uppercase or underscore (React components, constants) */
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },
])
