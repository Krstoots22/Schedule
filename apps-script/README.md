# Instructor Desk shared backend

This is the no-cost replacement for Firebase. Google Sheets stores the workspace metadata and Google Drive stores uploaded files. Instructors use the web app without GitHub or Google sign-in, protected by one shared access code.

## Setup

1. Create a Google Sheet and copy its ID from the URL.
2. Create a Google Drive folder for class files and copy its ID from the folder URL.
3. Open `Extensions -> Apps Script` from the Sheet, replace the starter code with `Code.gs`, and save.
4. In Apps Script, open `Project Settings -> Script Properties` and add:
   - `SHEET_ID`: the Google Sheet ID
   - `DRIVE_FOLDER_ID`: the Drive folder ID
   - `ACCESS_CODE`: a private shared instructor passcode
5. Run `setupInstructorDesk` once and approve the Google permissions.
6. Click `Deploy -> New deployment`.
7. Choose `Web app`, execute as `Me`, and set access to `Anyone`.
8. Copy the `/exec` URL. It is the shared backend URL for the dashboard.

The web app should use the `/exec` URL and include the shared access code with every request. Do not use the `/dev` URL for the class dashboard.

## Data preservation

Keep the current dashboard open on the machine that contains the existing local data. The migration step should export the current tabs, folders, links, and files, then send them to this backend before switching the public dashboard to it. Do not delete the old Firebase project or browser data until the migrated workspace has been verified.