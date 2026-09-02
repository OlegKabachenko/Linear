class SolverResultInfo(dict):

    def add(
            self,
            key,
            value,
            label,
            bold=False,
            item_label=None,
            value_suffix="",
            order=0,
            value_format="float"
    ):
        self[key] = {
            "value": value,
            "label": label,
            "bold": bold,
            "item_label": item_label,
            "value_suffix": value_suffix,
            "value_format": value_format,
            "order": order
        }

    def add_solution(self, value):
        self.add(
            "solution",
            value,
            "Знайдений розв'язок",
            bold=True,
            item_label="x",
            order=0
        )

    def add_iterations(self, iteration):
        self.add(
            "iterations",
            iteration,
            "Кількість ітерацій",
            bold=True,
            value_format="int",
            order=100
        )

    def add_spectral_radius(self, value):
        self.add(
            "spec_r",
            value,
            "Спектральний радіус",
            bold=True,
            order=10
        )

    def add_norms(self, m, n):
        self.add(
            "row_norm",
            m,
            "Норма по рядках",
            bold=True,
            order=20
        )

        self.add(
            "column_norm",
            n,
            "Норма по стовпцях",
            bold=True,
            order=30
        )

    def add_deltas(self, value):
        self.add(
            "deltas",
            value,
            "Похибки отриманих розв'язків",
            bold=True,
            item_label="Δ",
            order=5
        )

    def add_exec_time(self, value):
        self.add(
            "exec_time",
            value,
            "Час виконання",
            bold=True,
            value_suffix=" с.",
            order=110
        )
