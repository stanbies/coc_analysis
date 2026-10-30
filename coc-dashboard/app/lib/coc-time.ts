// The API's timestamps look like 20261029T184614.000Z
export function parseCocTime(value: string): Date {
  return new Date(Date.UTC(
    Number(value.slice(0, 4)), Number(value.slice(4, 6)) - 1, Number(value.slice(6, 8)),
    Number(value.slice(9, 11)), Number(value.slice(11, 13)),
  ));
}

// "29 Oct", formatted in UTC so the pre-rendered page and the browser agree
export function shortDate(value: string): string {
  return parseCocTime(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', timeZone: 'UTC' });
}
