# HQ Delete Endpoints Documentation

## Base URL
```
/api/hq
```

## Delete Endpoints

### 1. Delete Member from Group
**DELETE** `/delete-member/{group_id}/{member_id}`

Remove a specific member from a group.

**URL Parameters:**
- `group_id` (string) - The group ID
- `member_id` (string) - The member ID to remove

**Example:**
```
DELETE /api/hq/delete-member/68d2bffcd6aa5eede5858bf6/68d1101e5f759ee5b8186525
```

**Response:**
```json
{
  "message": "Member 68d1101e5f759ee5b8186525 removed from group 68d2bffcd6aa5eede5858bf6"
}
```

### 2. Delete Group
**DELETE** `/delete-group/{group_id}`

Delete an entire group by its ID.

**URL Parameters:**
- `group_id` (string) - The group ID to delete

**Example:**
```
DELETE /api/hq/delete-group/68d2bffcd6aa5eede5858bf6
```

**Response:**
```json
{
  "message": "Group 68d2bffcd6aa5eede5858bf6 has been deleted"
}
```

### 3. Delete User
**DELETE** `/delete-user/{user_id}`

Delete a user and remove them from all groups.

**URL Parameters:**
- `user_id` (string) - The user ID to delete

**Example:**
```
DELETE /api/hq/delete-user/68d1101e5f759ee5b8186525
```

**Response:**
```json
{
  "message": "User 68d1101e5f759ee5b8186525 has been deleted"
}
```

**Note:** This also automatically removes the user from any groups they were a member of.

## Error Responses

**404 Not Found:**
```json
{
  "detail": "Group not found"
}
```
or
```json
{
  "detail": "User not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Database error: [error message]"
}
```

## Frontend Usage Examples

### JavaScript/Fetch
```javascript
// Delete member from group
fetch('/api/hq/delete-member/GROUP_ID/MEMBER_ID', {
  method: 'DELETE'
})

// Delete group
fetch('/api/hq/delete-group/GROUP_ID', {
  method: 'DELETE'
})

// Delete user
fetch('/api/hq/delete-user/USER_ID', {
  method: 'DELETE'
})
```

### Axios
```javascript
// Delete member from group
axios.delete(`/api/hq/delete-member/${groupId}/${memberId}`)

// Delete group
axios.delete(`/api/hq/delete-group/${groupId}`)

// Delete user
axios.delete(`/api/hq/delete-user/${userId}`)
```
