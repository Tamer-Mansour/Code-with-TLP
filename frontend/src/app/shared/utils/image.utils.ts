/** Convert a File to a base64 data-URI string. */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsDataURL(file);
  });
}

/** Returns an error message string, or null when the file is acceptable. */
export function validateImageFile(file: File, maxMb = 2): string | null {
  if (!file.type.startsWith('image/')) return 'Please select an image file (JPEG, PNG, WebP…).';
  if (file.size > maxMb * 1024 * 1024) return `Image must be under ${maxMb} MB.`;
  return null;
}
