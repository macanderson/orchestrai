// ESLint flat configuration for web package
import sharedConfig from '@orchestrai/eslint-config/base';
import { FlatCompat } from '@eslint/eslintrc';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';

// Set up dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Create compatibility layer for working with traditional ESLint configs
const compat = new FlatCompat({
  baseDirectory: __dirname,
});

// Import Next.js config using the compatibility layer
const nextConfig = compat.extends(
  'next/core-web-vitals',
  'next/typescript'
);

export default [
  ...sharedConfig,
  ...nextConfig,
  {
    // Apply to all JavaScript and TypeScript files
    files: ['**/*.{js,jsx,ts,tsx}'],
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooksPlugin,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        React: 'readonly',
        JSX: 'readonly',
      },
    },
    rules: {
      // Add any web-specific rules here
      'react/react-in-jsx-scope': 'off', // Not needed in Next.js with React 17+
      'react/prop-types': 'off',         // We use TypeScript for type checking
      'react/jsx-uses-react': 'off',     // Not needed in Next.js with React 17+
    },
  },
];
