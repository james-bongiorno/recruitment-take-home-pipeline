# Interview material

A 45-minute live-interview problem written in the 8 languages most used for full-stack work. Candidates can use the one they're strongest in, and you can still compare them fairly.

| Language | File | Run it with |
|---|---|---|
| JavaScript | `problems/problem.js` | `node problem.js` |
| TypeScript | `problems/problem.ts` | `npx tsx problem.ts`, or `node --experimental-strip-types problem.ts` (Node 22.6+) |
| Python | `problems/problem.py` | `python3 problem.py` |
| Java | `problems/Problem.java` | `java Problem.java` (Java 17+) |
| C# | `problems/Problem.cs` | `dotnet run Problem.cs` (.NET 10+). Older versions: see the file header. |
| Go | `problems/problem.go` | `go run problem.go` (Go 1.21+) |
| PHP | `problems/problem.php` | `php problem.php` (PHP 8+) |
| Ruby | `problems/problem.rb` | `ruby problem.rb` |

Each file is self-contained, with no packages to install. The checks at the bottom print PASS or FAIL.

**The problem: library loans.** It works out how late each loan is, the late fee and whether it's overdue, then builds a per-member summary.
1. **Debug (~10 min):** three small functions, each with one bug.
2. **Implement (~15 min):** write `memberSummary`, which groups loans by member.
3. **Bonus (open-ended):** renewals, broken records, or serving the summary from an API.

`solutions/` has the answer key for each language, and **`INTERVIEWER_GUIDE.md`** covers running and scoring the session. Both are public here, so for real interviews, write your own problem in the same shape, or at least change the data and the bugs.

Every problem file was run before it went in. Each one fails the same 5 checks and passes the same 2, and every answer key passes all 7. The CI workflow checks the Python and JavaScript versions on every push.
