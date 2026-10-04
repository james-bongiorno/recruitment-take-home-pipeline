import type { Attendee } from "../types";

/** Attendees sorted by name, ignoring upper/lower case. Leaves the array it was given alone. */
export function sortAttendees(attendees: Attendee[]): Attendee[] {
  return attendees.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
}

/** True if the name or email contains the query, ignoring case and surrounding spaces. */
export function matchesSearch(attendee: Attendee, query: string): boolean {
  const q = query.trim().toLowerCase();
  return attendee.name.toLowerCase().includes(q) || attendee.email.toLowerCase().includes(q);
}

export function countCheckedIn(attendees: Attendee[]): number {
  return attendees.filter((a) => a.checkedIn).length;
}
