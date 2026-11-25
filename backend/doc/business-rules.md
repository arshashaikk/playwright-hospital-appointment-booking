# Business Rules

## Scheduling
- Slots are 30 minutes, 09:00–16:30, **no slots in the 13:00 hour** (lunch): 14 slots per day.
- Bookable window: today through today + 30 days. Past or later dates have no slots.
- A slot is unavailable if it is **pre-booked** (deterministic rule in `data.prebooked`:
  `(doctor_id + day_of_month + hour + minute/30) % 4 == 0`) or already booked in the store.
- Each doctor has their own availability; booking one doctor's slot does not affect another's.

## Patient details
| Field | Rule |
|-------|------|
| Name  | at least 2 characters after trimming |
| Phone | spaces, dashes and parentheses are stripped; must then match `^\+?\d{10,13}$`. Stored in cleaned form |
| Email | valid email address (`EmailStr` server side, simple regex client side) |

## Booking integrity
1. A slot can be booked once; a second attempt returns **409**.
2. The same email cannot book the same doctor on the same date twice (**409**), even for a different slot.
3. The confirmation shows exactly the doctor, date and time that were booked.
4. After a 409 the UI refreshes the slot grid so the taken slot is shown disabled.

## The four defects from the brief and the rule that prevents each
| # | Reported problem | Rule | Bug flag that breaks it |
|---|------------------|------|-------------------------|
| 1 | Patients book unavailable slots | rule 1 | `double_book` |
| 2 | Invalid phone numbers accepted | phone rule | `weak_phone` |
| 3 | Confirmation shows wrong doctor | rule 3 | `wrong_doctor` |
| 4 | Same appointment submitted twice | rule 2 + disabled button | `duplicate_submit` |
