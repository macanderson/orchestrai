# Global Cursor Rules

## 1. Developer Information

- Name: Mac Anderson
- Email: mac@macanderson.com
- Website: macanderson.com
- Github: https://github.com/macanderson
- Company Name: The Unnatural Group, LLC
- Default License: Apache v2.0

## 2. Code Style & Formatting

- Indentation: 2 spaces for all languages
- Line length: 100 characters maximum
- File endings: LF (Unix-style)
- Trailing whitespace: None
- Final newline: Required
- UTF-8 encoding: Required

## 3. Logging & Debugging

- Use structured logging over console.log/print
- Log levels: ERROR, WARN, INFO, DEBUG, TRACE
- Include context in log messages
- Use appropriate log levels for different environments
- Avoid logging sensitive information
- Include request IDs in logs for tracing

## 4. Error Handling

- Use try/catch blocks appropriately
- Custom error classes for domain-specific errors
- Meaningful error messages
- Proper error propagation
- Log errors with full context
- Handle async errors properly

## 5. Testing

- Unit tests required for all business logic
- Integration tests for API endpoints
- Test coverage minimum: 80%
- Use meaningful test descriptions
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies

## 6. Documentation

- JSDoc/TSDoc for TypeScript/JavaScript
- Docstrings for Python
- README.md in all projects
- API documentation using OpenAPI/Swagger
- Code comments for complex logic
- Keep documentation up to date

## 7. Security

- Input validation
- Output encoding
- Use parameterized queries
- Follow OWASP guidelines
- Regular dependency updates
- Security headers in web apps

## 8. Performance

- Optimize database queries
- Use appropriate caching
- Implement pagination for large datasets
- Monitor memory usage
- Profile performance bottlenecks
- Use async/await appropriately

## 9. Version Control

- Semantic versioning
- Conventional commits
- Feature branches
- Pull request reviews
- No direct commits to main
- Keep commits atomic

## 10. Dependencies

- Pin dependency versions
- Regular security audits
- Minimal dependencies
- Document dependency decisions
- Use lock files
- Regular updates

## 11. Environment

- Use environment variables
- Separate configs per environment
- No secrets in code
- Use .env files for local dev
- Document environment setup
- Use config validation

## 12. CI/CD

- Automated testing
- Linting checks
- Type checking
- Security scanning
- Automated deployments
- Environment-specific pipelines
- Use GitHub Actions for CI/CD

## 13. Code Organization

- Use the following directory structure for monorepo:

```text
my-project/
├── apps/
│   ├── api/                    # Python FastAPI backend
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── services/
│   │   │   │   ├── models/
│   │   │   │   ├── utils/
│   │   │   │   ├── tests/
│   │   │   │   └── __init__.py
│   │   ├── tests/
│   │   ├── .env
│   │   ├── .env.local
│   │   ├── .env.development.local
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── requirements.txt
│   │
│   └── web/                    # Next.js frontend
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   ├── lib/
│       │   ├── styles/
│       │   └── types/
│       ├── public/
│       ├── .env
│       ├── .env.local
│       ├── .env.development.local
│       ├── next.config.js
│       ├── package.json
│       ├── tsconfig.json
│       └── README.md
│
├── packages/
│   ├── db/                     # Shared database package
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── ui/                     # Shared UI components
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── config/                 # Shared configuration
│       ├── eslint/
│       ├── typescript/
│       ├── package.json
│       └── tsconfig.json
│
├── .github/
│   └── workflows/              # GitHub Actions workflows
│
├── .vscode/                    # VS Code settings
│
├── turbo.json                  # Turborepo configuration
├── package.json               # Root package.json
├── tsconfig.json             # Root TypeScript config
├── .gitignore
├── .prettierrc
├── .eslintrc.js
├── README.md
└── vercel.json               # Vercel deployment config
```
