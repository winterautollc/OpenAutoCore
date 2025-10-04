from openauto.repositories.repair_orders_repository import RepairOrdersRepository


class ROStatusService:
    @staticmethod
    def persist(ro_id: int, status_code: str, user_id: int | None = None):
        if status_code == "approved":
            # Approve ALL jobs + stamp RO (approved_at, approved_total)
            RepairOrdersRepository.approve_all(ro_id, user_id)
        else:
            # Just set RO status, then recompute RO approval based on job states
            RepairOrdersRepository.update_status(ro_id, status_code)
            RepairOrdersRepository.recompute_ro_approval(ro_id, approved_by_id=user_id)