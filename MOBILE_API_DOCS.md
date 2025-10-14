# 📱 Mobile App API Documentation

## 🌟 Overview
This API provides secure chat functionality for mobile applications with user authentication, group management, file sharing, and real-time messaging via WebSocket connections.

**Base URL**: `https://your-api-domain.com/api`

---

## 🔐 Authentication

All endpoints (except signup/login) require authentication using Bearer token in the Authorization header.

```
Authorization: Bearer your_jwt_token_here
```

---

## 👤 User Management

### 📝 Sign Up
Create a new user account.

**Endpoint**: `POST /users/signup`

**Request Body**:
```json
{
  "username": "john_doe",
  "email": "john@example.com", 
  "password": "securePassword123"
}
```

**Success Response** (200):
```json
{
  "message": "User created successfully",
  "token_type": "bearer",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
- `400`: Username/email already exists
- `422`: Invalid email format

---

### 🔑 Login
Authenticate existing user.

**Endpoint**: `POST /users/login`

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Success Response** (200):
```json
{
  "message": "User logged in successfully",
  "token_type": "bearer", 
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Response**:
- `400`: Invalid username or password

---

### 👤 Get My Profile
Retrieve current user's profile information.

**Endpoint**: `GET /users/me`

**Headers**: `Authorization: Bearer {token}`

**Success Response** (200):
```json
{
  "_id": "60a7c8b4f1d2e3a4b5c6d7e8",
  "role": "user",
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "is_verified": false
}
```

**Error Responses**:
- `401`: Invalid/missing token
- `404`: User not found

---

### 👥 Get My Groups
Retrieve all groups the current user belongs to.

**Endpoint**: `GET /users/user-groups`

**Headers**: `Authorization: Bearer {token}`

**Success Response** (200):
```json
{
  "groups": [
    {
      "_id": "60a7c8b4f1d2e3a4b5c6d7e9",
      "name": "Team Alpha",
      "symmetric_key": "base64encodedkey==",
      "members": [
        {
          "_id": "60a7c8b4f1d2e3a4b5c6d7e8",
          "username": "john_doe"
        },
        {
          "_id": "60a7c8b4f1d2e3a4b5c6d7ea",
          "username": "jane_smith"
        }
      ]
    }
  ]
}
```

**Error Responses**:
- `401`: Invalid/missing token
- `500`: Database error

---

## 💬 Messaging

### 📤 Upload File
Upload images or documents for sharing in chat.

**Endpoint**: `POST /messages/upload`

**Content-Type**: `multipart/form-data`

**Form Data**:
- `file`: File to upload (max 10MB)
- `access_token`: JWT token

**Supported File Types**:
- Images: PNG, JPG, JPEG
- Documents: PDF

**Success Response** (200):
```json
{
  "type": "file",
  "filename": "document.pdf",
  "url": "https://bucket.s3.amazonaws.com/unique-filename.pdf"
}
```

**Error Responses**:
- `400`: No file uploaded / File too large / Unsupported file type
- `401`: Invalid access token

---

### 🔌 WebSocket Connection
Real-time messaging via WebSocket.

**Endpoint**: `ws://your-domain.com/api/messages/ws?token={jwt_token}`

**Connection**:
```javascript
const websocket = new WebSocket('ws://your-domain.com/api/messages/ws?token=your_jwt_token');
```

#### 📨 Send Message
```json
{
  "group_id": "60a7c8b4f1d2e3a4b5c6d7e9",
  "message": "Hello everyone!"
}
```

#### 📥 Receive Message
```json
{
  "group_id": "60a7c8b4f1d2e3a4b5c6d7e9",
  "group_name": "Team Alpha",
  "sender_id": "60a7c8b4f1d2e3a4b5c6d7e8",
  "sender_username": "john_doe",
  "message": "Hello everyone!",
  "created_at": "2025-10-04T10:30:00Z"
}
```

#### 📁 Send File Message
After uploading a file, send the response as message:
```json
{
  "group_id": "60a7c8b4f1d2e3a4b5c6d7e9",
  "message": {
    "type": "file",
    "filename": "document.pdf", 
    "url": "https://bucket.s3.amazonaws.com/file.pdf"
  }
}
```

#### ⚠️ System Commands
You may receive system commands (like device wipe):
```json
{
  "command": "wipe_device",
  "message": "Your device data will be wiped by administrator",
  "reason": "Security measure"
}
```

**WebSocket Events**:
- `onopen`: Connection established
- `onmessage`: New message received
- `onclose`: Connection closed
- `onerror`: Connection error

---

## 📊 Mobile App Implementation Guide

### 🔧 Setup Steps

#### 1. Authentication Flow
```javascript
// 1. User Registration
const signUp = async (username, email, password) => {
  const response = await fetch('/api/users/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    // Store token in secure storage
    await AsyncStorage.setItem('access_token', data.access_token);
    return data;
  }
};

// 2. User Login
const login = async (username, password) => {
  const response = await fetch('/api/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    await AsyncStorage.setItem('access_token', data.access_token);
    return data;
  }
};

// 3. Get Profile
const getProfile = async () => {
  const token = await AsyncStorage.getItem('access_token');
  const response = await fetch('/api/users/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.ok) {
    return await response.json();
  }
};
```

#### 2. WebSocket Integration
```javascript
class ChatService {
  constructor() {
    this.websocket = null;
    this.messageHandlers = [];
  }
  
  async connect() {
    const token = await AsyncStorage.getItem('access_token');
    this.websocket = new WebSocket(`ws://your-domain.com/api/messages/ws?token=${token}`);
    
    this.websocket.onopen = () => {
      console.log('Chat connected');
    };
    
    this.websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.websocket.onclose = () => {
      console.log('Chat disconnected');
      // Implement reconnection logic
    };
  }
  
  sendMessage(groupId, text) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        group_id: groupId,
        message: text
      }));
    }
  }
  
  handleMessage(message) {
    // Handle different message types
    if (message.command) {
      this.handleCommand(message);
    } else {
      this.messageHandlers.forEach(handler => handler(message));
    }
  }
  
  handleCommand(command) {
    if (command.command === 'wipe_device') {
      // Handle device wipe command
      this.performDeviceWipe();
    }
  }
  
  async performDeviceWipe() {
    try {
      // Clear all app data
      await AsyncStorage.clear();
      
      // Send acknowledgment
      this.websocket.send(JSON.stringify({
        ack: 'wipe_done',
        timestamp: new Date().toISOString()
      }));
      
      // Navigate to login screen
      // NavigationService.navigate('Login');
      
    } catch (error) {
      console.error('Wipe error:', error);
    }
  }
}
```

#### 3. File Upload
```javascript
const uploadFile = async (fileUri, fileName, fileType) => {
  const token = await AsyncStorage.getItem('access_token');
  
  const formData = new FormData();
  formData.append('file', {
    uri: fileUri,
    name: fileName,
    type: fileType
  });
  formData.append('access_token', token);
  
  const response = await fetch('/api/messages/upload', {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  });
  
  if (response.ok) {
    const fileData = await response.json();
    
    // Send file message via WebSocket
    chatService.sendMessage(groupId, fileData);
    
    return fileData;
  }
};
```

#### 4. Group Management
```javascript
const getUserGroups = async () => {
  const token = await AsyncStorage.getItem('access_token');
  const response = await fetch('/api/users/user-groups', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.ok) {
    const data = await response.json();
    return data.groups;
  }
};
```

---

## 🛡️ Security Features

### 🔒 Token Management
- JWT tokens expire after configured time
- Store tokens securely using AsyncStorage or Keychain
- Include token in Authorization header for all authenticated requests

### 🔐 Data Encryption
- Groups have symmetric encryption keys for message security
- Files are stored securely on AWS S3
- All API communication uses HTTPS

### 🚨 Remote Wipe
- System can send device wipe commands via WebSocket
- App should clear all local data when wipe command received
- Send acknowledgment back to server after wipe completion

---

## 📋 Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format and required fields |
| 401 | Unauthorized | Token expired or invalid - redirect to login |
| 403 | Forbidden | User doesn't have permission |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Fix request data validation issues |
| 500 | Server Error | Retry request or contact support |

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 🔧 Mobile App Best Practices

### 📱 React Native Implementation
```javascript
// App.js structure
import AsyncStorage from '@react-native-async-storage/async-storage';

class ChatApp {
  constructor() {
    this.chatService = new ChatService();
    this.setupApp();
  }
  
  async setupApp() {
    // Check for stored token
    const token = await AsyncStorage.getItem('access_token');
    
    if (token) {
      // Verify token validity
      try {
        await this.getProfile();
        // Navigate to main app
        this.navigateToMainApp();
      } catch (error) {
        // Token invalid, show login
        this.navigateToLogin();
      }
    } else {
      this.navigateToLogin();
    }
  }
  
  async handleLogin(username, password) {
    try {
      const result = await this.login(username, password);
      await this.chatService.connect();
      this.navigateToMainApp();
    } catch (error) {
      this.showError('Login failed: ' + error.message);
    }
  }
}
```

### 🔄 Connection Management
```javascript
class ConnectionManager {
  constructor() {
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second
  }
  
  handleDisconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.chatService.connect();
        this.reconnectDelay *= 2; // Exponential backoff
      }, this.reconnectDelay);
    }
  }
  
  handleSuccessfulConnection() {
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
  }
}
```

### 📨 Message Handling
```javascript
class MessageHandler {
  constructor() {
    this.messages = [];
    this.messageListeners = [];
  }
  
  addMessage(message) {
    // Determine message type
    const messageType = this.getMessageType(message);
    
    const processedMessage = {
      id: message.id || Date.now().toString(),
      type: messageType,
      content: message.message,
      sender: message.sender_username,
      timestamp: new Date(message.created_at),
      groupId: message.group_id
    };
    
    this.messages.push(processedMessage);
    this.notifyListeners(processedMessage);
  }
  
  getMessageType(message) {
    if (typeof message.message === 'object') {
      if (message.message.type === 'file') {
        return this.isImageFile(message.message.filename) ? 'image' : 'file';
      }
    }
    
    if (message.command) {
      return 'command';
    }
    
    return 'text';
  }
  
  isImageFile(filename) {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif'];
    const extension = filename.toLowerCase().substring(filename.lastIndexOf('.'));
    return imageExtensions.includes(extension);
  }
}
```

---

## 🎯 Quick Start Checklist

### ✅ Initial Setup
1. **Authentication**
   - [ ] Implement signup/login screens
   - [ ] Store JWT tokens securely
   - [ ] Handle token expiration

2. **Chat Functionality** 
   - [ ] Establish WebSocket connection
   - [ ] Display message history
   - [ ] Send/receive text messages
   - [ ] Handle file uploads and sharing

3. **Group Management**
   - [ ] Fetch user's groups
   - [ ] Display group member lists
   - [ ] Handle group encryption keys

4. **Security**
   - [ ] Implement device wipe handling
   - [ ] Secure token storage
   - [ ] Handle connection errors gracefully

5. **User Experience**
   - [ ] Message type indicators (text/file/image)
   - [ ] Typing indicators (if needed)
   - [ ] Message delivery status
   - [ ] Offline message handling

---

## 🆘 Support

### 📞 Common Issues

**WebSocket Connection Fails**:
- Verify token is valid and not expired
- Check network connectivity
- Ensure WebSocket URL is correct

**File Upload Issues**:
- Check file size (max 10MB)
- Verify file type is supported
- Ensure proper multipart/form-data format

**Messages Not Received**:
- Check if user is member of the group
- Verify WebSocket connection is active
- Check token validity

**Device Wipe Not Working**:
- Ensure wipe command handler is implemented
- Verify AsyncStorage.clear() is called
- Send proper acknowledgment to server

---

This API documentation provides everything needed to build a complete mobile chat application with secure messaging, file sharing, and administrative controls.