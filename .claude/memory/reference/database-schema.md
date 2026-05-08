---
name: database-schema
description: Database models and relationships
type: reference
---

# Database Schema

## Models

### User
- `id` (int, primary key) - Legacy ID
- `new_id` (str, UUID, primary key) - New UUID identifier
- `email` (str) - User email (unique)
- `full_name` (str, nullable)
- `is_active` (bool)
- `is_superuser` (bool)
- `hashed_password` (str)
- `created_on` (datetime)
- `updated_on` (datetime | null)

### Item
- `id` (int, primary key)
- `new_owner_id` (str, UUID) - Owner's UUID
- `title` (str)
- `description` (str | null)
- `owner_id` (int) - Owner's legacy ID
- `created_on` (datetime)
- `updated_on` (datetime | null)

### Member
- `id` (str, UUID, primary key)
- `first_name` (str)
- `last_name` (str)
- `birthday` (datetime)
- `wedding_anniversary` (datetime | null)
- `baptism_date` (datetime)
- `created_on` (datetime)
- `updated_on` (datetime | null)

### ChurchService
- `id` (str, UUID, primary key)
- `service_date` (datetime)
- `speaker` (str | null)
- `service_title` (str | null)
- `file_location` (str | null)
- `edited` (bool)
- `uploaded` (bool)
- `created_on` (datetime)
- `updated_on` (datetime | null)

### VideoUpload
- `id` (str, UUID, primary key)
- `upload_location` (str)
- `upload_name` (str)
- `created_on` (datetime)
- `updated_on` (datetime | null)

### Announcement
- `id` (str, UUID, primary key)
- `sender` (str)
- `recipients` (str)
- `message` (str)
- `created_on` (datetime)
- `updated_on` (datetime | null)

### Media
- `id` (str, UUID, primary key)
- `name` (str)
- `uploaded_on` (datetime)
- `created_on` (datetime)
- `updated_on` (datetime)

## Relationships

- User → Item (user_id = owner_id)
- UUID fields use `new_id` / `new_owner_id`
- Integer fields use `id` / `owner_id`

## Migration Notes

- Recent migrations added media tables
- Cascade delete relationships added
- Nullable field adjustments made
- Church service tables added in migration fc2afb5a5fea

## How to Apply

- Use UUID strings for new relationships (new_id, new_owner_id)
- Keep both UUID and integer ID types for compatibility
- Check migration history in app/alembic/versions/
