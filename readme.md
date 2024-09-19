Here is the complete `README.md` for you to copy:

---

# Amastay - Flask Application

This repository contains the backend for Amastay, a Flask-based API designed for OTP-based authentication and property management using Supabase.

## Prerequisites

Before running the project, ensure the following are installed:

- **Python 3.9 or higher**
- **Pip** (Python package installer)
- **Virtualenv** (optional but recommended)
- **Supabase Account and Project** (for authentication)

## Setup and Run

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/amastay.git
   cd amastay
   ```

2. **Create and activate a virtual environment**:

   - On **macOS/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On **Windows**:
     ```bash
     python3 -m venv venv
     venv\Scripts\activate
     ```

3. **Install the project dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file to include your Supabase `SUPABASE_URL` and `SUPABASE_KEY`.

5. **Run the Flask app**:

   ```bash
   python3 app.py
   ```

   The app will run by default on [http://localhost:80](http://localhost:80).

## API Endpoints

- `POST /api/v1/auth/send_otp` - Sends an OTP to the specified phone number.
- `POST /api/v1/auth/verify_otp` - Verifies the OTP for the phone number.
- `POST /api/v1/auth/refresh_token` - Refreshes the access token using the refresh token.

## Troubleshooting

If you encounter any issues, check the logs in the `app.log` file located in the root directory.

---

This README includes steps for setting up the project, installing dependencies, configuring environment variables, and running the app. Let me know if you need any changes!
