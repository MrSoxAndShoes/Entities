# python entity.py --server X --database Y --username Z --password P --table T --entityNamespace MyProject.Entities --dtoNamespace MyProject.Dtos --entityFolder Entities --dtoFolder DTOs

import os, sys, re, argparse
import pyodbc

# Construct the script argument parser
def initParser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description = "Create C# entity and DTO classes from a SQL Server database table or view."
	)

	parser.add_argument("--server", required = True, help = "Name of the SQL Server instance.")
	parser.add_argument("--database", required = True, help = "Name of the database.")
	parser.add_argument("--username", required = True, help = "Username to access the database and table/view.")
	parser.add_argument("--password", required = True, help = "Password to the user login.")
	parser.add_argument("--schema", default = "DBO", help = "Schema the table/view is stored in. Default is 'DBO'.")
	parser.add_argument("--table", required = True, help = "The table or view to create from.")
	parser.add_argument("--entityNamespace", default = "Entities", help = "The C# namespace of the entity object. Default is 'Entities'.")
	parser.add_argument("--entityFolder", default = os.getcwd(), help = "The folder to write the entity class to. Default is current folder.")
	parser.add_argument("--dtoNamespace", default = "Dtos", help = "The C# namespace of the entity object. Default is 'Dtos'.")
	parser.add_argument("--dtoFolder", default = os.getcwd(), help = "The folder to write the DTO class to. Default is current folder.")

	return parser

# Rename plural-named table objects to singular
def pluralToSingular(pluralName):
	singular = re.sub("IES$", "Y", pluralName)
	singular = re.sub("(BATCH|CLASS|SEARCH|STATUS|TAX)ES$", r"\1", singular)
	singular = re.sub("SES$", "SE", singular)
	singular = re.sub("([^SU])S$", r"\1", singular)
	return singular

# Transform the table name to Pascal case
def snakeToPascal(snakeName):
	# snakeName = re.sub(r"^VW_(.+)$|^(.+)_VW$", r"\1_VIEW_RESULT", snakeName)
	# snakeName = re.sub(r"(.+)E*S$", r"\1", snakeName)
	return "".join([w.title() for w in snakeName.split("_")])

# Clean up the default value string given by SQL Server
def cleanDefaultValue(columnDefaultValue) -> str:
	# rmeove enclosing parentheses
	match = re.search(r"^\(+", columnDefaultValue)
	if match:
		s_len = len(match.group(0))
		return columnDefaultValue[s_len:-s_len]
	else:
		return columnDefaultValue

# TODO: Implement parsing of check constraints
def parseCheckConstraints(columnCheckConstraints) -> str:
	return columnCheckConstraints

# Convert SQL Server data type to comparable C# data type for an entity class
def sqlTypeToEntityType(sqlDataType, maxLength) -> str:
	if sqlDataType in ["DATE"]:
		return "DateOnly"
	elif sqlDataType in ["DATETIME", "DATETIME2", "DATETIMEOFFSET", "SMALLDATETIME"]:
		return "DateTime"
	elif sqlDataType in ["DECIMAL", "MONEY", "SMALLMONEY"]:
		return "decimal"
	elif sqlDataType in ["FLOAT", "NUMERIC", "REAL"]:
		return "double"
	elif sqlDataType in ["UNIQUEIDENTIFIER"]:
		return "Guid"
	elif sqlDataType in ["INT"]:
		return "int"
	elif sqlDataType in ["BIGINT"]:
		return "long"
	elif sqlDataType in ["SMALLINT", "TINYINT"]:
		return "short"
	elif sqlDataType in ["CHAR", "NCHAR", "NTEXT", "NVARCHAR", "VARCHAR"]:
		if maxLength > 1:
			return "string"
		else:
			return "char"
	elif sqlDataType in ["TIME"]:
		return "TimeOnly"

	# Not handled: ["BINARY", "BIT", "GEOGRAPHY", "GEOMETRY", "HIERARCHYID", "IMAGE", "SQL_VARIANT", "SYSNAME", "TEXT", "TIMESTAMP", "VARBINARY", "XML"]
	return "object"

# Convert SQL Server data type to comparable C# data type for a DTO
# (Difference here is conversion of Y/N string to boolean data type.)
def sqlTypeToTransferType(sqlDataType, maxLength, defaultValue) -> str:
	if sqlDataType in ["DATE"]:
		return "DateOnly"
	elif sqlDataType in ["DATETIME", "DATETIME2", "DATETIMEOFFSET", "SMALLDATETIME"]:
		return "DateTime"
	elif sqlDataType in ["DECIMAL", "MONEY", "SMALLMONEY"]:
		return "decimal"
	elif sqlDataType in ["FLOAT", "NUMERIC", "REAL"]:
		return "double"
	elif sqlDataType in ["UNIQUEIDENTIFIER"]:
		return "Guid"
	elif sqlDataType in ["INT"]:
		return "int"
	elif sqlDataType in ["BIGINT"]:
		return "long"
	elif sqlDataType in ["SMALLINT", "TINYINT"]:
		return "short"
	elif sqlDataType in ["TIME"]:
		return "TimeOnly"
	elif sqlDataType in ["CHAR", "NCHAR", "NTEXT", "NVARCHAR", "VARCHAR"]:
		if int(maxLength) > 1:
			return "string"
		else:
			# assume if the default value for a 1-character column is 'N' or
			# 'Y', it's a boolean
			return "bool" if defaultValue in ["'N'", "'Y'"] else "char"

	# Data types not handled
	# ["BINARY", "BIT", "GEOGRAPHY", "GEOMETRY", "HIERARCHYID", "IMAGE", "SQL_VARIANT", "SYSNAME", "TEXT", "TIMESTAMP", "VARBINARY", "XML"]
	return "object"

# Create an entity class from the table definition
def createEntity(tableName, schemaName, columns, dtoClassName, namespace = "Entities", dtoNamespace = "Dtos"):

	entity = []
	toDto = []

	entity.append(f"// ReSharper disable InconsistentNaming")
	entity.append("")
	entity.append("using System;")
	entity.append("using System.ComponentModel;")
	entity.append("using System.ComponentModel.DataAnnotations;")
	entity.append("using System.ComponentModel.DataAnnotations.Schema;")
	entity.append("using System.Diagnostics.CodeAnalysis;")
	entity.append("using System.Text;")
	entity.append("")
	entity.append("using Microsoft.EntityFrameworkCore;")
	entity.append("")

	if dtoNamespace == "":
		dtoNamespace = namespace.split(".")[0] + ".Dtos"

	entity.append(f"using {dtoNamespace};")
	entity.append("")
	entity.append(f"namespace {namespace};")
	entity.append("")
	entity.append(f"[Table(\"{tableName}\", Schema = \"{schemaName}\")]")
	entity.append(f"[Description(\"{(columns[0].COMMENT or "")}\")]")

	if columns[0].OBJECT_TYPE == 'VIEW':
		entity.append("[KeyLess]")

	entity.append(f"[ExcludeFromCodeCoverage]")
	entity.append(f"internal sealed class {tableName}")
	entity.append("{")
	entity.append("\t#region Table Columns")
	entity.append("")

	for col in columns:
		if col.COLUMN_ID == 0:
			continue

		entity.append(f"\t[Column(\"{col.COLUMN_NAME}\", TypeName = \"{col.FULL_DATA_TYPE}\")]")
		entity.append(f"\t[Description(\"{(col.COMMENT or "")}\")]")

		if (col.IS_NULLABLE == "N"):
			entity.append("\t[Required(ErrorMessage = \"Value for {0} is required.\")]")

		if col.DEFAULT_VALUE != None:
			colDefaultValue = cleanDefaultValue(col.DEFAULT_VALUE).upper()
		else:
			colDefaultValue = ""

		if int(col.MAX_LENGTH or 0) > 0:
			entity.append(f"\t[StringLength({col.MAX_LENGTH}, ErrorMessage = \"Maximum string length for {{0}} is {{1}} characters.\")]")

		if col.DATA_TYPE in ["CHAR", "NCHAR", "NTEXT", "NVARCHAR", "VARCHAR"]:
			entity.append(f"\t[Unicode({'true' if col.DATA_TYPE[0] == 'N' else 'false'})]")

		# Simple parsing of the default value constraint
		# (prone to failure.)
		if col.DEFAULT_VALUE != None:
			col.DEFAULT_VALUE = cleanDefaultValue(col.DEFAULT_VALUE)

			# default values ending with a closing parentheses would indicate
			# a T-SQL function call, meaning it's a computed value
			if col.DEFAULT_VALUE.endswith(")"):
				entity.append("\t[DatabaseGenerated(DatabaseGeneratedOption.Computed)]")
			# GUID values literal string values greater than 1-character should
			# be wrapped in double-quotes
			elif col.DATA_TYPE == "UNIQUEIDENTIFIER" or int(col.MAX_LENGTH or 0) > 1:
				entity.append(f"\t[DefaultValue(" + col.DEFAULT_VALUE.replace("'", "\"") + ")]")
			# additional elif statements could be added here before defaulting
			else:
				entity.append(f"\t[DefaultValue({col.DEFAULT_VALUE})]")

		# TODO: Implement parsing of check constraints
		if col.CHECK_CONSTRAINTS != None:
			entity.append(f"\t// CHECK_CONSTRAINTS: {col.CHECK_CONSTRAINTS}")

		dataType = sqlTypeToEntityType(col.DATA_TYPE, int(col.MAX_LENGTH or 0))

		if col.OBJECT_TYPE == "VIEW":
			entity.append(f"\t// TODO: The key column is not identified if the database doesn't define one.")
		if (col.IS_IDENTITY == "Y" or col.IS_ROWGUIDCOL == "Y"):
			entity.append(f"\t[Key]")

		if col.IS_NULLABLE == 'N' and dataType == "string":
			entity.append(f"\tpublic {dataType} {col.COLUMN_NAME} {{ get; set; }} = null!;")
		elif col.IS_NULLABLE == 'N':
			entity.append(f"\tpublic {dataType} {col.COLUMN_NAME} {{ get; set; }}")
		else:
			entity.append(f"\tpublic {dataType}? {col.COLUMN_NAME} {{ get; set; }}")

		entity.append("")

		# add member assignment from entity class to DTO
		dtoMemberName = snakeToPascal(col.COLUMN_NAME)
		if dataType == "char" and colDefaultValue in ["'N'", "'Y'"]:
			dtoMemberName = "Is" + dtoMemberName
			if col.IS_NULLABLE == 'Y':
				toDto.append(f"\t\t\t{dtoMemberName} = (({col.COLUMN_NAME} ?? 'Y') == 'Y'),")
			else:
				toDto.append(f"\t\t\t{dtoMemberName} = ({col.COLUMN_NAME} == 'Y'),")
		else:
			toDto.append(f"\t\t\t{dtoMemberName} = {col.COLUMN_NAME},")

	entity.append("\t#endregion")
	entity.append("")

	entity.append(f"\tpublic {dtoClassName} ToDto()")
	entity.append("\t{")
	entity.append(f"\t\treturn new {dtoClassName} {{")
	# append member assignments to the toDto method
	entity += toDto
	entity.append("\t\t};")
	entity.append("\t}")
	entity.append("")

	entity.append("\t// TODO: Format ToString() method output.")
	entity.append("\tpublic override string ToString()")
	entity.append("\t{")
	entity.append("\t\tvar sb = new StringBuilder();")
	entity.append("")

	for col in columns[1:]:
		entity.append(f"\t\tsb.AppendLine($\"{col.COLUMN_NAME}: {{{col.COLUMN_NAME}}}\");")

	entity.append("")
	entity.append("\t\treturn sb.ToString();")
	entity.append("\t}")
	entity.append("}")
	entity.append("")

	return entity

# Create a DTO class from the table definition
def createDto(className, sourceTable, columns, namespace = "Dtos", sourceSchema = "DBO"):

	dto = []

	dto.append("// ReSharper disable InconsistentNaming")
	dto.append("")
	dto.append("using System;")
	dto.append("using System.ComponentModel;")
	dto.append("using System.ComponentModel.DataAnnotations;")
	dto.append("using System.ComponentModel.DataAnnotations.Schema;")
	dto.append("using System.Diagnostics.CodeAnalysis;")
	dto.append("")
	dto.append(f"namespace {namespace};")
	dto.append("")
	dto.append(f"[Table(\"{sourceTable}\", Schema = \"{sourceSchema}\")]")
	dto.append(f"[Description(\"({columns[0].COMMENT} or "")\")]")
	dto.append(f"[ExcludeFromCodeCoverage]")
	dto.append(f"public sealed class {className} : DtoBase")
	dto.append("{")

	for col in columns:
		if col.COLUMN_ID == 0:
			continue

		dto.append(f"\t[Column(\"{col.COLUMN_NAME}\", TypeName = \"{col.FULL_DATA_TYPE}\")]")
		dto.append(f"\t[Description(\"{(col.COMMENT or "")}\")]")

		if (col.IS_NULLABLE == "N"):
			dto.append("\t[Required(ErrorMessage = \"Value for {0} is required.\")]")

		if col.DEFAULT_VALUE != None:
			colDefaultValue = cleanDefaultValue(col.DEFAULT_VALUE).upper()
		else:
			colDefaultValue = ""

		if int(col.MAX_LENGTH or 0) > 0 and colDefaultValue not in ['N', 'Y']:
			dto.append(f"\t[StringLength({col.MAX_LENGTH}, ErrorMessage = \"Maximum string length for {{0}} is {{1}} characters.\")]")

		# TODO: Implement parsing of check constraints
		if col.CHECK_CONSTRAINTS != None:
			dto.append(f"\t// CHECK_CONSTRAINTS: {col.CHECK_CONSTRAINTS}")

		dataType = sqlTypeToEntityType(col.DATA_TYPE, int(col.MAX_LENGTH or 0))

		# Simple parsing of the default value constraint
		# (prone to failure.)
		if col.DEFAULT_VALUE != None:
			# default values ending with a closing parentheses would indicate
			# a T-SQL function call, meaning it's a computed value that needs
			# to be converted to C# (if possible).
			if colDefaultValue.endswith(")"):
				dto.append("\t// TODO: Convert to C#")
				dto.append("\t[DefaultValue(\"" + colDefaultValue.replace("'", "\"") + "\")]")
			# GUID values literal string values greater than 1-character should
			# be wrapped in double-quotes
			elif col.DATA_TYPE == "UNIQUEIDENTIFIER" or (col.MAX_LENGTH != None and int(col.MAX_LENGTH) > 1):
				dto.append(f"\t[DefaultValue(" + col.DEFAULT_VALUE.replace("'", "\"") + ")]")
			elif col.DEFAULT_VALUE.upper() == "'N'":
				dto.append("\t[DefaultValue(false)]")
			elif col.DEFAULT_VALUE.upper() == "'Y'":
				dto.append("\t[DefaultValue(true)]")
			# additional elif statements could be added here before defaulting
			else:
				dto.append(f"\t[DefaultValue({col.DEFAULT_VALUE})]")

		dataType = sqlTypeToTransferType(col.DATA_TYPE, int(col.MAX_LENGTH or 0), colDefaultValue)

		if dataType == "bool" and col.IS_NULLABLE == 'N':
			dto.append(f"\tpublic {dataType} Is{snakeToPascal(col.COLUMN_NAME)} {{ get; set; }}")
		elif dataType == "bool":
			dto.append(f"\tpublic {dataType}? Is{snakeToPascal(col.COLUMN_NAME)} {{ get; set; }}")
		elif col.IS_NULLABLE == 'N' and dataType == "string":
			dto.append(f"\tpublic {dataType} {snakeToPascal(col.COLUMN_NAME)} {{ get; set; }} = null!;")
		elif col.IS_NULLABLE == 'N':
			dto.append(f"\tpublic {dataType} {snakeToPascal(col.COLUMN_NAME)} {{ get; set; }}")
		else:
			dto.append(f"\tpublic {dataType}? {snakeToPascal(col.COLUMN_NAME)} {{ get; set; }}")

		dto.append("")

	dto.pop() # remove blank line inserted after last member declaration
	dto.append("}")
	dto.append("")

	return dto

def main() -> int:

	parser = initParser()
	args = parser.parse_args()

	connectionString = ";".join([
		f"DRIVER={{ODBC Driver 17 for SQL Server}}",
		f"SERVER={args.server}",
		f"DATABASE={args.database}",
		f"UID={args.username}",
		f"PWD={args.password}"
		# "Encrypt=False"
	])

	sqlQuery = " ".join([
		"SELECT * FROM TABLE_PROPERTIES_VW",
		f"WHERE DATABASE_NAME = '{args.database}' AND SCHEMA_NAME = '{args.schema}' AND TABLE_NAME = '{args.table}'",
		"ORDER BY COLUMN_ID"
	])

	# connect to the SQL Server database and query the table properties view
	# to get column attributes
	with pyodbc.connect(connectionString) as conn:
		with conn.cursor() as cursor:
			tableColumns = cursor.execute(sqlQuery).fetchall()

	entityFileName = os.path.join(args.entityFolder, f"{args.table}.cs")

	dtoClassName = snakeToPascal(pluralToSingular(args.table))
	dtoFileName = os.path.join(args.dtoFolder, f"{dtoClassName}.cs")

	with open(entityFileName, "w") as entityFile:
		print(f"Creating '{entityFileName}'...", end = "")
		entityFile.writelines("\n".join(createEntity(
			tableName = args.table,
			schemaName = args.schema,
			namespace = args.entityNamespace,
			dtoClassName = dtoClassName,
			dtoNamespace = args.dtoNamespace,
			columns = tableColumns,
		)))
		print("done")

	with open(dtoFileName, "w") as dtoFile:
		print(f"Creating '{dtoFileName}'...", end = "")
		dtoFile.writelines("\n".join(createDto(
			className = dtoClassName,
			namespace = args.dtoNamespace,
			sourceTable = args.table,
			sourceSchema = args.schema,
			columns = tableColumns
		)))
		print("done")

	return 0

if __name__ == '__main__':
	sys.exit(main())

# end of script
