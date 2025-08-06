# Secure Directory System (Annuaire Sécurisé)

A directory system built with Flask and MySQL, implementing security principles and testing.

## Security Features

The system implements JWT token-based authentication, role-based authorization, secure password hashing with PBKDF2, audit logging for security events, and input validation and sanitization.

Security monitoring logs all security-relevant events including user login attempts both successful and failed, password changes, role modifications, user creation and deletion, and API access patterns. Logs were structured for easy integration with security monitoring tools.

## CI Pipeline

The GitHub Actions pipeline automatically sets up the test environment with Python 3.8 and MySQL services, installs dependencies including system libraries, waits for database availability before running tests, creates test databases with proper isolation, runs the complete test suite with detailed output, and generates coverage reports showing code coverage metrics.

Pipeline triggers include pushes to main, develop, or feature branches, pull requests targeting main or develop, and manual workflow dispatch.

## Test Suite

The project includes comprehensive test coverage across multiple layers.

### Model Tests (test_models.py)

The `test_create_user` function validates user model creation with proper username and role assignment. The `test_create_auth` function ensures authentication model correctly stores user credentials and metadata.

### API Route Tests (test_routes.py)

The `test_register_user` function tests the admin-only user creation endpoint, verifies proper authentication token requirement, and validates user data structure in response.

The `test_login` function tests user authentication with valid credentials, verifies JWT token generation and return, and ensures proper error handling for invalid credentials.

The `test_list_users` function tests the authenticated user listing endpoint, verifies that only authenticated users can access directory, and validates user data structure in response.

### Service Layer Tests (test_user_service.py)

The `test_user_creation` function tests the complete user creation workflow, verifies default role assignment as regular user, and ensures proper data persistence across databases.

The `test_password_change` function tests secure password update functionality, verifies old password validation before change, ensures new password is properly hashed and stored, and tests authentication with new password.

The `test_user_promotion` function tests role elevation from user to admin, verifies proper privilege escalation, and ensures role changes persist correctly.

## API Documentation

- `POST /api/login` - User authentication
- `POST /api/users` - Create new user (admin only)
- `GET /api/users` - List users (authenticated users only)
- `PUT /api/users/{id}/password` - Change password
- `PUT /api/users/{id}/promote` - Promote to admin (admin only)
- `PUT /api/users/{id}/demote` - Demote to user (admin only)
- `DELETE /api/users/{id}` - Delete user (admin or self)
