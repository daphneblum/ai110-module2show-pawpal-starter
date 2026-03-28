import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, TaskCategory, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Owner & Pet setup ---
st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=90)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize Owner and Pet in session state only on the first run
if "owner" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species, age=0)
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes=int(available_minutes),
        preferences="",
    )
    st.session_state.owner.add_pet(st.session_state.pet)

owner = st.session_state.owner
pet = st.session_state.pet

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    priority_map = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
    new_task = Task(
        id=f"t{len(pet.tasks) + 1}",
        title=task_title,
        category=TaskCategory.OTHER,
        duration_minutes=int(duration),
        priority=priority_map[priority],
    )
    pet.add_task(new_task)       # <- Pet.add_task()
    st.success(f"Added: {new_task}")

if pet.tasks:
    st.write(f"Tasks for {pet.name}:")
    st.table([
        {"title": t.title, "duration (min)": t.duration_minutes, "priority": t.priority.value}
        for t in pet.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    plan = owner.generate_plan()         # <- Owner.generate_plan()
    st.subheader("Today's Schedule")
    st.text(plan.get_summary())          # <- DailyPlan.get_summary()
    st.divider()
    st.subheader("Why each task was chosen")
    scheduler = Scheduler()
    st.text(scheduler.explain_plan(plan))  # <- Scheduler.explain_plan()
