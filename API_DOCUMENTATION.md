# HQ API Documentation

## Base URL
```
/api/hq
```

## Endpoints

### 1. Get All Users
**GET** `/all-users`

Get all users in the system (excluding passwords).

**Request:**
- No body required

**Response:**
```json
{
  "users": [
    {
      "_id": "68d1101e5f759ee5b8186525",
      "email": "user@example.com",
      "name": "John Doe",
      "is_verified": true,
      "role": "user"
    }
  ]
}
```

### 2. Get Unverified Users
**GET** `/unverified-users`

Get all users who are not yet verified.

**Request:**
- No body required

**Response:**
```json
{
  "unverified_users": [
    {
      "email": "newuser@example.com",
      "name": "Jane Smith",
      "is_verified": false,
      "role": "user"
    }
  ]
}
```

### 3. Set User as Verified
**PUT** `/set-verified/{id}`

Mark a user as verified by their ID.

**Request:**
- URL Parameter: `id` (string) - User ID

**Response:**
```json
{
  "message": "User 68d1101e5f759ee5b8186525 has been verified"
}
```

### 4. Get All Groups
**GET** `/all-groups`

Get all groups with their member details.

**Request:**
- No body required

**Response:**
```json
{
  "groups": [
    {
      "_id": "68d2bffcd6aa5eede5858bf6",
      "name": "Development Team",
      "members": [
        {
          "email": "dev1@example.com",
          "name": "Developer One",
          "is_verified": true,
          "role": "developer"
        }
      ]
    }
  ]
}
```

### 5. Create Group
**POST** `/create-group`

Create a new group with specified name and members.

**Request Body:**
```json
{
  "name": "New Team",
  "members_id": ["68d1101e5f759ee5b8186525", "68d1101e5f759ee5b8186526"]
}
```

**Response:**
```json
{
  "message": "Group created successfully",
  "group": {
    "name": "New Team",
    "members_id": ["68d1101e5f759ee5b8186525", "68d1101e5f759ee5b8186526"]
  }
}
```

### 6. Add Members to Group
**PUT** `/add-members/{group_id}`

Add new members to an existing group.

**Request:**
- URL Parameter: `group_id` (string) - Group ID

**Request Body:**
```json
{
  "members": ["68d1101e5f759ee5b8186527", "68d1101e5f759ee5b8186528"]
}
```

**Response:**
```json
{
  "message": "Members added to group 68d2bffcd6aa5eede5858bf6",
  "added_members": ["68d1101e5f759ee5b8186527", "68d1101e5f759ee5b8186528"]
}
```

### 7. Delete Member from Group
**DELETE** `/delete-member/{group_id}/{member_id}`

Remove a specific member from a group.

**Request:**
- URL Parameters: 
  - `group_id` (string) - Group ID
  - `member_id` (string) - Member ID to remove

**Response:**
```json
{
  "message": "Member 68d1101e5f759ee5b8186525 removed from group 68d2bffcd6aa5eede5858bf6"
}
```

## Error Responses

All endpoints may return these error responses:

**404 Not Found:**
```json
{
  "detail": "User not found"
}
```
or
```json
{
  "detail": "Group not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Database error: [error message]"
}
```

## Notes

- All user IDs and group IDs are MongoDB ObjectId strings
- The `members` field in add-members request contains an array of user IDs
- Duplicate members are automatically prevented when adding to groups
- Passwords are never included in any response
