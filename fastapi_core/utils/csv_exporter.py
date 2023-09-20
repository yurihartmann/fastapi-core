from io import StringIO

from fastapi.responses import StreamingResponse
from pydantic import BaseModel


class ModelExportValidationError(Exception):
    def __init__(self, model):
        super().__init__(f"CSVExporter expected data {model} instance")


class CSVExporter:
    __NEW_LINE = "\n"

    def __init__(self, model: type[BaseModel], separator: str = ","):
        self._MODEL = model
        self._sep = separator

    def __generate_headers(self) -> str:
        headers = []

        for filed_name, field_model in self._MODEL.__fields__.items():
            if field_model.field_info.title:
                headers.append(field_model.field_info.title)
            else:
                headers.append(filed_name)

        return self._sep.join(headers)

    def to_csv(self, data: list[type[BaseModel]]) -> StringIO:
        csv = StringIO()
        csv.write(self.__generate_headers())

        for item in data:
            if not isinstance(item, self._MODEL):
                raise ModelExportValidationError(self._MODEL)

            item_data = []
            csv.write(self.__NEW_LINE)

            for value in item.dict().values():
                if not isinstance(value, str) and value is not None:
                    value = str(value)

                item_data.append(value if value else "")

            csv.write(self._sep.join(item_data))

        return csv

    def to_csv_streaming_response(self, data: list[type[BaseModel]], filename: str = "export.csv") -> StreamingResponse:
        stream = self.to_csv(data=data)

        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")

        if not filename.__contains__(".csv"):
            filename += ".csv"

        response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response
