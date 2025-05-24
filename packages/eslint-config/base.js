// Custom ESLint base config for orchestrai monorepo
// Usage: import this file in your .eslintrc.js as: import config from 'eslint-config/base'

import turboConfig from 'eslint-config-turbo/flat';

export default [
  ...turboConfig,
  // Other configuration
  {
    rules: {
      'turbo/no-undeclared-env-vars': [
        'error',
        {
          allowList: ['^ENV_[A-Z]+$'],
        },
      ],
    },
  },
];
