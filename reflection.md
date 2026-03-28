# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

The design uses multiple one-to-many relationships and centers on an Owner who manages one or more Pets, where each Pet has a collection of care Tasks such as feeding, walking, or medication. A Scheduler class is responsible for organizing those tasks into a DailyPlan based on available time and task priority. Supporting classes such as ScheduledTask, Priority, and TaskCategory help represent the final schedule and classify the work clearly. Overall, the design separates data storage from scheduling logic so the system is easier to understand and extend.

- What classes did you include, and what responsibilities did you assign to each?

The classes I included were Owner, Pet, Task, Scheduler, DailyPlan, ScheduledTask, Priority, and TaskCategory.

Owner: stores owner information, preferences, and pets

Pet: stores pet details and its list of tasks

Task: represents an individual care task with duration, category, and priority

Scheduler: builds and prioritizes the plan

DailyPlan: stores the completed schedule for a day

ScheduledTask: represents a task placed into a specific time slot

Priority: defines urgency levels such as low, medium, and high

TaskCategory: classifies tasks like walking, feeding, or medication

**b. Design changes**

- Did your design change during implementation?

yes
- If yes, describe at least one change and why you made it.

Some of the classes created vague logic because they were missing certain information. For example, the Pet class was not linked to the Owner class in the DailyPlan and ScheduledTask classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

My scheduler considers available time and priority of tasks

- How did you decide which constraints mattered most?

If you only have 60 minutes and have 3 hours of tasks, you need a rule for what gets dropped. This is why the constraints are time and priority.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
Tradeoff: The scheduler always drops lower-priority tasks before higher-priority ones when time runs out, even if a dropped low-priority task is very short and a kept high-priority task is very long.

Example: If 10 minutes remain and there's a 5-minute LOW enrichment task and a 60-minute HIGH grooming task, the scheduler keeps the grooming task in the queue even though it can't fit — and drops the enrichment task that could fit.

Why it's reasonable: For pet care, safety-critical tasks like medication (HIGH) should never be skipped just because a shorter fun activity could technically squeeze in. Strict priority ordering ensures the most important care always gets scheduled first. The alternative — fitting as many tasks as possible by duration regardless of priority — risks dropping a medication in favor of three short walks, which would be the wrong outcome.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI throughout the project at several stages. During design, I asked it to generate an initial UML class diagram based on the README requirements, which gave me a starting structure to react to and refine. During implementation, I used it to generate Python class stubs from the finalized UML so I could focus on writing the actual logic rather than boilerplate. I also asked it to explain design decisions — for example, why certain relationships pointed in a particular direction — which helped me catch mistakes in the diagram before writing any code.

- What kinds of prompts or questions were most helpful?

Asking "why" questions was more useful than asking for code directly. For example, asking "why does the Scheduler use the Owner rather than the Owner using the Scheduler?" led to a real explanation of UML dependency direction, which helped me spot the error and correct it myself. Asking the AI to compare the final implementation against the original UML ("what updates should I make?") was also useful because it forced a concrete diff between design and reality rather than a vague summary.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When coming up with the UML code, Claude AI positioned the owner class as one that the Scheduler class uses, which I did not think made sense.

- How did you evaluate or verify what the AI suggested?

I evaluated it by thinking through the real-world flow of the app: in practice, the owner is the one who presses "Generate schedule," so the owner should be the initiator, not a passive data object consumed by the Scheduler. Once I articulated that reasoning, the error in the diagram became obvious. I verified the corrected version by tracing the call chain — `Owner.generate_plan()` creates a `Scheduler` and calls `build_plan()` — and confirming that matched the direction of the arrows in the updated UML.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

The test suite covers six areas: basic Task behavior (marking complete, string representation), Pet task management (adding, removing, and filtering pending tasks), Owner behavior (registering pets and generating a plan), core Scheduler behavior (priority ordering from HIGH to LOW, time-budget enforcement, and multi-pet plans), DailyPlan output (total minutes used and get_summary content), and the three smarter scheduling algorithms — sort_by_time (chronological ordering and untimed tasks sorted to the end), recurring tasks (daily and weekly next-occurrence dates, ID chaining, and one-time tasks returning None), and detect_conflicts (overlapping windows flagged, back-to-back windows not flagged, empty plan returns no warnings).

- Why were these tests important?

The scheduling logic has several places where the wrong behavior would be silent — for example, a task could be skipped without raising an error, or a recurring task could be registered on the wrong pet. Tests made those silent failures visible. Priority ordering was especially important to test because it is the core rule the scheduler uses to resolve time conflicts, and a bug there would affect every plan generated.

**b. Confidence**

- How confident are you that your scheduler works correctly?

4 out of 5. All 31 tests pass and the core behaviors — priority ordering, time-budget enforcement, recurrence chains, conflict detection, and time-based sorting — are covered with both happy-path and edge-case scenarios. One point is withheld because the scheduler is greedy: it skips tasks that do not fit without backtracking, which can leave available time unused when a shorter lower-priority task could have filled the gap. The current tests do not fully stress-test that behavior.

- What edge cases would you test next if you had more time?

The backtracking gap — specifically, a scenario where a LOW task is short enough to fit in remaining time but gets skipped because it sorts after a HIGH task that does not fit. I would also test an owner with zero available minutes, a pet with all tasks already completed, and two tasks with identical start and end times to confirm the conflict detection handles the boundary condition correctly.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The smarter scheduling features — recurring tasks, conflict detection, and time-based sorting — went well. Each one is a self-contained algorithm with a clear input and output, which made them straightforward to implement and test independently. The conflict detection in particular felt satisfying because the interval overlap test is simple to write but easy to get subtly wrong (especially the back-to-back boundary case), and the tests caught that edge case cleanly.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The greedy scheduling algorithm. Right now it processes tasks in strict priority order and skips any task that does not fit, which can leave large gaps in the schedule. A smarter approach would be to backtrack and try fitting shorter lower-priority tasks into the remaining time after a long task is skipped. I would also redesign the `preferences` field on `Owner` — it is currently a plain string with no defined structure, which means the scheduler cannot actually act on it. Making it a structured type (for example, a list of preferred categories or a preferred start time) would make it a real constraint rather than a placeholder.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most valuable thing I learned is that a UML diagram is a thinking tool, not a contract. The initial design had a directional error (Scheduler depending on Owner instead of the reverse) that only became obvious when I asked why the relationship pointed that way. That conversation changed how I think about class relationships — the direction of an arrow reflects who holds the reference, not just who is conceptually "more important." I also learned that AI output is most useful when you treat it as a draft to interrogate rather than an answer to accept, and that asking "why" produces more insight than asking "what."
