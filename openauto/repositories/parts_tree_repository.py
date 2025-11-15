import json
from openauto.repositories.db_handlers import connect_db


VALID_STATUSES = {"quoted", "ordered", "received", "returned", "cancelled"}


class PartsTreeRepository:
    def ensure_session(self, *, session_id: str, estimate_id: int | None = None, ro_id: int | None = None,
                                                vin: str | None = None) -> None:

        if not session_id:
            return

        # normalize inputs
        try:
            est = int(estimate_id) if estimate_id is not None else None
        except Exception:
            est = None
        try:
            ro = int(ro_id) if ro_id is not None else None
        except Exception:
            ro = None
        v = (vin or "").strip()
        if v and len(v) != 17:
            v = ""  # ignore bad VINs

        # only write meaningful values; keep existing ones otherwise
        est_val = est if (est and est > 0) else None
        ro_val  = ro  if (ro  and ro  > 0) else None

        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO pt_sessions (session_id, vin, estimate_id, ro_id)
            VALUES (%s, NULLIF(%s,''), %s, %s)
            ON DUPLICATE KEY UPDATE
              vin = COALESCE(NULLIF(%s,''), vin),
              estimate_id = COALESCE(%s, estimate_id),
              ro_id = COALESCE(%s, ro_id),
              updated_at = NOW()
            """,
            (session_id, v, est_val, ro_val,  # INSERT values
             v, est_val, ro_val)              # UPDATE values
        )
        conn.commit()
        cur.close()
        conn.close()

    def upsert_submit_cart(self, payload: dict, estimate_id: int | None = None, default_status: str = "quoted"):
        if not isinstance(payload, dict):
            return
        sess = str(payload.get("sessionId") or "")
        if not sess:
            return

        # Link session to estimate/VIN like before
        vin = ""
        v1 = (payload.get("vehicle") or {}).get("vin")
        v2 = payload.get("vin")
        if isinstance(v1, str):
            vin = v1
        elif isinstance(v2, str):
            vin = v2
        self.ensure_session(session_id=sess, estimate_id=estimate_id, vin=vin or None)

        conn = connect_db()
        try:
            with conn:
                cur = conn.cursor()

                seen_suppliers: set[int | None] = set()
                seen_order_items: set[str] = set()

                orders = payload.get("orders") or []
                for od in orders:
                    sup = od.get("supplier") or {}
                    sup_id = sup.get("id")
                    sup_name = sup.get("name")

                    # Upsert pt_orders with uniqueness on (session_id, supplier_id)
                    cur.execute(
                        """INSERT INTO pt_orders
                               (session_id, supplier_id, supplier_name, payment_type, tax,
                                total_price, total_discount, core_charge, fet, shipping_price)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE
                               supplier_name = VALUES(supplier_name),
                               payment_type  = VALUES(payment_type),
                               tax           = VALUES(tax),
                               total_price   = VALUES(total_price),
                               total_discount= VALUES(total_discount),
                               core_charge   = VALUES(core_charge),
                               fet           = VALUES(fet),
                               shipping_price= VALUES(shipping_price),
                               updated_at    = NOW(),
                               id = LAST_INSERT_ID(id)""",
                        (sess, sup_id, sup_name, od.get("paymentType"),
                         od.get("tax"), od.get("totalPrice"), od.get("totalDiscount"),
                         od.get("coreCharge"), od.get("fet"), od.get("shippingPrice"))
                    )
                    order_id = cur.lastrowid
                    seen_suppliers.add(sup_id)

                    # Upsert items for this order
                    for p in (od.get("parts") or []):
                        price = p.get("price") or {}
                        taxonomy = p.get("taxonomy") or {}
                        status = p.get("status") or default_status
                        if status not in VALID_STATUSES:
                            status = default_status
                        oi = str(p.get("orderItemId") or p.get("id") or "")
                        if not oi:
                            continue
                        seen_order_items.add(oi)
                        cur.execute(
                            """INSERT INTO pt_order_items
                                 (order_item_id, session_id, order_id, supplier_id, supplier_name,
                                  part_id, part_number, part_type_id, part_type_name,
                                  quantity, unit_cost, list_price, core, availability, status, raw_json)
                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, CAST(%s AS JSON))
                               ON DUPLICATE KEY UPDATE
                                  session_id=VALUES(session_id), order_id=VALUES(order_id),
                                  supplier_id=VALUES(supplier_id), supplier_name=VALUES(supplier_name),
                                  part_id=VALUES(part_id), part_number=VALUES(part_number),
                                  part_type_id=VALUES(part_type_id), part_type_name=VALUES(part_type_name),
                                  quantity=VALUES(quantity), unit_cost=VALUES(unit_cost), list_price=VALUES(list_price),
                                  core=VALUES(core), availability=VALUES(availability), 
                                  status = CASE
                                    WHEN pt_order_items.status IN ('ordered','received','returned','cancelled')
                                            THEN pt_order_items.status
                                    ELSE VALUES(status)
                                    END,
                                  raw_json=VALUES(raw_json), updated_at=NOW()""",
                            (oi, sess, order_id, sup_id, sup_name,
                             p.get("partId"), p.get("partNumber"),
                             taxonomy.get("partTypeId") or p.get("partTypeId"),
                             taxonomy.get("partTypeName") or p.get("partTypeName"),
                             p.get("quantity"),
                             price.get("cost"), price.get("list"), price.get("core"),
                             p.get("availability"), status,
                             json.dumps(p))
                        )

                # --- PRUNE: remove items not in the latest payload for this session
                if seen_order_items:
                    placeholders = ",".join(["%s"] * len(seen_order_items))
                    cur.execute(
                        f"""DELETE FROM pt_order_items
                             WHERE session_id=%s
                               AND order_item_id NOT IN ({placeholders})
                               AND status IN ('quoted')""",
                        [sess, *sorted(seen_order_items)]
                    )

                # --- PRUNE: remove supplier orders with no longer-present suppliers
                if seen_suppliers:
                    placeholders = ",".join(["%s"] * len(seen_suppliers))
                    cur.execute(
                        f"DELETE FROM pt_orders "
                        f"WHERE session_id=%s AND supplier_id NOT IN ({placeholders})",
                        [sess, *sorted(seen_suppliers)]
                    )
                else:
                    # No suppliers in callback -> purge all orders for session
                    cur.execute("DELETE FROM pt_orders WHERE session_id=%s", (sess,))

                # Also remove any orphan pt_orders that have zero items (defensive)
                cur.execute(
                    """DELETE o FROM pt_orders o
                       LEFT JOIN pt_order_items i ON i.order_id = o.id
                       WHERE o.session_id = %s AND i.order_id IS NULL""",
                    (sess,)
                )

                conn.commit()

        finally:
            try:
                conn.close()
            except Exception:
                pass

    def link_session_to_estimate(self, session_id: str, estimate_id: int) -> None:
        if not session_id:
            return
        try:
            est = int(estimate_id)
        except Exception:
            return
        if est <= 0:
            return
        conn = connect_db(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO pt_sessions (session_id, estimate_id) VALUES (%s,%s) "
            "ON DUPLICATE KEY UPDATE estimate_id=%s, updated_at=NOW()",
            (session_id, est, est)
        )
        conn.commit()
        cur.close(); conn.close()

    def get_estimate_for_session(self, session_id: str) -> int | None:
        if not session_id:
            return None
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT estimate_id from pt_sessions WHERE session_id=%s", (session_id, ))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        est = row[0]
        try:
            est = int(est)
        except Exception:
            return None
        return est if est and est > 0 else None

    def load_items_for_estimate(self, estimate_id: int) -> list[dict]:
        sql = """
        SELECT
            oi.order_item_id,
            oi.session_id,
            oi.quantity,
            oi.unit_cost,
            oi.list_price,
            oi.core,
            oi.status,
            oi.part_number,
            oi.part_type_name,
            oi.assigned_job_name,
            oi.assigned_job_id,
            COALESCE(oi.supplier_name, po.supplier_name) AS supplier_name
        FROM pt_order_items AS oi
        JOIN pt_sessions     AS s  ON s.session_id = oi.session_id
        LEFT JOIN pt_orders  AS po ON po.id = oi.order_id
        WHERE s.estimate_id = %s
        ORDER BY 
          CASE oi.status
            WHEN 'quoted'    THEN 0
            WHEN 'ordered'   THEN 1
            WHEN 'received'  THEN 2
            WHEN 'returned'  THEN 3
            WHEN 'cancelled' THEN 4
            ELSE 5
          END,
          oi.updated_at DESC, oi.order_item_id
        """
        rows = []
        conn = connect_db()
        with conn, conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (int(estimate_id),))
            for r in cur.fetchall():
                rows.append({
                    # model/meta fields your loader expects
                    "orderItemId": r["order_item_id"],
                    "sessionId": r["session_id"],
                    "session_id": r["session_id"],
                    "quantity": r["quantity"],
                    "unitCost": r["unit_cost"],
                    "listPrice": r["list_price"],
                    "core": r.get("core") or 0,
                    "status": (r["status"] or "quoted"),
                    "supplierName": r.get("supplier_name") or "",
                    "partNumber": r["part_number"],
                    "partTypeName": r["part_type_name"],
                    "assigned_job_name": r.get("assigned_job_name"),
                    "assigned_job_id":   r.get("assigned_job_id"),
                    # optional passthroughs:
                    "price": {"cost": r["unit_cost"], "list": r["list_price"], "core": r.get("core") or 0},
                    "sku": r["part_number"],
                })
        return rows

    # load rows by a specific session
    def load_items_for_session(self, session_id: str) -> list[dict]:
        if not session_id:
            return []
        conn = connect_db(); cur = conn.cursor()
        cur.execute(
            """
            SELECT supplier_name, part_number, part_type_name, quantity, unit_cost, list_price, core, order_item_id, status
            FROM pt_order_items
            WHERE session_id = %s
            ORDER BY updated_at ASC, order_item_id ASC
            """,
            (session_id,)
        )
        rows = cur.fetchall() or []
        cur.close(); conn.close()
        out = []
        for (supplier_name, part_number, part_type_name, quantity, unit_cost, list_price, core, order_item_id, status) in rows:
            out.append({
                "supplierName": supplier_name,
                "partNumber": part_number,
                "partTypeName": part_type_name,
                "taxonomy": {"partTypeName": part_type_name},
                "quantity": quantity,
                "price": {"cost": unit_cost, "list": list_price, "core": core},
                "orderItemId": order_item_id,
                "sku": part_number,
                "unitCost": unit_cost,
                "listPrice": list_price,
                "status": status or "quoted",
                "sessionId": session_id,
                "session_id": session_id,
                "core": core
            })
        return out

    # reuse the most recent session for an estimate (optionally VIN)
    def latest_session_for_estimate(self, estimate_id: int, vin: str | None = None) -> str | None:
        if not estimate_id:
            return None
        conn = connect_db(); cur = conn.cursor()
        if vin:
            cur.execute(
                """
                SELECT i.session_id
                FROM pt_order_items i
                JOIN pt_sessions s ON s.session_id = i.session_id
                WHERE s.estimate_id = %s
                ORDER BY i.updated_at DESC
                LIMIT 1
                """,
                (estimate_id,)
            )
        else:
            cur.execute(
                """
                SELECT i.session_id
                FROM pt_order_items i
                JOIN pt_sessions s ON s.session_id = i.session_id
                WHERE s.estimate_id = %s
                ORDER BY i.updated_at DESC
                LIMIT 1
                """,
                (estimate_id,)
            )
        row = cur.fetchone()
        cur.close(); conn.close()
        return row[0] if row else None

    def order_item_id_for(self, session_id: str, part_number: str) -> str | None:
        conn = connect_db()
        sql = """
            SELECT order_item_id
            FROM pt_order_items
            WHERE session_id = %s AND part_number = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """
        with conn, conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (session_id, part_number))
            row = cur.fetchone()
            return row["order_item_id"] if row else None


    def delete_order_items(self, session_id: str, order_item_ids: str) -> int:
        if not session_id or not order_item_ids:
            return 0
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM pt_order_items WHERE session_id=%s and order_item_id=%s", (session_id, order_item_ids))
        affected = cur.rowcount or 0
        conn.commit()
        cur.close()
        conn.close()
        return affected

    def get_session_for_order_item(self, order_item_id: str) -> str | None:
        if not order_item_id:
            return None
        conn = connect_db()
        with conn, conn.cursor() as cur:
            cur.execute("SELECT session_id FROM pt_order_items WHERE order_item_id=%s LIMIT 1", (order_item_id,))
            row = cur.fetchone()
        return row[0] if row else None

    def update_items_status(
            self,
            session_id: str,
            status: str,
            order_item_id: str | list[str] | tuple[str, ...] | set[str] | None = None,
    ) -> int:
        allowed = {"quoted", "ordered", "received", "returned", "cancelled"}
        if status not in allowed or not session_id:
            return 0

        conn = connect_db()
        with conn, conn.cursor() as cur:
            # No order_item_id provided ⇒ update ALL rows in this session
            if not order_item_id:
                cur.execute(
                    """
                    UPDATE pt_order_items
                       SET status=%s, updated_at=NOW()
                     WHERE session_id=%s
                    """,
                    (status, session_id),
                )
                affected = cur.rowcount or 0
                conn.commit()
                return affected

            # List/tuple/set of ids ⇒ build IN(...)
            if isinstance(order_item_id, (list, tuple, set)):
                ids = [str(x) for x in order_item_id if x]
                if not ids:
                    return 0
                placeholders = ",".join(["%s"] * len(ids))
                cur.execute(
                    f"""
                    UPDATE pt_order_items
                       SET status=%s, updated_at=NOW()
                     WHERE session_id=%s AND order_item_id IN ({placeholders})
                    """,
                    (status, session_id, *ids),
                )
                affected = cur.rowcount or 0
                conn.commit()
                return affected

            # Single id
            cur.execute(
                """
                UPDATE pt_order_items
                   SET status=%s, updated_at=NOW()
                 WHERE session_id=%s AND order_item_id=%s
                """,
                (status, session_id, str(order_item_id)),
            )
            affected = cur.rowcount or 0
            conn.commit()
            return affected

    def update_item_qty(self, session_id: str, order_item_id: str, new_qty: int) -> bool:
        if not session_id or not order_item_id:
            return False
        try:
            q = int(new_qty)
        except Exception:
            return False
        if q <= 0:
            q = 1
        conn = connect_db()
        with conn, conn.cursor() as cur:
            cur.execute(
                """UPDATE pt_order_items
                   SET quantity=%s, updated_at=NOW()
                 WHERE session_id=%s AND order_item_id=%s""",
                (q, session_id, order_item_id)
            )
            return cur.rowcount > 0


    def session_has_ordered_items(self, session_id: str) -> bool:
        if not session_id:
            return False
        conn = connect_db()
        with conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pt_order_items WHERE session_id=%s AND status='ordered' LIMIT 1",
                (session_id,)
            )
            row = cur.fetchone()
        return bool(row)

    def update_assigned_job(
        self,
        *,
        session_id: str,
        order_item_id: str,
        assigned_job_id: int | None = None,
        assigned_job_name: str | None = None,
    ) -> bool:
        if not (session_id and order_item_id):
            return False
        conn = connect_db()
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pt_order_items
                   SET assigned_job_id   = %s,
                       assigned_job_name = NULLIF(%s,''),
                       updated_at        = NOW()
                 WHERE session_id=%s AND order_item_id=%s
                """,
                (assigned_job_id, assigned_job_name or "", session_id, order_item_id),
            )
            return cur.rowcount > 0

    @staticmethod
    def fetch_estimate_stamps_for_pt():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.estimate_id, MAX(i.updated_at) AS last_ts
               FROM pt_sessions s
               JOIN pt_order_items i ON i.session_id = s.session_id
               WHERE s.estimate_id IS NOT NULL AND s.estimate_id > 0
               GROUP BY s.estimate_id"""
        )
        return cursor.fetchall() or []



