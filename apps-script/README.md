# Instructor Desk shared backend

This is the no-cost replacement for Firebase. Google Sheets stores the workspace metadata and Google Drive stores uploaded files. Instructors use the web app without GitHub or Google sign-in, protected by one shared access code.

## 1. Create the storage locations

1. Sign in to the Google account that should own the class resources.
2. Create a new Google Sheet, for example `Instructor Desk Data`.
3. Copy the Sheet ID from its URL. In this URL, the ID is between `/d/` and `/edit`:

   `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

4. Create a Google Drive folder, for example `Instructor Desk Files`.
5. Copy the folder ID from its URL. It is the text after `/folders/`.
6. Keep this Sheet and folder in the same Google account that will own the Apps Script deployment.

## 2. Create the Apps Script project

1. Open the Google Sheet.
2. Select **Extensions -> Apps Script**.
3. Delete the starter function in the Apps Script editor.
4. Open [Code.gs](Code.gs) from this repository.
5. Copy all of its contents into the Apps Script editor.
6. Click **Save**.
7. Rename the Apps Script project to `Instructor Desk Backend`.

## 3. Add private script properties

Script properties keep the Sheet ID, Drive folder ID, and passcode out of the code.

1. In Apps Script, click **Project Settings** in the left sidebar. It may look like a gear icon.
2. Scroll to **Script Properties**.
3. Click **Add script property** three times and enter these exact property names:

   | Property | Value |
   | --- | --- |
   | `SHEET_ID` | The ID copied from the Google Sheet URL |
   | `DRIVE_FOLDER_ID` | The ID copied from the Google Drive folder URL |
   | `ACCESS_CODE` | A private passcode for instructors, such as a long phrase |

4. Click **Save script properties**.

Use a new private passcode. Do not use `1234`, your company password, or a password used elsewhere.

## 4. Initialize the backend

1. Return to the Apps Script editor.
2. At the top, open the function selector.
3. Select `setupInstructorDesk`.
4. Click **Run**.
5. Google will ask you to authorize the script:
   - Click **Review permissions**.
   - Choose the Google account that owns the Sheet and Drive folder.
   - If Google displays an unverified-app warning, click **Advanced**, then **Go to Instructor Desk Backend**.
   - Click **Allow**.
6. Run `setupInstructorDesk` again if the first run only completed authorization.
7. Confirm that a sheet tab named `workspace` appears in the Google Sheet.

The script uses cell `A1` on that tab for workspace metadata. Do not manually edit that cell after initialization.

## 5. Deploy the web app

1. In Apps Script, click **Deploy -> New deployment**.
2. For deployment type, select **Web app**.
3. Set **Execute as** to **Me**.
4. Set **Who has access** to **Anyone**.
5. Click **Deploy**.
6. Copy the URL ending in `/exec`.

The URL should look similar to:

`https://script.google.com/macros/s/DEPLOYMENT_ID/exec`

Use the `/exec` URL for the dashboard. Do not use the `/dev` URL; `/dev` is only for the owner while testing.

## 6. Confirm the backend works

Open the `/exec` URL in a browser. It may show an invalid access-code response, which confirms that the web app is reachable.

The backend is working when:

- The URL opens without a Google login prompt.
- The Apps Script execution log shows a completed request.
- The `workspace` sheet exists.
- Uploaded files appear in the configured Drive folder.

## 7. Connect the dashboard

Send the `/exec` URL to the developer or place it in the dashboard's shared-backend configuration along with the exact `ACCESS_CODE`. The dashboard must send the access code with every request.

Do not put the Google Sheet ID, Drive folder ID, or private access code into a public README or GitHub repository.

## 8. Preserve and migrate existing data

1. Do not delete Firebase, the current browser data, or the local IndexedDB files yet.
2. Open the current dashboard on the computer that contains the existing data.
3. Export or migrate the tabs, folders, links, and uploaded files into the new backend.
4. Verify the data from a second browser or device.
5. Confirm that links open and uploaded files download.
6. Only after verification should Firebase Storage be disabled or deleted.

The migration must be completed from the browser that currently contains the local data. A new browser or the public GitHub Pages origin cannot automatically see another browser's localStorage or IndexedDB data.