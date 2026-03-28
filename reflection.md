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

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When coming up with the UML code, Claude Ai positioned the owner class as one that the scheduler class uses, which I did not think made sense.

- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
