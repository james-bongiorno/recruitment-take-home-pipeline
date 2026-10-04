import type { AttendeesApi } from "../types";
// You'll probably want these:
// import { useEffect, useState } from "react";
// import { countCheckedIn, matchesSearch, sortAttendees } from "../lib/attendees";

interface Props {
  eventId: string;
  api: AttendeesApi;
}

/** The door staff's check-in list for one event. See README.md for what it needs to do. */
export function CheckInList({ eventId, api }: Props) {
  // TODO: load attendees with api.list(eventId) and render them
  void api;
  return <p>TODO: check-in list for {eventId}</p>;
}
