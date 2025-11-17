from PyQt6.QtGui import QCursor

from openauto.repositories.db_handlers import connect_db
import datetime
from openauto.repositories import db_handlers
from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository
from typing import Optional





class RepairOrdersRepository:
    ALLOWED_STATUSES = {"open", "approved", "working", "checkout", "archived"}


    @staticmethod
    def create_repair_order(customer_id, vehicle_id, appointment_id=None, ro_number=None, created_by=None, assigned_writer_id=None):
        if ro_number is None:
            ro_number = RepairOrdersRepository.generate_next_ro_number()

        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO repair_orders (customer_id, vehicle_id, appointment_id, ro_number, created_by, assigned_writer_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (customer_id, vehicle_id, appointment_id, ro_number, created_by, assigned_writer_id)
        cursor.execute(query, values)
        conn.commit()
        ro_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return ro_id


    @staticmethod
    def get_repair_order_by_id(ro_id):
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ro.*,
                   CONCAT(t.first_name,' ',t.last_name) AS tech_name,
                   CONCAT(w.first_name,' ',w.last_name) AS writer_name,
                   ro.assigned_tech_id,
                   ro.assigned_writer_id,
                   ro.created_by,
                   ro.vehicle_id,
                   ro.created_at
            FROM repair_orders ro
            LEFT JOIN users t ON t.id = ro.assigned_tech_id
            -- writer fallback: assigned writer OR creator (writer can be writer or manager)
            LEFT JOIN users w ON w.id = COALESCE(ro.assigned_writer_id, ro.created_by)
            WHERE ro.id = %s
        """, (ro_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result


    @staticmethod
    def lock_repair_order(ro_id, locked_by):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE repair_orders
            SET locked_by = %s, locked_at = NOW()
            WHERE id = %s AND (locked_by IS NULL OR locked_by = %s)
        """, (locked_by, ro_id, locked_by))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def release_lock(ro_id, locked_by):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE repair_orders
            SET locked_by = NULL, locked_at = NULL
            WHERE id = %s AND locked_by = %s
        """, (ro_id, locked_by))
        conn.commit()
        cursor.close()
        conn.close()


    @staticmethod
    def generate_next_ro_number():
        conn = connect_db()
        cursor = conn.cursor()
        year = datetime.datetime.now().year
        prefix = f"{year}-%"

        query = """
            SELECT ro_number FROM repair_orders
            WHERE ro_number LIKE %s
            ORDER BY ro_number DESC LIMIT 1
        """
        cursor.execute(query, (prefix,))
        last = cursor.fetchone()
        cursor.close()
        conn.close()

        if last and last[0]:
            last_seq = int(last[0].split("-")[1])
        else:
            last_seq = 0

        return f"{year}-{last_seq + 1:05d}"

    @staticmethod
    def load_repair_orders(status="open", limit=200, offset=0):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """
            SELECT
                ro.id,
                ro.ro_number,
                ro.created_at,
                CONCAT(c.first_name, ' ', c.last_name) AS name,
                v.year,
                v.make,
                v.model,
                CONCAT(t.first_name,' ',t.last_name) AS tech,
                -- writer fallback to creator if no assigned writer
                CONCAT(w.first_name,' ',w.last_name) AS writer,
                0.00 AS total
            FROM repair_orders ro
            LEFT JOIN customers c ON c.customer_id = ro.customer_id
            LEFT JOIN vehicles  v ON v.id = ro.vehicle_id
            LEFT JOIN users     t ON t.id = ro.assigned_tech_id
            LEFT JOIN users     w ON w.id = COALESCE(ro.assigned_writer_id, ro.created_by)
            WHERE ro.status = %s
            ORDER BY ro.ro_number
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (status, limit, offset))
        result = cursor.fetchall() or []
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def delete_repair_order(estimate_id: int):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM repair_orders WHERE id = %s", (estimate_id,))
        conn.commit()
        cursor.close()
        conn.close()


    @staticmethod
    def update_status(ro_id: int, new_status: str):
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as c:
            c.execute(
                "UPDATE repair_orders SET status=%s, updated_at=NOW() WHERE id=%s",
                (new_status, ro_id)
            )
            conn.commit()

    @staticmethod
    def set_status_and_cascade(ro_id: int, status: str):
        status = (status or "open").strip().lower()
        RepairOrdersRepository.update_status(ro_id, status)
        if status == "open":
            est_id = RepairOrdersRepository.estimate_id_for_ro(ro_id)
            if est_id:
                EstimateJobsRepository.set_all_status_for_estimate(est_id, "proposed")

    @staticmethod
    def assign_staff(ro_id: int, writer_id: int | None = None, tech_id: int | None = None):
        sets, vals = [], []
        if writer_id is not None:
            sets.append("assigned_writer_id = %s")
            vals.append(writer_id)
        if tech_id is not None:
            sets.append("assigned_tech_id = %s")
            vals.append(tech_id)
        if not sets:
            return
        vals.append(ro_id)
        q = f"UPDATE repair_orders SET {', '.join(sets)} WHERE id = %s"

        cnx = db_handlers.connect_db()
        with cnx.cursor() as cur:
            cur.execute(q, tuple(vals))
            cnx.commit()

    @staticmethod
    def get_status(ro_id: int) -> str | None:
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT status FROM repair_orders WHERE id=%s""", (ro_id, ))
        result = cursor.fetchone()
        return result[0] if result else None


    @staticmethod
    def get_create_altered_date(ro_id):
        conn = db_handlers.connect_db()
        cursor = conn.cursor(dictionary=True)
        query = """SELECT created_at, updated_at, miles_in, miles_out, status FROM repair_orders WHERE id = %s"""
        cursor.execute(query, (ro_id, ))
        result = cursor.fetchone() or {}
        return result

    @staticmethod
    def update_miles(miles_in, miles_out, ro_id):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """UPDATE repair_orders set miles_in = %s, miles_out = %s where id = %s"""
        cursor.execute(query, (miles_in, miles_out, ro_id))
        cursor.close()
        conn.close()

    @staticmethod
    def estimate_id_for_ro(ro_id: int) -> Optional[int]:
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as c:
            c.execute("SELECT estimate_id FROM repair_orders WHERE id=%s", (ro_id,))
            row = c.fetchone()
            return row[0] if row and row[0] is not None else None

    @staticmethod
    def recompute_ro_approval(ro_id: int, approved_by_id: Optional[int] = None):
        conn = db_handlers.connect_db()
        with conn, conn.cursor(dictionary=True) as c:
            c.execute("SELECT estimate_id FROM repair_orders WHERE id=%s", (ro_id,))
            r = c.fetchone()
            if not r or r["estimate_id"] is None:
                return
            est_id = r["estimate_id"]

            # how many jobs total vs approved
            c.execute("""
              SELECT COUNT(*) AS total,
                     SUM(status='approved') AS approved
              FROM estimate_jobs
              WHERE estimate_id=%s
            """, (est_id,))
            row = c.fetchone()
            total = int(row["total"] or 0)
            approved = int(row["approved"] or 0)

            if total > 0 and approved == total:
                # fully approved: set status=approved + approved_at/by + approved_total (all jobs)
                c.execute("""
                    SELECT COALESCE(SUM(total),0) AS t
                      FROM estimate_jobs
                     WHERE estimate_id=%s
                """, (est_id,))
                (approved_total,) = c.fetchone().values()
                c.execute("""
                  UPDATE repair_orders
                     SET approved_at   = COALESCE(approved_at, NOW()),
                         approved_by_id= COALESCE(approved_by_id, %s),
                         approved_total= %s,
                         status        = 'approved',
                         updated_at    = NOW()
                   WHERE id = %s
                """, (approved_by_id, approved_total, ro_id))
            elif total > 0 and approved > 0:
                # partially approved: move tile bucket to 'approved' but DO NOT set approved_at/by
                # compute total of only approved jobs (for your badge/summary)
                c.execute("""
                    SELECT COALESCE(SUM(j.total),0) AS t
                      FROM estimate_jobs j
                     WHERE j.estimate_id=%s AND j.status='approved'
                """, (est_id,))
                (approved_total,) = c.fetchone().values()
                c.execute("""
                  UPDATE repair_orders
                     SET approved_total = %s,
                         approved_at    = NULL,
                         approved_by_id = NULL,
                         status         = 'approved',  -- <— key change for tiles bucket
                         updated_at     = NOW()
                   WHERE id = %s
                """, (approved_total, ro_id))
            else:
                # no approved jobs: tile goes back to Estimates
                c.execute("""
                  UPDATE repair_orders
                     SET approved_at    = NULL,
                         approved_by_id = NULL,
                         approved_total = NULL,
                         status         = 'open',
                         updated_at     = NOW()
                   WHERE id = %s
                """, (ro_id,))
            conn.commit()
            conn.close()



    @staticmethod
    def approve_all(ro_id: int, approved_by_id: Optional[int]):
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as c:
            c.execute("SELECT estimate_id FROM repair_orders WHERE id=%s", (ro_id,))
            (est_id,) = c.fetchone()

            # Approve all jobs + items for this estimate
            c.execute("""
              UPDATE estimate_jobs
                 SET status='approved', approved_at=NOW(), approved_by_id=%s
               WHERE estimate_id=%s
            """, (approved_by_id, est_id))
            c.execute("""
              UPDATE estimate_items i
              JOIN estimate_jobs j ON i.job_id=j.id
                 SET i.status='approved', i.approved_at=NOW(), i.approved_by_id=%s
               WHERE j.estimate_id=%s
            """, (approved_by_id, est_id))

            # Stamp RO
            c.execute("SELECT COALESCE(SUM(total),0) FROM estimate_jobs WHERE estimate_id=%s", (est_id,))
            (approved_total,) = c.fetchone()
            c.execute("""
               UPDATE repair_orders
                  SET approved_at=NOW(),
                      approved_by_id=%s,
                      approved_total=%s,
                      status='approved',
                      updated_at=NOW()
                WHERE id=%s
            """, (approved_by_id, approved_total, ro_id))
            conn.commit()
            conn.close()

    @staticmethod
    def _estimate_id_for_job(job_id: int) -> Optional[int]:
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as c:
            c.execute("SELECT estimate_id FROM estimate_jobs WHERE id=%s", (job_id,))
            row = c.fetchone()
            return row[0] if row else None

    @staticmethod
    def _ro_id_for_estimate(estimate_id: int) -> Optional[int]:
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as c:
            c.execute("SELECT id FROM repair_orders WHERE estimate_id=%s LIMIT 1", (estimate_id,))
            row = c.fetchone()
            return row[0] if row else None

    @staticmethod
    def approve_job(job_id: int, approved_by_id: Optional[int] = None):
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as c:
            # approve job
            c.execute("""
                 UPDATE estimate_jobs
                    SET status='approved', approved_at=NOW(), approved_by_id=%s
                  WHERE id=%s
             """, (approved_by_id, job_id))
            # approve all items in the job
            c.execute("""
                 UPDATE estimate_items
                    SET status='approved', approved_at=NOW(), approved_by_id=%s
                  WHERE job_id=%s
             """, (approved_by_id, job_id))
            conn.commit()

        # recompute RO approval
        est_id = RepairOrdersRepository._estimate_id_for_job(job_id)
        if est_id is not None:
            ro_id = RepairOrdersRepository._ro_id_for_estimate(est_id)
            if ro_id is not None:
                RepairOrdersRepository.recompute_ro_approval(ro_id, approved_by_id=approved_by_id)

    @staticmethod
    def decline_job(job_id: int, declined_by_id: Optional[int] = None):
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as c:
            # decline job
            c.execute("""
                 UPDATE estimate_jobs
                    SET status='declined', declined_at=NOW(), approved_by_id=%s
                  WHERE id=%s
             """, (declined_by_id, job_id))
            # decline all items in the job
            c.execute("""
                 UPDATE estimate_items
                    SET status='declined', declined_at=NOW(), approved_by_id=%s
                  WHERE job_id=%s
             """, (declined_by_id, job_id))
            conn.commit()

        # recompute RO approval (likely clears approved_at)
        est_id = RepairOrdersRepository._estimate_id_for_job(job_id)
        if est_id is not None:
            ro_id = RepairOrdersRepository._ro_id_for_estimate(est_id)
            if ro_id is not None:
                RepairOrdersRepository.recompute_ro_approval(ro_id, approved_by_id=declined_by_id)


    @staticmethod
    def jobs_counts_for_ro(ro_id: int) -> tuple[int, int, int]:
        conn = connect_db()
        with conn, conn.cursor() as c:
            c.execute("SELECT estimate_id FROM repair_orders WHERE id=%s", (ro_id,))
            row = c.fetchone()
            if not row or row[0] is None:
                return (0, 0, 0)
            est_id = row[0]
            c.execute("""
                SELECT COUNT(*) AS total,
                       SUM(status='approved') AS approved,
                       SUM(status='declined') AS declined
                FROM estimate_jobs
                WHERE estimate_id=%s
            """, (est_id,))
            total, approved, declined = c.fetchone()
            return int(total or 0), int(approved or 0), int(declined or 0)

    @staticmethod
    def get_approved_at(ro_id: int):
        conn = connect_db()
        with conn, conn.cursor() as c:
            c.execute("SELECT approved_at FROM repair_orders WHERE id=%s", (ro_id,))
            row = c.fetchone()
            return row[0] if row else None

    @staticmethod
    def ro_id_by_appointment(appointment_id: int) -> Optional[int]:
        conn = connect_db()
        with conn, conn.cursor() as c:
            c.execute("""
                SELECT id
                FROM repair_orders
                WHERE appointment_id=%s
                ORDER BY id DESC
                LIMIT 1
                """, (appointment_id, ))
            row = c.fetchone()
            return int(row[0]) if row else None

    @staticmethod
    def estimate_total_for_ro(ro_id: int) -> Optional[float]:
        est_id = RepairOrdersRepository.estimate_id_for_ro(ro_id)
        if not est_id:
            return None
        conn = db_handlers.connect_db()
        with conn, conn.cursor() as cur:
            # Compute a tax-inclusive total directly from items, and
            # ignore any declined jobs/items so tiles match what you
            # actually expect to bill.
            cur.execute(
                """
                SELECT COALESCE(SUM(
                           CASE
                               WHEN j.status = 'declined' OR i.status = 'declined'
                                   THEN 0
                               ELSE ROUND(
                                   COALESCE(i.qty, 1) * COALESCE(i.unit_price, 0) *
                                   (1 + (CASE WHEN i.taxable = 1
                                              THEN COALESCE(i.tax_pct, 0) / 100
                                              ELSE 0 END)),
                                   2
                               )
                           END
                       ), 0) AS t
                  FROM estimate_items i
                  LEFT JOIN estimate_jobs j
                         ON j.id = i.job_id
                 WHERE i.estimate_id = %s
                """,
                (est_id,),
            )
            row = cur.fetchone()
            if not row:
                return 0.0
            # row may be a tuple or dict depending on cursor config
            val = row[0] if not isinstance(row, dict) else row.get("t")
            try:
                return float(val or 0.0)
            except Exception:
                return 0.0

    @staticmethod
    def car_counts_by_day(start_date, end_date):
        """
        Return list of tuples (date, count) representing how many repair orders
        were created each day between start_date and end_date (inclusive).
        """
        conn = connect_db()
        try:
            with conn.cursor() as c:
                c.execute(
                    """
                    SELECT DATE(created_at) AS d, COUNT(*) AS total
                      FROM repair_orders
                     WHERE created_at BETWEEN %s AND %s
                       AND vehicle_id IS NOT NULL
                     GROUP BY DATE(created_at)
                     ORDER BY d
                    """,
                    (start_date, end_date),
                )
                rows = c.fetchall() or []
                # rows is list of tuples; ensure consistent types
                out = []
                for row in rows:
                    day = row[0]
                    count = row[1] if len(row) > 1 else None
                    out.append((day, int(count or 0)))
                return out
        finally:
            conn.close()

    @staticmethod
    def heartbeat():
        conn = connect_db()
        with conn, conn.cursor() as c:
            c.execute("""
                SELECT
                  UNIX_TIMESTAMP(COALESCE(MAX(updated_at), '1970-01-01')) AS maxu,
                  COUNT(*)                                  AS total,
                  SUM(status='open')                        AS open_cnt,
                  SUM(status='approved')                    AS appr_cnt,
                  SUM(status='working')                     AS work_cnt,
                  SUM(status='checkout')                    AS chk_cnt
                FROM repair_orders
            """)
            row = c.fetchone() or (0, 0, 0, 0, 0, 0)
            return tuple(int(x or 0) for x in row)

    @staticmethod
    def delete_repair_order_cascade(ro_id: int):
        from openauto.repositories.estimate_items_repository import EstimateItemsRepository
        from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository

        # get estimate_id
        est_id = RepairOrdersRepository.estimate_id_for_ro(ro_id)

        # wipe items by RO
        try:
            EstimateItemsRepository.delete_for_ro(ro_id)
        except Exception:
            pass

        # wipe jobs and estimate row, if present
        if est_id:
            try:
                EstimateJobsRepository.delete_jobs(est_id, [j["id"] for j in (EstimateJobsRepository.list_for_estimate(est_id) or [])])
            except Exception:
                pass
            try:
                cn = connect_db()
                with cn, cn.cursor() as c:
                    c.execute("DELETE FROM pt_sessions WHERE estimate_id=%s AND ro_id=%s", (est_id, ro_id))
                    c.execute("DELETE FROM estimates WHERE id=%s", (est_id,))
                    cn.commit()
            except Exception:
                pass

        # finally remove the RO
        cn = connect_db()
        with cn, cn.cursor() as c:
            c.execute("DELETE FROM repair_orders WHERE id=%s", (ro_id,))
            cn.commit()
            cn.close()

    @staticmethod
    def get_ro_items(ro_id: int | None = None):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM repair_orders WHERE id=%s", ro_id)
        result = cursor.fetchall()
        return result if result else None
