-- IMPORTANT: The user querying the view must have VIEW DEFINITION granted
-- to them to view the DEFAULT VALUE and CHECK CONSTRAINTS.

CREATE OR ALTER VIEW TABLE_PROPERTIES_VW AS
SELECT
	'TABLE'								OBJECT_TYPE,
	UPPER(DB_NAME())					DATABASE_NAME,
	UPPER(S.name)						SCHEMA_NAME,
	UPPER(T.name)						TABLE_NAME,
	0									COLUMN_ID,
	NULL								COLUMN_NAME,
	NULL								FULL_DATA_TYPE,
	NULL								DATA_TYPE,
	NULL								MAX_LENGTH,
	CONVERT(NVARCHAR(MAX), P.value)		COMMENT,
	NULL								DEFAULT_VALUE,
	NULL								CHECK_CONSTRAINTS,
	NULL								IS_NULLABLE,
	NULL								IS_IDENTITY,
	NULL								IS_ROWGUIDCOL
FROM SYS.tables T
INNER JOIN SYS.schemas S ON (T.schema_id = S.schema_id)
INNER JOIN SYS.extended_properties P ON (
	T.object_id = P.major_id
	AND P.minor_id = 0
	AND P.class = 1
	AND P.name = 'MS_Description')
UNION SELECT
	'TABLE'								OBJECT_TYPE,
	UPPER(DB_NAME())					DATABASE_NAME,
	UPPER(S.name)						SCHEMA_NAME,
	UPPER(T.name)						TABLE_NAME,
	C.column_id							COLUMN_ID,
	UPPER(C.name)						COLUMN_NAME,
	CASE
		WHEN C.max_length = -1 THEN UPPER(CONCAT(DT.name, '(MAX)'))
		WHEN DT.name IN ('BIT', 'CHAR', 'NCHAR', 'NVARCHAR', 'VARCHAR', 'VARBINARY', 'SYSNAME') THEN UPPER(CONCAT(DT.name, '(', C.max_length, ')'))
		WHEN DT.name IN ('DECIMAL', 'FLOAT', 'REAL', 'NUMERIC', 'MONEY') THEN
			IIF(C.scale = 0,
				UPPER(CONCAT(DT.name, '(', C.precision, ')')),
				UPPER(CONCAT(DT.name, '(', C.precision, ',', C.scale, ')')))
		ELSE UPPER(DT.name)
	END									FULL_DATA_TYPE,
	UPPER(DT.name)						DATA_TYPE,
	CASE
		WHEN DT.name IN ('CHAR', 'NCHAR', 'NTEXT', 'NVARCHAR', 'TEXT', 'VARBINARY', 'VARCHAR', 'XML') THEN C.max_length
		ELSE NULL
	END									MAX_LENGTH,
	CONVERT(NVARCHAR(MAX), P.value)		COMMENT,
	DF.definition						DEFAULT_VALUE,
	CK.definition						CHECK_CONSTRAINTS,
	IIF(C.IS_NULLABLE = 0, 'N', 'Y')	IS_NULLABLE,
	IIF(C.IS_IDENTITY = 0, 'N', 'Y')	IS_IDENTITY,
	IIF(C.IS_ROWGUIDCOL = 0, 'N', 'Y')	IS_ROWGUIDCOL
FROM SYS.tables T
INNER JOIN SYS.schemas S ON (T.schema_id = S.schema_id)
INNER JOIN SYS.columns C ON (T.object_id = C.object_id)
INNER JOIN SYS.types DT ON (C.system_type_id = DT.system_type_id AND DT.name NOT IN ('SYSNAME'))
LEFT OUTER JOIN SYS.extended_properties P ON (
	C.object_id = P.major_id
	AND C.column_id = P.minor_id
	AND P.class = 1
	AND P.name = 'MS_Description')
LEFT OUTER JOIN SYS.default_constraints DF on (C.object_id = DF.parent_object_id AND C.column_id = DF.parent_column_id)
LEFT OUTER JOIN SYS.check_constraints CK on (C.object_id = CK.parent_object_id AND C.column_id = CK.parent_column_id)
UNION SELECT
	'VIEW'								OBJECT_TYPE,
	UPPER(DB_NAME())					DATABASE_NAME,
	UPPER(S.name)						SCHEMA_NAME,
	UPPER(T.name)						TABLE_NAME,
	0									COLUMN_ID,
	NULL								COLUMN_NAME,
	NULL								FULL_DATA_TYPE,
	NULL								DATA_TYPE,
	NULL								MAX_LENGTH,
	CONVERT(NVARCHAR(MAX), P.value)		COMMENT,
	NULL								DEFAULT_VALUE,
	NULL								CHECK_CONSTRAINTS,
	NULL								IS_NULLABLE,
	NULL								IS_IDENTITY,
	NULL								IS_ROWGUIDCOL
FROM SYS.views T
INNER JOIN SYS.schemas S ON (T.schema_id = S.schema_id)
INNER JOIN SYS.extended_properties P ON (
	T.object_id = P.major_id
	AND P.minor_id = 0
	AND P.class = 1
	AND P.name = 'MS_Description')
UNION SELECT
	'VIEW'								OBJECT_TYPE,
	UPPER(DB_NAME())					DATABASE_NAME,
	UPPER(S.name)						SCHEMA_NAME,
	UPPER(T.name)						TABLE_NAME,
	C.column_id							COLUMN_ID,
	UPPER(C.name)						COLUMN_NAME,
	CASE
		WHEN C.max_length = -1 THEN UPPER(CONCAT(DT.name, '(MAX)'))
		WHEN DT.name IN ('BIT', 'CHAR', 'NCHAR', 'NVARCHAR', 'VARCHAR', 'VARBINARY', 'SYSNAME') THEN UPPER(CONCAT(DT.name, '(', C.max_length, ')'))
		WHEN DT.name IN ('DECIMAL', 'FLOAT', 'REAL', 'NUMERIC', 'MONEY') THEN
			IIF(C.scale = 0,
				UPPER(CONCAT(DT.name, '(', C.precision, ')')),
				UPPER(CONCAT(DT.name, '(', C.precision, ',', C.scale, ')')))
		ELSE UPPER(DT.name)
	END									FULL_DATA_TYPE,
	UPPER(DT.name)						DATA_TYPE,
	CASE
		WHEN DT.name IN ('CHAR', 'NCHAR', 'NTEXT', 'NVARCHAR', 'TEXT', 'VARBINARY', 'VARCHAR', 'XML') THEN C.max_length
		ELSE NULL
	END									MAX_LENGTH,
	CONVERT(NVARCHAR(MAX), P.value)		COMMENT,
	DF.definition						DEFAULT_VALUE,
	CK.definition						CHECK_CONSTRAINTS,
	IIF(C.IS_NULLABLE = 0, 'N', 'Y')	IS_NULLABLE,
	IIF(C.IS_IDENTITY = 0, 'N', 'Y')	IS_IDENTITY,
	IIF(C.IS_ROWGUIDCOL = 0, 'N', 'Y')	IS_ROWGUIDCOL
FROM SYS.views T
INNER JOIN SYS.schemas S ON (T.schema_id = S.schema_id)
INNER JOIN SYS.columns C ON (T.object_id = C.object_id)
INNER JOIN SYS.types DT ON (C.system_type_id = DT.system_type_id AND DT.name NOT IN ('SYSNAME'))
LEFT OUTER JOIN SYS.extended_properties P ON (
	C.object_id = P.major_id
	AND C.column_id = P.minor_id
	AND P.class = 1
	AND P.name = 'MS_Description')
LEFT OUTER JOIN SYS.default_constraints DF on (C.object_id = DF.parent_object_id AND C.column_id = DF.parent_column_id)
LEFT OUTER JOIN SYS.check_constraints CK on (C.object_id = CK.parent_object_id AND C.column_id = CK.parent_column_id)
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'List table and view properties.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Type of database object.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'OBJECT_TYPE'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Database name.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'DATABASE_NAME'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Schema name.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'SCHEMA_NAME'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Table or view name.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'TABLE_NAME'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Column number (0 indicates table/view comment).',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'COLUMN_ID'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Column name.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'COLUMN_NAME'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Formatted data type.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'FULL_DATA_TYPE'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Column data type.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'DATA_TYPE'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Maximum length of text columns.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'MAX_LENGTH'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Comment text.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'COMMENT'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Default value for the column if assigned.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'DEFAULT_VALUE'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Check constrants on the column value if assigned.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'CHECK_CONSTRAINTS'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Flag to indicate if column is nullable or not.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'IS_NULLABLE'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Flag to indicate if this is the identity column for the table.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'IS_IDENTITY'
GO

EXEC sys.sp_addextendedproperty
	@name = N'MS_Description', @value = N'Flag to indicate if this is the row GUID for the table.',
	@level0type = N'SCHEMA', @level0name = N'DBO',
	@level1type = N'VIEW', @level1name = N'TABLE_PROPERTIES_VW',
	@level2type = N'COLUMN', @level2name = N'IS_ROWGUIDCOL'
GO

GRANT SELECT ON TABLE_PROPERTIES_VW TO PUBLIC
GO

SELECT * FROM TABLE_PROPERTIES_VW
WHERE SCHEMA_NAME = 'DBO' AND TABLE_NAME = 'TABLE_PROPERTIES_VW'
ORDER BY COLUMN_ID
GO

SELECT * FROM TABLE_PROPERTIES_VW
WHERE SCHEMA_NAME = 'DBO' AND TABLE_NAME = 'X'
ORDER BY COLUMN_ID
GO

-- SELECT * FROM TABLE_PROPERTIES_VW
-- ORDER BY DATABASE_NAME, TABLE_NAME, COLUMN_ID
-- GO
