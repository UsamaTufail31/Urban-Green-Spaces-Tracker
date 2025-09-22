# Urban Green Spaces API - Authentication System

## 🔐 JWT Authentication Implementation Summary

### ✅ Components Implemented

#### 1. **Dependencies Added**
- `python-jose[cryptography]==3.3.0` - JWT token handling
- `passlib[bcrypt]==1.7.4` - Password hashing with bcrypt

#### 2. **Database Model**
- **User Model** (`app/models/user.py`)
  - Fields: id, username, email, hashed_password, full_name, role, is_active, created_at, last_login
  - Roles: ADMIN, VIEWER
  - Password hashing with bcrypt

#### 3. **Authentication Utilities** (`app/auth_utils.py`)
- Password hashing and verification
- JWT token creation and verification
- Password strength validation
- Token expiration checking

#### 4. **Authentication Service** (`app/services/auth_service.py`)
- User authentication with username/email and password
- User creation and management
- Password change functionality
- Admin user creation for initial setup

#### 5. **Authentication Router** (`app/routers/auth.py`)
- **POST** `/auth/login` - User login with JWT token response
- **POST** `/auth/register` - Create new user (admin only)
- **GET** `/auth/me` - Get current user info
- **PUT** `/auth/me` - Update current user info
- **PUT** `/auth/change-password` - Change user password
- **GET** `/auth/users` - List all users (admin only)
- **GET** `/auth/users/{user_id}` - Get specific user (admin only)
- **PUT** `/auth/users/{user_id}` - Update user (admin only)
- **DELETE** `/auth/users/{user_id}` - Deactivate user (admin only)
- **POST** `/auth/verify-token` - Verify JWT token
- **POST** `/auth/refresh-token` - Refresh JWT token

#### 6. **Authentication Dependencies** (`app/auth_dependencies.py`)
- `get_current_user()` - Extract authenticated user from JWT
- `get_admin_user()` - Require admin role
- `get_current_user_optional()` - Optional authentication
- Role-based permission checks

#### 7. **Protected Admin Endpoints**
- **Cities Management:**
  - `POST /cities` - Create city (admin only)
  - `PUT /cities/{id}` - Update city (admin only)
  - `DELETE /cities/{id}` - Delete city (admin only)

- **Parks Management:**
  - `POST /parks` - Create park (admin only)
  - `PUT /parks/{id}` - Update park (admin only)
  - `DELETE /parks/{id}` - Delete park (admin only)

- **Green Coverage Management:**
  - `POST /green-coverage` - Create coverage data (admin only)

- **System Management:**
  - `POST /background-tasks/trigger-update` - Manual updates (admin only)
  - `POST /background-tasks/start` - Start scheduler (admin only)
  - `POST /background-tasks/stop` - Stop scheduler (admin only)
  - `POST /cache/cleanup` - Clean cache (admin only)
  - `DELETE /cache/city/{name}` - Invalidate cache (admin only)

#### 8. **Database Initialization**
- Updated `app/init_db.py` to create User table
- Automatic creation of default admin user
- Support for environment variables for admin credentials

#### 9. **Configuration Updates**
- Added JWT settings to `app/config.py`
- JWT secret key, algorithm, and token expiration configuration
- Development and production config templates

### 🚀 Usage



#### Authentication Flow
1. **Login:** POST `/auth/login` with username/email and password
2. **Get Token:** Receive JWT token with 24-hour expiration
3. **Use Token:** Include `Authorization: Bearer <token>` header in requests
4. **Access Admin Routes:** Token must belong to user with 'admin' role



### 🔒 Security Features

1. **Password Security:**
   - Bcrypt hashing with salt
   - Password strength validation (8+ chars, upper, lower, number, special char)
   - No plain text password storage

2. **JWT Security:**
   - Configurable secret key and algorithm
   - Token expiration (24 hours default)
   - Token verification on each request
   - User status checking (active/inactive)

3. **Role-Based Access Control:**
   - Admin vs Viewer roles
   - Protected endpoints require admin role
   - Permission checking dependencies

4. **API Security:**
   - CORS configuration
   - Authentication required for sensitive operations
   - Input validation with Pydantic schemas

### 📚 API Documentation

- **Interactive Docs:** Available at `http://localhost:8001/docs`
- **OpenAPI Schema:** Available at `http://localhost:8001/openapi.json`
- **Authentication:** All endpoints documented with security requirements

### 🧪 Testing

A test script is provided (`test_auth_system.py`) that verifies:
- User login functionality
- Token generation and validation
- Admin endpoint access
- Protected route security
- User management operations

### 🚨 Production Recommendations

1. **Change Default Credentials:** Update admin password immediately
2. **Secure JWT Secret:** Use a strong, random secret key
3. **HTTPS Only:** Use secure connections in production
4. **Environment Variables:** Store sensitive config in environment variables
5. **Database Security:** Use PostgreSQL with proper access controls
6. **Rate Limiting:** Implement rate limiting for auth endpoints
7. **Audit Logging:** Add logging for authentication events

### 📝 Next Steps

1. Implement password reset functionality
2. Add email verification for new users
3. Implement role-based permissions for different resource types
4. Add API key authentication for service-to-service calls
5. Implement session management and logout functionality
6. Add two-factor authentication (2FA) support
