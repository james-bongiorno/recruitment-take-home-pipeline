export interface Attendee {
  id: string;
  name: string;
  email: string;
  ticket: "general" | "vip";
  checkedIn: boolean;
}

export interface AttendeesApi {
  list(eventId: string): Promise<Attendee[]>;
  /** Save a check-in (or undo one). Rejects if the server refuses. */
  setCheckedIn(attendeeId: string, checkedIn: boolean): Promise<void>;
}
