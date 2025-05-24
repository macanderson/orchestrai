// ESLint configuration for the web package
// Uses ES Modules syntax and extends the shared config

import sharedConfig from '@orchestrai/eslint-config/base';

export default [
  ...sharedConfig,
  {
    extends: [
      'next/core-web-vitals',
      'plugin:react/recommended',
      'plugin:react-hooks/recommended',
    ],
    plugins: ['react', 'react-hooks'],
    settings: {
      react: {
        version: 'detect',
      },
    },
    env: {
      browser: true,
      node: true,
      es2022: true,
    },
    parserOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      ecmaFeatures: {
        jsx: true,
      },
    },
    rules: {
      // Add any web-specific rules here
      'react/react-in-jsx-scope': 'off', // Not needed in Next.js with React 17+
      'react/prop-types': 'off', // We use TypeScript for type checking
      'react/jsx-uses-react': 'off', // Not needed in Next.js with React 17+
    },
  },
];

