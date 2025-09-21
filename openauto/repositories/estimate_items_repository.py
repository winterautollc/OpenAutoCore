from openauto.repositories.db_handlers import connect_db



class EstimateItemsRepository:
    @staticmethod
    def insert_item(item: dict) -> int:
        conn = connect_db()
        with conn.cursor() as cur:
            # try with ro_id column present
            try:
                cur.execute("""
                    INSERT INTO estimate_items
                      (estimate_id, ro_id, part_number, description, qty, unit_cost, unit_price, taxable, vendor, source, metadata)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (item["estimate_id"], item.get("ro_id"),
                      item.get("part_number"), item.get("description"),
                      item.get("qty", 1), item.get("unit_cost", 0.0), item.get("unit_price", 0.0),
                      item.get("taxable", 1), item.get("vendor"), item.get("source","manual"), item.get("metadata")))
            except Exception:
                # fallback: no ro_id column
                cur.execute("""
                    INSERT INTO estimate_items
                      (estimate_id, part_number, description, qty, unit_cost, unit_price, taxable, vendor, source, metadata)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (item["estimate_id"],
                      item.get("part_number"), item.get("description"),
                      item.get("qty", 1), item.get("unit_cost", 0.0), item.get("unit_price", 0.0),
                      item.get("taxable", 1), item.get("vendor"), item.get("source","manual"), item.get("metadata")))
            conn.commit()
            return cur.lastrowid