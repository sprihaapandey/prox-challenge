export function pageImageUrl(page: number, docId: string = 'owner-manual'): string {
  return `/media/pages/${docId}/page_${String(page).padStart(3, '0')}.png`
}
