from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Tuple, Dict, Any
from openauto.repositories import db_handlers
import mysql.connector


@dataclass
class MPIInspection:
    id: Optional[int] = None
    ro_id: Optional[int] = None
    estimate_id: Optional[int] = None
    vin: Optional[str] = None
    customer_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    mileage_in: Optional[int] = None
    inspection_at: Optional[str] = None  # ISO str or None; DB defaults to NOW
    created_by: Optional[int] = None
    status: str = "draft"  # 'draft' | 'final'
    notes: Optional[str] = None


@dataclass
class MPIFinding:
    id: Optional[int] = None
    inspection_id: int = 0
    section: str = ""         # 'tires','brakes','fluids','interior_exterior','under_hood','battery', etc.
    item_code: str = ""       # 'horn','head_lights','rf_tire','lf_brake','engine_oil', ...
    position: str = "na"      # 'na','rf','lf','rr','lr','front','rear','left','right'
    result_label: str = ""    # 'ok','attention','fail','measured','filled','recharge_test',...
    severity: Optional[int] = None  # 0,1,2 for sorting/dashboards
    measurement_value: Optional[float] = None
    measurement_unit: Optional[str] = None
    note: Optional[str] = None
    sort_order: int = 0



### For MPI inspections and findings ###
    # ensures indexes, create inspections etc.
class MPIRepository:
    def __init__(self, conn_factory=None):
        self._conn_factory = conn_factory or db_handlers.connect_db

    # ---------- Bootstrapping / Indexes ----------

    def ensure_indexes(self) -> None:
        sqls = [
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uniq_line
            ON mpi_findings (inspection_id, item_code, position);
            """,
            "CREATE INDEX IF NOT EXISTS idx_mpi_findings_ins ON mpi_findings (inspection_id);",
            "CREATE INDEX IF NOT EXISTS idx_mpi_ro   ON mpi_inspections (ro_id);",
            "CREATE INDEX IF NOT EXISTS idx_mpi_est  ON mpi_inspections (estimate_id);",
            "CREATE INDEX IF NOT EXISTS idx_mpi_vin  ON mpi_inspections (vin);",
        ]
        conn = self._conn_factory()
        try:
            cur = conn.cursor()
            for s in sqls:
                try:
                    cur.execute(s)
                except mysql.connector.Error:
                    conn.rollback()
            conn.commit()
        finally:
            conn.close()

    #Inspections
    def create_inspection(self, header: MPIInspection) -> int:
        conn = self._conn_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO mpi_inspections
                (ro_id, estimate_id, vin, customer_id, vehicle_id, mileage_in, inspection_at, created_by, status, notes)
                VALUES (%s,%s,%s,%s,%s,%s,COALESCE(%s, NOW()),%s,%s,%s)
                """,
                (
                    header.ro_id, header.estimate_id, header.vin,
                    header.customer_id, header.vehicle_id,
                    header.mileage_in, header.inspection_at,
                    header.created_by, header.status, header.notes
                )
            )
            new_id = cur.lastrowid
            conn.commit()
            return int(new_id)
        finally:
            conn.close()

    def ensure_inspection_for_context(
        self,
        ro_id: Optional[int] = None,
        estimate_id: Optional[int] = None,
        vin: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> int:

        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)

            if ro_id is not None:
                cur.execute(
                    "SELECT id FROM mpi_inspections WHERE ro_id=%s AND status='draft' ORDER BY id DESC LIMIT 1",
                    (ro_id,)
                )
                row = cur.fetchone()
                if row:
                    return int(row["id"])

            if estimate_id is not None:
                cur.execute(
                    "SELECT id FROM mpi_inspections WHERE estimate_id=%s AND status='draft' ORDER BY id DESC LIMIT 1",
                    (estimate_id,)
                )
                row = cur.fetchone()
                if row:
                    return int(row["id"])

            if vin:
                cur.execute(
                    "SELECT id FROM mpi_inspections WHERE vin=%s AND status='draft' ORDER BY id DESC LIMIT 1",
                    (vin,)
                )
                row = cur.fetchone()
                if row:
                    return int(row["id"])

            new_id = self.create_inspection(
                MPIInspection(
                    ro_id=ro_id, estimate_id=estimate_id, vin=vin,
                    created_by=created_by, status="draft"
                )
            )
            return new_id
        finally:
            conn.close()

    def update_inspection_header(self, inspection_id: int, **fields) -> None:
        if not fields:
            return
        columns = []
        params = []
        for k, v in fields.items():
            if k not in {
                "ro_id","estimate_id","vin","customer_id","vehicle_id",
                "mileage_in","inspection_at","created_by","status","notes"
            }:
                continue
            columns.append(f"{k}=%s")
            params.append(v)
        if not columns:
            return

        params.append(inspection_id)
        conn = self._conn_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE mpi_inspections SET {', '.join(columns)} WHERE id=%s",
                tuple(params)
            )
            conn.commit()
        finally:
            conn.close()

    def finalize_inspection(self, inspection_id: int) -> None:
        self.update_inspection_header(inspection_id, status="final")

    def delete_inspection(self, inspection_id: int) -> None:
        conn = self._conn_factory()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM mpi_inspections WHERE id=%s", (inspection_id,))
            conn.commit()
        finally:
            conn.close()

    #Findings
    def add_or_update_finding(self, f: MPIFinding) -> int:
        conn = self._conn_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO mpi_findings
                  (inspection_id, section, item_code, position, result_label, severity,
                   measurement_value, measurement_unit, note, sort_order)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  section=VALUES(section),
                  result_label=VALUES(result_label),
                  severity=VALUES(severity),
                  measurement_value=VALUES(measurement_value),
                  measurement_unit=VALUES(measurement_unit),
                  note=VALUES(note),
                  sort_order=VALUES(sort_order)
                """,
                (
                    f.inspection_id, f.section, f.item_code, f.position, f.result_label, f.severity,
                    f.measurement_value, f.measurement_unit, f.note, f.sort_order
                )
            )
            if cur.lastrowid:  # insert path
                finding_id = int(cur.lastrowid)
            else:
                cur.execute(
                    "SELECT id FROM mpi_findings WHERE inspection_id=%s AND item_code=%s AND position=%s",
                    (f.inspection_id, f.item_code, f.position)
                )
                row = cur.fetchone()
                finding_id = int(row[0]) if row else 0
            conn.commit()
            return finding_id
        finally:
            conn.close()

    def bulk_upsert_findings(self, findings: Iterable[MPIFinding]) -> None:
        items = list(findings)
        if not items:
            return
        conn = self._conn_factory()
        try:
            cur = conn.cursor()
            sql = """
                INSERT INTO mpi_findings
                (inspection_id, section, item_code, position, result_label, severity,
                 measurement_value, measurement_unit, note, sort_order)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  section=VALUES(section),
                  result_label=VALUES(result_label),
                  severity=VALUES(severity),
                  measurement_value=VALUES(measurement_value),
                  measurement_unit=VALUES(measurement_unit),
                  note=VALUES(note),
                  sort_order=VALUES(sort_order)
            """
            params = [
                (
                    f.inspection_id, f.section, f.item_code, f.position, f.result_label, f.severity,
                    f.measurement_value, f.measurement_unit, f.note, f.sort_order
                )
                for f in items
            ]
            cur.executemany(sql, params)
            conn.commit()
        finally:
            conn.close()

    def delete_finding(self, inspection_id: int, item_code: str, position: str = "na") -> None:
        conn = self._conn_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM mpi_findings WHERE inspection_id=%s AND item_code=%s AND position=%s",
                (inspection_id, item_code, position)
            )
            conn.commit()
        finally:
            conn.close()

    #Queries
    def get_inspection(self, inspection_id: int) -> Optional[MPIInspection]:
        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM mpi_inspections WHERE id=%s", (inspection_id,))
            row = cur.fetchone()
            if not row:
                return None
            return MPIInspection(**row)
        finally:
            conn.close()

    def get_inspection_with_findings(self, inspection_id: int) -> Tuple[Optional[MPIInspection], List[MPIFinding]]:
        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM mpi_inspections WHERE id=%s", (inspection_id,))
            head = cur.fetchone()
            if not head:
                return None, []
            cur.execute(
                "SELECT * FROM mpi_findings WHERE inspection_id=%s ORDER BY sort_order, id",
                (inspection_id,)
            )
            rows = cur.fetchall() or []
            return MPIInspection(**head), [MPIFinding(**r) for r in rows]
        finally:
            conn.close()

    def find_latest_by_context(
        self,
        ro_id: Optional[int] = None,
        estimate_id: Optional[int] = None,
        vin: Optional[str] = None,
        include_final: bool = True,
    ) -> Optional[int]:
        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)

            def _grab(q: str, p: Tuple[Any, ...]) -> Optional[int]:
                cur.execute(q, p)
                r = cur.fetchone()
                return int(r["id"]) if r else None

            if ro_id is not None:
                iid = _grab("SELECT id FROM mpi_inspections WHERE ro_id=%s AND status='draft' ORDER BY id DESC LIMIT 1", (ro_id,))
                if iid: return iid
                if include_final:
                    iid = _grab("SELECT id FROM mpi_inspections WHERE ro_id=%s ORDER BY id DESC LIMIT 1", (ro_id,))
                    if iid: return iid

            if estimate_id is not None:
                iid = _grab("SELECT id FROM mpi_inspections WHERE estimate_id=%s AND status='draft' ORDER BY id DESC LIMIT 1", (estimate_id,))
                if iid: return iid
                if include_final:
                    iid = _grab("SELECT id FROM mpi_inspections WHERE estimate_id=%s ORDER BY id DESC LIMIT 1", (estimate_id,))
                    if iid: return iid

            if vin:
                iid = _grab("SELECT id FROM mpi_inspections WHERE vin=%s AND status='draft' ORDER BY id DESC LIMIT 1", (vin,))
                if iid: return iid
                if include_final:
                    iid = _grab("SELECT id FROM mpi_inspections WHERE vin=%s ORDER BY id DESC LIMIT 1", (vin,))
                    if iid: return iid

            return None
        finally:
            conn.close()

    def list_by_ro(self, ro_id: int, limit: int = 20) -> List[MPIInspection]:
        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM mpi_inspections WHERE ro_id=%s ORDER BY id DESC LIMIT %s",
                (ro_id, limit)
            )
            return [MPIInspection(**r) for r in (cur.fetchall() or [])]
        finally:
            conn.close()

    def list_by_estimate(self, estimate_id: int, limit: int = 20) -> List[MPIInspection]:
        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM mpi_inspections WHERE estimate_id=%s ORDER BY id DESC LIMIT %s",
                (estimate_id, limit)
            )
            return [MPIInspection(**r) for r in (cur.fetchall() or [])]
        finally:
            conn.close()

    def list_by_vin(self, vin: str, limit: int = 20) -> List[MPIInspection]:
        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM mpi_inspections WHERE vin=%s ORDER BY id DESC LIMIT %s",
                (vin, limit)
            )
            return [MPIInspection(**r) for r in (cur.fetchall() or [])]
        finally:
            conn.close()

    # mpi_manager bridge
    def save_inspection(
        self,
        ro_number: str,
        data: Dict[str, Any],
        *,
        created_by: Optional[int] = None
    ) -> int:

        header = (data or {}).get("header", {}) or {}
        checks = (data or {}).get("checks", {}) or {}
        measures = (data or {}).get("measurements", {}) or {}

        ro_ctx = self._resolve_ro_context(ro_number)
        if not ro_ctx:
            raise ValueError(f"RO not found for ro_number={ro_number!r}")

        ro_id = ro_ctx["ro_id"]
        estimate_id = ro_ctx.get("estimate_id")
        vin = header.get("vin") or ro_ctx.get("vehicle_vin")
        customer_id = ro_ctx.get("customer_id")
        vehicle_id = ro_ctx.get("vehicle_id")

        inspection_id = self.ensure_inspection_for_context(
            ro_id=ro_id, estimate_id=estimate_id, vin=vin, created_by=created_by
        )

        mileage_in = self._parse_int(header.get("mileage"))
        self.update_inspection_header(
            inspection_id,
            mileage_in=mileage_in,
            notes=header.get("notes"),
            created_by=created_by
        )

        findings = list(self._payload_to_findings(inspection_id, checks, measures))

        self.bulk_upsert_findings(findings)

        return inspection_id

    #Internals
    def _resolve_ro_context(self, ro_number: str) -> Optional[Dict[str, Any]]:
        conn = self._conn_factory()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT
                    ro.id          AS ro_id,
                    ro.ro_number   AS ro_number,
                    ro.estimate_id AS estimate_id,
                    ro.customer_id AS customer_id,
                    ro.vehicle_id  AS vehicle_id,
                    v.vin          AS vehicle_vin
                FROM repair_orders ro
                LEFT JOIN vehicles v ON v.id = ro.vehicle_id
                WHERE ro.ro_number = %s
                LIMIT 1
                """,
                (ro_number,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def _parse_int(value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            s = str(value).replace(",", "").strip()
            return int(s) if s else None
        except Exception:
            return None

    @staticmethod
    def _tri_state(ok: bool, attn: bool, fail: bool) -> Optional[str]:
        # Priority: fail > attention > ok
        if fail:
            return "fail"
        if attn:
            return "attention"
        if ok:
            return "ok"
        return None

    #convert mpi_manager payload into mpi_findings
    def _payload_to_findings(
        self,
        inspection_id: int,
        checks: Dict[str, str],
        measures: Dict[str, Optional[int]],
    ) -> Iterable[MPIFinding]:

        measures = measures or {}
        measure_map: Dict[str, Tuple[float, Optional[str]]] = {}
        for name, val in measures.items():
            if val is None:
                continue
            item_code = name.replace("_line", "")
            unit = "32nds" if "tire" in item_code else ("mm" if "brake" in item_code else None)
            measure_map[item_code] = (float(val), unit)

        # ---- checks -> categorical results, attach measurement if present
        for code, state in (checks or {}).items():
            section = self._infer_section(code)
            position = self._infer_position(code)
            measurement_value = None
            measurement_unit = None
            if code in measure_map:
                measurement_value, measurement_unit = measure_map.pop(code)
            yield MPIFinding(
                inspection_id=inspection_id,
                section=section,
                item_code=code,
                position=position,
                result_label=state,
                severity={"ok": 0, "attention": 1, "fail": 2}.get(state, None),
                measurement_value=measurement_value,
                measurement_unit=measurement_unit,
                sort_order=10,
            )

        # ---- remaining measures (without checkboxes selected)
        for item_code, (value, unit) in measure_map.items():
            section = self._infer_section(item_code)
            position = self._infer_position(item_code)
            yield MPIFinding(
                inspection_id=inspection_id,
                section=section,
                item_code=item_code,
                position=position,
                result_label="measured",
                measurement_value=value,
                measurement_unit=unit,
                sort_order=50,
            )

    @staticmethod
    def _infer_position(code: str) -> str:
        prefixes = ("rf", "lf", "rr", "lr", "front", "rear", "left", "right")
        for p in prefixes:
            if code.startswith(p + "_"):
                return p
        return "na"

    @staticmethod
    def _infer_section(code: str) -> str:
        c = code.lower()
        if "tire" in c:
            return "tires"
        if "brake" in c:
            return "brakes"
        if any(k in c for k in ("oil", "coolant", "trans", "washer", "fluid")):
            return "fluids"
        if any(k in c for k in ("battery", "charging", "alt", "starter")):
            return "battery"
        if any(k in c for k in ("belt", "hose", "filter", "air", "engine")):
            return "under_hood"
        if any(k in c for k in ("wiper", "light", "lamp", "horn")):
            return "interior_exterior"
        return "general"
