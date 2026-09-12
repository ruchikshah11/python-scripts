SET NOCOUNT ON;

SELECT
    t.[ID]                  AS TenantID,
    t.[CompanyName],
    d.[Name]                AS ConfiguredDatabaseName
FROM [bsone_core].[dbo].[Tenant] t
LEFT JOIN [bsone_core].[dbo].[Tenant.Credential] tc
    ON tc.[TenantID] = t.[ID]
LEFT JOIN [bsone_core].[dbo].[Server.Instance.Database] d
    ON d.[ID] = tc.[DatabaseID]
ORDER BY t.[ID];
