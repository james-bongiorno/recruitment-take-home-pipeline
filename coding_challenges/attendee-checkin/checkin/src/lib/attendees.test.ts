import type { Attendee } from "../types";
import { countCheckedIn, matchesSearch, sortAttendees } from "./attendees";

const person = (id: string, name: string, checkedIn = false): Attendee => ({
  id, name, email: `${id}@example.com`, ticket: "general", checkedIn,
});

describe("sortAttendees", () => {
  it("sorts by name, ignoring case", () => {
    const sorted = sortAttendees([person("1", "marcus"), person("2", "Ada"), person("3", "ben")]);
    expect(sorted.map((a) => a.name)).toEqual(["Ada", "ben", "marcus"]);
  });

  it("does not change the array it was given", () => {
    const original = [person("1", "Marcus"), person("2", "Ada")];
    sortAttendees(original);
    expect(original.map((a) => a.name)).toEqual(["Marcus", "Ada"]);
  });
});

describe("matchesSearch", () => {
  it("matches name or email, ignoring case and spaces", () => {
    expect(matchesSearch(person("ada", "Ada Okafor"), "  OKA ")).toBe(true);
    expect(matchesSearch(person("ada", "Ada Okafor"), "ada@")).toBe(true);
    expect(matchesSearch(person("ada", "Ada Okafor"), "ben")).toBe(false);
  });
});

it("counts who is checked in", () => {
  expect(countCheckedIn([person("1", "A", true), person("2", "B")])).toBe(1);
});
