/** Reference solution (reviewer only). One reasonable answer, not the only one. */
import { useEffect, useState } from "react";
import { countCheckedIn, matchesSearch, sortAttendees } from "../lib/attendees";
import type { Attendee, AttendeesApi } from "../types";

interface Props {
  eventId: string;
  api: AttendeesApi;
}

type Load = { status: "loading" } | { status: "error" } | { status: "ready" };

export function CheckInList({ eventId, api }: Props) {
  const [load, setLoad] = useState<Load>({ status: "loading" });
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const [failure, setFailure] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    setLoad({ status: "loading" });
    api
      .list(eventId)
      .then((list) => {
        if (ignore) return;
        setAttendees(list);
        setLoad({ status: "ready" });
      })
      .catch(() => !ignore && setLoad({ status: "error" }));
    return () => {
      ignore = true;
    };
  }, [api, eventId, attempt]);

  const setChecked = (id: string, checkedIn: boolean) =>
    setAttendees((current) => current.map((a) => (a.id === id ? { ...a, checkedIn } : a)));

  async function toggle(attendee: Attendee) {
    const next = !attendee.checkedIn;
    setFailure(null);
    setChecked(attendee.id, next); // optimistic
    try {
      await api.setCheckedIn(attendee.id, next);
    } catch {
      setChecked(attendee.id, !next); // roll back
      setFailure(`Couldn't update ${attendee.name}. Try again.`);
    }
  }

  if (load.status === "loading") return <p role="status">Loading attendees…</p>;
  if (load.status === "error") {
    return (
      <div role="alert">
        <p>Couldn't load attendees.</p>
        <button onClick={() => setAttempt((n) => n + 1)}>Try again</button>
      </div>
    );
  }
  if (attendees.length === 0) return <p>No attendees yet.</p>;

  const shown = sortAttendees(attendees).filter((a) => matchesSearch(a, query));

  return (
    <section>
      <p>
        {countCheckedIn(attendees)} of {attendees.length} checked in
      </p>
      <label>
        Search attendees{" "}
        <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} />
      </label>
      {failure && <p role="alert">{failure}</p>}
      {shown.length === 0 ? (
        <p>No attendees match "{query.trim()}".</p>
      ) : (
        <ul>
          {shown.map((a) => (
            <li key={a.id}>
              <strong>{a.name}</strong> {a.email} {a.ticket === "vip" && <span>VIP</span>}{" "}
              <button onClick={() => toggle(a)}>{a.checkedIn ? "Undo check-in" : "Check in"}</button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
