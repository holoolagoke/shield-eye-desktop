def css_styles(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #07102a;
            color: #cbd5e1;
            font-size: 13px;
        }
        QTableView {
            gridline-color: #123047;
            background-color: #061323;
        }
        QHeaderView::section {
            background-color: #081428;
            padding: 4px;
            border: 1px solid #123047;
        }
        """)