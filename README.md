# Entities
Create C# entity and DTO classes for a SQL Server table or view.

## Description

This is a quick-and-dirty implementation to create EF entity classes and DTOs from a SQL Server table or view.

## SQL Server

To simplify the process, a SQL view is created to provide the attributes of each column in the table or view:

- Ordered by COLUMN_ID, the first row is 0 which simply includes the descriptive text (if defined) of the database object and its type (table or view).
- Database, schema, and table names
- Column index and name, data type attributes
- Column comment, default value, and check constraint
- Column attributes such as nullability and identity

__Note:__ The database user must have "VIEW DEFINITION" granted to read the contents of the default and check constraint values for __each table__.

## Python

The script was created using Python 3.9 with the PyODBC package installed.

1. The script retrieves the column details for the specified table (or view) in the database.
2. The columns are iterated through once to generate an entity class which is then written out to a file. The entity class contains:
  - Member declarations.
  - A ToDTO() method to create a DTO instance from the entity instance.
  - A ToString() method to provide custom string output (useful for debugging purposes).
3. The columns are iterated through again to generate a DTO which is also written out to a file.
  - The DTO contains only member declarations.

### Usage

```
python entity.py --server X --database Y --table T --entityNamespace MyProject.Entities --dtoNamespace MyProject.Dtos --entityFolder Entities --dtoFolder DTOs --username U --password P
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| --drivers | List the ODBC drivers available to PyODBC. If given, execution is stopped afterwards. | |
| --provider | Specify the ODBC driver to use. | _ODBC Driver 17 for SQL Server_ |
| --server | Name of the SQL Server instance. | |
| --database | Name of the database. | |
| --username | Username to access the database and table/view. If not used, a trusted connection is assumed. | |
| --password | Password to the user login. May be prompted if not passed in. | |
| --schema | Schema the table/view is stored in. | _DBO_ |
| --table | The table or view to create from. | |
| --entityNamespace | The C# namespace of the entity object. | _Entities_ |
| --entityFolder | The folder to write the entity class to.  | _Current folder_ |
| --dtoNamespace | The C# namespace of the entity object. | _Dtos_ |
| --dtoFolder | The folder to write the DTO class to. | _Current folder_ |

## TODO

- Implement parsing of the check constraints.
