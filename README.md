
# Program Overview

This program automates the process of gathering information from websites of community social services in South Bend, IN, and sending out questionnaires to verify the accuracy of that information. It consists of a series of scripts that work together to collect data, send emails, record responses, and update Google spreadsheets. These spreadsheets are accessible to organizations and the public via a dynamically updating webpage.

----------

## Table of Contents

1.  [Setup Instructions](#setup-instructions)
    -   [Backend Setup](#backend-setup)
    -   [Required APIs](#required-apis)
    -   [Required Packages](#required-packages)
    -   [Google Spreadsheets](#google-spreadsheets)
    -   [Code Variables](#code-variables)
2.  [Program Components](#program-components)
    -   [app.py](#app-py)
    -   [Email_notifs.py](#email-notifs-py)
    -   [scrape_events.py](#scrape-events-py)
    -   [info_extract.py](#info-extract-py)
    -   [Dockerfile](#dockerfile)
    -   [Requirements.txt](#requirements-txt)
    -   [.dockerignore / .gitignore](#dockerignore-gitignore)
    -   [env](#env)
    -   [README.md](#readme-md)
    -   [Credentials.json](#credentials-json)
3.  [Adding New Organizations](#adding-new-organizations)
    -   [Notification Functions](#notification-functions)
    -   [Google Spreadsheets](#google-spreadsheets)
    -   [Updating App Scripts](#updating-app-scripts)
4.  [Testing and Deployment](#testing-and-deployment)
5.  [Maintenance](#maintenance)
6.  [How the Program Works](#how-the-program-works)

----------

## Setup Instructions

### Backend Setup

1.  **Credentials.json Secret:**
    -   This secret is specific to a service account created with `rmetoye2@nd.edu`.
    -   If this email is terminated, create a new service account and rebuild/redeploy the app with the new account.
    -   Create a new secret using the Secret Manager with the updated `Credentials.json` file.

### Required APIs

-   **Sheets API**
-   **Secret Manager API**
-   **Cloud Run Admin API**
-  **OpenAI API**

### Required Packages
- **openai**
- **dotenv**
- **email.message**
- **os**
- **pathlib**
- **pdfkit**
- **PyPDF2**
- **ssl**
- **smtplib**
- **email.mime.multipart**
- **email.mime.text**
- **flask**
- **oauth2client.service_account**
- **google.cloud**


### Google Spreadsheets

-   Stored in the MetoyerLab shared drive.
-   If new organizations are added, new spreadsheets must be created.
-   New spreadsheet keys must be added to the code and app scripts
- Ensure new spreadsheets are formatted the exact same as old spreadsheets to ensure app scripts run consistently

### Code Variables

-   The code uses a list of variables for different organizations (e.g., St Margarets House, Our Lady of the Road, the Food Bank, Center for the Homeless).
-   This includes notification methods, email formats, and separate Google spreadsheets for each organization.
-   To scale the program, new variables must be added for each organization.
-   Similar variable lists appear in the app scripts, and must be updated as well

----------

## Program Components

### app.py

-   Runs the Flask application and handles all responses via HTTP

### Email_notifs.py

-   Inspects websites, sends emails, and records responses in tandem with `app.py`.

### scrape_events.py

-   Used by `Email_notifs.py` for scraping event data from websites.

### info_extract.py

-   Used by `Email_notifs.py` for extracting information from websites using OpenAI API (alterations to prompts should be done here)

### Dockerfile

-   Required for Google Cloud Run build.

### Requirements.txt

-   Lists dependencies required for Google Cloud Run build.

### .dockerignore / .gitignore

-   Files to ignore for Docker and Git.

### env

-   Environment variables file.

### README.md

-   Documentation file.

### Credentials.json

-   Not required for Google Cloud Run build but stored with the program if necessary

----------

## Adding New Organizations

### Notification Functions

1.  Replicate existing notification methods.
2.  Tailor the new function to the specific needs of the new organization.

### Google Spreadsheets

1.  Follow the structure used for existing organizations.
2.  Store the new spreadsheets in the MetoyerLab shared drive.

### Updating App Scripts

1.  Add the new organization as variables to each part of the code.
2.  Ensure all references to organizations in the code are updated to include the new organization.
3.  Check for consistency and accuracy to avoid errors.

----------

## Testing and Deployment

### Testing

1.  Thoroughly test each new addition to ensure it works seamlessly with the existing setup.
2.  Verify that emails are sent correctly, responses are recorded, and data is accurately updated in the Google spreadsheets.

### Deployment

1.  Ensure `Dockerfile`, `Requirements.txt`, and `.dockerignore` are correctly configured.
2. Navigate to Google Cloud Run.
3. Click on the service (email_notifs).
4. Click 'Edit and Deploy New Revision' and complete the deployment.
5.  Verify that the environment variables and APIs are correctly set up.

----------

## Maintenance

-   Regularly update `Credentials.json` and other secrets as needed.
-   Monitor the performance and scalability of the program.
-   Maintain the shared Google spreadsheets and ensure data integrity.

----------

## How the Program Works

1.  **Deployment**: Deploy the project on Google Cloud Run, which starts the Flask application (`app.py`).
2.  **Running the Program**: Run `email_notifs.py` to gather information from the websites and send out questionnaire emails.
3.  **Email Responses**: The emails contain HTML buttons that send HTTP responses to the Flask app, allowing it to record the information in Google spreadsheets.
4.  **Data Storage**: The responses (e.g., 'yes/no', the responder's email, the date, and any updated information) are stored in the respective Google spreadsheets.

Ultimately, `email_notifs.py` will run automatically as a recurring job connected with the Google Cloud Run Service. This functionality will be added later.