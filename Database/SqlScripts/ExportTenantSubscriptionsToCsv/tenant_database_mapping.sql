SET NOCOUNT ON;

SELECT
    t.[ID]                  AS TenantID,
    t.[CompanyName],
    d.[Name]                AS ConfiguredDatabaseName
FROM [bsone_core].[dbo].[Tenant] t WITH (NOLOCK)
LEFT JOIN [bsone_core].[dbo].[Tenant.Credential] tc WITH (NOLOCK)
    ON tc.[TenantID] = t.[ID]
LEFT JOIN [bsone_core].[dbo].[Server.Instance.Database] d WITH (NOLOCK)
    ON d.[ID] = tc.[DatabaseID]
ORDER BY t.[ID];
