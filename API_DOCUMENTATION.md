# API Endpoints Documentation for Frontend

## Base URL
Your FastAPI app runs on: `http://localhost:8000` (during development)

## Authentication
- **Required for protected endpoints**: Bearer token in Authorization header
- **Format**: `Authorization: Bearer <access_token>`

---

## 1. USER ENDPOINTS (Prefix: `/api/users`)

### 1.1 User Signup
- **Endpoint**: `POST /api/users/signup`
- **Description**: Register a new user
- **Request Body**:
```json
{
  "username": "string",
  "email": "valid_email@example.com",
  "password": "string"
}
```
- **Response** (201 Created):
```json
{
  "message": "User created successfully",
  "token_type": "bearer",
  "access_token": "jwt_token_string"
}
```
- **Error Responses**:
  - `400`: Username or email already exists
  - `422`: Validation error (invalid email format, missing fields)

### 1.2 User Login
- **Endpoint**: `POST /api/users/login`
- **Description**: Authenticate user and get access token
- **Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```
- **Response** (200 OK):
```json
{
  "message": "User logged in successfully",
  "token_type": "bearer",
  "access_token": "jwt_token_string"
}
```
- **Error Responses**:
  - `400`: Invalid username or password
  - `422`: Validation error

### 1.3 Get Current User
- **Endpoint**: `GET /api/users/me`
- **Description**: Get current user's profile information
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: None
- **Response** (200 OK):
```json
{
  "role": "user",
  "username": "string",
  "email": "string",
  "is_active": true,
  "is_verified": false
}
```
- **Error Responses**:
  - `401`: Missing or invalid authorization header
  - `404`: User not found

---

## 2. GROUP ENDPOINTS (Prefix: `/api/groups`)

### 2.1 Create Group
- **Endpoint**: `POST /api/groups/`
- **Description**: Create a new group (requires authentication)
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "name": "string",
  "description": "string (optional)",
  "members": ["member_id_1", "member_id_2"] // optional array of strings
}
```
- **Response** (200 OK):
```json
{
  "message": "Group created successfully",
  "group": {
    "name": "string",
    "description": "string",
    "members": ["array", "of", "member_ids"]
  }
}
```
- **Error Responses**:
  - `401`: Authentication required
  - `422`: Validation error

---

## 3. HQ ENDPOINTS (Note: NOT included in main.py - needs to be added)

**⚠️ IMPORTANT**: The HQ routes are defined in `app/hq/routes.py` but NOT included in `main.py`. 
To use these endpoints, add to main.py:
```python
from app.hq.routes import hq_router
app.include_router(hq_router, prefix="/api/hq")
```

### 3.1 Get All Users
- **Endpoint**: `GET /api/hq/all-users`
- **Description**: Get all users (for HQ dashboard)
- **Request Body**: None
- **Response** (200 OK):
```json
{
  "users": [
    {
      "role": "user",
      "username": "string",
      "email": "string",
      "is_active": true,
      "is_verified": false,
      "created_at": "2025-09-22T10:30:00Z"
    }
  ]
}
```

### 3.2 Get Unverified Users
- **Endpoint**: `GET /api/hq/unverified-users`
- **Description**: Get all users who are not verified
- **Request Body**: None
- **Response** (200 OK):
```json
{
  "unverified_users": [
    {
      "role": "user",
      "username": "string",
      "email": "string",
      "is_active": true,
      "is_verified": false,
      "created_at": "2025-09-22T10:30:00Z"
    }
  ]
}
```

### 3.3 Verify User
- **Endpoint**: `PUT /api/hq/set-verified/{id}`
- **Description**: Set a user as verified
- **Path Parameters**: `id` - MongoDB ObjectId of the user
- **Request Body**: None
- **Response** (200 OK):
```json
{
  "message": "User {id} has been verified"
}
```
- **Error Responses**:
  - `404`: User not found
  - `500`: Database error

### 3.4 Get All Groups
- **Endpoint**: `GET /api/hq/all-groups`
- **Description**: Get all groups in the system
- **Request Body**: None
- **Response** (200 OK):
```json
{
  "groups": [
    {
      "name": "string",
      "members_id": ["user_id_1", "user_id_2"]
    }
  ]
}
```

### 3.5 Create Group (HQ)
- **Endpoint**: `POST /api/hq/create-group`
- **Description**: Create a new group from HQ
- **Request Body**:
```json
{
  "name": "Group A",
  "members_id": ["user_id_1", "user_id_2"] // optional
}
```
- **Response** (200 OK):
```json
{
  "message": "Group created successfully",
  "group": {
    "name": "Group A",
    "members_id": ["user_id_1", "user_id_2"]
  }
}
```

### 3.6 Add Members to Group
- **Endpoint**: `PUT /api/hq/add-members/{group_id}`
- **Description**: Add members to an existing group
- **Path Parameters**: `group_id` - MongoDB ObjectId of the group
- **Request Body**:
```json
{
  "members_id": ["68d1101e5f759ee5b8186525", "68d1147241b456c064c56fa6"]
}
```
- **Response** (200 OK):
```json
{
  "message": "Members added to group {group_id}",
  "added_members": ["68d1101e5f759ee5b8186525", "68d1147241b456c064c56fa6"]
}
```
- **Error Responses**:
  - `404`: Group not found
  - `500`: Database error

### 3.7 Delete Member from Group
- **Endpoint**: `DELETE /api/hq/delete-member/{group_id}/{member_id}`
- **Description**: Remove a member from a group
- **Path Parameters**: 
  - `group_id` - MongoDB ObjectId of the group
  - `member_id` - User ID to remove
- **Request Body**: None
- **Response** (200 OK):
```json
{
  "message": "Member {member_id} removed from group {group_id}"
}
```
- **Error Responses**:
  - `404`: Group not found
  - `500`: Database error

---

## Error Response Format
All errors follow this format:
```json
{
  "detail": "Error message description"
}
```

## Common HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation error, duplicate data)
- **401**: Unauthorized (missing/invalid token)
- **404**: Not Found
- **422**: Unprocessable Entity (validation error)
- **500**: Internal Server Error

## Frontend Implementation Notes

1. **Authentication Flow**:
   - Use signup/login to get access token
   - Store token securely (localStorage/sessionStorage)
   - Include token in Authorization header for protected routes

2. **Token Management**:
   - Check token expiration
   - Implement token refresh if needed
   - Handle 401 responses by redirecting to login

3. **HQ Routes**:
   - Remember to add HQ router to main.py before using
   - HQ routes likely need admin-level authentication (not implemented yet)

4. **Error Handling**:
   - Handle all error status codes appropriately
   - Show user-friendly error messages
   - Validate data on frontend before sending to API

5. **Data Validation**:
   - Email format validation
   - Required field validation
   - Password strength requirements (if needed)