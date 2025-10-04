from openauto.repositories.settings_repository import SettingsRepository

class TaxConfigController:
    def __init__(self, ui):
        self.ui = ui

    def connect_tax_rate(self):
        try:
            tax, *rest = SettingsRepository.get_tax_rates()
            self.ui.tax_rate = tax
            self.ui.tax_edit.setText(f" {str(tax)}%")
        except:
            pass
