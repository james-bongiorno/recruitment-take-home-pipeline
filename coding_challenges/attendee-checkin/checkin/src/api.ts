import type { Attendee, AttendeesApi } from "./types";

/**
 * A fake API so you can run the app without a backend (npm run dev).
 * - "jazz-night" has a few attendees; checking in Olive Sato always fails
 * - "empty-room" has none
 * - "flaky" fails the first time you load it, then works
 */
const ATTENDEES: Record<string, Attendee[]> = {
  "jazz-night": [
    { id: "a3", name: "Marcus Webb", email: "marcus@example.com", ticket: "general", checkedIn: false },
    { id: "a1", name: "ada Okafor", email: "ada@example.com", ticket: "vip", checkedIn: true },
    { id: "a4", name: "Olive Sato", email: "olive@example.com", ticket: "general", checkedIn: false },
    { id: "a2", name: "Ben Ruiz", email: "ben.ruiz@example.com", ticket: "general", checkedIn: false },
  ],
  "empty-room": [],
  flaky: [{ id: "f1", name: "Fran Lee", email: "fran@example.com", ticket: "vip", checkedIn: false }],
};

let flakyCalls = 0;
const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const fakeApi: AttendeesApi = {
  async list(eventId) {
    await wait(500);
    if (eventId === "flaky" && flakyCalls++ === 0) throw new Error("503 Service Unavailable");
    return (ATTENDEES[eventId] ?? []).map((a) => ({ ...a }));
  },
  async setCheckedIn(attendeeId) {
    await wait(400);
    if (attendeeId === "a4") throw new Error("409 Conflict");
  },
};
