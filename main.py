from enum import Enum, auto
from typing import Tuple, List

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.response import KustoResponseDataSet
from termcolor import colored
from loguru import logger

DATABASE: str = "AdvancedHunting"

DOCS_LOCATION: str = "microsoft-365-docs"
ADVANCED_HUNTING_SCHEMA_FILES_LOCATION: str = (
    f"{DOCS_LOCATION}/microsoft-365/security/defender"
)

ADVANCED_HUNTING_SCHEMAS = [
    "AADSignInEventsBeta",
    "AADSpnSignInEventsBeta",
    "AlertEvidence",
    "AlertInfo",
    "BehaviorEntities",
    "BehaviorInfo",
    "CloudAppEvents",
    "DeviceEvents",
    "DeviceFileCertificateInfo",
    "DeviceFileEvents",
    "DeviceImageLoadEvents",
    "DeviceInfo",
    "DeviceLogonEvents",
    "DeviceNetworkEvents",
    "DeviceNetworkInfo",
    "DeviceProcessEvents",
    "DeviceRegistryEvents",
    "DeviceTvmHardwareFirmware",
    "DeviceTvmInfoGathering",
    "DeviceTvmInfoGatheringKB",
    "DeviceTvmSecureConfigurationAssessment",
    "DeviceTvmSecureConfigurationAssessmentKB",
    "DeviceTvmSoftwareEvidenceBeta",
    "DeviceTvmSoftwareInventory",
    "DeviceTvmSoftwareVulnerabilities",
    "DeviceTvmSoftwareVulnerabilitiesKB",
    "EmailAttachmentInfo",
    "EmailEvents",
    "EmailPostDeliveryEvents",
    "EmailUrlInfo",
    "IdentityDirectoryEvents",
    "IdentityInfo",
    "IdentityLogonEvents",
    "IdentityQueryEvents",
    "UrlClickEvents",
]


class KQLDataType(Enum):
    Bool = auto()
    DateTime = auto()
    Dynamic = auto()
    Guid = auto()
    Int = auto()
    Long = auto()
    Real = auto()
    String = auto()
    Timespan = auto()
    Decimal = auto()
    Boolean = auto()
    List = auto()

    def __str__(self):
        return f"{self.name.lower()}"


def map_to_kql_datatype(datatype: str) -> KQLDataType:
    if datatype == "string":
        return KQLDataType.String
    elif datatype == "datetime":
        return KQLDataType.DateTime
    elif datatype == "dynamic":
        return KQLDataType.Dynamic
    elif datatype == "guid":
        return KQLDataType.Guid
    elif datatype == "int":
        return KQLDataType.Int
    elif datatype == "long":
        return KQLDataType.Long
    elif datatype == "real":
        return KQLDataType.Real
    elif datatype == "timespan":
        return KQLDataType.Timespan
    elif datatype == "decimal":
        return KQLDataType.Decimal
    elif datatype == "boolean" or datatype == "bool":
        return KQLDataType.Boolean
    elif datatype == "list":
        return KQLDataType.Dynamic


class BaseMgmtQuery:
    query: str

    def verify_query(self) -> bool:
        return self.query.strip().startswith(".")


class CreateTableQuery(BaseMgmtQuery):
    def __init__(self, client: KustoClient, table: str) -> None:
        self.table = table
        self.client = client
        self.query = f".create table {self.table} (\n"

        if not self.verify_query():
            logger.error(f"Invalid mgmt syntax: '{self.query[0:-2]}...'")
            exit(1)

    def prettify_query(self) -> str:
        return (
            self.query.replace(".create", colored(".create", "light_blue"))
            .replace("table", colored("table", "light_blue"))
            .replace("string", colored("string", "yellow"))
            .replace("datetime", colored("datetime", "yellow"))
            .replace("dynamic", colored("dynamic", "yellow"))
            .replace("guid", colored("guid", "yellow"))
            .replace("int", colored("int", "yellow"))
            .replace("long", colored("long", "yellow"))
            .replace("decimal", colored("decimal", "yellow"))
            .replace("boolean", colored("boolean", "yellow"))
            .replace("timespan", colored("timespan", "yellow"))
            .replace("real", colored("real", "yellow"))
            .replace("(", colored("(", "light_red"))
            .replace(")", colored(")", "light_red"))
        )

    def add_column(self, key: str, datatype: KQLDataType, last=False):
        self.query += (
            f"\t{key}: {datatype},\n" if not last else f"\t{key}: {datatype}\n"
        )
        return self

    def close(self):
        if self.query.endswith(",\n"):
            self.query = self.query[0:-2]

        self.query += "\n)"
        return self

    def execute(self) -> KustoResponseDataSet:
        if not self.query.endswith(")"):
            if self.query.endswith(",\n"):
                self.query = self.query[0:-2]
            self.query += "\n)"

        response = self.client.execute_mgmt(database=DATABASE, query=self.query)
        return response


def get_advanced_hunting_schema_file_path(schema: str) -> str:
    return f"{ADVANCED_HUNTING_SCHEMA_FILES_LOCATION}/advanced-hunting-{schema.lower()}-table.md"


def parse_column(line: str) -> Tuple[str, str]:
    schema_values = line.split("|")[1:3]

    key = schema_values[0].strip().replace("`", "").replace("*", "").strip()
    if len(key.split(" ")) > 1:
        key = key.split(" ")[0]

    datatype = schema_values[1].strip().replace("`", "").strip()
    return (key, datatype)


def get_lines(path: str) -> List[str]:
    with open(path) as file:
        return [line.strip() for line in file]


def skip_line(line_number: int, start_column_index: int, line: str) -> bool:
    # Skip the line after the table header
    if line_number == (start_column_index + 1):
        return True

    # Skip weird lines like ||||
    if "`" not in line or line == "||||":
        return True

    return False


def end_of_table(line: str) -> bool:
    # End of table, stop parsing
    if not line.startswith("|"):
        return True

    return False


def parse_schemas_and_ingest(client: KustoClient):
    for schema in ADVANCED_HUNTING_SCHEMAS:
        path = get_advanced_hunting_schema_file_path(schema)
        lines = get_lines(path)

        logger.info(f"Parsing {schema} schema from {path}:")

        parsing = False
        parsed_columns: List[str] = []
        start_column_index = 0

        query = CreateTableQuery(client, schema)
        for i, line in enumerate(lines):
            if (
                "Column name" in line
                and "Data type" in line
                and "Description" in line
                and "|" in line
            ):
                parsing = True
                start_column_index = i
                continue

            if parsing:
                if skip_line(i, start_column_index, line):
                    continue
                if end_of_table(line):
                    break

                (key, datatype) = parse_column(line)
                if not key in parsed_columns:
                    parsed_columns.append(key)
                    query.add_column(key, map_to_kql_datatype(datatype))

        query.close()
        logger.info("Executing following data explorer management command:")
        logger.info(f"\n{query.prettify_query()}")
        query.execute()


def database_exists(db: str) -> bool:
    query = ".show databases"
    response = client.execute_mgmt(database="", query=query)

    for row in response.primary_results[0].rows:
        if row[0] == db:
            return True

    return False


if __name__ == "__main__":
    kcsb = KustoConnectionStringBuilder("http://localhost:8080")
    client = KustoClient(kcsb)

    if not database_exists("AdvancedHunting"):
        query = """
            .create database AdvancedHunting persist (
                @"/kustodata/dbs/AdvancedHunting/md",
                @"/kustodata/dbs/AdvancedHunting/data"
            )
        """
        client.execute_mgmt(database="", query=query)

    # Parse schemas and ingest as tables into Kustainer instance
    parse_schemas_and_ingest(client)

    response = client.execute_mgmt(
        database=DATABASE,
        query=".ingest inline into table EmailUrlInfo <| 2017-02-13T11:09:36.7992775Z,Network Message3,http://test3.nl,test3,007",
    )
