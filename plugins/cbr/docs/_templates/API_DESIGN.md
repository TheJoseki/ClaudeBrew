# API Design — [PROJECT_NAME]

> **Version**: 1.0
> **Backend**: [BACKEND_FRAMEWORK] + TypeScript + [ORM] + [AUTH_LIBRARY]
> **Base URL**: `/api/v1/`
> Copy from `docs/_templates/API_DESIGN.md` to `docs/API_DESIGN.md` and fill in per project.

---

## Overview

[CUSTOMIZE: fill in your API modules and endpoint counts]

| Module | Endpoints | Count |
|--------|-----------|-------|
| Authentication | login, refresh, logout, forgot-password, verify-otp, reset-password | 6 |
| Users / Profile | me, update-profile, update-avatar, change-password | 4 |
| [MODULE_1] | [list of endpoints] | [N] |
| [MODULE_2] | [list of endpoints] | [N] |
| [MODULE_3] (Admin) | list, create, update, delete, [additional] | [N] |
| **Total** | | **[TOTAL]** |

---

## Standard Patterns

### Authentication Header
All protected endpoints require:
```
Authorization: Bearer <access_token>
```

### Pagination Response Format
```json
{
  "count": 100,
  "page": 1,
  "pageSize": 20,
  "totalPages": 5,
  "results": [...]
}
```

### Error Response Format
```json
{
  "statusCode": 400,
  "message": "Error description",
  "error": "Bad Request",
  "errors": {
    "fieldName": ["Validation error message"]
  }
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 204 | Deleted (no content) |
| 400 | Validation error |
| 401 | Unauthorized (JWT expired/invalid) |
| 403 | Forbidden (role not permitted) |
| 404 | Not found |
| 409 | Conflict (duplicate) |
| 500 | Server error |

---

## 1. Authentication

### POST `/api/v1/auth/login/`
Login with username and password.

**Request**:
```json
{
  "username": "[TEST_USER_EMAIL]",
  "password": "[TEST_PASSWORD_PLACEHOLDER]"
}
```

**Response 200**:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "displayName": "[USER_DISPLAY_NAME]",
    "email": "[USER_EMAIL]",
    "roles": ["[role_code]"]
  }
}
```

**Error 401**: `{ "detail": "Invalid username or password" }`

### POST `/api/v1/auth/refresh/`
**Request**: `{ "refresh": "eyJ..." }`
**Response 200**: `{ "access": "eyJ..." }`

### POST `/api/v1/auth/logout/`
**Request**: `{ "refresh": "eyJ..." }`
**Response 204**: No content

### POST `/api/v1/auth/forgot-password/`
**Request**: `{ "email": "[user_email]" }`
**Response 200**: `{ "message": "OTP/reset link sent to email" }`
**Error 404**: `{ "detail": "Email not found" }`

### POST `/api/v1/auth/verify-otp/`
**Request**: `{ "email": "[user_email]", "otp": "123456" }`
**Response 200**: `{ "token": "reset_token_xxx" }`
**Error 400**: `{ "detail": "Invalid or expired OTP" }`

### POST `/api/v1/auth/reset-password/`
**Request**: `{ "token": "reset_token_xxx", "password": "[NEW_PASSWORD]", "confirmPassword": "[NEW_PASSWORD]" }`
**Response 200**: `{ "message": "Password reset successfully" }`

---

## 2. Users / Profile

### GET `/api/v1/users/me/`
Get current user's profile.

**Response 200**:
```json
{
  "id": 1,
  "displayName": "[USER_DISPLAY_NAME]",
  "email": "[USER_EMAIL]",
  "roles": [{ "id": 1, "roleCode": "[ROLE_CODE]", "roleName": "[ROLE_NAME]" }],
  "avatarUrl": "/media/avatars/1.jpg"
}
```

### PATCH `/api/v1/users/me/`
Update editable profile fields.

**Request**:
```json
{
  "displayName": "[NEW_DISPLAY_NAME]",
  "[EDITABLE_FIELD_1]": "[VALUE]",
  "[EDITABLE_FIELD_2]": "[VALUE]"
}
```

### POST `/api/v1/users/me/avatar/`
Upload avatar image. Content-Type: `multipart/form-data`

**Request**: `file` field (image only)
**Response 200**: `{ "avatarUrl": "/media/avatars/1.jpg" }`
**Error 400**: `{ "detail": "Invalid image format" }`

### POST `/api/v1/users/me/change-password/`
**Request**:
```json
{
  "currentPassword": "[CURRENT_PASSWORD]",
  "newPassword": "[NEW_PASSWORD]",
  "confirmPassword": "[NEW_PASSWORD]"
}
```

**Validations**:
- Current password must match
- New password must meet policy: [PASSWORD_POLICY_DESCRIPTION]
- confirmPassword must match newPassword

---

## 3. [MODULE_1] — [MODULE_DESCRIPTION]

[CUSTOMIZE: add your actual module endpoints]

### GET `/api/v1/[module1]/`
Get list with pagination and search.

**Query Params**:

| Param | Type | Description |
|-------|------|-------------|
| search | string | Search by [FIELD_NAME] |
| [FILTER_PARAM] | [TYPE] | Filter by [DESCRIPTION] |
| page | int | Page number (default 1) |
| pageSize | int | Items per page (default 20) |

**Response 200** (pagination format):
```json
{
  "count": 42,
  "page": 1,
  "pageSize": 20,
  "totalPages": 3,
  "results": [
    {
      "id": 1,
      "[FIELD_1]": "[VALUE]",
      "[FIELD_2]": "[VALUE]",
      "createdBy": { "id": 1, "displayName": "[USER_NAME]" },
      "createdDate": "2026-01-01T00:00:00Z",
      "updatedDate": "2026-01-02T00:00:00Z"
    }
  ]
}
```

### GET `/api/v1/[module1]/:id/`
Get single [entity] by ID.

**Response 200**: Full [entity] object with related data.
**Error 404**: `{ "detail": "[Entity] not found" }`

### POST `/api/v1/[module1]/`
Create new [entity].

**Request**:
```json
{
  "[REQUIRED_FIELD_1]": "[VALUE]",
  "[REQUIRED_FIELD_2]": "[VALUE]",
  "[OPTIONAL_FIELD]": "[VALUE]"
}
```

**Validations**:
- Required: [LIST_REQUIRED_FIELDS]
- `[FIELD]`: [VALIDATION_RULE]

**Response 201**: Created [entity] object.

### PATCH `/api/v1/[module1]/:id/`
Update [entity] (partial update).

**Request**: Any subset of create fields.
**Response 200**: Updated [entity] object.

### DELETE `/api/v1/[module1]/:id/`
Soft delete [entity].

**Response 204**: No content.

---

## 4. [MODULE_2] — [MODULE_DESCRIPTION]

[CUSTOMIZE: repeat pattern for each module]

---

## 5. [MODULE_3] (Admin Only)

### GET `/api/v1/admin/[module3]/?search=...&page=1&pageSize=20`
**Required role**: [ADMIN_ROLE]

**Response 200**: Paginated list.

### POST `/api/v1/admin/[module3]/`
**Required role**: [ADMIN_ROLE]

**Request**:
```json
{
  "[FIELD_1]": "[VALUE]",
  "[FIELD_2]": "[VALUE]"
}
```

**Validations**:
- Unique: [UNIQUE_FIELDS]
- Format: [FIELD_FORMATS]

**Response 201**: Created object.

### PATCH `/api/v1/admin/[module3]/:id/`
**Required role**: [ADMIN_ROLE]

### DELETE `/api/v1/admin/[module3]/:id/`
**Required role**: [ADMIN_ROLE]
Soft delete. Logs to [ACTIVITY_LOG_TABLE].

**Response 204**: No content.

### POST `/api/v1/admin/[module3]/import/`
Bulk import from file. Content-Type: `multipart/form-data`
**Required role**: [ADMIN_ROLE]

**Request**: `file` field ([FORMAT] file)

**Response 200**:
```json
{
  "total": 10,
  "success": 8,
  "failed": 2,
  "errors": [
    { "row": 3, "field": "[FIELD_NAME]", "message": "Duplicate value" },
    { "row": 7, "field": "[FIELD_NAME]", "message": "Required field missing" }
  ]
}
```

---

## [N]. Dashboard (if applicable)

### GET `/api/v1/dashboard/stats/`

**Response 200**:
```json
{
  "[STAT_1]": 42,
  "[STAT_2]": 8,
  "[STAT_3]": 156,
  "[RECENT_ITEMS]": [ "...top N items..." ],
  "[PENDING_ITEMS]": [ "...top N items..." ]
}
```

---

## [N+1]. Notifications (if applicable)

### GET `/api/v1/notifications/?page=1&pageSize=20`

**Response 200**:
```json
{
  "unreadCount": 3,
  "results": [
    {
      "id": 1,
      "title": "[NOTIFICATION_TITLE]",
      "content": "[NOTIFICATION_CONTENT]",
      "isRead": false,
      "createdDate": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### PATCH `/api/v1/notifications/:id/`
**Request**: `{ "isRead": true }`

### POST `/api/v1/notifications/mark-all-read/`
**Response 200**: `{ "updated": 3 }`

---

## Common Response Examples

### List Endpoint (Generic)
```json
{
  "count": 100,
  "page": 1,
  "pageSize": 20,
  "totalPages": 5,
  "results": [
    {
      "id": 1,
      "[key_field]": "[value]",
      "createdDate": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### Detail Endpoint (Generic)
```json
{
  "id": 1,
  "[field_1]": "[value]",
  "[field_2]": "[value]",
  "[nested_object]": {
    "id": 2,
    "name": "[related_name]"
  },
  "createdBy": { "id": 1, "displayName": "[USER_NAME]" },
  "createdDate": "2026-01-01T00:00:00Z",
  "updatedDate": "2026-01-02T00:00:00Z"
}
```

### Validation Error (400)
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request",
  "errors": {
    "email": ["Email format is invalid"],
    "name": ["Name is required", "Name must not exceed 200 characters"]
  }
}
```

### Auth Error (401)
```json
{
  "statusCode": 401,
  "message": "Unauthorized",
  "error": "Unauthorized"
}
```

### Permission Error (403)
```json
{
  "statusCode": 403,
  "message": "Forbidden resource",
  "error": "Forbidden"
}
```
