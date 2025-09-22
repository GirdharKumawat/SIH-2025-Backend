# Chat Communication Prototype - Essential FastAPI Endpoints

## 🔐 Authentication Endpoints

### 1. User Registration/Signup
```python
POST /auth/signup
```
**Body:** 
```json
{
    "username": "john_doe",
    "password": "secure_password",
    "full_name": "John Doe",
    "service_id": "MIL001234",
    "email": "john@defense.mil",
    "phone": "+1234567890",
    "justification": "Need access for Operation XYZ"
}
```
**Response:** 
```json
{
    "message": "Registration submitted successfully",
    "user_id": "uuid",
    "status": "pending_approval"
}
```

### 2. User Login
```python
POST /auth/login
```
**Body:** 
```json
{
    "username": "john_doe",
    "password": "secure_password"
}
```
**Response:** 
```json
{
    "access_token": "jwt_token",
    "token_type": "bearer",
    "user": {
        "user_id": "uuid",
        "username": "john_doe",
        "full_name": "John Doe",
        "status": "approved|pending|rejected",
        "groups": ["group_id_1", "group_id_2"]
    }
}
```

### 3. Get Current User Info
```python
GET /auth/me
```
**Headers:** `Authorization: Bearer <token>`
**Response:** 
```json
{
    "user_id": "uuid",
    "username": "john_doe",
    "full_name": "John Doe",
    "status": "approved",
    "groups": [
        {
            "group_id": "uuid",
            "name": "Alpha Team",
            "description": "Primary operations team"
        }
    ]
}
```

## 👥 User Group Management

### 4. Get User's Groups
```python
GET /groups/group_id/
```
**Headers:** `Authorization: Bearer <token>`
**Response:** 
```json
{
    "group": {
            "group_id": "uuid",
            "name": "Alpha Team",
            "description": "Primary operations team",
            "member_count": 5,
            "last_message": {
                "content": "Meeting at 0800",
                "timestamp": "2024-01-15T10:30:00Z",
                "sender": "Jane Smith"
            }
        }
    
}
```

 
## 💬 Chat/Messaging Endpoints

### 6. Get Group Messages
```python
GET /messages/group/{group_id}
```
**Query Params:** `?limit=50&offset=0`
**Headers:** `Authorization: Bearer <token>`
**Response:** 
```json
{
    "messages": [
        {
            "message_id": "uuid",
            "sender": {
                "user_id": "uuid",
                "username": "jane_doe",
                "full_name": "Jane Doe"
            },
            "content": "encrypted_message_content",
            "message_type": "text",
            "timestamp": "2024-01-15T10:30:00Z",
            "edited": false
        }
    ],
    "total": 150,
    "has_more": true
}
```

### 7. Send Message to Group
```python
POST /messages/send
```
**Body:** 
```json
{
    "group_id": "uuid",
    "content": "encrypted_message_content",
    "message_type": "text"
}
```
**Response:** 
```json
{
    "message_id": "uuid",
    "timestamp": "2024-01-15T10:30:00Z",
    "status": "sent"
}
```

### 8. WebSocket for Real-time Messages
```python
WS /ws/chat/{group_id}
```
**Headers:** `Authorization: Bearer <token>`
**Purpose:** Real-time message delivery and typing indicators

## 🏢 HQ Management Endpoints

### 9. HQ Login
```python
POST /hq/auth/login
```
**Body:** 
```json
{
    "admin_username": "hq_admin",
    "admin_password": "secure_admin_pass",
    "role": "administrator"
}
```
**Response:** 
```json
{
    "access_token": "jwt_admin_token",
    "token_type": "bearer",
    "admin": {
        "admin_id": "uuid",
        "username": "hq_admin",
        "role": "administrator",
    }
}
```

### 10. Get Pending User Registrations
```python
GET /hq/users/pending
```
**Headers:** `Authorization: Bearer <admin_token>`
**Response:** 
```json
{
    "pending_users": [
        {
            "user_id": "uuid",
            "username": "john_doe",
            "full_name": "John Doe",
            "service_id": "MIL001234",
            "email": "john@defense.mil",
            "justification": "Need access for Operation XYZ",
            "submitted_at": "2024-01-15T09:00:00Z"
        }
    ]
}
```

### 11. Approve/Reject User Registration
```python
POST /hq/users/{user_id}/approve
```
**Body:** 
```json
{
    "action": "approve|reject",
    "reason": "Verified service record and clearance"
}
```
**Response:** 
```json
{
    "message": "User approved successfully",
    "user_id": "uuid",
    "status": "approved"
}
```

### 12. Get All Approved Users
```python
GET /hq/users
```
**Query Params:** `?status=approved&limit=50&offset=0`
**Headers:** `Authorization: Bearer <admin_token>`
**Response:** 
```json
{
    "users": [
        {
            "user_id": "uuid",
            "username": "john_doe",
            "full_name": "John Doe",
            "status": "approved",
            "groups": ["group_id_1"],
            "last_login": "2024-01-15T08:30:00Z",
            "created_at": "2024-01-10T10:00:00Z"
        }
    ],
    "total": 25
}
```

### 13. Create New Group
```python
POST /hq/groups/create
```
**Body:** 
```json
{
    "name": "Alpha Team",
    "description": "Primary operations team",
    "clearance_level": "SECRET",
    "initial_members": ["user_id_1", "user_id_2"]
}
```
**Response:** 
```json
{
    "group_id": "uuid",
    "name": "Alpha Team",
    "e2ee_key": "generated_encryption_key",
    "created_at": "2024-01-15T11:00:00Z"
}
```

### 14. Get All Groups
```python
GET /hq/groups
```
**Headers:** `Authorization: Bearer <admin_token>`
**Response:** 
```json
{
    "groups": [
        {
            "group_id": "uuid",
            "name": "Alpha Team",
            "description": "Primary operations team",
            "member_count": 5,
            "created_at": "2024-01-15T11:00:00Z",
            "last_activity": "2024-01-15T14:30:00Z"
        }
    ]
}
```

### 15. Add User to Group
```python
POST /hq/groups/{group_id}/add-member
```
**Body:** 
```json
{
    "user_id": "uuid",
    "role": "member|admin"
}
```
**Response:** 
```json
{
    "message": "User added to group successfully",
    "group_id": "uuid",
    "user_id": "uuid"
}
```

### 16. Get Group Join Requests
```python
GET /hq/groups/join-requests
```
**Query Params:** `?status=pending&group_id=uuid`
**Headers:** `Authorization: Bearer <admin_token>`
**Response:** 
```json
{
    "requests": [
        {
            "request_id": "uuid",
            "user": {
                "user_id": "uuid",
                "username": "john_doe",
                "full_name": "John Doe"
            },
            "group": {
                "group_id": "uuid",
                "name": "Alpha Team"
            },
            "justification": "Need access for current assignment",
            "requested_at": "2024-01-15T12:00:00Z",
            "status": "pending"
        }
    ]
}
```

### 17. Approve/Reject Group Join Request
```python
POST /hq/groups/join-requests/{request_id}/respond
```
**Body:** 
```json
{
    "action": "approve|reject",
    "reason": "User has appropriate clearance"
}
```
**Response:** 
```json
{
    "message": "Join request approved",
    "request_id": "uuid",
    "status": "approved"
}
```

## 📊 Additional Utility Endpoints

### 18. Get Group Members (for users)
```python
GET /groups/{group_id}/members
```
**Headers:** `Authorization: Bearer <token>`
**Response:** 
```json
{
    "members": [
        {
            "user_id": "uuid",
            "username": "jane_doe",
            "full_name": "Jane Doe",
            "role": "admin",
            "joined_at": "2024-01-10T10:00:00Z",
            "last_seen": "2024-01-15T14:00:00Z"
        }
    ]
}
```

### 19. User Activity Status
```python
GET /users/status
```
**Headers:** `Authorization: Bearer <token>`
**Response:** 
```json
{
    "user_id": "uuid",
    "online": true,
    "last_seen": "2024-01-15T14:30:00Z"
}
```

### 20. System Health Check
```python
GET /health
```
**Response:** 
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T14:30:00Z",
    "services": {
        "database": "connected",
        "redis": "connected"
    }
}
```

## 🔄 User Flow Summary

### User Journey:
1. **Signup** → `POST /auth/signup`
2. **Wait for approval** → HQ uses `GET /hq/users/pending` & `POST /hq/users/{id}/approve`
3. **Login** → `POST /auth/login`
4. **Request group join** → `POST /groups/join-request`
5. **Wait for group approval** → HQ uses `GET /hq/groups/join-requests` & `POST /hq/groups/join-requests/{id}/respond`
6. **Start chatting** → `GET /groups/my-groups`, `GET /messages/group/{id}`, `POST /messages/send`

### HQ Journey:
1. **Login** → `POST /hq/auth/login`
2. **Review pending users** → `GET /hq/users/pending`
3. **Approve users** → `POST /hq/users/{id}/approve`
4. **Create groups** → `POST /hq/groups/create`
5. **Manage group requests** → `GET /hq/groups/join-requests` & approve/reject
6. **Monitor activity** → `GET /hq/users`, `GET /hq/groups`

## 🔒 Security Notes
- All user endpoints require JWT authentication
- All HQ endpoints require admin JWT with elevated permissions
- Message content should be E2EE encrypted before sending
- Rate limiting should be implemented on auth endpoints
- Input validation required on all endpoints