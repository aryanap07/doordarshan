# Security Policy

*Protecting the connections that bring people together.*

Doordarshan takes security seriously. The project includes authentication, Argon2 password hashing, input validation, rate limiting, and automated security checks, but it is still under active development. These measures do not guarantee that every vulnerability has been identified or that every deployment is secure.

## Supported Versions

Doordarshan is currently in **Alpha**. Security fixes are generally directed at the latest maintained project code.

| Version or branch | Security support |
|---|---|
| Latest maintained code | Best effort |
| Older releases and branches | Not guaranteed |

If you are using an older release, upgrade to the latest available version where practical and review the relevant release notes and changes.

## Reporting a Vulnerability

**Please do not report suspected security vulnerabilities in public issues, pull requests, or discussions.**

Use GitHub's private vulnerability reporting feature for this repository, if it is enabled:

1. Open the Doordarshan repository on GitHub.
2. Select the **Security** tab.
3. Look for **Report a vulnerability** and submit a private report.

Repository: https://github.com/aryanap07/doordarshan

If private vulnerability reporting is unavailable, contact the repository maintainer privately through a verified contact method listed on the maintainer's GitHub profile. Do not include exploit details in a public issue while seeking a contact.

Please do not assume that a public issue is a private report.

### What to Include

Where possible, provide:

- A concise description of the vulnerability and its potential impact.
- The affected version, commit, component, or endpoint.
- Reproduction steps or a minimal proof of concept.
- Relevant logs or request examples, with secrets and personal data removed.
- A suggested mitigation, if you have one.

Please share only the information needed to demonstrate the issue. Do not access, modify, or disclose other people's data, disrupt services, or test systems without authorization.

## Response and Disclosure

The maintainers will make a reasonable effort to review private reports, assess their impact, and coordinate a fix and disclosure. Response times depend on maintainer availability and the complexity of the issue; a specific response or resolution time is not guaranteed.

Please allow time for investigation and remediation before publicly disclosing an unpatched vulnerability. If a report is accepted, the maintainers may coordinate disclosure after a fix or mitigation is available.

## Security Scope

Security reports may include issues affecting:

- **Authentication and access control:** registration, login, JWT validation, token expiration, and authorization checks.
- **Passwords and secrets:** password handling, credential exposure, or unsafe secret management.
- **REST APIs:** authorization failures, input validation, data exposure, or unintended access to resources.
- **WebSocket connections:** authentication, room membership, message validation, cross-room access, and connection handling.
- **Meeting rooms and participants:** unauthorized joining, participant impersonation, or access to another room's data.
- **Database and migrations:** injection risks, unintended data exposure, or unsafe migration behavior.
- **Dependencies and build workflows:** vulnerabilities in project dependencies or repository automation.
- **Deployment configuration:** security-relevant defaults or configuration that could expose the application.

Reports should demonstrate a realistic security impact. General hardening suggestions without a specific vulnerability may be better suited to a normal issue or discussion.

## Deployment and Configuration Guidance

Operators deploying Doordarshan should review their environment and deployment configuration carefully.

### Secrets and Credentials

- Generate a strong, unique `SECRET_KEY` for each environment.
- Keep `.env` files, database credentials, JWT signing secrets, and TURN credentials out of version control.
- Configure production secrets through the deployment platform's secret-management facilities.
- Rotate any credential that may have been exposed.
- Do not place secrets in logs, screenshots, issue reports, or pull requests.

### Network and Transport

- Use HTTPS for browser traffic and WSS for WebSocket connections in production.
- Restrict database access to trusted application services and administrators.
- Configure firewall rules and deployment networking deliberately.
- Configure TURN services and credentials appropriately for the deployment.
- Avoid exposing development servers or administrative interfaces to untrusted networks.

### Authentication and Application Behavior

- Use appropriate token lifetimes and protect issued tokens.
- Review authorization rules for every protected resource and room operation.
- Validate incoming API and WebSocket messages.
- Configure rate limiting and request-size limits appropriate to the deployment.
- Review logs to ensure they do not contain credentials or sensitive meeting information.

### Dependencies and CI

Doordarshan uses automated checks, including CodeQL and dependency auditing. These checks are useful signals, not proof that the application is free of vulnerabilities.

- Review dependency advisories and security-audit findings.
- Update affected dependencies with compatibility and regression testing.
- Review changes to GitHub Actions workflows and other automation.
- Do not treat a passing CI run as a complete security assessment.

## Responsible Testing

Only test deployments and accounts that you own or have explicit permission to assess. Avoid actions that could disrupt meetings, expose participant information, affect other users, or damage data. Use a local development environment for testing whenever possible.

## Security Status

Doordarshan is an actively evolving Alpha project. Its security posture may change as features and deployment practices mature. Review this policy and the application's configuration before using it in environments that handle sensitive communications.

Thank you for helping keep Doordarshan and its users safer.
