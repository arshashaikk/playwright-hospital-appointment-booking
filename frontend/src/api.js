async function request(path, options) {
  const res = await fetch(path, options);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    let message = body.detail || "Something went wrong";
    if (Array.isArray(message))
      message = message.map((e) => e.msg.replace(/^Value error, /, "")).join(", ");
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  return body;
}

export const api = {
  departments: () => request("/api/departments"),
  doctors: (department, q) => {
    const p = new URLSearchParams();
    if (department) p.set("department", department);
    if (q) p.set("q", q);
    return request(`/api/doctors?${p}`);
  },
  slots: (doctorId, date) => request(`/api/doctors/${doctorId}/slots?date=${date}`),
  book: (payload) =>
    request("/api/appointments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
};
