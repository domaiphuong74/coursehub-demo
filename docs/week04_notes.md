# CourseHub - Buoi 4 Summary

## 1. Concurrency Test
- Endpoint: `POST /enrollments`
- Mechanism: Transaction row lock `SELECT ... FOR UPDATE` tren bang `class_sections`.
- Target: Class `RACE-01` (capacity = 1).
- Test Result:
  - Worker 1 (22000002): Status `201 Created`
  - Worker 2 (22000004): Status `409 Conflict` (Lop hoc phan da het cho)
  - Final State: `enrolled = 1`, `remaining = 0`.

## 2. Performance Tuning (100,000 events)
- Target Query: Tim 50 su kien gan nhat theo `dataset`, `student_id` va `occurred_at`.
- **Before Index**:
  - Scan Type: `Seq Scan`
  - Execution Time: ~11.099 ms
  - Rows Removed by Filter: ~99,183
- **Index Created**: `idx_enrollment_events_dataset_student_time` on `(dataset, student_id, occurred_at DESC)`
- **After Index**:
  - Scan Type: `Index Scan`
  - Execution Time: ~0.462 ms (Nhanh hon ~24 lan)
  - Buffers shared hit: Giam tu 1,140 xuong 53.