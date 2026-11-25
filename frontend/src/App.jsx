import { useEffect, useState } from "react";
import { api } from "./api";

const todayISO = () => new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD, local time
const maxISO = () => {
  const d = new Date();
  d.setDate(d.getDate() + 30);
  return d.toLocaleDateString("en-CA");
};
const prettyDate = (iso) =>
  new Date(iso + "T00:00:00").toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
const fmt12 = (t) => {
  const [h, m] = t.split(":").map(Number);
  return `${h % 12 || 12}:${String(m).padStart(2, "0")} ${h >= 12 ? "PM" : "AM"}`;
};
const initials = (name) =>
  name
    .replace(/^Dr\.\s*/, "")
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2);

const Icon = ({ d, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d={d} />
  </svg>
);
const ICONS = {
  cross: "M9 3h6v6h6v6h-6v6H9v-6H3V9h6z",
  phone: "M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z",
  calendar: "M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z",
  clock: "M12 6v6l4 2M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z",
  user: "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
  check: "M20 6 9 17l-5-5",
  search: "M21 21l-4.3-4.3M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z",
  shield: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
};

const STEPS = ["Doctor", "Date & time", "Your details"];

export default function App() {
  const [departments, setDepartments] = useState([]);
  const [department, setDepartment] = useState("");
  const [query, setQuery] = useState("");
  const [doctors, setDoctors] = useState([]);
  const [doctor, setDoctor] = useState(null);
  const [date, setDate] = useState(todayISO());
  const [slots, setSlots] = useState([]);
  const [time, setTime] = useState("");
  const [form, setForm] = useState({ name: "", phone: "", email: "" });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState("");
  const [confirmation, setConfirmation] = useState(null);

  useEffect(() => {
    api.departments().then(setDepartments);
  }, []);

  useEffect(() => {
    const t = setTimeout(() => api.doctors(department, query).then(setDoctors), 200);
    return () => clearTimeout(t);
  }, [department, query]);

  useEffect(() => {
    setTime("");
    if (doctor && date) api.slots(doctor.id, date).then(setSlots);
    else setSlots([]);
  }, [doctor, date]);

  const validate = () => {
    const e = {};
    if (form.name.trim().length < 2) e.name = "Name must be at least 2 characters";
    if (!/^\+?\d{10,13}$/.test(form.phone.replace(/[\s\-()]/g, "")))
      e.phone = "Enter a valid phone number (10-13 digits, optional +)";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = "Enter a valid email address";
    return e;
  };

  const submit = async (ev) => {
    ev.preventDefault();
    if (submitting) return;
    setServerError("");
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length) return;
    setSubmitting(true);
    try {
      const appt = await api.book({ doctor_id: doctor.id, date, time, ...form });
      setConfirmation(appt);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setServerError(err.message);
      if (err.status === 409 && doctor) api.slots(doctor.id, date).then(setSlots);
    } finally {
      setSubmitting(false);
    }
  };

  const reset = () => {
    setConfirmation(null);
    setDoctor(null);
    setTime("");
    setForm({ name: "", phone: "", email: "" });
    setErrors({});
    setServerError("");
    setDate(todayISO());
  };

  const currentStep = !doctor ? 0 : !time ? 1 : 2;
  const morning = slots.filter((s) => parseInt(s.time) < 12);
  const afternoon = slots.filter((s) => parseInt(s.time) >= 12);

  const Header = (
    <>
      <div className="topbar">
        <div className="wrap topbar-in">
          <span><Icon d={ICONS.phone} size={14} /> Emergency helpline: <b>108</b></span>
          <span>Open 24/7 · Appointments 9:00 AM – 5:00 PM</span>
        </div>
      </div>
      <header className="header">
        <div className="wrap header-in">
          <div className="brand">
            <span className="logo"><Icon d={ICONS.cross} size={22} /></span>
            <div>
              <div className="brand-name">CityCare Hospital</div>
              <div className="brand-tag">Compassionate care, every day</div>
            </div>
          </div>
          <span className="secure"><Icon d={ICONS.shield} size={16} /> Secure online booking</span>
        </div>
      </header>
    </>
  );

  if (confirmation) {
    return (
      <>
        {Header}
        <main className="wrap narrow">
          <section className="card confirmation" data-testid="confirmation">
            <div className="success-badge"><Icon d={ICONS.check} size={34} /></div>
            <h2>Appointment Confirmed</h2>
            <p className="muted center">
              A confirmation has been sent to <b>{confirmation.email}</b>. Please arrive 15 minutes early.
            </p>
            <div className="ticket">
              <div className="ticket-ref">
                <span>Reference</span>
                <strong data-testid="conf-id">{confirmation.id}</strong>
              </div>
              <dl>
                <dt>Doctor</dt>
                <dd data-testid="conf-doctor">{confirmation.doctor_name}</dd>
                <dt>Department</dt>
                <dd data-testid="conf-department" className="cap">{confirmation.department}</dd>
                <dt>Date</dt>
                <dd data-testid="conf-date">{confirmation.date}</dd>
                <dt>Time</dt>
                <dd data-testid="conf-time">{fmt12(confirmation.time)}</dd>
                <dt>Patient</dt>
                <dd data-testid="conf-name">{confirmation.name}</dd>
                <dt>Phone</dt>
                <dd data-testid="conf-phone">{confirmation.phone}</dd>
                <dt>Email</dt>
                <dd data-testid="conf-email">{confirmation.email}</dd>
              </dl>
            </div>
            <div className="actions">
              <button className="btn primary" onClick={reset} data-testid="book-another">
                Book another appointment
              </button>
              <button className="btn ghost" onClick={() => window.print()}>Print</button>
            </div>
          </section>
        </main>
      </>
    );
  }

  return (
    <>
      {Header}
      <section className="hero">
        <div className="wrap">
          <h1>Book an appointment</h1>
          <p>Choose your doctor, pick a time that suits you, and confirm in under a minute.</p>
        </div>
        <div className="hero-glow" aria-hidden="true" />
      </section>

      <div className="wrap">
        <ol className="stepper" aria-label="Booking progress">
          {STEPS.map((label, i) => (
            <li key={label} className={i < currentStep ? "done" : i === currentStep ? "active" : ""}>
              <span className="dot">{i < currentStep ? <Icon d={ICONS.check} size={14} /> : i + 1}</span>
              {label}
            </li>
          ))}
        </ol>
      </div>

      <main className="wrap layout">
        <div className="main-col">
          <section className="card">
            <h2><span className="num">1</span> Find a doctor</h2>
            <div className="row">
              <label>
                Department
                <select
                  data-testid="department-select"
                  value={department}
                  onChange={(e) => {
                    setDepartment(e.target.value);
                    setDoctor(null);
                  }}
                >
                  <option value="">All departments</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </label>
              <label>
                Search
                <span className="input-icon">
                  <Icon d={ICONS.search} size={16} />
                  <input
                    data-testid="doctor-search"
                    placeholder="Name or specialty"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </span>
              </label>
            </div>
            <ul className="doctors" data-testid="doctor-list">
              {doctors.length === 0 && (
                <li className="empty" data-testid="no-doctors">No doctors found</li>
              )}
              {doctors.map((d) => (
                <li key={d.id}>
                  <button
                    type="button"
                    data-testid={`doctor-${d.id}`}
                    className={doctor?.id === d.id ? "doctor selected" : "doctor"}
                    aria-pressed={doctor?.id === d.id}
                    onClick={() => setDoctor(d)}
                  >
                    <span className="avatar">{initials(d.name)}</span>
                    <span className="doc-info">
                      <strong>{d.name}</strong>
                      <span>{d.specialty}</span>
                    </span>
                    <span className="doc-meta">
                      <span className="tag cap">{d.department}</span>
                      <span className="exp">{d.experience} yrs exp.</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </section>

          {doctor && (
            <section className="card">
              <h2><span className="num">2</span> Choose date &amp; time</h2>
              <label className="date-label">
                Date
                <input
                  type="date"
                  data-testid="date-input"
                  value={date}
                  min={todayISO()}
                  max={maxISO()}
                  onChange={(e) => setDate(e.target.value)}
                />
              </label>
              <div data-testid="slot-grid">
                {slots.length === 0 && (
                  <p className="empty" data-testid="no-slots">No slots for this date</p>
                )}
                {[["Morning", morning], ["Afternoon", afternoon]].map(
                  ([label, list]) =>
                    list.length > 0 && (
                      <div key={label} className="slot-group">
                        <h3>{label}</h3>
                        <div className="slots">
                          {list.map((s) => (
                            <button
                              key={s.time}
                              type="button"
                              data-testid={`slot-${s.time}`}
                              disabled={!s.available}
                              title={s.available ? "Available" : "Unavailable"}
                              className={time === s.time ? "slot selected" : "slot"}
                              aria-pressed={time === s.time}
                              onClick={() => setTime(s.time)}
                            >
                              {fmt12(s.time)}
                            </button>
                          ))}
                        </div>
                      </div>
                    )
                )}
                {slots.length > 0 && (
                  <div className="legend">
                    <span><i className="lg avail" /> Available</span>
                    <span><i className="lg sel" /> Selected</span>
                    <span><i className="lg gone" /> Unavailable</span>
                  </div>
                )}
              </div>
            </section>
          )}

          {doctor && time && (
            <section className="card">
              <h2><span className="num">3</span> Patient details</h2>
              <p className="summary" data-testid="summary">
                {doctor.name} · {prettyDate(date)} at {fmt12(time)}
              </p>
              <form onSubmit={submit} noValidate>
                <label>
                  Full name
                  <input
                    data-testid="name-input"
                    value={form.name}
                    placeholder="e.g. Priya Sharma"
                    className={errors.name ? "invalid" : ""}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                  {errors.name && <span className="error" data-testid="name-error">{errors.name}</span>}
                </label>
                <div className="row">
                  <label>
                    Phone number
                    <input
                      data-testid="phone-input"
                      value={form.phone}
                      placeholder="e.g. 9876543210"
                      className={errors.phone ? "invalid" : ""}
                      onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    />
                    {errors.phone && <span className="error" data-testid="phone-error">{errors.phone}</span>}
                  </label>
                  <label>
                    Email
                    <input
                      data-testid="email-input"
                      value={form.email}
                      placeholder="you@example.com"
                      className={errors.email ? "invalid" : ""}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                    />
                    {errors.email && <span className="error" data-testid="email-error">{errors.email}</span>}
                  </label>
                </div>
                {serverError && (
                  <div className="banner" role="alert" data-testid="server-error">{serverError}</div>
                )}
                <button type="submit" className="btn primary block" data-testid="confirm-btn" disabled={submitting}>
                  {submitting ? "Booking…" : "Confirm appointment"}
                </button>
              </form>
            </section>
          )}
        </div>

        <aside className="side">
          <div className="card sticky">
            <h3 className="side-title">Your appointment</h3>
            <ul className="side-list">
              <li className={doctor ? "" : "pending"}>
                <Icon d={ICONS.user} />
                <div><small>Doctor</small>{doctor ? doctor.name : "Not selected"}</div>
              </li>
              <li className={doctor ? "" : "pending"}>
                <Icon d={ICONS.cross} />
                <div><small>Specialty</small>{doctor ? doctor.specialty : "—"}</div>
              </li>
              <li className={doctor ? "" : "pending"}>
                <Icon d={ICONS.calendar} />
                <div><small>Date</small>{doctor ? prettyDate(date) : "—"}</div>
              </li>
              <li className={time ? "" : "pending"}>
                <Icon d={ICONS.clock} />
                <div><small>Time</small>{time ? fmt12(time) : "Not selected"}</div>
              </li>
            </ul>
            <p className="note">Free cancellation up to 24 hours before your visit. Please bring a photo ID.</p>
          </div>
        </aside>
      </main>

      <footer className="footer">
        <div className="wrap">© {new Date().getFullYear()} CityCare Hospital · 24/7 Emergency 108 · care@citycare.example</div>
      </footer>
    </>
  );
}
