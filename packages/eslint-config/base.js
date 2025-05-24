// Custom ESLint base config for orchestrai monorepo
// Usage: require this file in your .eslintrc.js as: require('eslint-config/base')

const turboConfig = require('eslint-config-turbo/flat');

module.exports = [
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
