/**
 * Reference fix (reviewer only).
 * Bug: Array.prototype.sort sorts in place, so sortAttendees reordered the caller's array.
 * In React that means quietly mutating state (or props) during render.
 * Fix: sort a copy ([...attendees].sort(...)) or use toSorted().
 */
import type { Attendee } from "../types";

export function sortAttendees(attendees: Attendee[]): Attendee[] {
  return [...attendees].sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
}

export function matchesSearch(attendee: Attendee, query: string): boolean {
  const q = query.trim().toLowerCase();
  return attendee.name.toLowerCase().includes(q) || attendee.email.toLowerCase().includes(q);
}

export function countCheckedIn(attendees: Attendee[]): number {
  return attendees.filter((a) => a.checkedIn).length;
}
