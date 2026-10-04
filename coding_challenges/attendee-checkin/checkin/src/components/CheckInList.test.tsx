import { render, screen, within } from "@testing-library/react";
import type { Attendee, AttendeesApi } from "../types";
import { CheckInList } from "./CheckInList";

const ATTENDEES: Attendee[] = [
  { id: "a2", name: "Ben Ruiz", email: "ben@example.com", ticket: "general", checkedIn: false },
  { id: "a1", name: "Ada Okafor", email: "ada@example.com", ticket: "vip", checkedIn: true },
];

function fakeApi(attendees: Attendee[]): AttendeesApi {
  return {
    list: vi.fn().mockResolvedValue(attendees),
    setCheckedIn: vi.fn().mockResolvedValue(undefined),
  };
}

it("shows a loading message, then everyone sorted by name", async () => {
  const api = fakeApi(ATTENDEES);
  render(<CheckInList eventId="jazz-night" api={api} />);

  expect(screen.getByText("Loading attendees…")).toBeInTheDocument();

  const list = await screen.findByRole("list");
  const names = within(list).getAllByRole("listitem").map((li) => li.textContent);
  expect(names[0]).toContain("Ada Okafor");
  expect(names[1]).toContain("Ben Ruiz");
  expect(screen.getByText("1 of 2 checked in")).toBeInTheDocument();
  expect(api.list).toHaveBeenCalledWith("jazz-night");
});

// TODO: add your tests here (see README.md, task 3)
