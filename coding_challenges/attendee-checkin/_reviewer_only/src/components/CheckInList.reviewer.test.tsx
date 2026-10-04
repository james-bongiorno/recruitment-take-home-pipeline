/**
 * Extra checks (reviewer only). Copy into the candidate's src/components/ and run `npm test`.
 * They only rely on the visible text the README asks for.
 */
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { Attendee, AttendeesApi } from "../types";
import { CheckInList } from "./CheckInList";

const ATTENDEES: Attendee[] = [
  { id: "a3", name: "marcus Webb", email: "marcus@example.com", ticket: "general", checkedIn: false },
  { id: "a1", name: "Ada Okafor", email: "ada@example.com", ticket: "vip", checkedIn: true },
  { id: "a2", name: "Ben Ruiz", email: "ben.ruiz@example.com", ticket: "general", checkedIn: false },
];

const api = (overrides: Partial<AttendeesApi> = {}): AttendeesApi => ({
  list: vi.fn().mockResolvedValue(ATTENDEES.map((a) => ({ ...a }))),
  setCheckedIn: vi.fn().mockResolvedValue(undefined),
  ...overrides,
});

async function rows() {
  const list = await screen.findByRole("list");
  return within(list).getAllByRole("listitem");
}

const rowFor = async (name: string) => (await rows()).find((r) => r.textContent?.includes(name))!;

it("sorts by name ignoring case and marks VIPs", async () => {
  render(<CheckInList eventId="e" api={api()} />);
  const items = await rows();
  expect(items.map((r) => r.textContent)).toEqual([
    expect.stringContaining("Ada Okafor"),
    expect.stringContaining("Ben Ruiz"),
    expect.stringContaining("marcus Webb"),
  ]);
  expect(items[0]).toHaveTextContent("VIP");
  expect(items[1]).not.toHaveTextContent("VIP");
});

it("checks someone in right away and saves it", async () => {
  const a = api();
  render(<CheckInList eventId="e" api={a} />);
  await userEvent.click(within(await rowFor("Ben Ruiz")).getByRole("button", { name: "Check in" }));
  expect(within(await rowFor("Ben Ruiz")).getByRole("button", { name: "Undo check-in" })).toBeInTheDocument();
  expect(screen.getByText("2 of 3 checked in")).toBeInTheDocument();
  expect(a.setCheckedIn).toHaveBeenCalledWith("a2", true);
});

it("updates before the server answers (optimistic)", async () => {
  let finish!: () => void;
  const slow = api({ setCheckedIn: vi.fn(() => new Promise<void>((r) => (finish = r))) });
  render(<CheckInList eventId="e" api={slow} />);
  await userEvent.click(within(await rowFor("Ben Ruiz")).getByRole("button", { name: "Check in" }));
  expect(screen.getByText("2 of 3 checked in")).toBeInTheDocument();
  finish();
});

it("rolls back and explains when saving fails", async () => {
  const failing = api({ setCheckedIn: vi.fn().mockRejectedValue(new Error("409")) });
  render(<CheckInList eventId="e" api={failing} />);
  await userEvent.click(within(await rowFor("Ben Ruiz")).getByRole("button", { name: "Check in" }));
  expect(await screen.findByText("Couldn't update Ben Ruiz. Try again.")).toBeInTheDocument();
  expect(within(await rowFor("Ben Ruiz")).getByRole("button", { name: "Check in" })).toBeInTheDocument();
  expect(screen.getByText("1 of 3 checked in")).toBeInTheDocument();
});

it("can undo a check-in", async () => {
  const a = api();
  render(<CheckInList eventId="e" api={a} />);
  await userEvent.click(within(await rowFor("Ada Okafor")).getByRole("button", { name: "Undo check-in" }));
  expect(a.setCheckedIn).toHaveBeenCalledWith("a1", false);
  expect(screen.getByText("0 of 3 checked in")).toBeInTheDocument();
});

it("searches by name or email, ignoring case", async () => {
  render(<CheckInList eventId="e" api={api()} />);
  await rows();
  await userEvent.type(screen.getByLabelText("Search attendees"), "RUIZ");
  expect((await rows()).map((r) => r.textContent)).toEqual([expect.stringContaining("Ben Ruiz")]);
  await userEvent.clear(screen.getByLabelText("Search attendees"));
  await userEvent.type(screen.getByLabelText("Search attendees"), "ada@");
  expect((await rows()).map((r) => r.textContent)).toEqual([expect.stringContaining("Ada Okafor")]);
});

it("says so when nobody matches, and the count still covers everyone", async () => {
  render(<CheckInList eventId="e" api={api()} />);
  await rows();
  await userEvent.type(screen.getByLabelText("Search attendees"), "zed");
  expect(screen.getByText('No attendees match "zed".')).toBeInTheDocument();
  expect(screen.getByText("1 of 3 checked in")).toBeInTheDocument();
});

it("shows an empty state", async () => {
  render(<CheckInList eventId="e" api={api({ list: vi.fn().mockResolvedValue([]) })} />);
  expect(await screen.findByText("No attendees yet.")).toBeInTheDocument();
});

it("shows an error and retries", async () => {
  const flaky = api({
    list: vi.fn().mockRejectedValueOnce(new Error("503")).mockResolvedValueOnce(ATTENDEES),
  });
  render(<CheckInList eventId="e" api={flaky} />);
  expect(await screen.findByText("Couldn't load attendees.")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(await screen.findByRole("list")).toBeInTheDocument();
  expect(flaky.list).toHaveBeenCalledTimes(2);
});
