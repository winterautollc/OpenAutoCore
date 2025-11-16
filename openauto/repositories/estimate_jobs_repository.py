from typing import Optional
from openauto.repositories.db_handlers import connect_db

class EstimateJobsRepository:
    @staticmethod
    def get_or_create(estimate_id: int, name: str) -> int:
        conn = connect_db()
        name = (name or "General").strip()
        with conn, conn.cursor() as c:
            c.execute(
                "SELECT id FROM estimate_jobs WHERE estimate_id=%s AND name=%s LIMIT 1",
                (estimate_id, name)
            )
            row = c.fetchone()
            if row:
                return row[0]
            c.execute(
                "INSERT INTO estimate_jobs (estimate_id, name, status, total) VALUES (%s,%s,'proposed',0)",
                (estimate_id, name)
            )
            conn.commit()
            conn.close()
            return c.lastrowid


    @staticmethod
    def recompute_totals_for_estimate(estimate_id: int) -> None:
        conn = connect_db()
        with conn, conn.cursor() as c:
            c.execute(
                """
                UPDATE estimate_jobs j
                LEFT JOIN (
                  SELECT job_id, COALESCE(SUM(line_total), 0) AS t
                  FROM estimate_items
                  WHERE estimate_id = %s
                  GROUP BY job_id
                ) x ON x.job_id = j.id
                SET j.total = COALESCE(x.t, 0)
                WHERE j.estimate_id = %s
                """,
                (estimate_id, estimate_id),
            )
            conn.commit()
            conn.close()

    @staticmethod
    def rename_or_merge(job_id: int, new_name: str) -> int:
        new_name = (new_name or "General").strip()
        conn = connect_db()
        with conn, conn.cursor(dictionary=True) as c:
            # 1) find this job's estimate
            c.execute("SELECT id, estimate_id FROM estimate_jobs WHERE id=%s", (job_id,))
            row = c.fetchone()
            if not row:
                return job_id  # nothing to do
            est_id = row["estimate_id"]

            # 2) is there already a job with the target name on this estimate?
            c.execute("""
                SELECT id FROM estimate_jobs
                WHERE estimate_id=%s AND name=%s AND id<>%s
                LIMIT 1
            """, (est_id, new_name, job_id))
            existing = c.fetchone()

            if existing:
                keep_id = int(existing["id"])
                # move items from 'job_id' to 'keep_id'
                c.execute("UPDATE estimate_items SET job_id=%s WHERE job_id=%s", (keep_id, job_id))
                # delete the duplicate job
                c.execute("DELETE FROM estimate_jobs WHERE id=%s", (job_id,))
                # recompute totals for the kept job
                c.execute("""
                    UPDATE estimate_jobs j
                    LEFT JOIN (
                      SELECT job_id, COALESCE(SUM(line_total),0) AS t
                      FROM estimate_items
                      WHERE job_id=%s
                      GROUP BY job_id
                    ) x ON x.job_id = j.id
                    SET j.total = COALESCE(x.t,0)
                    WHERE j.id=%s
                """, (keep_id, keep_id))
                conn.commit()
                return keep_id
            else:
                # no collision: plain rename
                c.execute("UPDATE estimate_jobs SET name=%s WHERE id=%s", (new_name, job_id))
                conn.commit()
                return job_id

    @staticmethod
    def delete_jobs(estimate_id: int, job_ids: list[int]) -> None:
        conn = connect_db()
        cursor = conn.cursor()
        if not job_ids:
            return
        sql = f"DELETE FROM estimate_jobs WHERE estimate_id=%s AND id IN ({','.join(['%s'] * len(job_ids))})"
        cursor.execute(sql, (estimate_id, *job_ids))
        cursor.close()
        conn.close()

    @staticmethod
    def list_for_estimate(estimate_id: int):
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as c:
                c.execute("""
                    SELECT id, name, status, total
                    FROM estimate_jobs
                    WHERE estimate_id=%s
                    ORDER BY id
                """, (estimate_id,))
                return c.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def get_jobs_for_estimate(estimate_id: int):
        return EstimateJobsRepository.list_for_estimate(estimate_id)

    @staticmethod
    def get_jobs_for_ro(ro_id: int):
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as c:
                c.execute(
                    """
                    SELECT j.id, j.name, j.status, j.total
                    FROM estimate_jobs j
                    JOIN estimates e ON e.id = j.estimate_id
                    WHERE e.ro_id = %s
                    ORDER BY j.id
                    """,
                    (ro_id,),
                )
                return c.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def set_status(job_id: int, status: str, by_user_id: Optional[int] = None):
        """Set a job's status and mirror to its items. Maps 'open' -> 'proposed' for ENUM."""
        db_status = "approved" if status == "approved" else ("declined" if status == "declined" else "proposed")
        conn = connect_db()
        with conn, conn.cursor() as c:
            if db_status == "approved":
                # job
                c.execute("""
                      UPDATE estimate_jobs
                         SET status='approved',
                             approved_at   = COALESCE(approved_at, NOW()),
                             approved_by_id= COALESCE(approved_by_id, %s),
                             declined_at   = NULL
                       WHERE id=%s
                  """, (by_user_id, job_id))
                # items
                c.execute("""
                      UPDATE estimate_items
                         SET status='approved',
                             approved_at   = COALESCE(approved_at, NOW()),
                             approved_by_id= COALESCE(approved_by_id, %s),
                             declined_at   = NULL
                       WHERE job_id=%s
                  """, (by_user_id, job_id))

            elif db_status == "declined":
                # job
                c.execute("""
                      UPDATE estimate_jobs
                         SET status='declined',
                             declined_at   = COALESCE(declined_at, NOW()),
                             approved_by_id= NULL,
                             approved_at   = NULL
                       WHERE id=%s
                  """, (job_id,))
                # items
                c.execute("""
                      UPDATE estimate_items
                         SET status='declined',
                             declined_at   = COALESCE(declined_at, NOW()),
                             approved_by_id= NULL,
                             approved_at   = NULL
                       WHERE job_id=%s
                  """, (job_id,))

            else:  # proposed (aka 'open' in UI)
                # job
                c.execute("""
                      UPDATE estimate_jobs
                         SET status='proposed',
                             approved_at   = NULL,
                             approved_by_id= NULL,
                             declined_at   = NULL
                       WHERE id=%s
                  """, (job_id,))
                # items
                c.execute("""
                      UPDATE estimate_items
                         SET status='proposed',
                             approved_at   = NULL,
                             approved_by_id= NULL,
                             declined_at   = NULL
                       WHERE job_id=%s
                  """, (job_id,))
            conn.commit()

    @staticmethod
    def set_all_status_for_estimate(estimate_id: int, status: str):
        # db_status = "approved" if status == "approved" else ("declined" if status == "declined" else "proposed")
        conn = connect_db()
        with conn, conn.cursor() as c:
            # jobs
            c.execute(
                "UPDATE estimate_jobs SET status=%s, approved_at=NULL, approved_by_id=NULL, declined_at=NULL WHERE estimate_id=%s",
                (status, estimate_id))
            # items
            c.execute("UPDATE estimate_items SET status=%s, approved_at=NULL, approved_by_id=NULL, declined_at=NULL "
                      "WHERE estimate_id=%s", (status, estimate_id))
            conn.commit()
