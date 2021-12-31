import math

import pandas as pd

from mabooia.collections import Stream


def read_excel_table(filepath, sheet) -> Stream:
    with open(filepath, "rb") as file:
        dfs = pd.read_excel(file, sheet_name=sheet)\
            if isinstance(sheet, str)\
            else pd.read_csv(file)

        cols = Stream.of(dfs.head().columns) \
            .take(1000) \
            .to_list()

        def to_obj(row):
            obj = dict()
            for idx in range(len(cols)):
                field = str(cols[idx])
                val = row[idx]
                obj[field] = val if not isinstance(val, float) or not math.isnan(val) else None

            return obj

        return Stream.of(dfs.values) \
            .map(to_obj)
