const WORKSPACE_SHEET = 'workspace';

function doGet(request) {
  try {
    const params = request.parameter || {};
    authorize_(params.code);
    if (params.action !== 'workspace') return json_({ ok: true, service: 'Instructor Desk' });
    return json_({ ok: true, workspace: readWorkspace_() });
  } catch (error) {
    return json_({ ok: false, error: error.message });
  }
}

function doPost(request) {
  try {
    const body = JSON.parse(request.postData.contents || '{}');
    authorize_(body.code);
    if (body.action === 'workspace') {
      writeWorkspace_(body.workspace || {});
      return json_({ ok: true });
    }
    if (body.action === 'upload') return json_({ ok: true, file: uploadFile_(body) });
    if (body.action === 'delete') {
      deleteFile_(body.fileId);
      return json_({ ok: true });
    }
    throw new Error('Unknown action.');
  } catch (error) {
    return json_({ ok: false, error: error.message });
  }
}

function setupInstructorDesk() {
  const properties = PropertiesService.getScriptProperties();
  const spreadsheetId = properties.getProperty('SHEET_ID');
  const folderId = properties.getProperty('DRIVE_FOLDER_ID');
  if (!spreadsheetId || !folderId) throw new Error('Set SHEET_ID and DRIVE_FOLDER_ID in Script Properties first.');
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  let sheet = spreadsheet.getSheetByName(WORKSPACE_SHEET);
  if (!sheet) sheet = spreadsheet.insertSheet(WORKSPACE_SHEET);
  if (!sheet.getRange('A1').getValue()) sheet.getRange('A1').setValue(JSON.stringify({ fileRecords: [] }));
  DriveApp.getFolderById(folderId).getName();
}

function readWorkspace_() {
  const spreadsheet = SpreadsheetApp.openById(requiredProperty_('SHEET_ID'));
  const sheet = spreadsheet.getSheetByName(WORKSPACE_SHEET);
  if (!sheet) return { fileRecords: [] };
  const value = sheet.getRange('A1').getValue();
  return value ? JSON.parse(value) : { fileRecords: [] };
}

function writeWorkspace_(workspace) {
  const spreadsheet = SpreadsheetApp.openById(requiredProperty_('SHEET_ID'));
  let sheet = spreadsheet.getSheetByName(WORKSPACE_SHEET);
  if (!sheet) sheet = spreadsheet.insertSheet(WORKSPACE_SHEET);
  sheet.getRange('A1').setValue(JSON.stringify(workspace));
}

function uploadFile_(body) {
  if (!body.name || !body.data) throw new Error('A file name and data are required.');
  const bytes = Utilities.base64Decode(body.data);
  const blob = Utilities.newBlob(bytes, body.type || 'application/octet-stream', body.name);
  const file = DriveApp.getFolderById(requiredProperty_('DRIVE_FOLDER_ID')).createFile(blob);
  return {
    id: file.getId(),
    name: file.getName(),
    size: file.getSize(),
    type: file.getMimeType(),
    url: file.getDownloadUrl()
  };
}

function deleteFile_(fileId) {
  if (!fileId) return;
  DriveApp.getFileById(fileId).setTrashed(true);
}

function authorize_(code) {
  const expected = requiredProperty_('ACCESS_CODE');
  if (!code || code !== expected) throw new Error('Invalid access code.');
}

function requiredProperty_(name) {
  const value = PropertiesService.getScriptProperties().getProperty(name);
  if (!value) throw new Error(`Missing Script Property: ${name}`);
  return value;
}

function json_(value) {
  return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON);
}