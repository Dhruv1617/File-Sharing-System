# File Sharing System

A secure file-sharing API built with **FastAPI**, **MySQL**, and **SendGrid**. It enables **ops users** to upload files (`.pptx`, `.docx`, `.xlsx`) and **client users** to list and download files, secured with JWT-based authentication and email verification.

## Features
- **User Roles**:
  - **Ops**: Upload files securely.
  - **Client**: List and download files after email verification.
- **Endpoints**:
  - `POST /signup`: Register a new user (client role requires email verification).
  - `GET /verify-email/{token}`: Verify user email via SendGrid link.
  - `POST /login`: Authenticate and receive a JWT token.
  - `POST /upload-file`: Upload files (ops only, `.pptx`, `.docx`, `.xlsx`).
  - `GET /list-files`: List uploaded files (client only).
  - `GET /download-file/{id}`: Generate a secure download link (client only).
  - `GET /download/{token}`: Download a file using a secure link (client only).
- **Security**:
  - JWT-based authentication for all protected endpoints.
  - Email verification for client users via SendGrid.
  - File type validation to allow only `.pptx`, `.docx`, and `.xlsx`.
- **Database**: MySQL for storing user and file metadata.
- **Storage**: Files stored in the `uploads/` directory.

## Prerequisites
- **Python**: 3.13 or higher
- **MySQL**: 8.0 or higher
- **SendGrid**: Account for email verification
- **Git**: For cloning the repository
- **Postman** (optional): For testing API endpoints

## Installation
1. Clone the Repository:
   ```bash
   git clone https://github.com/Dhruv1617/File-Sharing-System.git
   cd File-Sharing-System
   ```

2. Set Up Virtual Environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure Environment Variables:

   4.1 Copy the example environment file:

   ```bash
   cp .env.example .env
   ```
   
   4.2 Edit .env with your credentials:
 
     ```bash
     nano .env
     ```
 
     ```env
     SECRET_KEY=your-secure-secret-key
     DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/file_sharing
     SENDGRID_API_KEY=SG.your-sendgrid-api-key
     UPLOAD_FOLDER=uploads
     ```
     - Generate a secure SECRET_KEY (e.g., using python -c "import secrets; print(secrets.token_hex(32))").
     - Replace user:password with your MySQL credentials.
     - Obtain SENDGRID_API_KEY from your SendGrid account.

6. Set Up MySQL Database:
    ```bash
    mysql -u root -p
    ```
    ```sql
    CREATE DATABASE file_sharing;
    EXIT;
    ```
    - The application automatically creates tables(users, files) on startup.

6. Run the Application:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
   - Access the API at http://localhost:8000/docs (Swagger UI).



## Usage:

### Register a User:

- Method: POST
- URL: http://localhost:8000/signup
- Headers:
    
   | Key          | Value            |
  | ------------ | ---------------- |
  | Content-Type | application/json |

- Body(raw -> JSON)
  ```json
  {
  "email": "client@example.com",
  "password": "client_password123"
  }
  ```
  - A verification email is sent to client@example.com. Click the link to complete registration.

---

### Verify Email
- Method: GET
- URL: http://localhost:8000/verify-email/{token}
  **NOTE:**: The token is embedded in the email link. Open the link in a browser to complete email verification.

--- 

  
### Log In:
- Method: POST
- URL: http://localhost:8000/login
- Headers:
  
    | Key          | Value                             |
  | ------------ | --------------------------------- |
  | Content-Type | application/x-www-form-urlencoded |

- Body (x-www-form-urlencoded)

    | Key      | Value                                           |
  | -------- | ----------------------------------------------- |
  | username | [client@example.com](mailto:client@example.com) |
  | password | client\_password123                             |

- Response (JSON)
  ```json
  {
  "access_token": "eyJ...",
  "token_type": "bearer"
  }
  ```
  **NOTE:** Save this access_token for all future requests that require authentication.

---

### Upload a File (Ops User Only)
- Method: POST
- URL: http://localhost:8000/upload-file
- Headers:
  
    | Key           | Value                |
  | ------------- | -------------------- |
  | Authorization | Bearer `<ops_token>` |

- Body (form-data)
  
    | Key  | Type | Value                |
  | ---- | ---- | -------------------- |
  | file | File | `test.docx` (upload) |

  **NOTE:** Only the following file types are supported: .pptx, .docx, .xlsx.

---

### List Files (Client User)
- Method : GET
- URL: http://localhost:8000/list-files
- Headers:
  
    | Key           | Value                   |
  | ------------- | ----------------------- |
  | Authorization | Bearer `<client_token>` |

- Response:
  ```json
  [
    {
      "filename": "test.docx",
      "id": 1,
      "upload_time": "2025-07-03T00:06:00",
      "uploaded_by": 1
    }
  ]
  ```
---

### Download a File (Client User)
- Step 1:  Get Download Link
  - Method : GET
  - URL: http://localhost:8000/download-file/{id}
  - Headers:
 
    
    | Key           | Value                   |
    | ------------- | ----------------------- |
    | Authorization | Bearer `<client_token>` |

     
  - Response:
    ```json
    {
      "download_link": "http://localhost:8000/download/eyJ...",
      "message": "success"
    }
    ```
-  Step 2: Download the File
  
    - Method: GET
    - URL: http://localhost:8000/download/{token}
      **NOTE:** This step can be done in a browser, Postman, or with tools like curl.





