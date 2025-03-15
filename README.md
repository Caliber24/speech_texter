# Speech Texter

A Django application for OCR processing of images and PDFs.

## Features

- Extract text from images using OCR
- Extract text from PDF documents
- Store extracted text with metadata (title, user ID, timestamp)
- Retrieve user posts after a specific timestamp
- Automatic handling of duplicate titles

## API Endpoints

### 1. Image OCR

```
POST /ocr-image/
{
    "image": [image file],
    "title": "My Image Title",  // Optional
    "user_id": "user123"        // Optional
}
```

Response:
```json
{
    "id": 1,
    "text": "Extracted text content...",
    "image_url": "/media/ocr_images/image.jpg",
    "title": "My Image Title",
    "created_at": "2023-01-01T12:00:00Z",
    "user_id": "user123"
}
```

### 2. PDF OCR

```
POST /ocr-pdf/
{
    "pdf": [pdf file],
    "title": "My PDF Title",    // Optional
    "user_id": "user123"        // Optional
}
```

Response:
```json
{
    "id": 2,
    "pages": [
        {"page": 1, "text": "Page 1 content..."},
        {"page": 2, "text": "Page 2 content..."}
    ],
    "title": "My PDF Title",
    "created_at": "2023-01-01T12:00:00Z",
    "user_id": "user123"
}
```

### 3. Get User Posts After Timestamp

```
GET /user-posts/?user_id=user123&timestamp=1672531200
```

Parameters:
- `user_id`: The user identifier
- `timestamp`: Unix timestamp (seconds since epoch)

Response:
```json
{
    "posts": [
        {
            "id": 1,
            "title": "My Image Title",
            "extracted_text": "Extracted text content...",
            "created_at": 1672531200,
            "image_url": "/media/ocr_images/image.jpg"
        },
        {
            "id": 2,
            "title": "My PDF Title",
            "extracted_text": "Combined text from all pages...",
            "created_at": 1672617600,
            "image_url": null
        }
    ]
}
```

## Special Features

### Duplicate Title Handling

When a title already exists for a user, the system automatically appends an incremented number in parentheses:

- Original: "My Title"
- If exists: "My Title (1)"
- If "My Title (1)" exists: "My Title (2)"

This ensures that each title is unique while maintaining readability.

### Timestamp Format

All timestamps in API responses are in Unix timestamp format (seconds since epoch).
 
