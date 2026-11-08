import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function EventHistory({ studentId, refresh }) {
  const [events, setEvents] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const limit = 5;

  useEffect(() => {
    async function fetchEvents() {
      setLoading(true);
      try {
        const skip = (page - 1) * limit;
        const data = await api(
          `/enrollment-events?student_id=${encodeURIComponent(studentId)}&skip=${skip}&limit=${limit}`
        );
        setEvents(data || []);
      } catch (err) {
        console.error("Loi lay nhat ky:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchEvents();
  }, [studentId, page, refresh]);

  return (
    <section className="panel" style={{ marginTop: "18px" }}>
      <h2>4. Nhật ký thao tác (enrollment_events)</h2>
      {loading ? (
        <p>Đang tải nhật ký...</p>
      ) : events.length === 0 ? (
        <p>Không có lịch sử giao dịch cho sinh viên này.</p>
      ) : (
        <ul className="enrollments">
          {events.map((ev) => (
            <li key={ev.id}>
              <div>
                <strong>Lớp: {ev.class_section_id}</strong> -{" "}
                <span className={ev.event_type === "CREATED" ? "badge" : "badge full"}>
                  {ev.event_type}
                </span>
                <span className="subtext">
                  Thời gian: {new Date(ev.occurred_at).toLocaleString("vi-VN")}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div style={{ display: "flex", gap: "10px", marginTop: "12px", alignItems: "center" }}>
        <button
          type="button"
          className="secondary"
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
        >
          Trang trước
        </button>
        <span>Trang {page}</span>
        <button
          type="button"
          className="secondary"
          disabled={events.length < limit}
          onClick={() => setPage((p) => p + 1)}
        >
          Trang sau
        </button>
      </div>
    </section>
  );
}