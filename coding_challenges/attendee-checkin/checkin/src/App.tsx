import { useState } from "react";
import { fakeApi } from "./api";
import { CheckInList } from "./components/CheckInList";

export function App() {
  const [eventId, setEventId] = useState("jazz-night");
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 640, margin: "2rem auto" }}>
      <h1>Door check-in</h1>
      <label>
        Event{" "}
        <select value={eventId} onChange={(e) => setEventId(e.target.value)}>
          <option value="jazz-night">Jazz Night</option>
          <option value="empty-room">Empty Room (no attendees)</option>
          <option value="flaky">Flaky (fails once)</option>
        </select>
      </label>
      <CheckInList key={eventId} eventId={eventId} api={fakeApi} />
    </main>
  );
}
