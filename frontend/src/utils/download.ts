import { client } from '../api/client';

/**
 * Downloads a file from the backend API.
 * Uses Axios with responseType = 'blob' to support binary files.
 * Extracts the filename from Content-Disposition headers if present,
 * otherwise falls back to a default name based on file extension/type.
 * 
 * @param url The API endpoint path (e.g., '/results/exams/123/export/csv')
 * @returns typed Promise<void>
 */
export async function downloadFile(url: string): Promise<void> {
  const response = await client.get(url, {
    responseType: 'blob',
  });

  // Extract content type and determine standard fallback extension
  const contentType = String(response.headers['content-type'] || '');
  let fallbackFilename = 'export.csv';
  if (contentType.toLowerCase().includes('application/pdf')) {
    fallbackFilename = 'report.pdf';
  }

  // Extract filename from Content-Disposition header
  let filename = fallbackFilename;
  const disposition = response.headers['content-disposition'] ? String(response.headers['content-disposition']) : undefined;
  if (disposition) {
    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
    const matches = filenameRegex.exec(disposition);
    if (matches !== null && matches[1]) {
      filename = matches[1].replace(/['"]/g, '');
    }
  }

  // Create temporary object URL for browser download
  const blob = response.data;
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  
  // Trigger download
  link.click();
  
  // Clean up resource references
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
}
